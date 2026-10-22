"""Append-only audit trail of agent-loop activity: output/audit_trail.json.

One record per chat turn: when it happened, every tool the agent called (short args and result), which model
answered, usage, and why the turn stopped. The file is a JSON array that only ever grows: a new record is
written over the closing "]" and the array is closed again. Existing records are never rewritten, reordered
or deleted, and nothing in the app clears the file between runs or restarts.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart, ToolReturnPart

from models import AuditRecord, AuditStep

AUDIT_PATH = Path(os.getenv("AUDIT_PATH", Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"))
SHORT = 160  # max characters kept for args, results and the shopper's message
_lock = threading.Lock()
log = logging.getLogger("campus_customs.audit")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def short(value: object, limit: int = SHORT) -> str:
    """Compact one-line text for the log."""
    if not isinstance(value, str):
        try:
            value = json.dumps(value, default=lambda o: o.model_dump() if hasattr(o, "model_dump") else str(o))
        except (TypeError, ValueError):
            value = str(value)
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def steps_from(messages: list[ModelMessage]) -> list[AuditStep]:
    """Pair each tool call with its result, in order. The final_result 'tool' is PydanticAI's structured-output step."""
    calls: dict[str, AuditStep] = {}
    steps: list[AuditStep] = []
    for m in messages:
        for part in m.parts:
            if isinstance(part, ToolCallPart):
                step = AuditStep(
                    time=(m.timestamp.isoformat(timespec="milliseconds") if getattr(m, "timestamp", None) else now()),
                    tool=part.tool_name,
                    args=short(part.args),
                )
                calls[part.tool_call_id] = step
                steps.append(step)
            elif isinstance(part, ToolReturnPart) and part.tool_call_id in calls:
                calls[part.tool_call_id].result = short(part.content)
    return steps


def finish_reason(messages: list[ModelMessage]) -> str | None:
    responses = [m for m in messages if isinstance(m, ModelResponse)]
    return responses[-1].finish_reason if responses else None


def append(record: AuditRecord) -> None:
    """Append one record to the JSON array without touching what is already there."""
    entry = json.dumps(record.model_dump(exclude_none=True), ensure_ascii=False, indent=2)
    entry = "\n".join("  " + line for line in entry.splitlines())
    with _lock:
        try:
            AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
            if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
                AUDIT_PATH.write_text("[\n" + entry + "\n]\n", encoding="utf-8")
                return
            with AUDIT_PATH.open("r+b") as f:
                # Find the closing bracket at the end of the file (skipping trailing whitespace).
                f.seek(0, os.SEEK_END)
                pos = f.tell()
                while pos > 0:
                    pos -= 1
                    f.seek(pos)
                    ch = f.read(1)
                    if not ch.isspace():
                        break
                if ch != b"]":
                    # Never "repair" by wiping: leave the file alone and report it.
                    log.error("audit_trail.json does not end with ']'; record not written")
                    return
                f.seek(pos)
                f.write(b",\n" + entry.encode("utf-8") + b"\n]\n")
                f.truncate()  # only drops the old trailing "]\n" we just wrote past; earlier records are untouched
        except OSError:
            log.exception("could not write audit record")  # auditing must never break the shop

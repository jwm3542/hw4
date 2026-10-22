"""Chat safety (Problem 9): rate limits, input screening, and an output guard. Enforced in code, not just the prompt."""

from __future__ import annotations

import os
import re
import time
import unicodedata
from collections import defaultdict, deque

# ---------------------------------------------------------------- rate limits

PER_MIN = int(os.getenv("CHAT_TURNS_PER_IP_MIN", "8"))  # burst limit per visitor
PER_DAY = int(os.getenv("CHAT_TURNS_PER_IP_DAY", "150"))  # per visitor per 24 h
SITE_PER_DAY = int(os.getenv("CHAT_TURNS_PER_DAY", "2000"))  # whole site per 24 h (protects the Portkey bill)
DAY = 24 * 3600
_HITS: defaultdict[str, deque[float]] = defaultdict(deque)
_SITE: deque[float] = deque()


def check_rate(visitor: str) -> str | None:
    """Record one chat turn for this visitor. Returns a friendly refusal if over a limit, else None."""
    now = time.time()
    hits = _HITS[visitor]
    while hits and now - hits[0] > DAY:
        hits.popleft()
    while _SITE and now - _SITE[0] > DAY:
        _SITE.popleft()
    if sum(1 for t in hits if now - t < 60) >= PER_MIN:
        return "Whoa, slow down, speed racer! Give it a minute and ask again."
    if len(hits) >= PER_DAY:
        return "You've hit today's chat limit. Browse the Products page or call (475) 301-4205 and we'll help you out."
    if len(_SITE) >= SITE_PER_DAY:
        return "Our chat helper is taking a breather. Please try again later or call (475) 301-4205."
    hits.append(now)
    _SITE.append(now)
    return None


# ---------------------------------------------------------------- input screening

_INJECTION = [
    r"ignore (all |any |your |the )?(previous |prior |above )?(instructions|rules|prompt)",
    r"disregard (all |your |the )?(previous |prior )?(instructions|rules)",
    r"(reveal|show|print|repeat|tell me) (me )?(your |the )?(system |hidden |secret )?(prompt|instructions)",
    r"system prompt",
    r"you are now\b",
    r"\b(developer|dan|god) mode\b",
    r"\b(api[ _-]?key|portkey|password[ _-]?hash|pbkdf2)\b",
    r"\b(other|another) (customer|user)s?'?s? (email|info|data|password|account)",
]
_INJECTION_RE = re.compile("|".join(_INJECTION), re.IGNORECASE)


def clean_input(text: str) -> str:
    """Normalize unicode tricks and drop control characters (keeps newlines)."""
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if ch in "\n\t" or unicodedata.category(ch)[0] != "C").strip()


def screen_input(text: str) -> list[str]:
    """Return the suspicious phrases found (empty list = looks normal). Flagged turns get a fixed refusal."""
    return sorted({m.group(0).lower() for m in _INJECTION_RE.finditer(text)})


# ---------------------------------------------------------------- output guard

SAFE_REFUSAL = (
    "I can't share that, but I'd love to help you find some Yale gear. "
    "Ask me about hoodies, sizes, prices, or what's in stock!"
)


def _secret_markers() -> list[str]:
    markers = ["pbkdf2_sha256$", "## Honesty rules", "## Safety basics", "# Campus Customs Shopping Assistant"]
    key = os.getenv("PORTKEY_API_KEY", "")
    if len(key) >= 8:
        markers.append(key)
    return markers


def guard_output(reply: str) -> tuple[str, bool]:
    """Block a reply that leaks secrets or the system prompt. Returns (reply to send, was_blocked)."""
    if any(m and m in reply for m in _secret_markers()):
        return SAFE_REFUSAL, True
    return reply, False


def is_content_filter(exc: BaseException) -> bool:
    """True if the model provider refused the prompt (e.g. Azure content filter), on every fallback tier."""
    return "content_filter" in repr(exc) or "content management policy" in repr(exc)

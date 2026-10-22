"""Customer memory: chat history in the chat_messages table for logged-in shoppers.

Row shape (matches the seed data): user_id, role ('user' | 'assistant'), content, products_json, created_at.
products_json holds the product cards shown with an assistant reply (null when none).
Guests are never written here.
"""

from __future__ import annotations

import json

from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart

import tools
from models import Customer, HistoryMessage, ProductCard

RELOAD_LIMIT = 50  # messages shown in the chat panel on return
AGENT_LIMIT = 20  # most recent messages replayed to the agent as memory


def load_customer(user_id: int) -> Customer | None:
    """Only the fields the agent is allowed to see. password_hash is never selected."""
    with tools.db() as conn:
        row = conn.execute(
            "SELECT id, first_name, last_name, name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    if row is None:
        return None
    first = row["first_name"] or row["name"].split(" ")[0]
    last = row["last_name"] or " ".join(row["name"].split(" ")[1:])
    return Customer(
        user_id=row["id"], first_name=first, last_name=last, name=row["name"], email=row["email"],
        member_since=row["created_at"],
    )


def save_turn(user_id: int, user_text: str, reply: str, cards: list[ProductCard]) -> None:
    """Write the shopper's message and the assistant's reply as two rows."""
    products_json = json.dumps([c.model_dump() for c in cards]) if cards else None
    with tools.db(write=True) as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, user_text),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply, products_json),
        )


def _recent_rows(user_id: int, limit: int) -> list:
    with tools.db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages WHERE user_id = ? "
            "ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return list(reversed(rows))


def _product_ids(products_json: str | None) -> list[str]:
    try:
        return [p["product_id"] for p in json.loads(products_json or "[]") if isinstance(p, dict) and "product_id" in p]
    except (ValueError, TypeError):
        return []


def history_for_ui(user_id: int) -> list[HistoryMessage]:
    """Saved chat for the panel. Cards are rebuilt from the DB by product_id, so prices/stock/images are current."""
    return [
        HistoryMessage(
            role=r["role"], content=r["content"], products=tools.get_cards(_product_ids(r["products_json"])),
            created_at=r["created_at"],
        )
        for r in _recent_rows(user_id, RELOAD_LIMIT)
    ]


def history_for_agent(user_id: int) -> list[ModelMessage]:
    """Replay recent saved turns as plain text so the agent remembers past visits.

    Product ids shown are appended to assistant turns so "that one" still resolves after a reload.
    """
    messages: list[ModelMessage] = []
    for r in _recent_rows(user_id, AGENT_LIMIT):
        if r["role"] == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=r["content"])]))
        else:
            ids = _product_ids(r["products_json"])
            note = f"\n[products shown: {', '.join(ids)}]" if ids else ""
            messages.append(ModelResponse(parts=[TextPart(content=r["content"] + note)]))
    while messages and not isinstance(messages[0], ModelRequest):  # history must start with the shopper
        messages.pop(0)
    return messages

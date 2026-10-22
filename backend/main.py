"""Campus Customs API: products, product images, accounts, and the PydanticAI chat agent.

Run from backend/:  uvicorn main:app --reload --port 8000
(.venv/Scripts/python -m uvicorn ... if the venv isn't activated)
"""

from __future__ import annotations

import logging
import os
import re
import secrets
import sqlite3
import time
from collections import OrderedDict, defaultdict, deque
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # HW 4
# .env may live in backend/, HW 4, or the course folder above it (where PORTKEY_API_KEY lives).
for d in (HERE, ROOT, ROOT.parent):
    load_dotenv(d / ".env")

from fastapi import Cookie, FastAPI, HTTPException, Request, Response  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from pydantic_ai.messages import ModelMessage  # noqa: E402

import agent  # noqa: E402
import audit  # noqa: E402
import auth  # noqa: E402
import memory  # noqa: E402
import safety  # noqa: E402
import tools  # noqa: E402
from models import (  # noqa: E402
    AuditRecord, AuditStep, ChatRequest, ChatResponse, HistoryMessage, ProductCard, ProductDetail,
)
from pydantic_ai.exceptions import UsageLimitExceeded  # noqa: E402
from tools import db  # noqa: E402

log = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True,
)
# Product photos: catalogue.image_file_path is relative to data/ (e.g. products/x.jpg).
app.mount("/images", StaticFiles(directory=tools.DATA_DIR / "products"), name="images")


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": tools.DB_PATH.exists(),
        "model": agent.model_name("fast"),
        "catalogue_cache": {**tools.CACHE_STATS, "ttl_seconds": tools.CATALOGUE_TTL},
        "rate_limits": {"per_min": safety.PER_MIN, "per_day": safety.PER_DAY, "site_per_day": safety.SITE_PER_DAY},
    }


# ---------------------------------------------------------------- products

@app.get("/api/products")
def list_products(limit: int = 200) -> list[ProductCard]:
    return tools.list_products(limit)


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> ProductDetail:
    product = tools.get_product(product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product


@app.get("/api/products/{product_id}/similar")
def similar_products(product_id: str, limit: int = 4) -> list[ProductCard]:
    """'You may also like': in-stock items similar to this one (same logic as the agent's find_alternatives tool)."""
    hits = tools.find_alternatives(product_id, limit=min(max(limit, 1), 8))
    if isinstance(hits, str):
        raise HTTPException(404, "Product not found")
    return tools.get_cards([h.product_id for h in hits])


# ---------------------------------------------------------------- chat

MAX_CONVERSATIONS = 500
MAX_HISTORY = 40  # messages kept per live conversation
# conversation_id -> (owner user_id or None for guests, PydanticAI message history); least recently used first.
# This is short-term memory for the current visit. Logged-in users' turns are also saved to chat_messages.
CONVERSATIONS: OrderedDict[str, tuple[int | None, list[ModelMessage]]] = OrderedDict()


def _trim(history: list[ModelMessage]) -> list[ModelMessage]:
    """Keep the tail, but start on a user request so tool calls/returns are never split."""
    if len(history) <= MAX_HISTORY:
        return history
    tail = history[-MAX_HISTORY:]
    for i, m in enumerate(tail):
        if m.kind == "request" and any(p.part_kind == "user-prompt" for p in m.parts):
            return tail[i:]
    return []


def _page_deps(body: ChatRequest) -> tuple[str, ProductDetail | None]:
    """Page context comes from the browser, so only trust a product_id that really exists in the catalogue."""
    page = body.page
    if page is None:
        return "/", None
    product_id = page.product_id
    if not product_id and page.path.startswith("/products/"):
        product_id = page.path.removeprefix("/products/").strip("/") or None
    return page.path, tools.get_product(product_id) if product_id else None


def _visitor(request: Request, user_id: int | None) -> str:
    """Rate-limit key: the account if logged in, otherwise the client IP."""
    if user_id:
        return f"user:{user_id}"
    # X-Forwarded-For can be faked by the client, so only trust it behind a known proxy (e.g. a hosting platform).
    fwd = request.headers.get("x-forwarded-for") if os.getenv("TRUST_PROXY") == "1" else None
    return "ip:" + (fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "unknown"))


@app.post("/api/chat")
async def chat(body: ChatRequest, request: Request, cc_session: str | None = Cookie(default=None)) -> ChatResponse:
    started = time.perf_counter()
    user_id = auth.session_user_id(cc_session)
    page_path = body.page.path if body.page else None

    def audit_turn(stop_reason: str, conv: str | None, text: str, **extra) -> None:
        """Every exit from this route writes one record to output/audit_trail.json."""
        audit.append(AuditRecord(
            time=audit.now(), conversation_id=conv, user_id=user_id, page=page_path, message=audit.short(text, 120),
            stop_reason=stop_reason, duration_ms=round((time.perf_counter() - started) * 1000), **extra,
        ))

    limited = safety.check_rate(_visitor(request, user_id))
    if limited:
        audit_turn("rate_limited", body.conversation_id, body.message, model="rate-limit")
        raise HTTPException(429, limited)
    customer = memory.load_customer(user_id) if user_id else None
    owner = customer.user_id if customer else None

    # Reuse the live conversation only if it belongs to the same shopper (guest vs. each account).
    known = CONVERSATIONS.get(body.conversation_id or "")
    if known and known[0] == owner:
        conv_id, history = body.conversation_id, known[1]
    else:
        conv_id = secrets.token_urlsafe(12)
        # A returning logged-in shopper starts with their saved history from the database.
        history = memory.history_for_agent(owner) if owner else []

    page_path, page_product = _page_deps(body)
    text = safety.clean_input(body.message)
    if not text:
        raise HTTPException(422, "Please type a message.")
    flags = safety.screen_input(text)
    if flags:
        # Prompt-injection / secret-extraction attempt: answer with a fixed refusal and skip the model entirely
        # (no tokens spent, nothing for the model to be tricked into). Not saved to history.
        log.warning("chat input blocked by screen: %s", flags)
        audit_turn("safety_screen", conv_id, text, model="safety-screen",
                   steps=[AuditStep(time=audit.now(), tool="screen_input", args=audit.short(flags), result="blocked")])
        return ChatResponse(reply=safety.SAFE_REFUSAL, products=[], conversation_id=conv_id, model="safety-screen")
    deps = agent.ChatDeps(customer=customer, page_path=page_path, page_product=page_product)
    try:
        result = await agent.run_chat(text, history, deps)
    except UsageLimitExceeded:
        log.warning("chat turn hit the agent loop limit")
        audit_turn("usage_limit", conv_id, text, model_requests=agent.REQUEST_LIMIT)
        raise HTTPException(503, "That one took too many steps. Could you ask in a simpler way?")
    except Exception as exc:
        if safety.is_content_filter(exc):
            log.warning("provider content filter rejected the message")
            audit_turn("content_filter", conv_id, text, model="content-filter")
            return ChatResponse(reply=safety.SAFE_REFUSAL, products=[], conversation_id=conv_id, model="content-filter")
        log.exception("chat turn failed")
        audit_turn("error", conv_id, text)
        raise HTTPException(502, "The shop assistant hit a snag. Please try again in a moment.")

    reply, new_messages = result.output, result.new_messages()
    model_used = agent.answered_by(new_messages)
    CONVERSATIONS[conv_id] = (owner, _trim(result.all_messages()))
    CONVERSATIONS.move_to_end(conv_id)
    while len(CONVERSATIONS) > MAX_CONVERSATIONS:
        CONVERSATIONS.popitem(last=False)

    # Output guard: never send a reply that leaks the prompt, a key, or a password hash.
    reply_text, blocked = safety.guard_output(reply.reply)
    if blocked:
        log.warning("chat output blocked by guard")
    # Cards are rebuilt from the DB, so prices/stock shown are real and unknown IDs are dropped.
    products = [] if blocked else tools.get_cards(reply.product_ids)
    if owner:
        memory.save_turn(owner, text, reply_text, products)  # guests are not persisted

    usage = result.usage() if callable(result.usage) else result.usage
    audit_turn(
        "output_guard" if blocked else "final_result", conv_id, text,
        steps=audit.steps_from(new_messages), model=model_used, model_requests=usage.requests,
        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
        products_shown=[p.product_id for p in products], finish_reason=audit.finish_reason(new_messages),
    )
    return ChatResponse(
        reply=reply_text,
        products=products,
        results_title=(reply.results_title or "Picked for you") if products else None,
        conversation_id=conv_id,
        model=model_used,
    )


@app.get("/api/chat/history")
def chat_history(cc_session: str | None = Cookie(default=None)) -> list[HistoryMessage]:
    """Saved chat for the logged-in shopper (oldest first). Guests get 401."""
    user_id = auth.session_user_id(cc_session)
    if user_id is None:
        raise HTTPException(401, "Log in to see your saved chat.")
    return memory.history_for_ui(user_id)


# ---------------------------------------------------------------- accounts

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LOGIN_WINDOW, LOGIN_MAX_FAILS = 300, 5  # 5 failed tries per email+IP per 5 minutes
_FAILS: defaultdict[str, deque[float]] = defaultdict(deque)


class SignupIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(max_length=128)


class LoginIn(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=128)


def public_user(row: sqlite3.Row) -> dict:
    """The only user fields that ever leave the server. password_hash is never included."""
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": row["name"],
        "email": row["email"],
    }


def start_session(response: Response, user_id: int) -> None:
    response.set_cookie(
        auth.SESSION_COOKIE, auth.create_session(user_id),
        httponly=True, samesite="lax", max_age=auth.SESSION_TTL, path="/",
    )


def user_by_id(user_id: int) -> dict | None:
    with db() as conn:
        row = conn.execute("SELECT id, first_name, last_name, name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row) if row else None


def current_user(token: str | None) -> dict | None:
    user_id = auth.session_user_id(token)
    return None if user_id is None else user_by_id(user_id)


@app.post("/api/signup", status_code=201)
def signup(body: SignupIn, response: Response) -> dict:
    email = body.email.strip().lower()
    first, last = body.first_name.strip(), body.last_name.strip()
    if not EMAIL_RE.match(email):
        raise HTTPException(422, "Please enter a valid email address.")
    if not first or not last:
        raise HTTPException(422, "Please enter your first and last name.")
    if body.password != body.confirm_password:
        raise HTTPException(422, "Passwords don't match.")
    stored = auth.hash_password(body.password)  # fresh random salt for every new account
    try:
        with db(write=True) as conn:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", email, stored, first, last),
            )
            user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with that email already exists. Try logging in.")
    start_session(response, user_id)
    return user_by_id(user_id)


@app.post("/api/login")
def login(body: LoginIn, request: Request, response: Response) -> dict:
    email = body.email.strip().lower()
    key = f"{request.client.host if request.client else '?'}|{email}"
    now, fails = time.time(), _FAILS[key]
    while fails and now - fails[0] > LOGIN_WINDOW:
        fails.popleft()
    if len(fails) >= LOGIN_MAX_FAILS:
        raise HTTPException(429, "Too many failed attempts. Wait a few minutes and try again.")

    with db() as conn:
        row = conn.execute(
            "SELECT id, first_name, last_name, name, email, password_hash FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()
    # Always run one PBKDF2 check so a missing email takes as long as a wrong password.
    ok = auth.verify_password(body.password, row["password_hash"] if row else auth.DUMMY_HASH) and row is not None
    if not ok:
        fails.append(now)
        raise HTTPException(401, "Email or password is incorrect.")  # same message either way
    fails.clear()
    start_session(response, row["id"])
    return public_user(row)


@app.post("/api/logout")
def logout(response: Response, cc_session: str | None = Cookie(default=None)) -> dict:
    auth.end_session(cc_session)
    response.delete_cookie(auth.SESSION_COOKIE, path="/")
    return {"ok": True}


@app.get("/api/me")
def me(cc_session: str | None = Cookie(default=None)) -> dict:
    user = current_user(cc_session)
    if user is None:
        raise HTTPException(401, "Not logged in.")
    return user

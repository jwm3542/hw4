"""Campus Customs shopping agent: PydanticAI wiring (prompt file + model tiers + tools).

Model tiers come from .env (see .env.example):
  OPENAI_MODEL           fast      gpt-5.6-luna   default for every chat turn
  OPENAI_MODEL_STANDARD  standard  gpt-5.6-terra  used if fast fails
  OPENAI_MODEL_SMART     smart     gpt-6-astra    used if standard fails (harder steps get routed here later)
All calls go through Portkey with PORTKEY_API_KEY.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dataclasses import dataclass  # noqa: E402

from pydantic_ai import Agent, RunContext  # noqa: E402
from pydantic_ai.messages import ModelMessage  # noqa: E402
from pydantic_ai.models.fallback import FallbackModel  # noqa: E402
from pydantic_ai.models.openai import OpenAIResponsesModel  # noqa: E402
from pydantic_ai.providers.openai import OpenAIProvider  # noqa: E402
from pydantic_ai.usage import UsageLimits  # noqa: E402

import tools  # noqa: E402
from models import ChatReply, Customer, ProductDetail, ProductHit, StockCheck  # noqa: E402

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
REQUEST_LIMIT = 8  # max model calls per chat turn (agent-loop limit)
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")

TIERS = {
    "fast": ("OPENAI_MODEL", "gpt-5.6-luna"),
    "standard": ("OPENAI_MODEL_STANDARD", "gpt-5.6-terra"),
    "smart": ("OPENAI_MODEL_SMART", "gpt-6-astra"),
}


def model_name(tier: str = "fast") -> str:
    env, default = TIERS[tier]
    return os.getenv(env, default)


@lru_cache(maxsize=1)
def _provider() -> OpenAIProvider:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set; put it in the course folder's .env.")
    return OpenAIProvider(base_url=PORTKEY_BASE_URL, api_key=api_key)


def build_model(tier: str = "fast") -> OpenAIResponsesModel:
    # Portkey only passes function tools for these models through the Responses API (same as Lecture 7).
    return OpenAIResponsesModel(model_name(tier), provider=_provider())


@lru_cache(maxsize=1)
def chat_model() -> FallbackModel:
    """Fast tier first; on an API error, move up one tier."""
    return FallbackModel(build_model("fast"), build_model("standard"), build_model("smart"))


@dataclass
class ChatDeps:
    """Per-turn context handed to the agent: who is chatting and what they're looking at."""

    customer: Customer | None = None  # None = guest
    page_path: str = "/"
    page_product: ProductDetail | None = None  # the product on screen, already looked up in the DB


shop_agent = Agent(
    deps_type=ChatDeps,
    output_type=ChatReply,
    instructions=PROMPT_PATH.read_text(encoding="utf-8"),
    retries=2,
)


@shop_agent.instructions
def session_context(ctx: RunContext[ChatDeps]) -> str:
    """Added to the system prompt on every turn, after prompt.md."""
    d = ctx.deps
    if d.customer:
        who = (
            f"The shopper is LOGGED IN as {d.customer.name} "
            f"(first name {d.customer.first_name}, email {d.customer.email}, member since {d.customer.member_since[:10]}). "
            "Greet them by first name when it fits. Earlier messages in this chat may be from previous visits."
        )
    else:
        who = "The shopper is a GUEST (not logged in). You don't know their name or email; don't guess."
    if d.page_product:
        p = d.page_product
        where = (
            f"They are viewing the product page for **{p.name}** (product_id `{p.product_id}`, "
            f"${p.price:.2f}, colors: {', '.join(p.colors)}). "
            '"This", "it", "this one" or "that" with no other item named means THIS product. '
            "Still use check_stock / get_product_details for stock and price."
        )
    else:
        where = f"They are on the page {d.page_path!r} (not a single product page)."
    return "\n".join(["## Current session", who, where])


@shop_agent.tool
def current_customer(ctx: RunContext[ChatDeps]) -> Customer | str:
    """The logged-in shopper's name, email and member-since date, or a note that they are a guest."""
    return ctx.deps.customer or "Guest shopper: not logged in, no name or email on file."


@shop_agent.tool
def current_page_product(ctx: RunContext[ChatDeps]) -> ProductDetail | str:
    """The product the shopper is looking at right now (with colors, price and stock per size), if any."""
    if ctx.deps.page_product is None:
        return f"The shopper is not on a product page (page: {ctx.deps.page_path})."
    return tools.get_product(ctx.deps.page_product.product_id) or "That product no longer exists."


@shop_agent.tool_plain
def search_products(
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    size: str | None = None,
    limit: int = 10,
) -> list[ProductHit]:
    """Search the Campus Customs catalogue.

    Args:
        query: keywords such as "navy hoodie", "Branford", "baseball", "quarter-zip". Every word must match.
            Use a broader query (fewer words) if nothing comes back.
        max_price: only items at or below this price in USD.
        min_price: only items at or above this price in USD.
        size: put items in stock in this size (XS, S, M, L, XL, XXL) first. Items sold out in that size are
            still returned; check sizes_in_stock and tell the shopper honestly.
        limit: max results (1-20).
    """
    return tools.search_products(query, max_price, min_price, size, limit)


@shop_agent.tool_plain
def get_product_details(product_id: str) -> ProductDetail | str:
    """Full details for one product: description, colors, price, total stock and stock for every size.

    Use for "tell me about", "how much", "what colors", or "which sizes do you have" questions.
    """
    return tools.get_product(product_id) or f"No product with id {product_id!r}."


@shop_agent.tool_plain
def check_stock(product_id: str, size: str) -> StockCheck | str:
    """Is this product in stock in this size, and how many? Use for any "do you have it in <size>" question.

    Args:
        product_id: exact product_id from search_products.
        size: XS, S, M, L, XL or XXL.
    """
    return tools.check_stock(product_id, size)


@shop_agent.tool_plain
def find_alternatives(
    product_id: str,
    size: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    limit: int = 4,
) -> list[ProductHit] | str:
    """Similar items that ARE in stock: same garment type first, then same college/sport/school theme.

    Use when an item is sold out in the shopper's size, isn't offered in the color they want, is over budget,
    or they ask for "something like this" / "what else". Every result has stock (in `size`, if given).

    Args:
        product_id: the item to find alternatives for (exact product_id).
        size: only items in stock in this size (XS, S, M, L, XL, XXL).
        color: only items offered in this color, e.g. "navy".
        max_price: only items at or below this price in USD.
        limit: how many to return (1-8).
    """
    return tools.find_alternatives(product_id, size, color, max_price, limit)


@shop_agent.tool_plain
def shop_info() -> dict:
    """Store basics: sizes carried, price range, product types, and how many items are in the catalogue."""
    cards = tools.list_products()
    return {
        "sizes": tools.SIZE_ORDER,
        "product_count": len(cards),
        "price_range_usd": [min(c.price for c in cards), max(c.price for c in cards)],
        "garment_types": sorted({c.garment_type.lower() for c in cards}),
    }


async def run_chat(message: str, history: list[ModelMessage], deps: ChatDeps):
    """One chat turn. Returns the PydanticAI run result (output = ChatReply, plus messages and usage)."""
    return await shop_agent.run(
        message,
        model=chat_model(),
        deps=deps,
        message_history=history,
        usage_limits=UsageLimits(request_limit=REQUEST_LIMIT),
    )


def answered_by(new_messages: list[ModelMessage]) -> str | None:
    responses = [m for m in new_messages if getattr(m, "model_name", None)]
    return responses[-1].model_name if responses else None

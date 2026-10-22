"""Pydantic / PydanticAI structured types for the Campus Customs API and agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    size: str = Field(description="XS, S, M, L, XL or XXL")
    quantity: int = Field(ge=0, description="Units in stock; 0 means sold out in this size")


class ProductCard(BaseModel):
    """One product as the website shows it (grid cards and chat cards). Built from the DB, never by the model."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    price: float
    image_url: str
    total_stock: int
    sizes_in_stock: list[str] = Field(default_factory=list, description="Sizes with quantity > 0, XS..XXL")


class ProductDetail(ProductCard):
    inventory: list[SizeStock]


class ProductHit(BaseModel):
    """Compact search result handed to the agent (keeps tool output small)."""

    product_id: str
    name: str
    garment_type: str
    description: str = Field(description="Catalogue description, so the agent can describe items without a second lookup")
    colors: list[str]
    price: float
    total_stock: int
    sizes_in_stock: list[str]


class StockCheck(BaseModel):
    """Answer to "is <product> in stock in <size>?" straight from the inventory table."""

    product_id: str
    name: str
    price: float
    size: str
    quantity: int = Field(ge=0, description="Units on hand in this size")
    in_stock: bool = Field(description="True only if quantity > 0")
    other_sizes_in_stock: list[str] = Field(description="Sizes of this product that do have stock, for alternatives")
    message: str = Field(description="Plain-language summary the agent can relay")


class ChatReply(BaseModel):
    """What the agent must return each turn."""

    reply: str = Field(description="Message shown to the shopper, in the Campus Customs voice (Markdown allowed)")
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Exact product_ids from tool results to show as cards on the page, best match first; empty if none",
    )
    results_title: str | None = Field(
        default=None,
        max_length=60,
        description="Short heading for the cards shown on the page, e.g. 'Navy hoodies under $70'; null if no cards",
    )


class PageContext(BaseModel):
    """Where the shopper is on the site when they send a chat message (sent by the browser; untrusted)."""

    path: str = Field(default="/", max_length=200, description="Current URL path, e.g. /products/branford-1-4-zip")
    product_id: str | None = Field(default=None, max_length=120, description="Product on screen, if on a product page")


class Customer(BaseModel):
    """The logged-in shopper as the agent sees them. Never includes the password hash."""

    user_id: int
    first_name: str
    last_name: str
    name: str
    email: str
    member_since: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = Field(default=None, max_length=64)
    page: PageContext | None = None


class HistoryMessage(BaseModel):
    """One saved chat line, as reloaded into the chat panel."""

    role: str
    content: str
    products: list[ProductCard] = Field(default_factory=list)
    created_at: str


class ChatResponse(BaseModel):
    """What /api/chat returns to the browser: the reply plus product cards filled in from the database."""

    reply: str
    products: list[ProductCard] = Field(description="Cards rebuilt from the DB for the agent's product_ids, in order")
    results_title: str | None = None
    conversation_id: str
    model: str | None = None


class AuditStep(BaseModel):
    """One tool call inside a chat turn."""

    time: str = Field(description="UTC ISO time of the model response that made the call")
    tool: str = Field(description="Tool name, e.g. check_stock; final_result = the structured reply")
    args: str = Field(description="Arguments, shortened to 160 chars")
    result: str | None = Field(default=None, description="What the tool returned, shortened to 160 chars")


class AuditRecord(BaseModel):
    """One chat turn in output/audit_trail.json (append-only)."""

    time: str = Field(description="UTC ISO time the turn finished")
    conversation_id: str | None = None
    user_id: int | None = Field(default=None, description="Logged-in account id; null for guests (no names/emails)")
    page: str | None = Field(default=None, description="Page the shopper was on")
    message: str = Field(description="Shopper's message, shortened")
    steps: list[AuditStep] = Field(default_factory=list, description="Tool calls in order")
    model: str | None = Field(default=None, description="Model that answered, or the safety layer that did")
    model_requests: int = Field(default=0, description="Model calls this turn (loop limit is 8)")
    input_tokens: int | None = None
    output_tokens: int | None = None
    products_shown: list[str] = Field(default_factory=list, description="product_ids put on the page")
    stop_reason: str = Field(
        description="final_result | usage_limit | rate_limited | safety_screen | content_filter | output_guard | error"
    )
    finish_reason: str | None = Field(default=None, description="Model's own finish reason on the last response")
    duration_ms: int | None = None

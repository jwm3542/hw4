"""Read-only catalogue and inventory queries. Used by the agent's tools and by the product endpoints in main.py.

Prices and stock always come from campus_customs.db; nothing here touches the users table.

Caching (Problem 9): the catalogue (names, prices, descriptions, tags) rarely changes, so it is cached in memory for
CATALOGUE_TTL seconds. Inventory is NOT cached: it is read fresh in one query every time, so stock answers stay exact.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import time
from pathlib import Path

from models import ProductCard, ProductDetail, ProductHit, SizeStock, StockCheck

ROOT = Path(__file__).resolve().parent.parent  # HW 4
DATA_DIR = Path(os.getenv("CAMPUS_DATA_DIR", ROOT / "data"))
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
_RANK = {s: i for i, s in enumerate(SIZE_ORDER)}
CATALOGUE_TTL = float(os.getenv("CATALOGUE_TTL", "300"))

_cache: dict[str, object] = {"at": 0.0, "rows": None}
CACHE_STATS = {"hits": 0, "misses": 0}


def db(write: bool = False) -> sqlite3.Connection:
    """Read-only by default; only signup and the chat log open a writable connection."""
    conn = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode={'rw' if write else 'ro'}", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _catalogue() -> dict[str, dict]:
    """product_id -> catalogue row (as a dict), cached for CATALOGUE_TTL seconds, in name order."""
    now = time.monotonic()
    if _cache["rows"] is not None and now - _cache["at"] < CATALOGUE_TTL:
        CACHE_STATS["hits"] += 1
        return _cache["rows"]  # type: ignore[return-value]
    CACHE_STATS["misses"] += 1
    with db() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    parsed = {
        r["product_id"]: {**dict(r), "colors": json.loads(r["colors"]), "search_tags": json.loads(r["search_tags"])}
        for r in rows
    }
    _cache.update(at=now, rows=parsed)
    return parsed


def _inventory(product_ids: list[str] | None = None) -> dict[str, list[SizeStock]]:
    """Fresh stock (never cached): product_id -> sizes XS..XXL. One query for all products or a given set."""
    with db() as conn:
        if product_ids is None:
            rows = conn.execute("SELECT product_id, size, quantity FROM inventory").fetchall()
        else:
            marks = ",".join("?" * len(product_ids)) or "''"
            rows = conn.execute(
                f"SELECT product_id, size, quantity FROM inventory WHERE product_id IN ({marks})", product_ids
            ).fetchall()
    out: dict[str, list[SizeStock]] = {}
    for r in rows:
        out.setdefault(r["product_id"], []).append(SizeStock(size=r["size"], quantity=r["quantity"]))
    for sizes in out.values():
        sizes.sort(key=lambda s: _RANK.get(s.size, 99))
    return out


def _card(row: dict, stock: list[SizeStock]) -> ProductCard:
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=row["colors"],
        search_tags=row["search_tags"],
        price=row["price"],
        image_url="/images/" + Path(row["image_file_path"]).name,
        total_stock=sum(s.quantity for s in stock),
        sizes_in_stock=[s.size for s in stock if s.quantity > 0],
    )


def _hit(row: dict, stock: list[SizeStock]) -> ProductHit:
    return ProductHit(
        product_id=row["product_id"], name=row["name"], garment_type=row["garment_type"],
        description=row["description"], colors=row["colors"], price=row["price"],
        total_stock=sum(s.quantity for s in stock), sizes_in_stock=[s.size for s in stock if s.quantity > 0],
    )


def list_products(limit: int = 200) -> list[ProductCard]:
    cat, inv = _catalogue(), _inventory()
    return [_card(r, inv.get(pid, [])) for pid, r in list(cat.items())[:limit]]


def get_product(product_id: str) -> ProductDetail | None:
    row = _catalogue().get(product_id)
    if row is None:
        return None
    stock = _inventory([product_id]).get(product_id, [])
    return ProductDetail(**_card(row, stock).model_dump(), inventory=stock)


def get_cards(product_ids: list[str]) -> list[ProductCard]:
    """Cards for the given IDs in the given order; unknown IDs are dropped (the model can't invent products)."""
    cat = _catalogue()
    ids = [p for p in dict.fromkeys(product_ids) if p in cat]
    inv = _inventory(ids) if ids else {}
    return [_card(cat[p], inv.get(p, [])) for p in ids]


def search_products(
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    size: str | None = None,
    limit: int = 10,
) -> list[ProductHit]:
    """Keyword search across name, type, description, colors and tags. Every word must match somewhere.

    size: rank products with stock in that size first. Sold-out matches are still returned (never hidden), so the
    caller can honestly say "we carry it, but it's sold out in that size".
    Results are ranked by size availability, then by how many words hit the name/tags.
    """
    words = [w for w in query.lower().replace(",", " ").split() if len(w) > 1]
    size = size.upper() if size else None
    cat, inv = _catalogue(), _inventory()
    hits: list[tuple[int, ProductHit]] = []
    for pid, r in cat.items():
        if max_price is not None and r["price"] > max_price:
            continue
        if min_price is not None and r["price"] < min_price:
            continue
        haystack = " ".join([r["name"], r["garment_type"], r["description"], *r["colors"], *r["search_tags"]]).lower()
        # light plural handling: "hoodies" should match "hoodie"
        if not all(w in haystack or w.rstrip("s") in haystack for w in words):
            continue
        hit = _hit(r, inv.get(pid, []))
        strong = " ".join([r["name"], *r["search_tags"]]).lower()
        score = sum(w.rstrip("s") in strong for w in words) + (100 if size and size in hit.sizes_in_stock else 0)
        hits.append((score, hit))
    hits.sort(key=lambda h: (-h[0], h[1].name))
    return [h for _, h in hits[: max(1, min(limit, 20))]]


def check_stock(product_id: str, size: str) -> StockCheck | str:
    """Stock for one product in one size. Returns an explanation string if the product or size doesn't exist."""
    product = get_product(product_id)
    if product is None:
        return f"No product with id {product_id!r}. Search first to get a valid product_id."
    size = size.strip().upper()
    stock = {s.size: s.quantity for s in product.inventory}
    if size not in stock:
        return f"We don't carry size {size!r}. Sizes are {', '.join(SIZE_ORDER)}."
    qty = stock[size]
    others = [s for s, q in stock.items() if q > 0 and s != size]
    if qty > 0:
        msg = f"{product.name} is in stock in {size}: {qty} available at ${product.price:.2f}."
    else:
        msg = f"{product.name} is SOLD OUT in {size}. In stock in: {', '.join(others) or 'no sizes'}."
    return StockCheck(
        product_id=product.product_id, name=product.name, price=product.price, size=size,
        quantity=qty, in_stock=qty > 0, other_sizes_in_stock=others, message=msg,
    )


# ---------------------------------------------------------------- alternatives (Problem 9)

_FAMILIES = [  # garment_type is typed inconsistently; group it into families shoppers think in
    ("quarter-zip", ("quarter-zip", "1/4 zip", "1-4-zip")),
    ("hoodie", ("hoodie", "hooded")),
    ("jacket", ("jacket", "fleece")),
    ("crewneck", ("crewneck", "crew-neck sweatshirt", "mockneck", "sweatshirt")),
    ("long-sleeve", ("long-sleeve",)),
    ("t-shirt", ("t-shirt", "tee")),
]
_STOP = {"yale", "university", "logo", "apparel", "college", "shirt", "sweatshirt"}


def garment_family(garment_type: str) -> str:
    g = garment_type.lower()
    for family, keys in _FAMILIES:
        if any(k in g for k in keys):
            return family
    return g


def _tag_words(row: dict) -> set[str]:
    words = set(re.findall(r"[a-z]+", " ".join([row["name"], *row["search_tags"]]).lower()))
    return {w for w in words if len(w) > 2 and w not in _STOP}


def find_alternatives(
    product_id: str,
    size: str | None = None,
    color: str | None = None,
    max_price: float | None = None,
    limit: int = 4,
) -> list[ProductHit] | str:
    """In-stock items similar to product_id: same garment family first, then shared theme (college, sport, school).

    size: only items with stock in that size. color: only items offered in that color. max_price: budget cap.
    """
    cat = _catalogue()
    base = cat.get(product_id)
    if base is None:
        return f"No product with id {product_id!r}. Search first to get a valid product_id."
    size = size.strip().upper() if size else None
    if size and size not in SIZE_ORDER:
        return f"We don't carry size {size!r}. Sizes are {', '.join(SIZE_ORDER)}."
    inv = _inventory()
    family, theme = garment_family(base["garment_type"]), _tag_words(base)
    scored: list[tuple[float, ProductHit]] = []
    for pid, r in cat.items():
        if pid == product_id:
            continue
        hit = _hit(r, inv.get(pid, []))
        if not hit.sizes_in_stock or (size and size not in hit.sizes_in_stock):
            continue
        if color and not any(color.lower() in c.lower() for c in r["colors"]):
            continue
        if max_price is not None and r["price"] > max_price:
            continue
        score = (10 if garment_family(r["garment_type"]) == family else 0) + 2 * len(theme & _tag_words(r))
        score += len(set(map(str.lower, base["colors"])) & set(map(str.lower, r["colors"]))) * 0.5
        score -= abs(r["price"] - base["price"]) / 100
        scored.append((score, hit))
    scored.sort(key=lambda s: (-s[0], s[1].name))
    return [h for _, h in scored[: max(1, min(limit, 8))]]

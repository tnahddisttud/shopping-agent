"""LangChain tools for the shopping agent: product search and order placement."""

import sqlite3
from typing import Optional

from langchain_core.tools import tool

from src.reviews_api import get_ratings_for_products
from src.setup_db import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@tool
def search_products(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    organic_only: bool = False,
    min_rating: Optional[float] = None,
) -> list[dict]:
    """Search the store catalog.

    Args:
        keyword: Product type to look for, matched against product name and category
            (e.g. "honey", "almond", "coffee"). Do not include words like "organic" here.
        category: Exact category. One of: honey, oil, nuts, seeds, grains, tea, coffee,
            snacks, dairy-alt.
        max_price: Maximum price in USD (inclusive).
        min_price: Minimum price in USD (inclusive).
        organic_only: True to return only organic products.
        min_rating: Minimum average customer rating (0-5), inclusive.

    Returns products sorted by rating (highest first), each with id, name, category,
    price, description, is_organic, average_rating and review_count.
    """
    sql = "SELECT id, name, category, price, description, is_organic FROM products WHERE 1=1"
    params: list = []
    if keyword:
        sql += " AND (name LIKE ? OR category LIKE ?)"
        params += [f"%{keyword}%", f"%{keyword}%"]
    if category:
        sql += " AND category = ?"
        params.append(category.lower())
    if max_price is not None:
        sql += " AND price <= ?"
        params.append(max_price)
    if min_price is not None:
        sql += " AND price >= ?"
        params.append(min_price)
    if organic_only:
        sql += " AND is_organic = 1"

    with _connect() as conn:
        products = [dict(r) for r in conn.execute(sql, params).fetchall()]

    ratings = {r["product_id"]: r for r in get_ratings_for_products([p["id"] for p in products])}
    results = []
    for p in products:
        r = ratings[p["id"]]
        p["is_organic"] = bool(p["is_organic"])
        p["average_rating"] = r["average_rating"]
        p["review_count"] = r["review_count"]
        if min_rating is None or p["average_rating"] >= min_rating:
            results.append(p)

    results.sort(key=lambda p: (-p["average_rating"], p["price"]))
    return results


@tool
def place_order(product_id: int) -> dict:
    """Place an order for one product by its product id. Only call this when the user
    has clearly asked to buy/order a specific product."""
    with _connect() as conn:
        row = conn.execute("SELECT id, name, price FROM products WHERE id = ?", (product_id,)).fetchone()
        if row is None:
            return {"success": False, "error": f"No product with id {product_id}"}
        cur = conn.execute(
            "INSERT INTO orders (product_id, product_name, price) VALUES (?, ?, ?)",
            (row["id"], row["name"], row["price"]),
        )
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {"success": True, "order": dict(order)}


TOOLS = [search_products, place_order]

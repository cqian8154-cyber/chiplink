from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter()

class CartAdd(BaseModel):
    session_id: str
    product_id: int
    quantity: int

@router.get("/{session_id}")
def get_cart(session_id: str):
    conn = get_conn()
    rows = conn.execute("""SELECT c.*, p.sale_price, p.stock, p.brand, p.package
        FROM cart_items c JOIN products p ON c.product_id = p.id
        WHERE c.session_id=?""", (session_id,)).fetchall()
    items = [dict(r) for r in rows]
    subtotal = sum(i["quantity"] * i["unit_price"] for i in items)
    tax = round(subtotal * 0.13, 2)
    conn.close()
    return {"items": items, "subtotal": subtotal, "tax": tax, "total": round(subtotal + tax, 2)}

@router.post("/add")
def add_to_cart(item: CartAdd):
    conn = get_conn()
    product = conn.execute("SELECT * FROM products WHERE id=?", (item.product_id,)).fetchone()
    if not product:
        raise HTTPException(404, "产品不存在")
    existing = conn.execute("SELECT id FROM cart_items WHERE session_id=? AND product_id=?",
                            (item.session_id, item.product_id)).fetchone()
    if existing:
        conn.execute("UPDATE cart_items SET quantity=quantity+? WHERE id=?",
                     (item.quantity, existing["id"]))
    else:
        conn.execute("""INSERT INTO cart_items (session_id,product_id,model,quantity,unit_price)
            VALUES (?,?,?,?,?)""",
            (item.session_id, item.product_id, product["model"], item.quantity, product["sale_price"]))
    conn.commit()
    conn.close()
    return {"message": "已加入购物车"}

@router.delete("/{session_id}/{item_id}")
def remove_from_cart(session_id: str, item_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM cart_items WHERE id=? AND session_id=?", (item_id, session_id))
    conn.commit()
    conn.close()
    return {"message": "已移除"}

@router.delete("/{session_id}/clear")
def clear_cart(session_id: str):
    conn = get_conn()
    conn.execute("DELETE FROM cart_items WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()
    return {"message": "购物车已清空"}

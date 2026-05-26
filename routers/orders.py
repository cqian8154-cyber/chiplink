from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import get_conn
from datetime import datetime

router = APIRouter()

class OrderItem(BaseModel):
    product_id: int
    model: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    company: str
    contact: str
    phone: Optional[str] = ""
    notes: Optional[str] = ""
    items: List[OrderItem]

@router.get("/")
def list_orders(status: Optional[str] = None, limit: int = 50):
    conn = get_conn()
    sql = "SELECT * FROM orders"
    params = []
    if status:
        sql += " WHERE status=?"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_order(order: OrderCreate):
    conn = get_conn()
    subtotal = sum(i.quantity * i.unit_price for i in order.items)
    tax = round(subtotal * 0.13, 2)
    total = round(subtotal + tax, 2)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    order_no = f"ORD-{ts}"
    cur = conn.execute("""INSERT INTO orders (order_no,company,contact,phone,total,tax,status,notes)
        VALUES (?,?,?,?,?,?,'confirmed',?)""",
        (order_no, order.company, order.contact, order.phone, total, tax, order.notes))
    order_id = cur.lastrowid
    for item in order.items:
        conn.execute("""INSERT INTO order_items (order_id,product_id,model,quantity,unit_price)
            VALUES (?,?,?,?,?)""",
            (order_id, item.product_id, item.model, item.quantity, item.unit_price))
        conn.execute("UPDATE products SET stock = MAX(0, stock - ?) WHERE id=?",
                     (item.quantity, item.product_id))
    conn.commit()
    conn.close()
    return {"order_no": order_no, "total": total, "tax": tax, "message": "订单创建成功"}

@router.put("/{order_id}/status")
def update_order_status(order_id: int, status: str):
    allowed = ["confirmed", "processing", "shipped", "completed", "cancelled"]
    if status not in allowed:
        raise HTTPException(400, f"状态必须是: {allowed}")
    conn = get_conn()
    conn.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()
    return {"message": "状态更新成功"}

@router.get("/stats/summary")
def order_stats():
    conn = get_conn()
    total_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    total_revenue = conn.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status != 'cancelled'").fetchone()[0]
    processing = conn.execute("SELECT COUNT(*) FROM orders WHERE status='processing'").fetchone()[0]
    shipped = conn.execute("SELECT COUNT(*) FROM orders WHERE status='shipped'").fetchone()[0]
    conn.close()
    return {"total_orders": total_orders, "total_revenue": total_revenue,
            "processing": processing, "shipped": shipped}

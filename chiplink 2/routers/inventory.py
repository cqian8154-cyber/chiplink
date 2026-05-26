from fastapi import APIRouter
from database import get_conn

router = APIRouter()

@router.get("/")
def get_inventory():
    conn = get_conn()
    rows = conn.execute("""SELECT id, model, brand, category, stock, cost_price, sale_price,
        CASE WHEN stock = 0 THEN 'out'
             WHEN stock <= 500 THEN 'low'
             ELSE 'ok' END as stock_status
        FROM products ORDER BY stock ASC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/alerts")
def stock_alerts():
    conn = get_conn()
    rows = conn.execute("""SELECT model, brand, stock FROM products WHERE stock <= 500
        ORDER BY stock ASC""").fetchall()
    conn.close()
    return [dict(r) for r in rows]

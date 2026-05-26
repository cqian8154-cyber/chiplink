from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn

router = APIRouter()

class ProductCreate(BaseModel):
    model: str
    brand: str
    category: str
    package: Optional[str] = ""
    description: Optional[str] = ""
    specs: Optional[str] = ""
    stock: int = 0
    cost_price: float = 0
    sale_price: float = 0
    min_qty: int = 1
    is_domestic: int = 0

@router.get("/")
def list_products(
    q: Optional[str] = Query(None),
    category: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    is_domestic: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    conn = get_conn()
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if q:
        sql += " AND (model LIKE ? OR brand LIKE ? OR description LIKE ?)"
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if category:
        sql += " AND category = ?"
        params.append(category)
    if brand:
        sql += " AND brand = ?"
        params.append(brand)
    if in_stock is True:
        sql += " AND stock > 0"
    if is_domestic is True:
        sql += " AND is_domestic = 1"
    sql += " LIMIT ? OFFSET ?"
    params += [limit, offset]
    rows = conn.execute(sql, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    return {"total": total, "items": [dict(r) for r in rows]}

@router.get("/{product_id}")
def get_product(product_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "产品不存在")
    return dict(row)

@router.post("/")
def create_product(p: ProductCreate):
    conn = get_conn()
    cur = conn.execute("""INSERT INTO products
        (model,brand,category,package,description,specs,stock,cost_price,sale_price,min_qty,is_domestic)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (p.model,p.brand,p.category,p.package,p.description,p.specs,
         p.stock,p.cost_price,p.sale_price,p.min_qty,p.is_domestic))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "message": "产品创建成功"}

@router.put("/{product_id}")
def update_product(product_id: int, p: ProductCreate):
    conn = get_conn()
    conn.execute("""UPDATE products SET
        model=?,brand=?,category=?,package=?,description=?,specs=?,
        stock=?,cost_price=?,sale_price=?,min_qty=?,is_domestic=?
        WHERE id=?""",
        (p.model,p.brand,p.category,p.package,p.description,p.specs,
         p.stock,p.cost_price,p.sale_price,p.min_qty,p.is_domestic,product_id))
    conn.commit()
    conn.close()
    return {"message": "更新成功"}

@router.delete("/{product_id}")
def delete_product(product_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "删除成功"}

@router.get("/stats/summary")
def product_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    in_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock > 100").fetchone()[0]
    low_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock > 0 AND stock <= 100").fetchone()[0]
    out_stock = conn.execute("SELECT COUNT(*) FROM products WHERE stock = 0").fetchone()[0]
    conn.close()
    return {"total": total, "in_stock": in_stock, "low_stock": low_stock, "out_stock": out_stock}

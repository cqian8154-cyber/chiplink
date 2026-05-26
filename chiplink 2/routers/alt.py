from fastapi import APIRouter, Query
from typing import Optional
from database import get_conn

router = APIRouter()

@router.get("/")
def find_alternatives(model: Optional[str] = Query(None)):
    conn = get_conn()
    if model:
        rows = conn.execute("""SELECT * FROM alt_products
            WHERE UPPER(original_model) = UPPER(?)
            ORDER BY alt_price ASC""", (model,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM alt_products ORDER BY original_model").fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["tags"] = d["tags"].split(",") if d["tags"] else []
        if d["orig_price"] and d["alt_price"]:
            d["save_pct"] = round((1 - d["alt_price"] / d["orig_price"]) * 100)
        else:
            d["save_pct"] = 0
        result.append(d)
    conn.close()
    return result

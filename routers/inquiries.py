from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_conn
from datetime import datetime

router = APIRouter()

class InquiryCreate(BaseModel):
    model: str
    brand: Optional[str] = ""
    quantity: int
    target_price: Optional[float] = None
    company: Optional[str] = ""
    contact: Optional[str] = ""
    phone: Optional[str] = ""
    email: Optional[str] = ""
    delivery: Optional[str] = ""
    need_date: Optional[str] = ""
    notes: Optional[str] = ""

class QuoteUpdate(BaseModel):
    quoted_price: float
    notes: Optional[str] = ""

@router.get("/")
def list_inquiries(status: Optional[str] = None, limit: int = 50):
    conn = get_conn()
    sql = "SELECT * FROM inquiries"
    params = []
    if status:
        sql += " WHERE status = ?"
        params.append(status)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/")
def create_inquiry(inq: InquiryCreate):
    conn = get_conn()
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    inq_no = f"INQ-{ts}"
    conn.execute("""INSERT INTO inquiries
        (inquiry_no,model,brand,quantity,target_price,company,contact,phone,email,delivery,need_date,notes,status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'pending')""",
        (inq_no,inq.model,inq.brand,inq.quantity,inq.target_price,
         inq.company,inq.contact,inq.phone,inq.email,
         inq.delivery,inq.need_date,inq.notes))
    conn.commit()
    conn.close()
    return {"inquiry_no": inq_no, "message": "询价提交成功，我们将在2小时内回复"}

@router.put("/{inq_id}/quote")
def quote_inquiry(inq_id: int, q: QuoteUpdate):
    conn = get_conn()
    conn.execute("UPDATE inquiries SET quoted_price=?, status='quoted' WHERE id=?",
                 (q.quoted_price, inq_id))
    conn.commit()
    conn.close()
    return {"message": "报价已发送"}

@router.put("/{inq_id}/confirm")
def confirm_inquiry(inq_id: int):
    conn = get_conn()
    conn.execute("UPDATE inquiries SET status='confirmed' WHERE id=?", (inq_id,))
    conn.commit()
    conn.close()
    return {"message": "已确认"}

@router.get("/stats/pending-count")
def pending_count():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM inquiries WHERE status='pending'").fetchone()[0]
    conn.close()
    return {"pending": count}

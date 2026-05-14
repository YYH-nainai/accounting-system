from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Receivable, Customer
from ..schemas import ReceivableCreate, ReceivableUpdate, ReceivableOut
from ..auth import require_auth

router = APIRouter(prefix="/api/receivables", tags=["receivables"])


@router.get("", response_model=List[ReceivableOut])
def list_receivables(request: Request, customer_id: int = None, unreceived: bool = None, db: Session = Depends(get_db)):
    require_auth(request)
    q = db.query(Receivable).join(Customer)
    if customer_id:
        q = q.filter(Receivable.customer_id == customer_id)
    if unreceived:
        q = q.filter(Receivable.is_received == False)
    rows = q.order_by(Receivable.invoice_date.desc()).all()
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "customer_id": r.customer_id,
            "customer_name": r.customer.name,
            "invoice_no": r.invoice_no,
            "invoice_date": r.invoice_date,
            "amount": r.amount,
            "tax": r.tax,
            "total_amount": r.total_amount,
            "description": r.description,
            "due_date": r.due_date,
            "is_received": r.is_received,
            "received_date": r.received_date,
            "received_notes": r.received_notes,
        })
    return result


@router.get("/{receivable_id}", response_model=ReceivableOut)
def get_receivable(receivable_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(Receivable).filter(Receivable.id == receivable_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="應收款項不存在")
    return {
        "id": r.id,
        "customer_id": r.customer_id,
        "customer_name": r.customer.name,
        "invoice_no": r.invoice_no,
        "invoice_date": r.invoice_date,
        "amount": r.amount,
        "tax": r.tax,
        "total_amount": r.total_amount,
        "description": r.description,
        "due_date": r.due_date,
        "is_received": r.is_received,
        "received_date": r.received_date,
        "received_notes": r.received_notes,
    }


@router.post("", response_model=ReceivableOut)
def create_receivable(data: ReceivableCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=400, detail="客戶不存在")
    r = Receivable(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return get_receivable(r.id, request, db)


@router.put("/{receivable_id}/payment", response_model=ReceivableOut)
def update_receivable_payment(receivable_id: int, data: ReceivableUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(Receivable).filter(Receivable.id == receivable_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="應收款項不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(r, key, value)
    db.commit()
    return get_receivable(receivable_id, request, db)


@router.delete("/{receivable_id}")
def delete_receivable(receivable_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(Receivable).filter(Receivable.id == receivable_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="應收款項不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}

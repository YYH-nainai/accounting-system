from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ..database import get_db
from ..models import VendorInvoice, Vendor
from ..schemas import VendorInvoiceCreate, VendorInvoiceUpdate, VendorInvoiceOut
from ..auth import require_auth

router = APIRouter(prefix="/api/vendor-invoices", tags=["vendor_invoices"])


@router.get("", response_model=List[VendorInvoiceOut])
def list_vendor_invoices(request: Request, vendor_id: int = None, unpaid: bool = None, db: Session = Depends(get_db)):
    require_auth(request)
    q = db.query(VendorInvoice).join(Vendor)
    if vendor_id:
        q = q.filter(VendorInvoice.vendor_id == vendor_id)
    if unpaid:
        q = q.filter(VendorInvoice.is_paid == False)
    rows = q.order_by(VendorInvoice.invoice_date.desc()).all()
    result = []
    for r in rows:
        result.append({
            "id": r.id,
            "vendor_id": r.vendor_id,
            "vendor_name": r.vendor.name,
            "invoice_no": r.invoice_no,
            "invoice_date": r.invoice_date,
            "amount": r.amount,
            "tax": r.tax,
            "total_amount": r.total_amount,
            "description": r.description,
            "due_date": r.due_date,
            "is_paid": r.is_paid,
            "paid_date": r.paid_date,
            "paid_notes": r.paid_notes,
        })
    return result


@router.get("/{invoice_id}", response_model=VendorInvoiceOut)
def get_vendor_invoice(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(VendorInvoice).filter(VendorInvoice.id == invoice_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="發票不存在")
    return {
        "id": r.id,
        "vendor_id": r.vendor_id,
        "vendor_name": r.vendor.name,
        "invoice_no": r.invoice_no,
        "invoice_date": r.invoice_date,
        "amount": r.amount,
        "tax": r.tax,
        "total_amount": r.total_amount,
        "description": r.description,
        "due_date": r.due_date,
        "is_paid": r.is_paid,
        "paid_date": r.paid_date,
        "paid_notes": r.paid_notes,
    }


@router.post("", response_model=VendorInvoiceOut)
def create_vendor_invoice(data: VendorInvoiceCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    vendor = db.query(Vendor).filter(Vendor.id == data.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=400, detail="廠商不存在")
    inv = VendorInvoice(**data.model_dump())
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return get_vendor_invoice(inv.id, request, db)


@router.put("/{invoice_id}/payment", response_model=VendorInvoiceOut)
def update_vendor_invoice_payment(invoice_id: int, data: VendorInvoiceUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    inv = db.query(VendorInvoice).filter(VendorInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="發票不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)
    db.commit()
    return get_vendor_invoice(invoice_id, request, db)


@router.delete("/{invoice_id}")
def delete_vendor_invoice(invoice_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    inv = db.query(VendorInvoice).filter(VendorInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="發票不存在")
    db.delete(inv)
    db.commit()
    return {"ok": True}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Vendor
from ..schemas import VendorCreate, VendorUpdate, VendorOut
from ..auth import require_auth

router = APIRouter(prefix="/api/vendors", tags=["vendors"])


@router.get("", response_model=List[VendorOut])
def list_vendors(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    return db.query(Vendor).order_by(Vendor.id).all()


@router.get("/next-code")
def next_vendor_code(request: Request, prefix: str = "H", db: Session = Depends(get_db)):
    require_auth(request)
    pattern = prefix + "%"
    last = db.query(Vendor).filter(Vendor.code.like(pattern)).order_by(Vendor.id.desc()).first()
    if last:
        num_part = last.code[len(prefix):]
        if num_part.isdigit():
            seq = int(num_part) + 1
        else:
            seq = 1
    else:
        seq = 1
    return {"code": f"{prefix}{seq:02d}"}


@router.get("/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="廠商不存在")
    return vendor


@router.post("", response_model=VendorOut)
def create_vendor(data: VendorCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    if db.query(Vendor).filter(Vendor.code == data.code).first():
        raise HTTPException(status_code=400, detail="廠商編號已存在")
    vendor = Vendor(**data.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.put("/{vendor_id}", response_model=VendorOut)
def update_vendor(vendor_id: int, data: VendorUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="廠商不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor


@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="廠商不存在")
    db.delete(vendor)
    db.commit()
    return {"ok": True}

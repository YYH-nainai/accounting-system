from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Customer
from ..schemas import CustomerCreate, CustomerUpdate, CustomerOut
from ..auth import require_auth

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=List[CustomerOut])
def list_customers(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    return db.query(Customer).order_by(Customer.id).all()


@router.get("/next-code")
def next_customer_code(request: Request, prefix: str = "C", db: Session = Depends(get_db)):
    require_auth(request)
    pattern = prefix + "%"
    last = db.query(Customer).filter(Customer.code.like(pattern)).order_by(Customer.id.desc()).first()
    if last:
        num_part = last.code[len(prefix):]
        if num_part.isdigit():
            seq = int(num_part) + 1
        else:
            seq = 1
    else:
        seq = 1
    return {"code": f"{prefix}{seq:02d}"}


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="客戶不存在")
    return c


@router.post("", response_model=CustomerOut)
def create_customer(data: CustomerCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    if db.query(Customer).filter(Customer.code == data.code).first():
        raise HTTPException(status_code=400, detail="客戶編號已存在")
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, data: CustomerUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="客戶不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="客戶不存在")
    db.delete(c)
    db.commit()
    return {"ok": True}

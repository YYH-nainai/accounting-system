from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Account
from ..schemas import AccountCreate, AccountUpdate, AccountOut
from ..auth import require_auth

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountOut])
def list_accounts(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    return db.query(Account).order_by(Account.code).all()


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="科目不存在")
    return account


@router.post("", response_model=AccountOut)
def create_account(data: AccountCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    if db.query(Account).filter(Account.code == data.code).first():
        raise HTTPException(status_code=400, detail="科目代碼已存在")
    account = Account(**data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: int, data: AccountUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="科目不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(account_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="科目不存在")
    db.delete(account)
    db.commit()
    return {"ok": True}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Voucher, JournalEntry, Account
from ..schemas import VoucherCreate, VoucherOut
from ..auth import require_auth
from datetime import date

router = APIRouter(prefix="/api/vouchers", tags=["vouchers"])


def generate_voucher_no(db: Session) -> str:
    today = date.today()
    prefix = today.strftime("%Y%m%d")
    last = db.query(Voucher).filter(Voucher.voucher_no.like(f"{prefix}%")).order_by(Voucher.id.desc()).first()
    if last:
        seq = int(last.voucher_no[-4:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


@router.get("", response_model=List[VoucherOut])
def list_vouchers(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    vouchers = db.query(Voucher).order_by(Voucher.id.desc()).all()
    result = []
    for v in vouchers:
        entries = []
        for e in v.entries:
            entries.append({
                "id": e.id,
                "account_id": e.account_id,
                "account_name": e.account.name if e.account else None,
                "account_code": e.account.code if e.account else None,
                "debit": e.debit,
                "credit": e.credit,
                "description": e.description,
            })
        result.append({
            "id": v.id,
            "voucher_no": v.voucher_no,
            "date": v.date,
            "description": v.description,
            "user_id": v.user_id,
            "created_at": v.created_at,
            "entries": entries,
        })
    return result


@router.get("/{voucher_id}", response_model=VoucherOut)
def get_voucher(voucher_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    v = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="傳票不存在")
    entries = []
    for e in v.entries:
        entries.append({
            "id": e.id,
            "account_id": e.account_id,
            "account_name": e.account.name if e.account else None,
            "account_code": e.account.code if e.account else None,
            "debit": e.debit,
            "credit": e.credit,
            "description": e.description,
        })
    return {
        "id": v.id,
        "voucher_no": v.voucher_no,
        "date": v.date,
        "description": v.description,
        "user_id": v.user_id,
        "created_at": v.created_at,
        "entries": entries,
    }


@router.post("", response_model=VoucherOut)
def create_voucher(data: VoucherCreate, request: Request, db: Session = Depends(get_db)):
    user = require_auth(request)

    total_debit = sum(e.debit for e in data.entries)
    total_credit = sum(e.credit for e in data.entries)
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(status_code=400, detail=f"借貸不平衡: 借方={total_debit:.2f}, 貸方={total_credit:.2f}")
    if total_debit == 0:
        raise HTTPException(status_code=400, detail="金額不能為零")

    for e in data.entries:
        if e.debit > 0 and e.credit > 0:
            raise HTTPException(status_code=400, detail="一筆分錄不能同時有借貸方金額")
        if e.debit == 0 and e.credit == 0:
            raise HTTPException(status_code=400, detail="金額不能為零")
        account = db.query(Account).filter(Account.id == e.account_id).first()
        if not account:
            raise HTTPException(status_code=400, detail=f"科目ID {e.account_id} 不存在")

    voucher_no = generate_voucher_no(db)
    voucher = Voucher(
        voucher_no=voucher_no,
        date=data.date,
        description=data.description,
        user_id=user.id,
    )
    db.add(voucher)
    db.flush()

    for e in data.entries:
        entry = JournalEntry(
            voucher_id=voucher.id,
            account_id=e.account_id,
            debit=e.debit,
            credit=e.credit,
            description=e.description,
        )
        db.add(entry)

    db.commit()
    db.refresh(voucher)
    return get_voucher(voucher.id, request, db)


@router.delete("/{voucher_id}")
def delete_voucher(voucher_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="傳票不存在")
    db.delete(voucher)
    db.commit()
    return {"ok": True}

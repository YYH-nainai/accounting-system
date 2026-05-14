from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..database import get_db
from ..models import Account, JournalEntry, Voucher
from ..auth import require_auth

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


@router.get("/{account_id}")
def get_ledger(account_id: int, request: Request,
               start_date: Optional[str] = None, end_date: Optional[str] = None,
               db: Session = Depends(get_db)):
    require_auth(request)
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        return {"error": "科目不存在"}

    q = db.query(JournalEntry).join(Voucher).filter(JournalEntry.account_id == account_id)
    if start_date:
        q = q.filter(Voucher.date >= date.fromisoformat(start_date))
    if end_date:
        q = q.filter(Voucher.date <= date.fromisoformat(end_date))
    q = q.order_by(Voucher.date, Voucher.id)

    entries = q.all()
    rows = []
    balance = 0
    is_debit_normal = account.type in ("asset", "expense")

    for e in entries:
        if is_debit_normal:
            balance += e.debit - e.credit
        else:
            balance += e.credit - e.debit
        rows.append({
            "id": e.id,
            "voucher_no": e.voucher.voucher_no,
            "date": e.voucher.date.isoformat(),
            "voucher_description": e.voucher.description,
            "debit": e.debit,
            "credit": e.credit,
            "description": e.description,
            "balance": round(balance, 2),
        })

    return {
        "account": {"id": account.id, "code": account.code, "name": account.name, "type": account.type},
        "entries": rows,
    }

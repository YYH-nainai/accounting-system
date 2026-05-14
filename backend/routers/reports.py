from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional

from ..database import get_db
from ..models import Account, JournalEntry, Voucher
from ..auth import require_auth

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_account_balance(db: Session, account_id: int, up_to: Optional[date] = None) -> float:
    q = db.query(func.sum(JournalEntry.debit), func.sum(JournalEntry.credit))
    q = q.join(Voucher)
    if up_to:
        q = q.filter(Voucher.date <= up_to)
    q = q.filter(JournalEntry.account_id == account_id)
    row = q.first()
    total_debit = row[0] or 0
    total_credit = row[1] or 0
    account = db.query(Account).filter(Account.id == account_id).first()
    if account.type in ("asset", "expense"):
        return round(total_debit - total_credit, 2)
    else:
        return round(total_credit - total_debit, 2)


@router.get("/trial-balance")
def trial_balance(request: Request, as_of: Optional[str] = None, db: Session = Depends(get_db)):
    require_auth(request)
    up_to = date.fromisoformat(as_of) if as_of else None
    accounts = db.query(Account).filter(Account.is_active == True).order_by(Account.code).all()
    rows = []
    for acc in accounts:
        bal = get_account_balance(db, acc.id, up_to)
        if bal != 0:
            if acc.type in ("asset", "expense"):
                rows.append({"code": acc.code, "name": acc.name, "debit": abs(bal) if bal > 0 else 0, "credit": abs(bal) if bal < 0 else 0})
            else:
                rows.append({"code": acc.code, "name": acc.name, "debit": abs(bal) if bal < 0 else 0, "credit": abs(bal) if bal > 0 else 0})
    total_debit = sum(r["debit"] for r in rows)
    total_credit = sum(r["credit"] for r in rows)
    return {"rows": rows, "total_debit": round(total_debit, 2), "total_credit": round(total_credit, 2)}


@router.get("/income-statement")
def income_statement(request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None, db: Session = Depends(get_db)):
    require_auth(request)
    s = date.fromisoformat(start_date) if start_date else date(2000, 1, 1)
    e = date.fromisoformat(end_date) if end_date else date.today()

    revenues = db.query(Account).filter(Account.type == "revenue", Account.is_active == True).order_by(Account.code).all()
    expenses = db.query(Account).filter(Account.type == "expense", Account.is_active == True).order_by(Account.code).all()

    def get_sum(account_id):
        q = db.query(func.sum(JournalEntry.credit) - func.sum(JournalEntry.debit))
        q = q.join(Voucher).filter(JournalEntry.account_id == account_id, Voucher.date >= s, Voucher.date <= e)
        row = q.first()
        return round(row[0] or 0, 2)

    rev_rows = [{"code": a.code, "name": a.name, "amount": get_sum(a.id)} for a in revenues]
    exp_rows = [{"code": a.code, "name": a.name, "amount": abs(get_sum(a.id))} for a in expenses]

    total_revenue = sum(r["amount"] for r in rev_rows)
    total_expense = sum(r["amount"] for r in exp_rows)
    net_income = round(total_revenue - total_expense, 2)

    return {
        "revenues": rev_rows,
        "expenses": exp_rows,
        "total_revenue": total_revenue,
        "total_expense": total_expense,
        "net_income": net_income,
    }


@router.get("/balance-sheet")
def balance_sheet(request: Request, as_of: Optional[str] = None, db: Session = Depends(get_db)):
    require_auth(request)
    up_to = date.fromisoformat(as_of) if as_of else date.today()

    assets = db.query(Account).filter(Account.type == "asset", Account.is_active == True).order_by(Account.code).all()
    liabilities = db.query(Account).filter(Account.type == "liability", Account.is_active == True).order_by(Account.code).all()
    equities = db.query(Account).filter(Account.type == "equity", Account.is_active == True).order_by(Account.code).all()

    def get_bal(account_id):
        return get_account_balance(db, account_id, up_to)

    asset_rows = [{"code": a.code, "name": a.name, "amount": get_bal(a.id)} for a in assets if get_bal(a.id) != 0]
    liability_rows = [{"code": l.code, "name": l.name, "amount": get_bal(l.id)} for l in liabilities if get_bal(l.id) != 0]
    equity_rows = [{"code": e.code, "name": e.name, "amount": get_bal(e.id)} for e in equities if get_bal(e.id) != 0]

    total_assets = sum(r["amount"] for r in asset_rows)
    total_liabilities = sum(r["amount"] for r in liability_rows)
    total_equity = sum(r["amount"] for r in equity_rows)

    return {
        "assets": asset_rows,
        "liabilities": liability_rows,
        "equities": equity_rows,
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "total_equity": round(total_equity, 2),
    }

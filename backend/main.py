import os
from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import math
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .database import engine, Base, get_db, SessionLocal, DATABASE_URL
from .models import User, Account
from .auth import hash_password, verify_password, get_current_user, require_auth
from .routers import accounts, vouchers, ledger, reports

app = FastAPI(title="會計管理系統")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "accounting-system-secret-key-change-in-production"))

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates"))

app.include_router(accounts.router)
app.include_router(vouchers.router)
app.include_router(ledger.router)
app.include_router(reports.router)


def seed_default_data():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(username="admin", password_hash=hash_password("admin123"), display_name="管理員")
            db.add(admin)
            user2 = User(username="user1", password_hash=hash_password("user123"), display_name="使用者一")
            db.add(user2)
            user3 = User(username="user2", password_hash=hash_password("user123"), display_name="使用者二")
            db.add(user3)

        if not db.query(Account).first():
            accounts_data = [
                ("1100", "現金", "asset"),
                ("1200", "銀行存款", "asset"),
                ("1300", "應收帳款", "asset"),
                ("1400", "存貨", "asset"),
                ("1500", "辦公設備", "asset"),
                ("1600", "累計折舊", "asset"),
                ("2100", "應付帳款", "liability"),
                ("2200", "短期借款", "liability"),
                ("2300", "應付薪資", "liability"),
                ("3100", "股本", "equity"),
                ("3200", "保留盈餘", "equity"),
                ("4100", "銷貨收入", "revenue"),
                ("4200", "利息收入", "revenue"),
                ("5100", "薪資費用", "expense"),
                ("5200", "租金費用", "expense"),
                ("5300", "水電費用", "expense"),
                ("5400", "辦公費用", "expense"),
                ("5500", "折舊費用", "expense"),
            ]
            for code, name, typ in accounts_data:
                db.add(Account(code=code, name=name, type=typ))
        db.commit()
    finally:
        db.close()


@app.get("/api/storage")
def storage_info(request: Request):
    user = get_current_user(request)
    if not user:
        return {"error": "unauthorized"}
    limit_mb = 1024
    try:
        if DATABASE_URL.startswith("sqlite"):
            db_path = "accounting.db"
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
            else:
                size_bytes = 0
        else:
            db = SessionLocal()
            try:
                row = db.execute(text("SELECT pg_database_size(current_database())")).scalar()
                size_bytes = row
            finally:
                db.close()
        used_mb = round(size_bytes / (1024 * 1024), 2)
        pct = round((used_mb / limit_mb) * 100, 1)
        return {
            "used_mb": used_mb,
            "limit_mb": limit_mb,
            "percent": pct,
            "warn": pct >= 80,
            "danger": pct >= 95,
        }
    except Exception as e:
        return {"used_mb": 0, "limit_mb": limit_mb, "percent": 0, "warn": False, "danger": False, "error": str(e)}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_default_data()


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "帳號或密碼錯誤"})
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=302)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/accounts", response_class=HTMLResponse)
def accounts_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("accounts.html", {"request": request, "user": user})


@app.get("/vouchers", response_class=HTMLResponse)
def vouchers_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("vouchers.html", {"request": request, "user": user})


@app.get("/vouchers/new", response_class=HTMLResponse)
def new_voucher_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("voucher_form.html", {"request": request, "user": user})


@app.get("/vouchers/{voucher_id}/edit", response_class=HTMLResponse)
def edit_voucher_page(voucher_id: int, request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("voucher_form.html", {"request": request, "user": user, "voucher_id": voucher_id})


@app.get("/ledger", response_class=HTMLResponse)
def ledger_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("ledger.html", {"request": request, "user": user})


@app.get("/reports/trial-balance", response_class=HTMLResponse)
def trial_balance_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("trial_balance.html", {"request": request, "user": user})


@app.get("/reports/income-statement", response_class=HTMLResponse)
def income_statement_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("income_statement.html", {"request": request, "user": user})


@app.get("/reports/balance-sheet", response_class=HTMLResponse)
def balance_sheet_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("balance_sheet.html", {"request": request, "user": user})

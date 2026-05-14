from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str


class UserOut(BaseModel):
    id: int
    username: str
    display_name: str
    is_active: bool

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    code: str
    name: str
    type: str
    parent_id: Optional[int] = None
    description: Optional[str] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class AccountOut(BaseModel):
    id: int
    code: str
    name: str
    type: str
    parent_id: Optional[int] = None
    is_active: bool
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class EntryCreate(BaseModel):
    account_id: int
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None


class VoucherCreate(BaseModel):
    date: date
    description: Optional[str] = None
    entries: List[EntryCreate]


class EntryOut(BaseModel):
    id: int
    account_id: int
    account_name: Optional[str] = None
    account_code: Optional[str] = None
    debit: float
    credit: float
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class VoucherOut(BaseModel):
    id: int
    voucher_no: str
    date: date
    description: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    entries: List[EntryOut] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str

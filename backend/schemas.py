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


# === Vendor ===
class VendorCreate(BaseModel):
    code: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_code: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_code: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None


class VendorOut(BaseModel):
    id: int
    code: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None
    bank_name: Optional[str] = None
    bank_branch: Optional[str] = None
    bank_code: Optional[str] = None
    bank_account: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# === Vendor Invoice ===
class VendorInvoiceCreate(BaseModel):
    vendor_id: int
    invoice_no: str
    invoice_date: date
    amount: float = 0.0
    tax: float = 0.0
    total_amount: float = 0.0
    description: Optional[str] = None
    due_date: Optional[date] = None


class VendorInvoiceUpdate(BaseModel):
    is_paid: Optional[bool] = None
    paid_date: Optional[date] = None
    paid_notes: Optional[str] = None


class VendorInvoiceOut(BaseModel):
    id: int
    vendor_id: int
    vendor_name: Optional[str] = None
    invoice_no: str
    invoice_date: date
    amount: float
    tax: float
    total_amount: float
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_paid: bool
    paid_date: Optional[date] = None
    paid_notes: Optional[str] = None

    model_config = {"from_attributes": True}


# === Customer ===
class CustomerCreate(BaseModel):
    code: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None


class CustomerOut(BaseModel):
    id: int
    code: str
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# === Receivable ===
class ReceivableCreate(BaseModel):
    customer_id: int
    invoice_no: str
    invoice_date: date
    amount: float = 0.0
    tax: float = 0.0
    total_amount: float = 0.0
    description: Optional[str] = None
    due_date: Optional[date] = None


class ReceivableUpdate(BaseModel):
    is_received: Optional[bool] = None
    received_date: Optional[date] = None
    received_notes: Optional[str] = None


class ReceivableOut(BaseModel):
    id: int
    customer_id: int
    customer_name: Optional[str] = None
    invoice_no: str
    invoice_date: date
    amount: float
    tax: float
    total_amount: float
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_received: bool
    received_date: Optional[date] = None
    received_notes: Optional[str] = None

    model_config = {"from_attributes": True}


# === Employee ===
class EmployeeCreate(BaseModel):
    code: str
    name: str
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    position: Optional[str] = None
    base_salary: float = 0.0
    labor_grade_id: Optional[int] = None
    health_grade_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    position: Optional[str] = None
    base_salary: Optional[float] = None
    labor_grade_id: Optional[int] = None
    health_grade_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeOut(BaseModel):
    id: int
    code: str
    name: str
    id_number: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    position: Optional[str] = None
    base_salary: float
    labor_grade_id: Optional[int] = None
    health_grade_id: Optional[int] = None
    is_active: bool

    model_config = {"from_attributes": True}


# === Insurance Grade ===
class InsuranceGradeCreate(BaseModel):
    year: int
    type: str
    grade: int
    salary_from: float = 0.0
    salary_to: float = 0.0
    insured_amount: float = 0.0


class InsuranceGradeOut(BaseModel):
    id: int
    year: int
    type: str
    grade: int
    salary_from: float
    salary_to: float
    insured_amount: float

    model_config = {"from_attributes": True}


# === Insurance Rate ===
class InsuranceRateCreate(BaseModel):
    year: int
    type: str
    rate_percent: float
    employee_share: float
    employer_share: float


class InsuranceRateOut(BaseModel):
    id: int
    year: int
    type: str
    rate_percent: float
    employee_share: float
    employer_share: float

    model_config = {"from_attributes": True}

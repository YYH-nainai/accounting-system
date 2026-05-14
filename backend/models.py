from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import date, datetime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # asset, liability, equity, revenue, expense
    parent_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

    children = relationship("Account", backref="parent", remote_side=[id])


class Voucher(Base):
    __tablename__ = "vouchers"

    id = Column(Integer, primary_key=True, index=True)
    voucher_no = Column(String(30), unique=True, index=True, nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    entries = relationship("JournalEntry", back_populates="voucher", cascade="all, delete-orphan")
    user = relationship("User")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    description = Column(Text, nullable=True)

    voucher = relationship("Voucher", back_populates="entries")
    account = relationship("Account")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(100), nullable=True)
    bank_code = Column(String(20), nullable=True)
    bank_account = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True, comment="廠商分類")
    payment_terms = Column(String(100), nullable=True, comment="月結票期，如：月結30天")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    invoices = relationship("VendorInvoice", back_populates="vendor", cascade="all, delete-orphan")


class VendorInvoice(Base):
    __tablename__ = "vendor_invoices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    invoice_no = Column(String(50), index=True, nullable=False)
    invoice_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    is_paid = Column(Boolean, default=False)
    paid_date = Column(Date, nullable=True)
    paid_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    vendor = relationship("Vendor", back_populates="invoices")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    contact_person = Column(String(50), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    payment_terms = Column(String(100), nullable=True, comment="月結票期，如：月結30天")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    receivables = relationship("Receivable", back_populates="customer", cascade="all, delete-orphan")


class Receivable(Base):
    __tablename__ = "receivables"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_no = Column(String(50), index=True, nullable=False)
    invoice_date = Column(Date, nullable=False, default=date.today)
    amount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    is_received = Column(Boolean, default=False)
    received_date = Column(Date, nullable=True)
    received_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    customer = relationship("Customer", back_populates="receivables")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    id_number = Column(String(20), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    position = Column(String(100), nullable=True)
    base_salary = Column(Float, default=0.0)
    labor_grade_id = Column(Integer, ForeignKey("insurance_grades.id"), nullable=True)
    health_grade_id = Column(Integer, ForeignKey("insurance_grades.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    labor_grade = relationship("InsuranceGrade", foreign_keys=[labor_grade_id])
    health_grade = relationship("InsuranceGrade", foreign_keys=[health_grade_id])


class InsuranceGrade(Base):
    __tablename__ = "insurance_grades"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(10), nullable=False)  # labor or health
    grade = Column(Integer, nullable=False)
    salary_from = Column(Float, default=0.0)
    salary_to = Column(Float, default=0.0)
    insured_amount = Column(Float, default=0.0)

    __table_args__ = ({"sqlite_autoincrement": True},)  # prevent duplicate (year, type, grade)


class InsuranceRate(Base):
    __tablename__ = "insurance_rates"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False, index=True)
    type = Column(String(10), nullable=False)  # labor or health
    rate_percent = Column(Float, nullable=False)
    employee_share = Column(Float, nullable=False)
    employer_share = Column(Float, nullable=False)

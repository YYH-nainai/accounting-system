from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Employee, InsuranceGrade, InsuranceRate
from ..schemas import EmployeeCreate, EmployeeUpdate, EmployeeOut
from ..auth import require_auth

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.get("", response_model=List[EmployeeOut])
def list_employees(request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    return db.query(Employee).order_by(Employee.code).all()


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(employee_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="員工不存在")
    return emp


@router.post("", response_model=EmployeeOut)
def create_employee(data: EmployeeCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    if db.query(Employee).filter(Employee.code == data.code).first():
        raise HTTPException(status_code=400, detail="員工編號已存在")
    emp = Employee(**data.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@router.put("/{employee_id}", response_model=EmployeeOut)
def update_employee(employee_id: int, data: EmployeeUpdate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="員工不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return emp


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="員工不存在")
    db.delete(emp)
    db.commit()
    return {"ok": True}


@router.get("/{employee_id}/insurance-detail")
def employee_insurance_detail(employee_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="員工不存在")

    result = {
        "base_salary": emp.base_salary,
        "labor": None,
        "health": None,
    }

    if emp.labor_grade_id:
        lg = db.query(InsuranceGrade).filter(InsuranceGrade.id == emp.labor_grade_id).first()
        lr = db.query(InsuranceRate).filter(
            InsuranceRate.year == lg.year, InsuranceRate.type == "labor"
        ).first() if lg else None
        if lg and lr:
            emp_premium = round(lg.insured_amount * lr.rate_percent / 100 * lr.employee_share / 100, 0)
            result["labor"] = {
                "grade": lg.grade,
                "insured_amount": lg.insured_amount,
                "rate_percent": lr.rate_percent,
                "employee_premium": emp_premium,
                "employer_premium": round(lg.insured_amount * lr.rate_percent / 100 * lr.employer_share / 100, 0),
            }

    if emp.health_grade_id:
        hg = db.query(InsuranceGrade).filter(InsuranceGrade.id == emp.health_grade_id).first()
        hr = db.query(InsuranceRate).filter(
            InsuranceRate.year == hg.year, InsuranceRate.type == "health"
        ).first() if hg else None
        if hg and hr:
            emp_premium = round(hg.insured_amount * hr.rate_percent / 100 * hr.employee_share / 100, 0)
            result["health"] = {
                "grade": hg.grade,
                "insured_amount": hg.insured_amount,
                "rate_percent": hr.rate_percent,
                "employee_premium": emp_premium,
                "employer_premium": round(hg.insured_amount * hr.rate_percent / 100 * hr.employer_share / 100, 0),
            }

    return result

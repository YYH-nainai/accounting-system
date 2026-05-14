from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List

from ..database import get_db
from ..models import InsuranceGrade, InsuranceRate
from ..schemas import InsuranceGradeCreate, InsuranceGradeOut, InsuranceRateCreate, InsuranceRateOut
from ..auth import require_auth

router = APIRouter(prefix="/api/insurance", tags=["insurance"])


@router.get("/grades", response_model=List[InsuranceGradeOut])
def list_grades(request: Request, year: int = None, type: str = None, db: Session = Depends(get_db)):
    require_auth(request)
    q = db.query(InsuranceGrade)
    if year:
        q = q.filter(InsuranceGrade.year == year)
    if type:
        q = q.filter(InsuranceGrade.type == type)
    return q.order_by(InsuranceGrade.year.desc(), InsuranceGrade.type, InsuranceGrade.grade).all()


@router.post("/grades", response_model=InsuranceGradeOut)
def create_grade(data: InsuranceGradeCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    existing = db.query(InsuranceGrade).filter(
        InsuranceGrade.year == data.year,
        InsuranceGrade.type == data.type,
        InsuranceGrade.grade == data.grade,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="該年度此級距已存在")
    g = InsuranceGrade(**data.model_dump())
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


@router.delete("/grades/{grade_id}")
def delete_grade(grade_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    g = db.query(InsuranceGrade).filter(InsuranceGrade.id == grade_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="級距不存在")
    db.delete(g)
    db.commit()
    return {"ok": True}


@router.get("/rates", response_model=List[InsuranceRateOut])
def list_rates(request: Request, year: int = None, type: str = None, db: Session = Depends(get_db)):
    require_auth(request)
    q = db.query(InsuranceRate)
    if year:
        q = q.filter(InsuranceRate.year == year)
    if type:
        q = q.filter(InsuranceRate.type == type)
    return q.order_by(InsuranceRate.year.desc(), InsuranceRate.type).all()


@router.post("/rates", response_model=InsuranceRateOut)
def create_rate(data: InsuranceRateCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    existing = db.query(InsuranceRate).filter(
        InsuranceRate.year == data.year,
        InsuranceRate.type == data.type,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="該年度此類別費率已存在")
    r = InsuranceRate(**data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/rates/{rate_id}", response_model=InsuranceRateOut)
def update_rate(rate_id: int, data: InsuranceRateCreate, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(InsuranceRate).filter(InsuranceRate.id == rate_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="費率不存在")
    for key, value in data.model_dump().items():
        setattr(r, key, value)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/rates/{rate_id}")
def delete_rate(rate_id: int, request: Request, db: Session = Depends(get_db)):
    require_auth(request)
    r = db.query(InsuranceRate).filter(InsuranceRate.id == rate_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="費率不存在")
    db.delete(r)
    db.commit()
    return {"ok": True}

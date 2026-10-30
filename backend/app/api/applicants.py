from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime, date
from backend.app.database import get_db
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.schemas.applicant import ApplicantCreate, ApplicantResponse, ApplicantListResponse, InsuredAssetResponse, InsuredAssetCreate
from backend.app.utils.sequence import generate_applicant_id, generate_asset_id

router = APIRouter(prefix="/applicants", tags=["Applicants"])


@router.get("", response_model=ApplicantListResponse)
def list_applicants(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Applicant)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Applicant.business_id.ilike(search_filter),
                Applicant.first_name.ilike(search_filter),
                Applicant.last_name.ilike(search_filter),
                Applicant.email.ilike(search_filter),
                Applicant.city.ilike(search_filter)
            )
        )
    total = query.count()
    items = query.order_by(Applicant.id.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return ApplicantListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/{id}", response_model=ApplicantResponse)
def get_applicant(id: int, db: Session = Depends(get_db)):
    app = db.query(Applicant).filter(Applicant.id == id).first()
    if not app:
        raise HTTPException(status_code=404, detail=f"Applicant with ID {id} not found.")
    return app


@router.post("", response_model=ApplicantResponse, status_code=201)
def create_applicant(payload: ApplicantCreate, db: Session = Depends(get_db)):
    # Calculate age
    today = date.today()
    age = today.year - payload.date_of_birth.year - (
        (today.month, today.day) < (payload.date_of_birth.month, payload.date_of_birth.day)
    )

    # Next business ID
    count = db.query(Applicant).count()
    business_id = generate_applicant_id(count + 1)

    app = Applicant(
        business_id=business_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        age=age,
        gender=payload.gender,
        address_line=payload.address_line,
        city=payload.city,
        state=payload.state,
        postal_code=payload.postal_code,
        country=payload.country,
        annual_income=payload.annual_income,
        credit_score=payload.credit_score,
        occupation=payload.occupation,
        employment_status=payload.employment_status,
        claims_count_5yr=payload.claims_count_5yr
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Optional initial asset creation
    if payload.initial_asset:
        ast_count = db.query(InsuredAsset).count()
        ast_business_id = generate_asset_id(ast_count + 1)
        ident = payload.initial_asset.identifier or f"ID-{payload.initial_asset.asset_type[:3]}-{ast_count + 1:06d}"
        asset = InsuredAsset(
            business_id=ast_business_id,
            applicant_id=app.id,
            asset_type=payload.initial_asset.asset_type,
            identifier=ident,
            asset_value=payload.initial_asset.asset_value,
            year_built_or_manufactured=payload.initial_asset.year_built_or_manufactured,
            make_model=payload.initial_asset.make_model,
            location_tier=payload.initial_asset.location_tier,
            details=payload.initial_asset.details or {}
        )
        db.add(asset)
        db.commit()
        db.refresh(app)

    return app


@router.post("/{id}/assets", response_model=InsuredAssetResponse, status_code=201)
def add_applicant_asset(id: int, payload: InsuredAssetCreate, db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail=f"Applicant with ID {id} not found.")

    ast_count = db.query(InsuredAsset).count()
    ast_business_id = generate_asset_id(ast_count + 1)
    ident = payload.identifier or f"ID-{payload.asset_type[:3]}-{ast_count + 1:06d}"

    asset = InsuredAsset(
        business_id=ast_business_id,
        applicant_id=applicant.id,
        asset_type=payload.asset_type,
        identifier=ident,
        asset_value=payload.asset_value,
        year_built_or_manufactured=payload.year_built_or_manufactured,
        make_model=payload.make_model,
        location_tier=payload.location_tier,
        details=payload.details or {}
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get("/{id}/assets", response_model=List[InsuredAssetResponse])
def list_applicant_assets(id: int, db: Session = Depends(get_db)):
    applicant = db.query(Applicant).filter(Applicant.id == id).first()
    if not applicant:
        raise HTTPException(status_code=404, detail=f"Applicant with ID {id} not found.")
    return applicant.assets

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.anomaly import AnomalyRecord
from backend.app.schemas.anomaly import AnomalyResponse, AnomalySummaryResponse
from backend.app.anomaly_detection.detector import run_anomaly_detection
from backend.app.anomaly_detection.evaluator import evaluate_anomaly_metrics

router = APIRouter(prefix="/anomalies", tags=["Anomalies"])


@router.get("", response_model=List[AnomalyResponse])
def list_anomalies(
    severity: Optional[str] = None,
    issue_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AnomalyRecord)
    if severity:
        query = query.filter(AnomalyRecord.severity == severity)
    if issue_type:
        query = query.filter(AnomalyRecord.issue_type == issue_type)
    return query.order_by(AnomalyRecord.id.desc()).all()


@router.get("/summary", response_model=AnomalySummaryResponse)
def get_anomalies_summary(db: Session = Depends(get_db)):
    all_anomalies = db.query(AnomalyRecord).all()
    
    sev_counts = {}
    issue_counts = {}
    for a in all_anomalies:
        sev_counts[a.severity] = sev_counts.get(a.severity, 0) + 1
        issue_counts[a.issue_type] = issue_counts.get(a.issue_type, 0) + 1

    eval_metrics = evaluate_anomaly_metrics(db)

    return AnomalySummaryResponse(
        total_anomalies=len(all_anomalies),
        severity_breakdown=sev_counts,
        issue_type_breakdown=issue_counts,
        evaluation_metrics=eval_metrics
    )


@router.get("/{id}", response_model=AnomalyResponse)
def get_anomaly(id: int, db: Session = Depends(get_db)):
    anm = db.query(AnomalyRecord).filter(AnomalyRecord.id == id).first()
    if not anm:
        raise HTTPException(status_code=404, detail="Anomaly record not found.")
    return anm


@router.post("/detect", response_model=List[AnomalyResponse])
def trigger_detection(db: Session = Depends(get_db)):
    detected = run_anomaly_detection(db)
    return detected

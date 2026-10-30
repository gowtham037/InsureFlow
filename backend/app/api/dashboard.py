from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from backend.app.database import get_db
from backend.app.models.applicant import Applicant
from backend.app.models.quote import Quote
from backend.app.models.policy import Policy
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.models.renewal import Renewal
from backend.app.models.anomaly import AnomalyRecord
from backend.app.models.product import Product
from backend.app.schemas.dashboard import (
    DashboardSummary,
    DashboardMetrics,
    ProductDistributionItem,
    RiskDistributionItem
)
from backend.app.anomaly_detection.evaluator import evaluate_anomaly_metrics
from backend.app.validation.validator import run_comprehensive_validation

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_applicants = db.query(Applicant).count()
    total_quotes = db.query(Quote).count()
    issued_policies = db.query(Policy).count()
    active_policies = db.query(Policy).filter(Policy.status == "ACTIVE").count()
    
    # Decisions
    total_decisions = db.query(UnderwritingDecision).count()
    approved_decisions = db.query(UnderwritingDecision).filter(
        UnderwritingDecision.decision.in_(["APPROVED", "APPROVED_WITH_CONDITIONS"])
    ).count()
    declined_decisions = db.query(UnderwritingDecision).filter(
        UnderwritingDecision.decision == "DECLINED"
    ).count()
    referred_decisions = db.query(UnderwritingDecision).filter(
        UnderwritingDecision.decision == "REFERRED"
    ).count()

    approval_rate = round((approved_decisions / total_decisions) * 100, 2) if total_decisions > 0 else 0.0
    rejection_rate = round((declined_decisions / total_decisions) * 100, 2) if total_decisions > 0 else 0.0
    referral_rate = round((referred_decisions / total_decisions) * 100, 2) if total_decisions > 0 else 0.0

    renewals = db.query(Renewal).count()
    total_anomalies = db.query(AnomalyRecord).count()

    return DashboardSummary(
        total_applicants=total_applicants,
        total_quotes=total_quotes,
        issued_policies=issued_policies,
        active_policies=active_policies,
        pending_underwriting_reviews=referred_decisions,
        renewals=renewals,
        total_anomalies=total_anomalies,
        approval_rate=approval_rate,
        rejection_rate=rejection_rate,
        referral_rate=referral_rate
    )


@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    total_quotes = db.query(Quote).count()
    
    decisions = db.query(UnderwritingDecision).all()
    total_dec = len(decisions)
    appr = sum(1 for d in decisions if d.decision in ["APPROVED", "APPROVED_WITH_CONDITIONS"])
    decl = sum(1 for d in decisions if d.decision == "DECLINED")
    ref = sum(1 for d in decisions if d.decision == "REFERRED")

    appr_rate = round((appr / total_dec) * 100, 2) if total_dec > 0 else 0.0
    decl_rate = round((decl / total_dec) * 100, 2) if total_dec > 0 else 0.0
    ref_rate = round((ref / total_dec) * 100, 2) if total_dec > 0 else 0.0

    total_policies = db.query(Policy).count()
    cancelled_policies = db.query(Policy).filter(Policy.status == "CANCELLED").count()
    canc_rate = round((cancelled_policies / total_policies) * 100, 2) if total_policies > 0 else 0.0

    renewals = db.query(Renewal).all()
    total_ren = len(renewals)
    acc_ren = sum(1 for r in renewals if r.status == "ACCEPTED")
    ren_acc_rate = round((acc_ren / total_ren) * 100, 2) if total_ren > 0 else 0.0

    avg_prem = db.query(func.avg(Policy.annual_premium)).scalar() or 0.0
    avg_risk = db.query(func.avg(Quote.risk_score)).scalar() or 0.0

    # Anomaly evaluation metrics
    eval_metrics = evaluate_anomaly_metrics(db)

    # Validation pass rate
    val_report = run_comprehensive_validation(db)

    return DashboardMetrics(
        total_quotes_evaluated=total_quotes,
        approval_rate=appr_rate,
        decline_rate=decl_rate,
        referral_rate=ref_rate,
        total_policies_issued=total_policies,
        renewal_acceptance_rate=ren_acc_rate,
        cancellation_rate=canc_rate,
        average_premium=round(float(avg_prem), 2),
        average_risk_score=round(float(avg_risk), 1),
        total_anomalies=eval_metrics.get("total_detected", 0),
        true_positives=eval_metrics.get("true_positives", 0),
        false_positives=eval_metrics.get("false_positives", 0),
        false_negatives=eval_metrics.get("false_negatives", 0),
        precision=eval_metrics.get("precision", 0.0),
        recall=eval_metrics.get("recall", 0.0),
        f1_score=eval_metrics.get("f1_score", 0.0),
        dataset_validation_pass_rate=val_report.get("validation_pass_rate_pct", 100.0)
    )


@router.get("/product-distribution", response_model=List[ProductDistributionItem])
def get_product_distribution(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    result = []
    for p in products:
        pol_count = db.query(Policy).filter(Policy.product_id == p.id).count()
        qte_count = db.query(Quote).filter(Quote.product_id == p.id).count()
        tot_prem = db.query(func.sum(Policy.annual_premium)).filter(Policy.product_id == p.id).scalar() or 0.0
        result.append(ProductDistributionItem(
            product_code=p.product_code,
            product_name=p.name,
            line_of_business=p.line_of_business,
            policy_count=pol_count,
            quote_count=qte_count,
            total_premium=round(float(tot_prem), 2)
        ))
    return result


@router.get("/risk-distribution", response_model=List[RiskDistributionItem])
def get_risk_distribution(db: Session = Depends(get_db)):
    tiers = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    result = []
    for t in tiers:
        q_count = db.query(Quote).filter(Quote.risk_tier == t).count()
        p_count = db.query(Policy).join(Quote).filter(Quote.risk_tier == t).count()
        avg_s = db.query(func.avg(Quote.risk_score)).filter(Quote.risk_tier == t).scalar() or 0.0
        result.append(RiskDistributionItem(
            risk_tier=t,
            quote_count=q_count,
            policy_count=p_count,
            average_score=round(float(avg_s), 1)
        ))
    return result


@router.get("/policy-lifecycle")
def get_lifecycle_distribution(db: Session = Depends(get_db)):
    statuses = ["ISSUED", "ACTIVE", "CANCELLED", "EXPIRED"]
    data = []
    for s in statuses:
        cnt = db.query(Policy).filter(Policy.status == s).count()
        data.append({"status": s, "count": cnt})
    return data


@router.get("/renewal-outcomes")
def get_renewal_outcomes(db: Session = Depends(get_db)):
    statuses = ["ACCEPTED", "OFFERED", "DECLINED"]
    data = []
    for s in statuses:
        cnt = db.query(Renewal).filter(Renewal.status == s).count()
        data.append({"status": s, "count": cnt})
    return data

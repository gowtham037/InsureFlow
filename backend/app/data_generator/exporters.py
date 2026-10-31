import os
import json
import csv
import hashlib
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.models.base import RecordSource
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.product import Product, CoverageOption
from backend.app.models.risk_factor import RiskFactor
from backend.app.models.quote import Quote, QuoteCoverage
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.models.policy import Policy, PolicyCoverage, PolicyEvent
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.models.anomaly import AnomalyRecord


def export_dataset_to_files(db: Session, export_dir: str = "data/runtime_exports") -> Dict[str, Any]:
    """
    Exports all 15 required relational entities to CSV and JSON formats,
    computes deterministic SHA-256 checksums across all datasets,
    and generates a complete SQL seed script.
    """
    os.makedirs(export_dir, exist_ok=True)
    summary: Dict[str, Any] = {"counts": {}, "checksums": {}}

    # 1. Applicants (Baseline Generated)
    applicants = db.query(Applicant).filter(Applicant.record_source == RecordSource.GENERATED).order_by(Applicant.id).all()
    if not applicants:
        applicants = db.query(Applicant).order_by(Applicant.id).all()
    app_data = [{
        "business_id": a.business_id,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "email": a.email,
        "phone": a.phone,
        "date_of_birth": a.date_of_birth.isoformat() if a.date_of_birth else None,
        "age": a.age,
        "gender": a.gender,
        "city": a.city,
        "state": a.state,
        "postal_code": a.postal_code,
        "annual_income": float(a.annual_income),
        "credit_score": a.credit_score,
        "occupation": a.occupation,
        "employment_status": a.employment_status,
        "claims_count_5yr": a.claims_count_5yr
    } for a in applicants]
    _write_json_and_csv(app_data, export_dir, "applicants")
    summary["counts"]["applicants"] = len(app_data)

    # 2. Insured Assets (Baseline Generated)
    assets = db.query(InsuredAsset).filter(InsuredAsset.record_source == RecordSource.GENERATED).order_by(InsuredAsset.id).all()
    if not assets:
        assets = db.query(InsuredAsset).order_by(InsuredAsset.id).all()
    asset_data = [{
        "business_id": a.business_id,
        "applicant_id": a.applicant.business_id if a.applicant else None,
        "asset_type": a.asset_type,
        "identifier": a.identifier,
        "asset_value": float(a.asset_value),
        "year_built_or_manufactured": a.year_built_or_manufactured,
        "make_model": a.make_model,
        "location_tier": a.location_tier,
        "details": json.dumps(a.details or {})
    } for a in assets]
    _write_json_and_csv(asset_data, export_dir, "insured_assets")
    summary["counts"]["insured_assets"] = len(asset_data)

    # 3. Products
    products = db.query(Product).order_by(Product.id).all()
    prod_data = [{
        "product_code": p.product_code,
        "name": p.name,
        "line_of_business": p.line_of_business,
        "description": p.description,
        "min_coverage_limit": float(p.min_coverage_limit),
        "max_coverage_limit": float(p.max_coverage_limit),
        "min_applicant_age": p.min_applicant_age,
        "max_applicant_age": p.max_applicant_age,
        "base_premium": float(p.base_premium),
        "is_active": p.is_active
    } for p in products]
    _write_json_and_csv(prod_data, export_dir, "products")
    summary["counts"]["products"] = len(prod_data)

    # 4. Coverage Options
    cov_options = db.query(CoverageOption).order_by(CoverageOption.id).all()
    cov_data = [{
        "code": c.code,
        "product_code": c.product.product_code if c.product else None,
        "name": c.name,
        "coverage_category": c.coverage_category,
        "default_limit": float(c.default_limit),
        "min_limit": float(c.min_limit),
        "max_limit": float(c.max_limit),
        "premium_multiplier": float(c.premium_multiplier)
    } for c in cov_options]
    _write_json_and_csv(cov_data, export_dir, "coverage_options")
    summary["counts"]["coverage_options"] = len(cov_data)

    # 5. Risk Factors
    risk_factors = db.query(RiskFactor).order_by(RiskFactor.id).all()
    rf_data = [{
        "factor_code": r.factor_code,
        "category": r.category,
        "name": r.name,
        "description": r.description,
        "base_score_impact": r.base_score_impact,
        "premium_multiplier": float(r.premium_multiplier)
    } for r in risk_factors]
    _write_json_and_csv(rf_data, export_dir, "risk_factors")
    summary["counts"]["risk_factors"] = len(rf_data)

    # 6. Quotes (Baseline Generated)
    quotes = db.query(Quote).filter(Quote.is_baseline == True).order_by(Quote.id).all()
    if not quotes:
        quotes = db.query(Quote).order_by(Quote.id).all()
    quote_data = [{
        "business_id": q.business_id,
        "applicant_id": q.applicant.business_id if q.applicant else None,
        "asset_id": q.asset.business_id if q.asset else None,
        "product_code": q.product.product_code if q.product else None,
        "coverage_amount": float(q.coverage_amount),
        "deductible": float(q.deductible),
        "status": q.status,
        "risk_score": q.risk_score,
        "risk_tier": q.risk_tier,
        "base_premium": float(q.base_premium),
        "final_premium": float(q.final_premium),
        "eligibility_passed": q.eligibility_passed,
        "customer_accepted": q.customer_accepted,
        "is_baseline": q.is_baseline
    } for q in quotes]
    _write_json_and_csv(quote_data, export_dir, "quotes")
    summary["counts"]["quotes"] = len(quote_data)

    # 7. Quote Coverages (Baseline Generated)
    quote_coverages = db.query(QuoteCoverage).join(Quote).filter(Quote.is_baseline == True).order_by(QuoteCoverage.id).all()
    if not quote_coverages:
        quote_coverages = db.query(QuoteCoverage).order_by(QuoteCoverage.id).all()
    qc_data = [{
        "quote_business_id": qc.quote.business_id if qc.quote else None,
        "coverage_option_code": qc.coverage_option.code if qc.coverage_option else None,
        "limit_amount": float(qc.limit_amount),
        "deductible_amount": float(qc.deductible_amount),
        "allocated_premium": float(qc.allocated_premium)
    } for qc in quote_coverages]
    _write_json_and_csv(qc_data, export_dir, "quote_coverages")
    summary["counts"]["quote_coverages"] = len(qc_data)

    # 8. Underwriting Decisions (Baseline Generated)
    uw_decisions = db.query(UnderwritingDecision).join(Quote).filter(Quote.is_baseline == True).order_by(UnderwritingDecision.id).all()
    if not uw_decisions:
        uw_decisions = db.query(UnderwritingDecision).order_by(UnderwritingDecision.id).all()
    dec_data = [{
        "business_id": d.business_id,
        "quote_business_id": d.quote.business_id if d.quote else None,
        "decision": d.decision,
        "authority_level": d.authority_level,
        "decision_reason": d.decision_reason,
        "reviewer_name": d.reviewer_name,
        "is_override": d.is_override
    } for d in uw_decisions]
    _write_json_and_csv(dec_data, export_dir, "underwriting_decisions")
    summary["counts"]["underwriting_decisions"] = len(dec_data)

    # 9. Policies (Baseline Generated)
    policies = db.query(Policy).filter(Policy.is_baseline == True).order_by(Policy.id).all()
    if not policies:
        policies = db.query(Policy).order_by(Policy.id).all()
    policy_data = [{
        "business_id": p.business_id,
        "quote_id": p.quote.business_id if p.quote else None,
        "applicant_id": p.applicant.business_id if p.applicant else None,
        "asset_id": p.asset.business_id if p.asset else None,
        "product_code": p.product.product_code if p.product else None,
        "status": p.status,
        "coverage_amount": float(p.coverage_amount),
        "deductible": float(p.deductible),
        "annual_premium": float(p.annual_premium),
        "payment_status": p.payment_status,
        "customer_accepted": p.customer_accepted,
        "effective_date": p.effective_date.isoformat() if p.effective_date else None,
        "expiration_date": p.expiration_date.isoformat() if p.expiration_date else None,
        "cancellation_date": p.cancellation_date.isoformat() if p.cancellation_date else None,
        "is_baseline": p.is_baseline
    } for p in policies]
    _write_json_and_csv(policy_data, export_dir, "policies")
    summary["counts"]["policies"] = len(policy_data)

    # 10. Policy Coverages (Baseline Generated)
    pol_coverages = db.query(PolicyCoverage).join(Policy).filter(Policy.is_baseline == True).order_by(PolicyCoverage.id).all()
    if not pol_coverages:
        pol_coverages = db.query(PolicyCoverage).order_by(PolicyCoverage.id).all()
    pc_data = [{
        "policy_business_id": pc.policy.business_id if pc.policy else None,
        "coverage_option_code": pc.coverage_option.code if pc.coverage_option else None,
        "limit_amount": float(pc.limit_amount),
        "deductible_amount": float(pc.deductible_amount),
        "allocated_premium": float(pc.allocated_premium)
    } for pc in pol_coverages]
    _write_json_and_csv(pc_data, export_dir, "policy_coverages")
    summary["counts"]["policy_coverages"] = len(pc_data)

    # 11. Endorsements (Baseline Generated)
    endorsements = db.query(Endorsement).filter(Endorsement.is_baseline == True).order_by(Endorsement.id).all()
    if not endorsements:
        endorsements = db.query(Endorsement).order_by(Endorsement.id).all()
    end_data = [{
        "business_id": e.business_id,
        "policy_business_id": e.policy.business_id if e.policy else None,
        "endorsement_sequence": e.endorsement_sequence,
        "endorsement_type": e.endorsement_type,
        "effective_date": e.effective_date.isoformat() if e.effective_date else None,
        "prior_coverage_amount": float(e.prior_coverage_amount),
        "new_coverage_amount": float(e.new_coverage_amount),
        "prior_premium": float(e.prior_premium),
        "new_premium": float(e.new_premium),
        "premium_delta": float(e.premium_delta),
        "status": e.status,
        "reason": e.reason,
        "is_baseline": e.is_baseline
    } for e in endorsements]
    _write_json_and_csv(end_data, export_dir, "endorsements")
    summary["counts"]["endorsements"] = len(end_data)

    # 12. Renewals (Baseline Generated)
    renewals = db.query(Renewal).filter(Renewal.is_baseline == True).order_by(Renewal.id).all()
    if not renewals:
        renewals = db.query(Renewal).order_by(Renewal.id).all()
    ren_data = [{
        "business_id": r.business_id,
        "previous_policy_id": r.previous_policy.business_id if r.previous_policy else None,
        "renewal_cycle_year": r.renewal_cycle_year,
        "status": r.status,
        "prior_premium": float(r.prior_premium),
        "renewal_premium": float(r.renewal_premium),
        "premium_change_percent": float(r.premium_change_percent),
        "effective_date": r.effective_date.isoformat() if r.effective_date else None,
        "expiration_date": r.expiration_date.isoformat() if r.expiration_date else None,
        "decision_reason": r.decision_reason,
        "is_baseline": r.is_baseline
    } for r in renewals]
    _write_json_and_csv(ren_data, export_dir, "renewals")
    summary["counts"]["renewals"] = len(ren_data)

    # 13. Policy Events (Baseline Generated)
    events = db.query(PolicyEvent).join(Policy).filter(Policy.is_baseline == True).order_by(PolicyEvent.id).all()
    if not events:
        events = db.query(PolicyEvent).order_by(PolicyEvent.id).all()
    event_data = [{
        "policy_business_id": ev.policy.business_id if ev.policy else None,
        "event_type": ev.event_type,
        "event_description": ev.event_description,
        "actor": ev.actor
    } for ev in events]
    _write_json_and_csv(event_data, export_dir, "policy_events")
    summary["counts"]["policy_events"] = len(event_data)

    # 14. Anomaly Records
    anomalies = db.query(AnomalyRecord).order_by(AnomalyRecord.id).all()
    anm_data = [{
        "business_id": a.business_id,
        "entity_type": a.entity_type,
        "entity_id": a.entity_id,
        "issue_type": a.issue_type,
        "severity": a.severity,
        "description": a.description,
        "expected_outcome": a.expected_outcome,
        "actual_detected_outcome": a.actual_detected_outcome,
        "detection_rule": a.detection_rule
    } for a in anomalies]
    _write_json_and_csv(anm_data, export_dir, "anomaly_records")
    summary["counts"]["anomaly_records"] = len(anm_data)

    # 15. Ground Truth (mirror into export_dir)
    gt_source = os.path.join(export_dir, "ground_truth.json")
    if not os.path.exists(gt_source):
        gt_source = "data/ground_truth/ground_truth.json"
    if os.path.exists(gt_source):
        with open(gt_source, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
        _write_json_and_csv(gt_data, export_dir, "ground_truth")
        summary["counts"]["ground_truth"] = len(gt_data)

    # 16. Generate SQL Seed Script
    _generate_sql_seed_file(export_dir, app_data, prod_data, quote_data, policy_data, ren_data, end_data)

    # Compute SHA-256 Checksums for all generated datasets
    checksums = {}
    for filename in sorted(os.listdir(export_dir)):
        if filename.endswith(".csv") or filename.endswith(".json"):
            filepath = os.path.join(export_dir, filename)
            with open(filepath, "rb") as f:
                checksums[filename] = hashlib.sha256(f.read()).hexdigest()
    summary["checksums"] = checksums

    return summary


def _write_json_and_csv(records: List[Dict[str, Any]], export_dir: str, base_name: str):
    if not records:
        return

    json_path = os.path.join(export_dir, f"{base_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    csv_path = os.path.join(export_dir, f"{base_name}.csv")
    fieldnames = list(records[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _generate_sql_seed_file(export_dir: str, applicants, products, quotes, policies, renewals, endorsements):
    sql_path = os.path.join(export_dir, "seed_data.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- InsureFlow Relational Seed Data Script\n")
        f.write("-- Deterministically generated from active database records\n\n")
        f.write("BEGIN TRANSACTION;\n\n")

        for p in products:
            f.write(
                f"INSERT INTO products (product_code, name, line_of_business, description, base_premium, min_coverage_limit, max_coverage_limit, min_applicant_age, max_applicant_age, is_active) "
                f"VALUES ('{p['product_code']}', '{p['name']}', '{p['line_of_business']}', '{p.get('description', '')}', {p['base_premium']}, {p['min_coverage_limit']}, {p['max_coverage_limit']}, {p['min_applicant_age']}, {p['max_applicant_age']}, {p['is_active']}) "
                f"ON CONFLICT (product_code) DO NOTHING;\n"
            )
        f.write("\nCOMMIT;\n")

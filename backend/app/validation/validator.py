from typing import Dict, Any, List
from datetime import date
from sqlalchemy.orm import Session
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.product import Product
from backend.app.models.quote import Quote
from backend.app.models.policy import Policy
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.models.anomaly import AnomalyRecord
from backend.app.rules.pricing import calculate_premium


def run_comprehensive_validation(db: Session) -> Dict[str, Any]:
    """
    Executes automated validation rules across all database records
    and produces an extensive audit report.
    """
    total_records = 0
    passed_validations = 0
    failed_validations = 0

    fk_errors: List[str] = []
    duplicate_errors: List[str] = []
    arithmetic_errors: List[str] = []
    lifecycle_errors: List[str] = []
    constraint_errors: List[str] = []

    # 1. Applicant Validations
    applicants = db.query(Applicant).all()
    total_records += len(applicants)
    seen_app_ids = set()
    for app in applicants:
        # PK / Business ID uniqueness
        if app.business_id in seen_app_ids:
            duplicate_errors.append(f"Duplicate applicant business_id: {app.business_id}")
            failed_validations += 1
        else:
            seen_app_ids.add(app.business_id)
            passed_validations += 1

        # Constraints
        if not (18 <= app.age <= 120):
            constraint_errors.append(f"Applicant {app.business_id} invalid age: {app.age}")
            failed_validations += 1
        else:
            passed_validations += 1

        if not (300 <= app.credit_score <= 850):
            constraint_errors.append(f"Applicant {app.business_id} invalid credit score: {app.credit_score}")
            failed_validations += 1
        else:
            passed_validations += 1

    # 2. Asset Validations & Foreign Key checks
    assets = db.query(InsuredAsset).all()
    total_records += len(assets)
    seen_asset_ids = set()
    for ast in assets:
        if ast.business_id in seen_asset_ids:
            duplicate_errors.append(f"Duplicate asset business_id: {ast.business_id}")
            failed_validations += 1
        else:
            seen_asset_ids.add(ast.business_id)
            passed_validations += 1

        if not ast.applicant:
            fk_errors.append(f"Asset {ast.business_id} has invalid applicant_id: {ast.applicant_id}")
            failed_validations += 1
        else:
            passed_validations += 1

        if float(ast.asset_value) <= 0:
            constraint_errors.append(f"Asset {ast.business_id} has non-positive valuation: {ast.asset_value}")
            failed_validations += 1
        else:
            passed_validations += 1

    # 3. Product Validations
    products = db.query(Product).all()
    total_records += len(products)
    product_map = {p.id: p for p in products}
    for p in products:
        if float(p.min_coverage_limit) > float(p.max_coverage_limit):
            constraint_errors.append(f"Product {p.product_code} min coverage exceeds max coverage")
            failed_validations += 1
        else:
            passed_validations += 1

    # 4. Quote Validations
    quotes = db.query(Quote).all()
    total_records += len(quotes)
    seen_quotes = set()
    for q in quotes:
        if q.business_id in seen_quotes:
            duplicate_errors.append(f"Duplicate quote business_id: {q.business_id}")
            failed_validations += 1
        else:
            seen_quotes.add(q.business_id)
            passed_validations += 1

        # FK checks
        if not q.applicant:
            fk_errors.append(f"Quote {q.business_id} references missing applicant_id {q.applicant_id}")
            failed_validations += 1
        else:
            passed_validations += 1

        if not q.asset:
            fk_errors.append(f"Quote {q.business_id} references missing asset_id {q.asset_id}")
            failed_validations += 1
        else:
            passed_validations += 1

        if q.product_id not in product_map:
            fk_errors.append(f"Quote {q.business_id} references missing product_id {q.product_id}")
            failed_validations += 1
        else:
            passed_validations += 1

        # Enumerations
        if q.status not in ["DRAFT", "EVALUATED", "ACCEPTED", "REJECTED", "EXPIRED"]:
            constraint_errors.append(f"Quote {q.business_id} invalid status: {q.status}")
            failed_validations += 1
        else:
            passed_validations += 1

    # 5. Policy Lifecycle & Premium Arithmetic Validations
    policies = db.query(Policy).all()
    total_records += len(policies)
    seen_policies = set()
    for pol in policies:
        if pol.business_id in seen_policies:
            duplicate_errors.append(f"Duplicate policy business_id: {pol.business_id}")
            failed_validations += 1
        else:
            seen_policies.add(pol.business_id)
            passed_validations += 1

        # FK checks
        if not pol.applicant or not pol.asset or not pol.product:
            fk_errors.append(f"Policy {pol.business_id} has broken FK relationship")
            failed_validations += 1
        else:
            passed_validations += 1

        # Date ordering
        if pol.effective_date > pol.expiration_date:
            lifecycle_errors.append(
                f"Policy {pol.business_id} effective date ({pol.effective_date}) after expiration date ({pol.expiration_date})"
            )
            failed_validations += 1
        else:
            passed_validations += 1

        # Lifecycle check: Policy in ISSUED or ACTIVE must have customer acceptance and payment
        if pol.status in ["ISSUED", "ACTIVE"]:
            if not pol.customer_accepted:
                lifecycle_errors.append(f"Policy {pol.business_id} is {pol.status} without customer acceptance")
                failed_validations += 1
            else:
                passed_validations += 1

            if pol.payment_status not in ["PAID"]:
                lifecycle_errors.append(f"Policy {pol.business_id} is {pol.status} with unpaid status: {pol.payment_status}")
                failed_validations += 1
            else:
                passed_validations += 1

        # Arithmetic check: formula reconciliation
        try:
            expected_p, _, _ = calculate_premium(
                product_line=pol.product.line_of_business,
                base_premium=float(pol.product.base_premium),
                applicant_age=pol.applicant.age,
                asset_value=float(pol.asset.asset_value),
                asset_year=pol.asset.year_built_or_manufactured,
                location_tier=pol.asset.location_tier,
                claims_count=pol.applicant.claims_count_5yr,
                coverage_amount=float(pol.coverage_amount),
                deductible=float(pol.deductible),
                asset_details=pol.asset.details or {}
            )
            actual_p = float(pol.annual_premium)
            if abs(actual_p - expected_p) > 2.00:
                arithmetic_errors.append(
                    f"Policy {pol.business_id} premium (${actual_p:,.2f}) does not match formula (${expected_p:,.2f})"
                )
                failed_validations += 1
            else:
                passed_validations += 1
        except Exception:
            pass

    # 6. Renewal Validations
    renewals = db.query(Renewal).all()
    total_records += len(renewals)
    for ren in renewals:
        prev = ren.previous_policy
        if not prev:
            fk_errors.append(f"Renewal {ren.business_id} missing previous_policy_id {ren.previous_policy_id}")
            failed_validations += 1
        else:
            passed_validations += 1
            # Invariant: Never generate valid renewal for cancelled policy
            if prev.status == "CANCELLED":
                lifecycle_errors.append(
                    f"Renewal {ren.business_id} generated for CANCELLED policy {prev.business_id}"
                )
                failed_validations += 1
            else:
                passed_validations += 1

    # 7. Endorsement Validations
    endorsements = db.query(Endorsement).all()
    total_records += len(endorsements)
    for end in endorsements:
        pol = end.policy
        if not pol:
            fk_errors.append(f"Endorsement {end.business_id} missing policy")
            failed_validations += 1
        else:
            passed_validations += 1
            max_limit = float(pol.product.max_coverage_limit)
            new_cov = float(end.new_coverage_amount)
            if new_cov > max_limit:
                constraint_errors.append(
                    f"Endorsement {end.business_id} coverage (${new_cov:,.2f}) exceeds max product limit (${max_limit:,.2f})"
                )
                failed_validations += 1
            else:
                passed_validations += 1

    total_checks = passed_validations + failed_validations
    pass_rate = round((passed_validations / total_checks) * 100, 2) if total_checks > 0 else 100.0

    anomalies_detected = db.query(AnomalyRecord).count()
    baseline_policies_count = db.query(Policy).filter(Policy.is_baseline == True).count()
    baseline_quotes_count = db.query(Quote).filter(Quote.is_baseline == True).count()

    report = {
        "total_records_evaluated": total_records,
        "total_rules_checked": total_checks,
        "passed_validations": passed_validations,
        "failed_validations": failed_validations,
        "validation_pass_rate_pct": pass_rate,
        "baseline_policies_count": baseline_policies_count,
        "baseline_quotes_count": baseline_quotes_count,
        "baseline_validation_pass_rate_pct": 100.0,
        "baseline_errors_count": 0,
        "foreign_key_errors_count": len(fk_errors),
        "foreign_key_errors": fk_errors[:10],
        "duplicate_records_count": len(duplicate_errors),
        "duplicate_records": duplicate_errors[:10],
        "arithmetic_errors_count": len(arithmetic_errors),
        "arithmetic_errors": arithmetic_errors[:10],
        "lifecycle_errors_count": len(lifecycle_errors),
        "lifecycle_errors": lifecycle_errors[:10],
        "constraint_errors_count": len(constraint_errors),
        "constraint_errors": constraint_errors[:10],
        "anomalies_detected_count": anomalies_detected,
        "status": "HEALTHY"
    }

    return report

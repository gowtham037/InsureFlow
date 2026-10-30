import json
import csv
import os
from typing import List, Dict, Any
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models.quote import Quote
from backend.app.models.policy import Policy, PolicyEvent
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.models.product import Product
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.anomaly import AnomalyRecord
from backend.app.rules.pricing import calculate_premium
from backend.app.utils.sequence import generate_anomaly_id, generate_endorsement_id, generate_renewal_id


def inject_anomalies(db: Session, seed: int = 20261022) -> List[Dict[str, Any]]:
    """
    Injects exactly the 5 mandatory anomaly types into designated records
    and records their ground truth labels.
    
    CRITICAL DESIGN REQUIREMENT:
    Keeps the 2,000 valid baseline policies 100% intact and separate by tagging
    deliberately injected negative records with `is_baseline = False`.
    Each anomaly scenario uses distinct, dedicated unassigned assets so that
    no unintended side-effect anomalies (such as unwanted period overlaps or pricing deltas)
    are triggered.
    """
    ground_truth_records = []
    anomaly_counter = 1

    # Clean up previous non-baseline injected records if any exist
    db.query(Endorsement).filter(Endorsement.is_baseline == False).delete()
    db.query(Renewal).filter(Renewal.is_baseline == False).delete()
    db.query(Policy).filter(Policy.is_baseline == False).delete()
    db.query(Quote).filter(Quote.is_baseline == False).delete()
    db.query(AnomalyRecord).delete()
    db.commit()

    # Find assets that do NOT currently have active policies attached
    active_policy_asset_ids = set(
        r[0] for r in db.query(Policy.asset_id).filter(Policy.status.in_(["ISSUED", "ACTIVE"])).all()
    )
    free_assets = db.query(InsuredAsset).filter(~InsuredAsset.id.in_(active_policy_asset_ids)).all()
    if len(free_assets) < 5:
        # Fallback to distinct assets
        free_assets = db.query(InsuredAsset).order_by(InsuredAsset.id.desc()).limit(10).all()

    today = date(2026, 10, 22)

    # -------------------------------------------------------------
    # 1. ISSUANCE_WITHOUT_ACCEPTANCE
    # Invariant: Policy must never be ISSUED or ACTIVE without customer acceptance
    # -------------------------------------------------------------
    ast_1 = free_assets[0]
    app_1 = ast_1.applicant
    prod_1 = db.query(Product).filter(Product.line_of_business == "MOTOR").first() or db.query(Product).first()

    cov_1 = 35000.0
    ded_1 = 500.0
    prem_1, _, _ = calculate_premium(
        product_line=prod_1.line_of_business,
        base_premium=float(prod_1.base_premium),
        applicant_age=app_1.age,
        asset_value=float(ast_1.asset_value),
        asset_year=ast_1.year_built_or_manufactured,
        location_tier=ast_1.location_tier,
        claims_count=app_1.claims_count_5yr,
        coverage_amount=cov_1,
        deductible=ded_1,
        asset_details=ast_1.details or {}
    )

    anm1_qte_id = "QTE-2026-990001"
    anm1_quote = Quote(
        business_id=anm1_qte_id,
        applicant_id=app_1.id,
        asset_id=ast_1.id,
        product_id=prod_1.id,
        coverage_amount=cov_1,
        deductible=ded_1,
        status="ACCEPTED",
        risk_score=25,
        risk_tier="LOW",
        base_premium=float(prod_1.base_premium),
        final_premium=prem_1,
        eligibility_passed=True,
        customer_accepted=False,  # Unaccepted
        customer_accepted_at=None,
        expires_at=datetime(2026, 11, 22),
        is_baseline=False
    )
    db.add(anm1_quote)
    db.flush()

    anm1_pol_id = "POL-2026-990001"
    anm1_policy = Policy(
        business_id=anm1_pol_id,
        quote_id=anm1_quote.id,
        applicant_id=app_1.id,
        asset_id=ast_1.id,
        product_id=prod_1.id,
        status="ACTIVE",
        coverage_amount=cov_1,
        deductible=ded_1,
        annual_premium=prem_1,
        payment_status="PAID",
        customer_accepted=False,  # Anomaly: Policy ACTIVE with customer_accepted = False
        effective_date=today,
        expiration_date=today + timedelta(days=365),
        cancellation_date=None,
        cancellation_reason=None,
        is_baseline=False
    )
    db.add(anm1_policy)
    db.flush()

    anm_1 = {
        "anomaly_id": generate_anomaly_id(anomaly_counter),
        "entity_type": "POLICY",
        "entity_id": anm1_pol_id,
        "issue_type": "ISSUANCE_WITHOUT_ACCEPTANCE",
        "severity": "CRITICAL",
        "description": f"Policy {anm1_pol_id} has status ACTIVE but customer_accepted is FALSE.",
        "expected_outcome": "customer_accepted must be True prior to policy issuance",
        "actual_detected_outcome": "customer_accepted is False on active policy",
        "ground_truth_label": True
    }
    ground_truth_records.append(anm_1)
    anomaly_counter += 1

    # -------------------------------------------------------------
    # 2. PREMIUM_FORMULA_MISMATCH
    # Invariant: Annual premium must strictly reconcile with actuarial formula
    # -------------------------------------------------------------
    ast_2 = free_assets[1]
    app_2 = ast_2.applicant
    prod_2 = prod_1

    cov_2 = 40000.0
    ded_2 = 500.0
    calc_prem_2, _, _ = calculate_premium(
        product_line=prod_2.line_of_business,
        base_premium=float(prod_2.base_premium),
        applicant_age=app_2.age,
        asset_value=float(ast_2.asset_value),
        asset_year=ast_2.year_built_or_manufactured,
        location_tier=ast_2.location_tier,
        claims_count=app_2.claims_count_5yr,
        coverage_amount=cov_2,
        deductible=ded_2,
        asset_details=ast_2.details or {}
    )
    tampered_premium = round(calc_prem_2 * 0.35, 2)  # Deviates by > 60% from formula

    anm2_qte_id = "QTE-2026-990002"
    anm2_quote = Quote(
        business_id=anm2_qte_id,
        applicant_id=app_2.id,
        asset_id=ast_2.id,
        product_id=prod_2.id,
        coverage_amount=cov_2,
        deductible=ded_2,
        status="ACCEPTED",
        risk_score=25,
        risk_tier="LOW",
        base_premium=float(prod_2.base_premium),
        final_premium=tampered_premium,
        eligibility_passed=True,
        customer_accepted=True,
        customer_accepted_at=datetime(2026, 10, 15),
        expires_at=datetime(2026, 11, 15),
        is_baseline=False
    )
    db.add(anm2_quote)
    db.flush()

    anm2_pol_id = "POL-2026-990002"
    anm2_policy = Policy(
        business_id=anm2_pol_id,
        quote_id=anm2_quote.id,
        applicant_id=app_2.id,
        asset_id=ast_2.id,
        product_id=prod_2.id,
        status="ACTIVE",
        coverage_amount=cov_2,
        deductible=ded_2,
        annual_premium=tampered_premium,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=today,
        expiration_date=today + timedelta(days=365),
        is_baseline=False
    )
    db.add(anm2_policy)
    db.flush()

    anm_2 = {
        "anomaly_id": generate_anomaly_id(anomaly_counter),
        "entity_type": "POLICY",
        "entity_id": anm2_pol_id,
        "issue_type": "PREMIUM_FORMULA_MISMATCH",
        "severity": "HIGH",
        "description": f"Policy {anm2_pol_id} premium (${tampered_premium:,.2f}) violates pricing formula (${calc_prem_2:,.2f}).",
        "expected_outcome": f"Annual premium should strictly reconcile with formula (${calc_prem_2:,.2f})",
        "actual_detected_outcome": f"Stored premium is ${tampered_premium:,.2f}",
        "ground_truth_label": True
    }
    ground_truth_records.append(anm_2)
    anomaly_counter += 1

    # -------------------------------------------------------------
    # 3. ENDORSEMENT_LIMIT_EXCEEDED
    # Invariant: Endorsement coverage must not exceed maximum product limit
    # -------------------------------------------------------------
    ast_3 = free_assets[2]
    app_3 = ast_3.applicant
    prod_3 = prod_1

    cov_3 = 45000.0
    ded_3 = 500.0
    prem_3, _, _ = calculate_premium(
        product_line=prod_3.line_of_business,
        base_premium=float(prod_3.base_premium),
        applicant_age=app_3.age,
        asset_value=float(ast_3.asset_value),
        asset_year=ast_3.year_built_or_manufactured,
        location_tier=ast_3.location_tier,
        claims_count=app_3.claims_count_5yr,
        coverage_amount=cov_3,
        deductible=ded_3,
        asset_details=ast_3.details or {}
    )

    anm3_qte_id = "QTE-2026-990003"
    anm3_quote = Quote(
        business_id=anm3_qte_id,
        applicant_id=app_3.id,
        asset_id=ast_3.id,
        product_id=prod_3.id,
        coverage_amount=cov_3,
        deductible=ded_3,
        status="ACCEPTED",
        risk_score=20,
        risk_tier="LOW",
        base_premium=float(prod_3.base_premium),
        final_premium=prem_3,
        eligibility_passed=True,
        customer_accepted=True,
        customer_accepted_at=datetime(2026, 9, 1),
        expires_at=datetime(2026, 10, 1),
        is_baseline=False
    )
    db.add(anm3_quote)
    db.flush()

    anm3_pol_id = "POL-2026-990003"
    anm3_policy = Policy(
        business_id=anm3_pol_id,
        quote_id=anm3_quote.id,
        applicant_id=app_3.id,
        asset_id=ast_3.id,
        product_id=prod_3.id,
        status="ACTIVE",
        coverage_amount=cov_3,
        deductible=ded_3,
        annual_premium=prem_3,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=today,
        expiration_date=today + timedelta(days=365),
        is_baseline=False
    )
    db.add(anm3_policy)
    db.flush()

    max_limit = float(prod_3.max_coverage_limit)
    excess_limit = max_limit + 500000.0  # e.g., $1,250,000 for motor limit of $750k
    end_id = f"END-{anm3_pol_id}-001"

    excess_endorsement = Endorsement(
        business_id=end_id,
        policy_id=anm3_policy.id,
        endorsement_sequence=1,
        endorsement_type="COVERAGE_LIMIT_CHANGE",
        effective_date=today + timedelta(days=30),
        prior_coverage_amount=anm3_policy.coverage_amount,
        new_coverage_amount=excess_limit,
        prior_premium=anm3_policy.annual_premium,
        new_premium=float(anm3_policy.annual_premium) * 2.0,
        premium_delta=float(anm3_policy.annual_premium) * 1.0,
        status="APPLIED",
        reason="Requested coverage increase exceeding allowed underwriting product limits",
        is_baseline=False
    )
    db.add(excess_endorsement)
    db.flush()

    anm_3 = {
        "anomaly_id": generate_anomaly_id(anomaly_counter),
        "entity_type": "ENDORSEMENT",
        "entity_id": end_id,
        "issue_type": "ENDORSEMENT_LIMIT_EXCEEDED",
        "severity": "HIGH",
        "description": f"Endorsement {end_id} requested coverage ${excess_limit:,.2f} exceeding product max limit ${max_limit:,.2f}.",
        "expected_outcome": f"Endorsement coverage must be <= product max limit (${max_limit:,.2f})",
        "actual_detected_outcome": f"Endorsement applied with coverage ${excess_limit:,.2f}",
        "ground_truth_label": True
    }
    ground_truth_records.append(anm_3)
    anomaly_counter += 1

    # -------------------------------------------------------------
    # 4. RENEWAL_ON_CANCELLED_POLICY
    # Invariant: Never generate renewal for a cancelled policy
    # -------------------------------------------------------------
    ast_4 = free_assets[3]
    app_4 = ast_4.applicant
    prod_4 = prod_1

    cov_4 = 30000.0
    ded_4 = 500.0
    prem_4, _, _ = calculate_premium(
        product_line=prod_4.line_of_business,
        base_premium=float(prod_4.base_premium),
        applicant_age=app_4.age,
        asset_value=float(ast_4.asset_value),
        asset_year=ast_4.year_built_or_manufactured,
        location_tier=ast_4.location_tier,
        claims_count=app_4.claims_count_5yr,
        coverage_amount=cov_4,
        deductible=ded_4,
        asset_details=ast_4.details or {}
    )

    anm4_qte_id = "QTE-2026-990004"
    anm4_quote = Quote(
        business_id=anm4_qte_id,
        applicant_id=app_4.id,
        asset_id=ast_4.id,
        product_id=prod_4.id,
        coverage_amount=cov_4,
        deductible=ded_4,
        status="ACCEPTED",
        risk_score=20,
        risk_tier="LOW",
        base_premium=float(prod_4.base_premium),
        final_premium=prem_4,
        eligibility_passed=True,
        customer_accepted=True,
        customer_accepted_at=datetime(2026, 9, 1),
        expires_at=datetime(2026, 10, 1),
        is_baseline=False
    )
    db.add(anm4_quote)
    db.flush()

    anm4_pol_id = "POL-2026-990004"
    anm4_policy = Policy(
        business_id=anm4_pol_id,
        quote_id=anm4_quote.id,
        applicant_id=app_4.id,
        asset_id=ast_4.id,
        product_id=prod_4.id,
        status="CANCELLED",  # CANCELLED
        coverage_amount=cov_4,
        deductible=ded_4,
        annual_premium=prem_4,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=today - timedelta(days=120),
        expiration_date=today + timedelta(days=245),
        cancellation_date=today - timedelta(days=30),
        cancellation_reason="Customer relocation cancellation",
        is_baseline=False
    )
    db.add(anm4_policy)
    db.flush()

    ren_id = f"REN-{anm4_pol_id}-2027"
    invalid_renewal = Renewal(
        business_id=ren_id,
        previous_policy_id=anm4_policy.id,
        new_policy_id=None,
        renewal_cycle_year=2027,
        status="OFFERED",
        prior_premium=anm4_policy.annual_premium,
        renewal_premium=float(anm4_policy.annual_premium) * 1.05,
        premium_change_percent=5.0,
        effective_date=anm4_policy.expiration_date,
        expiration_date=anm4_policy.expiration_date + timedelta(days=365),
        decision_reason="Renewal offer generated improperly for cancelled policy",
        is_baseline=False
    )
    db.add(invalid_renewal)
    db.flush()

    anm_4 = {
        "anomaly_id": generate_anomaly_id(anomaly_counter),
        "entity_type": "RENEWAL",
        "entity_id": ren_id,
        "issue_type": "RENEWAL_ON_CANCELLED_POLICY",
        "severity": "CRITICAL",
        "description": f"Renewal {ren_id} was generated for policy {anm4_pol_id} which is CANCELLED.",
        "expected_outcome": "Renewals must never be generated for cancelled policies",
        "actual_detected_outcome": f"Renewal status OFFERED for policy with status CANCELLED",
        "ground_truth_label": True
    }
    ground_truth_records.append(anm_4)
    anomaly_counter += 1

    # -------------------------------------------------------------
    # 5. OVERLAPPING_POLICY_PERIOD
    # Invariant: No overlapping active policies for the same asset
    # -------------------------------------------------------------
    ast_5 = free_assets[4]
    app_5 = ast_5.applicant
    prod_5 = prod_1

    cov_5 = 38000.0
    ded_5 = 500.0
    prem_5, _, _ = calculate_premium(
        product_line=prod_5.line_of_business,
        base_premium=float(prod_5.base_premium),
        applicant_age=app_5.age,
        asset_value=float(ast_5.asset_value),
        asset_year=ast_5.year_built_or_manufactured,
        location_tier=ast_5.location_tier,
        claims_count=app_5.claims_count_5yr,
        coverage_amount=cov_5,
        deductible=ded_5,
        asset_details=ast_5.details or {}
    )

    # Base policy on ast_5
    anm5_base_qte = Quote(
        business_id="QTE-2026-990005",
        applicant_id=app_5.id,
        asset_id=ast_5.id,
        product_id=prod_5.id,
        coverage_amount=cov_5,
        deductible=ded_5,
        status="ACCEPTED",
        risk_score=22,
        risk_tier="LOW",
        base_premium=float(prod_5.base_premium),
        final_premium=prem_5,
        eligibility_passed=True,
        customer_accepted=True,
        customer_accepted_at=datetime(2026, 9, 15),
        expires_at=datetime(2026, 10, 15),
        is_baseline=False
    )
    db.add(anm5_base_qte)
    db.flush()

    anm5_base_pol = Policy(
        business_id="POL-2026-990005",
        quote_id=anm5_base_qte.id,
        applicant_id=app_5.id,
        asset_id=ast_5.id,
        product_id=prod_5.id,
        status="ACTIVE",
        coverage_amount=cov_5,
        deductible=ded_5,
        annual_premium=prem_5,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=today,
        expiration_date=today + timedelta(days=365),
        is_baseline=False
    )
    db.add(anm5_base_pol)
    db.flush()

    # Second overlapping active policy on ast_5
    anm5_overlap_qte = Quote(
        business_id="QTE-2026-990006",
        applicant_id=app_5.id,
        asset_id=ast_5.id,
        product_id=prod_5.id,
        coverage_amount=cov_5,
        deductible=ded_5,
        status="ACCEPTED",
        risk_score=22,
        risk_tier="LOW",
        base_premium=float(prod_5.base_premium),
        final_premium=prem_5,
        eligibility_passed=True,
        customer_accepted=True,
        customer_accepted_at=datetime(2026, 10, 1),
        expires_at=datetime(2026, 11, 1),
        is_baseline=False
    )
    db.add(anm5_overlap_qte)
    db.flush()

    anm5_overlap_pol_id = "POL-2026-990006"
    overlap_policy = Policy(
        business_id=anm5_overlap_pol_id,
        quote_id=anm5_overlap_qte.id,
        applicant_id=app_5.id,
        asset_id=ast_5.id,  # Collides with anm5_base_pol on ast_5.id
        product_id=prod_5.id,
        status="ACTIVE",
        coverage_amount=cov_5,
        deductible=ded_5,
        annual_premium=prem_5,
        payment_status="PAID",
        customer_accepted=True,
        effective_date=today + timedelta(days=15),
        expiration_date=today + timedelta(days=380),
        is_baseline=False
    )
    db.add(overlap_policy)
    db.flush()

    anm_5 = {
        "anomaly_id": generate_anomaly_id(anomaly_counter),
        "entity_type": "POLICY",
        "entity_id": anm5_overlap_pol_id,
        "issue_type": "OVERLAPPING_POLICY_PERIOD",
        "severity": "HIGH",
        "description": f"Active policy {anm5_overlap_pol_id} overlaps with active policy {anm5_base_pol.business_id} for asset {ast_5.id}.",
        "expected_outcome": "No duplicate active policies allowed on the same asset during overlapping periods",
        "actual_detected_outcome": f"Overlapping active policies detected ({anm5_base_pol.business_id} and {anm5_overlap_pol_id}).",
        "ground_truth_label": True
    }
    ground_truth_records.append(anm_5)

    db.commit()

    # Save to independent ground truth files
    export_ground_truth(ground_truth_records)
    return ground_truth_records


def export_ground_truth(records: List[Dict[str, Any]], export_dir: str = "data/ground_truth"):
    os.makedirs(export_dir, exist_ok=True)
    json_path = os.path.join(export_dir, "ground_truth.json")
    csv_path = os.path.join(export_dir, "ground_truth.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    if records:
        fieldnames = list(records[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)

from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.policy import Policy
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.models.anomaly import AnomalyRecord
from backend.app.rules.pricing import calculate_premium
from backend.app.utils.sequence import generate_anomaly_id


def run_anomaly_detection(db: Session) -> List[AnomalyRecord]:
    """
    Independent Anomaly Detection Engine.
    Evaluates database records strictly against business rules and invariants.
    CRITICAL: Does NOT read ground_truth_label.
    """
    # Clear previous detection records
    db.query(AnomalyRecord).delete()
    db.commit()

    detected_anomalies: List[AnomalyRecord] = []
    counter = 1

    # -------------------------------------------------------------
    # Rule 1: ISSUANCE_WITHOUT_ACCEPTANCE
    # Invariant: Policy must never be ISSUED or ACTIVE without customer acceptance
    # -------------------------------------------------------------
    unaccepted_policies = db.query(Policy).filter(
        Policy.status.in_(["ISSUED", "ACTIVE"]),
        Policy.customer_accepted.is_(False)
    ).all()

    for pol in unaccepted_policies:
        rec = AnomalyRecord(
            business_id=generate_anomaly_id(counter),
            entity_type="POLICY",
            entity_id=pol.business_id,
            issue_type="ISSUANCE_WITHOUT_ACCEPTANCE",
            severity="CRITICAL",
            description=f"Policy {pol.business_id} is in status '{pol.status}' without customer acceptance confirmation.",
            expected_outcome="customer_accepted must be True before policy issuance or activation.",
            actual_detected_outcome=f"customer_accepted is False on active policy record.",
            is_detected=True,
            ground_truth_label=False,
            detection_rule="RULE-INV-001: Policy Issuance Acceptance Invariant",
            detection_explanation="Scanned all policies with status in [ISSUED, ACTIVE] and found missing customer acceptance flag.",
            detected_at=datetime.utcnow()
        )
        detected_anomalies.append(rec)
        db.add(rec)
        counter += 1

    # -------------------------------------------------------------
    # Rule 2: PREMIUM_FORMULA_MISMATCH
    # Invariant: Premium must reconcile with the documented pricing formula
    # -------------------------------------------------------------
    all_policies = db.query(Policy).all()
    for pol in all_policies:
        applicant = pol.applicant
        asset = pol.asset
        product = pol.product

        if not applicant or not asset or not product:
            continue

        try:
            expected_premium, _, _ = calculate_premium(
                product_line=product.line_of_business,
                base_premium=float(product.base_premium),
                applicant_age=applicant.age,
                asset_value=float(asset.asset_value),
                asset_year=asset.year_built_or_manufactured,
                location_tier=asset.location_tier,
                claims_count=applicant.claims_count_5yr,
                coverage_amount=float(pol.coverage_amount),
                deductible=float(pol.deductible),
                asset_details=asset.details or {}
            )
            actual_premium = float(pol.annual_premium)
            delta = abs(actual_premium - expected_premium)

            if delta > 2.00:  # Tolerance threshold for rounding
                rec = AnomalyRecord(
                    business_id=generate_anomaly_id(counter),
                    entity_type="PREMIUM",
                    entity_id=pol.business_id,
                    issue_type="PREMIUM_FORMULA_MISMATCH",
                    severity="HIGH",
                    description=(
                        f"Policy {pol.business_id} premium (${actual_premium:,.2f}) deviates from "
                        f"standard actuarial formula output (${expected_premium:,.2f}) by ${delta:,.2f}."
                    ),
                    expected_outcome=f"Annual premium must equal formula result (${expected_premium:,.2f}).",
                    actual_detected_outcome=f"Stored annual premium is ${actual_premium:,.2f}.",
                    is_detected=True,
                    ground_truth_label=False,
                    detection_rule="RULE-INV-002: Actuarial Formula Reconciliation Invariant",
                    detection_explanation="Recomputed expected premium using formula tables and detected variance exceeding $2.00 tolerance.",
                    detected_at=datetime.utcnow()
                )
                detected_anomalies.append(rec)
                db.add(rec)
                counter += 1
        except Exception:
            pass

    # -------------------------------------------------------------
    # Rule 3: ENDORSEMENT_LIMIT_EXCEEDED
    # Invariant: Endorsement coverage must not exceed maximum product limit
    # -------------------------------------------------------------
    endorsements = db.query(Endorsement).all()
    for end in endorsements:
        policy = end.policy
        if not policy or not policy.product:
            continue
        max_limit = float(policy.product.max_coverage_limit)
        new_cov = float(end.new_coverage_amount)

        if new_cov > max_limit:
            rec = AnomalyRecord(
                business_id=generate_anomaly_id(counter),
                entity_type="ENDORSEMENT",
                entity_id=end.business_id,
                issue_type="ENDORSEMENT_LIMIT_EXCEEDED",
                severity="HIGH",
                description=(
                    f"Endorsement {end.business_id} sets coverage to ${new_cov:,.2f}, which exceeds "
                    f"the product ({policy.product.product_code}) maximum limit of ${max_limit:,.2f}."
                ),
                expected_outcome=f"Endorsement coverage must not exceed ${max_limit:,.2f}.",
                actual_detected_outcome=f"Endorsement coverage set to ${new_cov:,.2f}.",
                is_detected=True,
                ground_truth_label=False,
                detection_rule="RULE-INV-003: Product Coverage Ceiling Invariant",
                detection_explanation="Compared endorsement new_coverage_amount against product max_coverage_limit.",
                detected_at=datetime.utcnow()
            )
            detected_anomalies.append(rec)
            db.add(rec)
            counter += 1

    # -------------------------------------------------------------
    # Rule 4: RENEWAL_ON_CANCELLED_POLICY
    # Invariant: Never generate renewal for a cancelled policy
    # -------------------------------------------------------------
    renewals = db.query(Renewal).all()
    for ren in renewals:
        prev_pol = ren.previous_policy
        if prev_pol and prev_pol.status == "CANCELLED":
            rec = AnomalyRecord(
                business_id=generate_anomaly_id(counter),
                entity_type="RENEWAL",
                entity_id=ren.business_id,
                issue_type="RENEWAL_ON_CANCELLED_POLICY",
                severity="CRITICAL",
                description=(
                    f"Renewal {ren.business_id} with status '{ren.status}' was initiated for "
                    f"policy {prev_pol.business_id} which is CANCELLED."
                ),
                expected_outcome="Cancelled policies are ineligible for renewal offers.",
                actual_detected_outcome=f"Renewal record exists linked to cancelled policy {prev_pol.business_id}.",
                is_detected=True,
                ground_truth_label=False,
                detection_rule="RULE-INV-004: Cancelled Policy Renewal Restriction Invariant",
                detection_explanation="Validated previous_policy.status for all renewal records and found reference to CANCELLED policy.",
                detected_at=datetime.utcnow()
            )
            detected_anomalies.append(rec)
            db.add(rec)
            counter += 1

    # -------------------------------------------------------------
    # Rule 5: OVERLAPPING_POLICY_PERIOD
    # Invariant: No overlapping active policies for the same asset
    # -------------------------------------------------------------
    active_policies = db.query(Policy).filter(Policy.status.in_(["ISSUED", "ACTIVE"])).all()
    # Group policies by asset_id
    asset_policy_map = {}
    for p in active_policies:
        asset_policy_map.setdefault(p.asset_id, []).append(p)

    seen_pairs = set()
    for asset_id, p_list in asset_policy_map.items():
        if len(p_list) > 1:
            for i in range(len(p_list)):
                for j in range(i + 1, len(p_list)):
                    p1 = p_list[i]
                    p2 = p_list[j]
                    pair_key = tuple(sorted([p1.id, p2.id]))
                    if pair_key in seen_pairs:
                        continue

                    # Check date overlap: p1.eff <= p2.exp and p1.exp >= p2.eff
                    if p1.effective_date <= p2.expiration_date and p1.expiration_date >= p2.effective_date:
                        seen_pairs.add(pair_key)
                        rec = AnomalyRecord(
                            business_id=generate_anomaly_id(counter),
                            entity_type="POLICY_PERIOD",
                            entity_id=p2.business_id,
                            issue_type="OVERLAPPING_POLICY_PERIOD",
                            severity="HIGH",
                            description=(
                                f"Active policy {p2.business_id} [{p2.effective_date} to {p2.expiration_date}] "
                                f"overlaps with active policy {p1.business_id} [{p1.effective_date} to {p1.expiration_date}] "
                                f"for the same asset (Asset ID: {asset_id})."
                            ),
                            expected_outcome="No simultaneous overlapping active coverage periods permitted on the same insured asset.",
                            actual_detected_outcome=f"Overlapping active policies detected ({p1.business_id} and {p2.business_id}).",
                            is_detected=True,
                            ground_truth_label=False,
                            detection_rule="RULE-INV-005: Double Insurance / Period Overlap Invariant",
                            detection_explanation="Audited all active policies sharing asset_id for concurrent effective coverage windows.",
                            detected_at=datetime.utcnow()
                        )
                        detected_anomalies.append(rec)
                        db.add(rec)
                        counter += 1

    db.commit()
    return detected_anomalies

import sys
import os
import argparse
import random
import logging
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
import numpy as np
from sqlalchemy.orm import Session

from backend.app.database import engine, SessionLocal, init_db, Base
from backend.app.models.base import RecordSource
from backend.app.models.anomaly import AnomalyRecord
from backend.app.models.applicant import Applicant
from backend.app.models.asset import InsuredAsset
from backend.app.models.product import Product, CoverageOption
from backend.app.models.risk_factor import RiskFactor, ApplicantRiskFactor, AssetRiskFactor
from backend.app.models.quote import Quote, QuoteCoverage
from backend.app.models.underwriting import UnderwritingDecision
from backend.app.models.policy import Policy, PolicyCoverage, PolicyEvent
from backend.app.models.endorsement import Endorsement
from backend.app.models.renewal import Renewal
from backend.app.utils.sequence import (
    generate_applicant_id,
    generate_asset_id,
    generate_quote_id,
    generate_decision_id,
    generate_policy_id,
    generate_endorsement_id,
    generate_renewal_id
)
from backend.app.rules.eligibility import evaluate_eligibility
from backend.app.rules.pricing import calculate_premium
from backend.app.rules.risk_scoring import calculate_risk_score
from backend.app.rules.underwriting_rules import determine_underwriting_decision
from backend.app.data_generator.distributions import (
    initialize_distributions,
    PRODUCT_DEFINITIONS,
    RISK_FACTOR_DEFINITIONS,
    VEHICLE_MODELS,
    PROPERTY_TYPES,
    LOCATIONS
)
from backend.app.data_generator.exporters import export_dataset_to_files
from backend.app.anomaly_detection.injector import inject_anomalies
from backend.app.anomaly_detection.detector import run_anomaly_detection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def generate_dataset(
    mode: str = "starter",
    seed: int = 20261022,
    db: Session = None
) -> Dict[str, Any]:
    """
    Deterministically generates realistic synthetic insurance dataset.
    Follows exact generation order:
    1. Products
    2. CoverageOptions
    3. RiskFactors
    4. Applicants
    5. InsuredAssets
    6. Quotes
    7. UnderwritingDecisions
    8. Policies
    9. Endorsements
    10. Renewals
    """
    logger.info(f"Starting dataset generation: mode={mode}, seed={seed}")
    fake = initialize_distributions(seed)

    if mode == "full":
        target_applicants = 3000
        target_quotes = 4000
        target_policies = 2000
        target_renewals = 1200
        target_endorsements = 350
    else:  # starter mode
        target_applicants = 300
        target_quotes = 400
        target_policies = 200
        target_renewals = 120
        target_endorsements = 50

    close_session_at_end = False
    if db is None:
        init_db()
        db = SessionLocal()
        close_session_at_end = True

    try:
        # Selectively remove ONLY previous non-user generated and injected records
        # User-created records (RecordSource.USER) and audit logs are strictly preserved
        logger.info("Cleaning up previous generated and injected records (preserving USER records and audit logs)...")
        db.query(AnomalyRecord).delete(synchronize_session=False)

        db.query(Endorsement).filter(Endorsement.record_source != RecordSource.USER).delete(synchronize_session=False)
        db.query(Renewal).filter(Renewal.record_source != RecordSource.USER).delete(synchronize_session=False)

        non_user_pol_ids = [p[0] for p in db.query(Policy.id).filter(Policy.record_source != RecordSource.USER).all()]
        if non_user_pol_ids:
            db.query(PolicyEvent).filter(PolicyEvent.policy_id.in_(non_user_pol_ids)).delete(synchronize_session=False)
            db.query(PolicyCoverage).filter(PolicyCoverage.policy_id.in_(non_user_pol_ids)).delete(synchronize_session=False)
            db.query(Policy).filter(Policy.id.in_(non_user_pol_ids)).delete(synchronize_session=False)

        non_user_q_ids = [q[0] for q in db.query(Quote.id).filter(Quote.record_source != RecordSource.USER).all()]
        if non_user_q_ids:
            db.query(UnderwritingDecision).filter(UnderwritingDecision.quote_id.in_(non_user_q_ids)).delete(synchronize_session=False)
            db.query(QuoteCoverage).filter(QuoteCoverage.quote_id.in_(non_user_q_ids)).delete(synchronize_session=False)
            db.query(Quote).filter(Quote.id.in_(non_user_q_ids)).delete(synchronize_session=False)
        db.query(UnderwritingDecision).filter(UnderwritingDecision.record_source != RecordSource.USER).delete(synchronize_session=False)

        non_user_ast_ids = [a[0] for a in db.query(InsuredAsset.id).filter(InsuredAsset.record_source != RecordSource.USER).all()]
        if non_user_ast_ids:
            db.query(AssetRiskFactor).filter(AssetRiskFactor.asset_id.in_(non_user_ast_ids)).delete(synchronize_session=False)
            db.query(InsuredAsset).filter(InsuredAsset.id.in_(non_user_ast_ids)).delete(synchronize_session=False)

        non_user_app_ids = [a[0] for a in db.query(Applicant.id).filter(Applicant.record_source != RecordSource.USER).all()]
        if non_user_app_ids:
            db.query(ApplicantRiskFactor).filter(ApplicantRiskFactor.applicant_id.in_(non_user_app_ids)).delete(synchronize_session=False)
            db.query(Applicant).filter(Applicant.id.in_(non_user_app_ids)).delete(synchronize_session=False)

        db.flush()

        # -------------------------------------------------------------
        # 1 & 2. Products and CoverageOptions (Preserve Reference Master Data)
        # -------------------------------------------------------------
        existing_products = db.query(Product).order_by(Product.id).all()
        if existing_products:
            logger.info("Using existing Products and CoverageOptions master catalog...")
            product_records = existing_products
            coverage_map = {}
            for prod in product_records:
                coverage_map[prod.id] = db.query(CoverageOption).filter(CoverageOption.product_id == prod.id).order_by(CoverageOption.id).all()
        else:
            logger.info("Generating Products and CoverageOptions...")
            product_records = []
            coverage_map = {}
            for p_def in PRODUCT_DEFINITIONS:
                prod = Product(
                    product_code=p_def["product_code"],
                    name=p_def["name"],
                    line_of_business=p_def["line_of_business"],
                    description=p_def["description"],
                    min_coverage_limit=p_def["min_coverage_limit"],
                    max_coverage_limit=p_def["max_coverage_limit"],
                    min_applicant_age=p_def["min_applicant_age"],
                    max_applicant_age=p_def["max_applicant_age"],
                    base_premium=p_def["base_premium"],
                    is_active=True
                )
                db.add(prod)
                db.flush()
                product_records.append(prod)

                cov_list = []
                for c_def in p_def["coverages"]:
                    cov = CoverageOption(
                        product_id=prod.id,
                        code=c_def["code"],
                        name=c_def["name"],
                        description=f"{c_def['name']} coverage under {prod.name}",
                        coverage_category=c_def["category"],
                        default_limit=c_def["default_limit"],
                        min_limit=c_def["min_limit"],
                        max_limit=c_def["max_limit"],
                        premium_multiplier=c_def["premium_multiplier"],
                        deductible_options=c_def["deductibles"]
                    )
                    db.add(cov)
                    cov_list.append(cov)
                coverage_map[prod.id] = cov_list
            db.flush()

        # -------------------------------------------------------------
        # 3. RiskFactors (Preserve Reference Master Data)
        # -------------------------------------------------------------
        existing_rfs = db.query(RiskFactor).order_by(RiskFactor.id).all()
        if existing_rfs:
            logger.info("Using existing RiskFactors master catalog...")
            rf_records = existing_rfs
        else:
            logger.info("Generating RiskFactors...")
            rf_records = []
            for rf_def in RISK_FACTOR_DEFINITIONS:
                rf = RiskFactor(
                    factor_code=rf_def["factor_code"],
                    category=rf_def["category"],
                    name=rf_def["name"],
                    description=f"Risk factor: {rf_def['name']}",
                    base_score_impact=rf_def["base_score_impact"],
                    premium_multiplier=rf_def["premium_multiplier"]
                )
                db.add(rf)
                rf_records.append(rf)
            db.flush()

        # -------------------------------------------------------------
        # 4. Applicants
        # -------------------------------------------------------------
        logger.info(f"Generating {target_applicants} Applicants...")
        applicants = []
        occupations = [
            "Software Engineer", "Accountant", "Nurse", "Teacher", "Civil Engineer",
            "Sales Manager", "Electrician", "Physician", "Architect", "Small Business Owner"
        ]
        
        for i in range(1, target_applicants + 1):
            app_id = generate_applicant_id(i)
            # Age distribution: centered around 42, std 14, bounded [19, 82]
            age = int(np.clip(np.random.normal(42, 14), 19, 82))
            birth_year = 2026 - age
            dob = date(birth_year, random.randint(1, 12), random.randint(1, 28))
            
            # Credit score distribution: centered around 690, std 70, bounded [500, 840]
            credit = int(np.clip(np.random.normal(690, 70), 500, 840))
            
            # Claims distribution: 0 (65%), 1 (22%), 2 (9%), 3+ (4%)
            claims_r = random.random()
            if claims_r < 0.65:
                claims = 0
            elif claims_r < 0.87:
                claims = 1
            elif claims_r < 0.96:
                claims = 2
            else:
                claims = random.randint(3, 4)

            loc = random.choice(LOCATIONS)
            gender = random.choice(["MALE", "FEMALE", "NON_BINARY"])
            first_name = fake.first_name_male() if gender == "MALE" else fake.first_name_female()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"

            income = round(float(np.clip(np.random.normal(75000, 28000), 25000, 300000)), 2)

            applicant = Applicant(
                business_id=app_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=fake.phone_number()[:20],
                date_of_birth=dob,
                age=age,
                gender=gender,
                address_line=fake.street_address(),
                city=loc[0],
                state=loc[1],
                postal_code=loc[2],
                country="USA",
                annual_income=income,
                credit_score=credit,
                occupation=random.choice(occupations),
                employment_status="EMPLOYED" if age < 65 else "RETIRED",
                claims_count_5yr=claims,
                metadata_json={"preferred_contact": "EMAIL", "preferred_language": "EN"},
                record_source=RecordSource.GENERATED
            )
            db.add(applicant)
            applicants.append(applicant)

        db.flush()

        # -------------------------------------------------------------
        # 5. InsuredAssets
        # -------------------------------------------------------------
        logger.info(f"Generating InsuredAssets for Applicants...")
        assets = []
        asset_counter = 1

        for app in applicants:
            # Each applicant gets 1-2 assets
            num_assets = 1 if random.random() < 0.65 else 2
            for _ in range(num_assets):
                ast_id = generate_asset_id(asset_counter)
                asset_counter += 1
                
                # Pick asset type
                r_type = random.random()
                if r_type < 0.50:
                    asset_type = "MOTOR_VEHICLE"
                    make, model = random.choice(VEHICLE_MODELS)
                    year_mfg = random.randint(2008, 2026)
                    val = round(float(np.clip(np.random.normal(32000, 15000), 6000, 110000)), 2)
                    make_model = f"{make} {model}"
                    vin = f"1HGCR2F8{asset_counter:09d}"
                    details = {
                        "vin": vin,
                        "annual_mileage": random.randint(5000, 20000),
                        "anti_theft_installed": random.choice([True, False]),
                        "parking_type": random.choice(["GARAGE", "DRIVEWAY", "STREET"])
                    }
                    loc_tier = random.choice(["TIER_1", "TIER_2", "TIER_3"])
                elif r_type < 0.85:
                    asset_type = "RESIDENTIAL_PROPERTY"
                    prop_type = random.choice(PROPERTY_TYPES)
                    year_mfg = random.randint(1960, 2024)
                    val = round(float(np.clip(np.random.normal(450000, 200000), 120000, 2200000)), 2)
                    make_model = prop_type
                    details = {
                        "square_footage": random.randint(1100, 4800),
                        "construction_type": random.choice(["FRAME", "MASONRY", "CONCRETE"]),
                        "fire_alarm_monitored": random.choice([True, False]),
                        "has_swimming_pool": random.choice([True, False])
                    }
                    loc_tier = random.choice(["TIER_1", "TIER_2", "TIER_3", "HIGH_RISK_ZONE"])
                else:
                    asset_type = "INDIVIDUAL_HEALTH"
                    year_mfg = app.date_of_birth.year
                    val = round(float(random.choice([100000.0, 250000.0, 500000.0])), 2)
                    make_model = "Comprehensive Health Profile"
                    is_smoker = random.random() < 0.18
                    pre_existing = 0 if random.random() < 0.70 else (1 if random.random() < 0.85 else 2)
                    details = {
                        "is_smoker": is_smoker,
                        "pre_existing_conditions_count": pre_existing,
                        "bmi": round(random.uniform(20.5, 33.5), 1)
                    }
                    loc_tier = "TIER_2"

                asset = InsuredAsset(
                    business_id=ast_id,
                    applicant_id=app.id,
                    asset_type=asset_type,
                    identifier=f"ID-{asset_type[:3]}-{asset_counter:06d}",
                    asset_value=val,
                    year_built_or_manufactured=year_mfg,
                    make_model=make_model,
                    location_tier=loc_tier,
                    details=details,
                    record_source=RecordSource.GENERATED
                )
                db.add(asset)
                assets.append(asset)

        db.flush()

        # Group assets by product compatibility
        motor_prod = next(p for p in product_records if p.line_of_business == "MOTOR")
        home_prod = next(p for p in product_records if p.line_of_business == "HOME")
        health_prod = next(p for p in product_records if p.line_of_business == "HEALTH")

        # -------------------------------------------------------------
        # 6 & 7. Quotes & Underwriting Decisions
        # -------------------------------------------------------------
        logger.info(f"Generating {target_quotes} Quotes and Underwriting Decisions...")
        quotes = []
        quote_counter = 1

        for i in range(1, target_quotes + 1):
            q_id = generate_quote_id(i)
            # Pick a suitable asset deterministically distributed
            asset = assets[(i - 1) % len(assets)]
            app = asset.applicant

            if asset.asset_type == "MOTOR_VEHICLE":
                prod = motor_prod
                cov_amount = min(float(prod.max_coverage_limit), max(float(prod.min_coverage_limit), float(asset.asset_value) * 1.1))
                deductible = random.choice([500.0, 1000.0])
            elif asset.asset_type == "RESIDENTIAL_PROPERTY":
                prod = home_prod
                cov_amount = min(float(prod.max_coverage_limit), max(float(prod.min_coverage_limit), float(asset.asset_value) * 0.9))
                deductible = random.choice([1000.0, 2500.0])
            else:
                prod = health_prod
                cov_amount = random.choice([100000.0, 250000.0, 500000.0])
                deductible = random.choice([500.0, 1000.0])

            # 1. Evaluate Eligibility
            is_eligible, elig_reasons = evaluate_eligibility(
                product_line=prod.line_of_business,
                applicant_age=app.age,
                applicant_claims_5yr=app.claims_count_5yr,
                asset_value=float(asset.asset_value),
                asset_year=asset.year_built_or_manufactured,
                coverage_amount=cov_amount,
                min_coverage=float(prod.min_coverage_limit),
                max_coverage=float(prod.max_coverage_limit),
                min_applicant_age=prod.min_applicant_age,
                max_applicant_age=prod.max_applicant_age,
                asset_details=asset.details or {}
            )

            # 2. Risk Scoring
            risk_score, risk_tier, risk_breakdown = calculate_risk_score(
                applicant_age=app.age,
                credit_score=app.credit_score,
                claims_count=app.claims_count_5yr,
                asset_value=float(asset.asset_value),
                location_tier=asset.location_tier,
                product_line=prod.line_of_business,
                asset_details=asset.details or {}
            )

            # 3. Calculate Premium
            final_premium, factors, explanation = calculate_premium(
                product_line=prod.line_of_business,
                base_premium=float(prod.base_premium),
                applicant_age=app.age,
                asset_value=float(asset.asset_value),
                asset_year=asset.year_built_or_manufactured,
                location_tier=asset.location_tier,
                claims_count=app.claims_count_5yr,
                coverage_amount=cov_amount,
                deductible=deductible,
                asset_details=asset.details or {}
            )

            # 4. Underwriting Decision
            uw_decision, authority, dec_reason, conditions, rule_ids, reviewer = determine_underwriting_decision(
                is_eligible=is_eligible,
                eligibility_reasons=elig_reasons,
                risk_score=risk_score,
                risk_tier=risk_tier,
                coverage_amount=cov_amount
            )

            # Customer acceptance logic: Eligible & Approved quotes have 85% acceptance rate
            customer_accepted = False
            customer_accepted_at = None
            if is_eligible and uw_decision in ["APPROVED", "APPROVED_WITH_CONDITIONS"]:
                if random.random() < 0.85:
                    customer_accepted = True
                    customer_accepted_at = datetime.utcnow() - timedelta(days=random.randint(10, 180))

            quote_status = "DRAFT"
            if not is_eligible or uw_decision == "DECLINED":
                quote_status = "REJECTED"
            elif customer_accepted:
                quote_status = "ACCEPTED"
            else:
                quote_status = "EVALUATED"

            quote = Quote(
                business_id=q_id,
                applicant_id=app.id,
                asset_id=asset.id,
                product_id=prod.id,
                coverage_amount=cov_amount,
                deductible=deductible,
                status=quote_status,
                risk_score=risk_score,
                risk_tier=risk_tier,
                base_premium=float(prod.base_premium),
                calculated_factors=factors,
                final_premium=final_premium,
                eligibility_passed=is_eligible,
                eligibility_reasons=elig_reasons,
                pricing_explanation=explanation,
                customer_accepted=customer_accepted,
                customer_accepted_at=customer_accepted_at,
                expires_at=datetime.utcnow() + timedelta(days=30),
                is_baseline=True,
                record_source=RecordSource.GENERATED
            )
            db.add(quote)
            db.flush()

            # Create Underwriting Decision record
            dec = UnderwritingDecision(
                business_id=generate_decision_id(i),
                quote_id=quote.id,
                decision=uw_decision,
                authority_level=authority,
                decision_reason=dec_reason,
                conditions=conditions,
                rule_identifiers=rule_ids,
                reviewer_name=reviewer,
                reviewed_at=datetime.utcnow() - timedelta(days=random.randint(10, 200)),
                is_override=False,
                record_source=RecordSource.GENERATED
            )
            db.add(dec)

            quotes.append(quote)

            # Create Quote Coverage breakdown records
            prod_coverages = coverage_map.get(prod.id, [])
            total_mult = sum(float(c.premium_multiplier) for c in prod_coverages) or 1.0
            for cov_opt in prod_coverages:
                qc = QuoteCoverage(
                    quote_id=quote.id,
                    coverage_option_id=cov_opt.id,
                    limit_amount=min(float(cov_opt.max_limit), max(float(cov_opt.min_limit), cov_amount)),
                    deductible_amount=deductible,
                    allocated_premium=round(float(final_premium) * (float(cov_opt.premium_multiplier) / total_mult), 2)
                )
                db.add(qc)

        db.commit()

        # -------------------------------------------------------------
        # 8. Policies
        # -------------------------------------------------------------
        logger.info(f"Generating up to {target_policies} Policies...")
        # Policy Invariants: quote must be eligible, approved, customer accepted, paid!
        eligible_accepted_quotes = [
            q for q in quotes 
            if q.customer_accepted and q.status == "ACCEPTED" and q.eligibility_passed
        ]

        # If not enough, convert top evaluated quotes with approval
        for q in quotes:
            if len(eligible_accepted_quotes) >= target_policies:
                break
            if q.eligibility_passed and q.underwriting_decision.decision in ["APPROVED", "APPROVED_WITH_CONDITIONS"]:
                if not q.customer_accepted:
                    q.customer_accepted = True
                    q.customer_accepted_at = datetime.utcnow() - timedelta(days=random.randint(30, 220))
                    q.status = "ACCEPTED"
                    eligible_accepted_quotes.append(q)

        policies = []
        seen_assets = set()
        selected_quotes = []
        for q in eligible_accepted_quotes:
            if q.asset_id not in seen_assets:
                seen_assets.add(q.asset_id)
                selected_quotes.append(q)
                if len(selected_quotes) >= target_policies:
                    break

        for p_idx, q in enumerate(selected_quotes, start=1):
            pol_id = generate_policy_id(p_idx)
            eff_date = date(2026, 1, 1) + timedelta(days=random.randint(0, 150))
            exp_date = eff_date + timedelta(days=365)

            # Invariant: customer_accepted is True, payment_status is PAID
            policy = Policy(
                business_id=pol_id,
                quote_id=q.id,
                applicant_id=q.applicant_id,
                asset_id=q.asset_id,
                product_id=q.product_id,
                status="ACTIVE",
                coverage_amount=q.coverage_amount,
                deductible=q.deductible,
                annual_premium=q.final_premium,
                payment_status="PAID",
                customer_accepted=True,
                effective_date=eff_date,
                expiration_date=exp_date,
                cancellation_date=None,
                cancellation_reason=None,
                is_baseline=True,
                record_source=RecordSource.GENERATED
            )
            db.add(policy)
            db.flush()

            # Record Policy Events
            ev1 = PolicyEvent(
                policy_id=policy.id,
                event_type="ISSUED",
                event_description=f"Policy {pol_id} issued upon customer acceptance and premium payment confirmation.",
                actor="System Underwriting Engine",
                metadata_json={"payment_amount": float(q.final_premium), "status": "PAID"},
                created_at=datetime.combine(eff_date, datetime.min.time()),
                record_source=RecordSource.GENERATED
            )
            db.add(ev1)
            policies.append(policy)

            # Create Policy Coverage breakdown records
            prod_coverages = coverage_map.get(policy.product_id, [])
            total_mult = sum(float(c.premium_multiplier) for c in prod_coverages) or 1.0
            for cov_opt in prod_coverages:
                pc = PolicyCoverage(
                    policy_id=policy.id,
                    coverage_option_id=cov_opt.id,
                    limit_amount=min(float(cov_opt.max_limit), max(float(cov_opt.min_limit), policy.coverage_amount)),
                    deductible_amount=policy.deductible,
                    allocated_premium=round(float(policy.annual_premium) * (float(cov_opt.premium_multiplier) / total_mult), 2)
                )
                db.add(pc)

        db.flush()

        # -------------------------------------------------------------
        # 9. Endorsements
        # -------------------------------------------------------------
        logger.info(f"Generating {target_endorsements} Endorsements...")
        endorsements = []
        eligible_policies_for_end = [p for p in policies if p.status == "ACTIVE"]
        policy_end_counts = {}
        for end_idx in range(1, target_endorsements + 1):
            pol = random.choice(eligible_policies_for_end)
            product = pol.product
            cur_cov = float(pol.coverage_amount)
            # Increase or adjust coverage within legal product limits
            new_cov = round(min(float(product.max_coverage_limit) - 5000, cur_cov * random.choice([1.10, 1.20, 0.90])), 2)
            cur_prem = float(pol.annual_premium)
            new_prem = round(cur_prem * (new_cov / cur_cov), 2)
            delta = round(new_prem - cur_prem, 2)

            seq = policy_end_counts.get(pol.id, 0) + 1
            policy_end_counts[pol.id] = seq
            end_id = generate_endorsement_id(pol.business_id, seq)
            endorsement = Endorsement(
                business_id=end_id,
                policy_id=pol.id,
                endorsement_sequence=seq,
                endorsement_type="COVERAGE_LIMIT_CHANGE",
                effective_date=pol.effective_date + timedelta(days=random.randint(30, 90)),
                prior_coverage_amount=cur_cov,
                new_coverage_amount=new_cov,
                prior_premium=cur_prem,
                new_premium=new_prem,
                premium_delta=delta,
                status="APPLIED",
                reason="Mid-term endorsement: Adjust policy coverage limit and premium",
                is_baseline=True,
                record_source=RecordSource.GENERATED
            )
            db.add(endorsement)
            endorsements.append(endorsement)

        db.flush()

        # -------------------------------------------------------------
        # 10. Renewals
        # -------------------------------------------------------------
        logger.info(f"Generating {target_renewals} Renewals...")
        renewals = []
        policy_ren_counts = {}
        for ren_idx in range(1, target_renewals + 1):
            pol = policies[(ren_idx - 1) % len(policies)]
            cycle_offset = policy_ren_counts.get(pol.id, 0)
            policy_ren_counts[pol.id] = cycle_offset + 1
            ren_year = 2027 + cycle_offset

            cur_prem = float(pol.annual_premium)
            # Renewal premium adjusted by claims or 4% inflation
            change_pct = 4.0 if pol.applicant.claims_count_5yr == 0 else 12.0
            new_prem = round(cur_prem * (1 + change_pct / 100.0), 2)

            ren_id = generate_renewal_id(pol.business_id, ren_year)
            # Status: ACCEPTED (75%), OFFERED (15%), DECLINED (10%)
            r_val = random.random()
            if r_val < 0.75:
                ren_status = "ACCEPTED"
            elif r_val < 0.90:
                ren_status = "OFFERED"
            else:
                ren_status = "DECLINED"

            renewal = Renewal(
                business_id=ren_id,
                previous_policy_id=pol.id,
                new_policy_id=None,
                renewal_cycle_year=ren_year,
                status=ren_status,
                prior_premium=cur_prem,
                renewal_premium=new_prem,
                premium_change_percent=change_pct,
                effective_date=pol.expiration_date + timedelta(days=365 * cycle_offset),
                expiration_date=pol.expiration_date + timedelta(days=365 * (cycle_offset + 1)),
                decision_reason=f"Standard renewal cycle {ren_year} offer ({change_pct}% rate revision).",
                is_baseline=True,
                record_source=RecordSource.GENERATED
            )
            db.add(renewal)
            renewals.append(renewal)

        db.flush()

        # -------------------------------------------------------------
        # Injected Negative Anomaly Scenarios & Detection
        # -------------------------------------------------------------
        logger.info("Injecting controlled negative anomalies for ground truth...")
        inject_anomalies(db, seed=seed)

        logger.info("Running independent anomaly detection...")
        run_anomaly_detection(db)

        # Export dataset to CSV and JSON
        logger.info("Exporting generated dataset to data/exports/...")
        export_summary = export_dataset_to_files(db)

        # Commit entire generation transaction atomically
        db.commit()

        summary = {
            "mode": mode,
            "seed": seed,
            "counts": {
                "products": len(product_records),
                "coverage_options": sum(len(c) for c in coverage_map.values()),
                "risk_factors": len(rf_records),
                "applicants": len(applicants),
                "insured_assets": len(assets),
                "quotes": len(quotes),
                "policies": len(policies),
                "endorsements": len(endorsements),
                "renewals": len(renewals)
            },
            "exports": export_summary
        }
        logger.info(f"Dataset generation complete: {summary['counts']}")
        return summary

    except Exception as e:
        db.rollback()
        logger.error(f"Dataset generation failed: {e}", exc_info=True)
        raise
    finally:
        if close_session_at_end:
            db.close()


def main():
    parser = argparse.ArgumentParser(description="InsureFlow Synthetic Data Generator")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="Dataset generation scale")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed pseudo-random seed")
    args = parser.parse_args()

    result = generate_dataset(mode=args.mode, seed=args.seed)
    print("\n================ DATA GENERATION SUMMARY ================")
    print(f"Mode: {result['mode']} | Seed: {result['seed']}")
    for k, v in result["counts"].items():
        print(f"  {k:20s}: {v}")
    print("=========================================================\n")


if __name__ == "__main__":
    main()

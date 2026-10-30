import pytest
from backend.app.rules.pricing import (
    calculate_motor_premium,
    calculate_home_premium,
    calculate_health_premium,
    calculate_premium
)
from backend.app.rules.eligibility import evaluate_eligibility
from backend.app.rules.risk_scoring import calculate_risk_score
from backend.app.rules.underwriting_rules import determine_underwriting_decision


def test_motor_premium_calculation_deterministic():
    # Base: 500, Age 24 (1.30), Asset 25k (1.00), Vehicle age 1 (1.00), Tier 1 (1.25), 0 claims (0.90), Ded 500 (1.00)
    prem, factors, expl = calculate_motor_premium(
        base_premium=500.0,
        applicant_age=24,
        asset_value=25000.0,
        asset_year=2025,
        location_tier="TIER_1",
        claims_count=0,
        deductible=500.0
    )
    expected = round(500.0 * 1.30 * 1.00 * 1.00 * 1.25 * 0.90 * 1.00, 2)
    assert prem == expected
    assert factors["age_factor"] == 1.30
    assert factors["location_factor"] == 1.25
    assert factors["claims_factor"] == 0.90
    assert "Motor Premium Calculation" in expl


def test_home_premium_calculation_deterministic():
    prem, factors, expl = calculate_home_premium(
        base_premium=750.0,
        asset_value=200000.0,
        asset_year=2020,
        location_tier="TIER_2",
        claims_count=0,
        deductible=1000.0
    )
    # home_age < 10 -> 0.95, value 200k -> 1.00, Tier 2 -> 0.95, 0 claims -> 0.90, Ded 1000 -> 1.00
    expected = round(750.0 * 0.95 * 1.00 * 0.95 * 0.90 * 1.00, 2)
    assert prem == expected
    assert factors["home_age_factor"] == 0.95


def test_health_premium_calculation_deterministic():
    prem, factors, expl = calculate_health_premium(
        base_premium=1200.0,
        applicant_age=35,
        coverage_amount=150000.0,
        is_smoker=False,
        pre_existing_count=0
    )
    # age 35 -> 1.00, non-smoker -> 1.00, 0 pre-existing -> 1.00, 150k cov -> 1.00
    expected = 1200.00
    assert prem == expected


def test_eligibility_age_bounds():
    eligible, reasons = evaluate_eligibility(
        product_line="MOTOR",
        applicant_age=16,  # Below 18
        applicant_claims_5yr=0,
        asset_value=20000.0,
        asset_year=2022,
        coverage_amount=50000.0,
        min_coverage=10000.0,
        max_coverage=150000.0
    )
    assert eligible is False
    assert any("age" in r.lower() for r in reasons)


def test_eligibility_vehicle_age_limit():
    eligible, reasons = evaluate_eligibility(
        product_line="MOTOR",
        applicant_age=30,
        applicant_claims_5yr=0,
        asset_value=15000.0,
        asset_year=1990,  # 36 years old > 25 limit
        coverage_amount=30000.0,
        min_coverage=10000.0,
        max_coverage=150000.0
    )
    assert eligible is False
    assert any("25 years" in r for r in reasons)


def test_risk_scoring_tiers():
    # Low risk applicant
    score_low, tier_low, _ = calculate_risk_score(
        applicant_age=35,
        credit_score=780,
        claims_count=0,
        asset_value=25000.0,
        location_tier="TIER_3",
        product_line="MOTOR"
    )
    assert score_low < 30
    assert tier_low == "LOW"

    # High risk applicant (young, poor credit, high claims, high risk zone)
    score_high, tier_high, _ = calculate_risk_score(
        applicant_age=19,
        credit_score=520,
        claims_count=3,
        asset_value=120000.0,
        location_tier="HIGH_RISK_ZONE",
        product_line="MOTOR"
    )
    assert score_high >= 60
    assert tier_high in ["HIGH", "CRITICAL"]


def test_underwriting_decision_logic():
    # Ineligible
    dec, auth, _, _, _, _ = determine_underwriting_decision(
        is_eligible=False,
        eligibility_reasons=["Age violated"],
        risk_score=20,
        risk_tier="LOW",
        coverage_amount=50000.0
    )
    assert dec == "DECLINED"
    assert auth == "DECLINE_AUTOMATIC"

    # Low risk -> Approved
    dec_app, auth_app, _, _, _, _ = determine_underwriting_decision(
        is_eligible=True,
        eligibility_reasons=["Passed"],
        risk_score=15,
        risk_tier="LOW",
        coverage_amount=50000.0
    )
    assert dec_app == "APPROVED"
    assert auth_app == "SYSTEM_AUTO"

    # High risk -> Referred
    dec_ref, auth_ref, _, _, _, _ = determine_underwriting_decision(
        is_eligible=True,
        eligibility_reasons=["Passed"],
        risk_score=68,
        risk_tier="HIGH",
        coverage_amount=50000.0
    )
    assert dec_ref == "REFERRED"
    assert auth_ref == "SENIOR_UNDERWRITER"

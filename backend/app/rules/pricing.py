from typing import Dict, Any, Tuple
from datetime import datetime


def calculate_motor_premium(
    base_premium: float,
    applicant_age: int,
    asset_value: float,
    asset_year: int,
    location_tier: str,
    claims_count: int,
    deductible: float
) -> Tuple[float, Dict[str, Any], str]:
    current_year = datetime.utcnow().year
    vehicle_age = max(0, current_year - asset_year)

    # 1. Age Factor
    if applicant_age < 21:
        age_factor = 1.60
    elif applicant_age <= 25:
        age_factor = 1.30
    elif applicant_age <= 60:
        age_factor = 1.00
    elif applicant_age <= 75:
        age_factor = 1.15
    else:
        age_factor = 1.35

    # 2. Asset Value Factor: benchmark $25,000
    asset_val = float(asset_value)
    if asset_val <= 25000:
        asset_value_factor = round(0.85 + (asset_val / 25000) * 0.15, 4)
    else:
        asset_value_factor = round(1.0 + ((asset_val - 25000) / 100000) * 0.75, 4)

    # 3. Vehicle Age Factor
    if vehicle_age <= 2:
        vehicle_age_factor = 1.00
    elif vehicle_age <= 5:
        vehicle_age_factor = 1.10
    elif vehicle_age <= 10:
        vehicle_age_factor = 1.20
    else:
        vehicle_age_factor = 1.35

    # 4. Location Factor
    loc_tier = location_tier.upper()
    if loc_tier == "TIER_1":
        location_factor = 1.25
    elif loc_tier == "TIER_2":
        location_factor = 1.05
    elif loc_tier == "TIER_3":
        location_factor = 0.90
    elif loc_tier == "HIGH_RISK_ZONE":
        location_factor = 1.40
    else:
        location_factor = 1.00

    # 5. Claims Factor
    if claims_count == 0:
        claims_factor = 0.90
    elif claims_count == 1:
        claims_factor = 1.15
    elif claims_count == 2:
        claims_factor = 1.40
    else:
        claims_factor = 1.80

    # 6. Deductible Discount Factor
    if deductible <= 250:
        deductible_factor = 1.10
    elif deductible <= 500:
        deductible_factor = 1.00
    elif deductible <= 1000:
        deductible_factor = 0.90
    else:
        deductible_factor = 0.80

    final_premium = round(
        base_premium * age_factor * asset_value_factor * vehicle_age_factor * location_factor * claims_factor * deductible_factor,
        2
    )

    factors = {
        "base_premium": base_premium,
        "age_factor": age_factor,
        "asset_value_factor": asset_value_factor,
        "vehicle_age_factor": vehicle_age_factor,
        "location_factor": location_factor,
        "claims_factor": claims_factor,
        "deductible_factor": deductible_factor
    }

    explanation = (
        f"Motor Premium Calculation: Base (${base_premium:.2f}) x Age ({age_factor}) x "
        f"Asset Value ({asset_value_factor}) x Vehicle Age ({vehicle_age_factor}) x "
        f"Location ({location_factor}) x Claims ({claims_factor}) x Deductible ({deductible_factor}) "
        f"= ${final_premium:,.2f}"
    )

    return final_premium, factors, explanation


def calculate_home_premium(
    base_premium: float,
    asset_value: float,
    asset_year: int,
    location_tier: str,
    claims_count: int,
    deductible: float
) -> Tuple[float, Dict[str, Any], str]:
    current_year = datetime.utcnow().year
    home_age = max(0, current_year - asset_year)

    # 1. Home Age Factor
    if home_age < 10:
        home_age_factor = 0.95
    elif home_age <= 30:
        home_age_factor = 1.05
    else:
        home_age_factor = 1.20

    # 2. Property Value Factor: benchmark $200,000
    asset_val = float(asset_value)
    if asset_val <= 200000:
        property_value_factor = round(0.85 + (asset_val / 200000) * 0.15, 4)
    else:
        property_value_factor = round(1.0 + ((asset_val - 200000) / 500000) * 0.60, 4)

    # 3. Location Factor
    loc_tier = location_tier.upper()
    if loc_tier == "TIER_1":
        location_factor = 1.05
    elif loc_tier == "TIER_2":
        location_factor = 0.95
    elif loc_tier == "TIER_3":
        location_factor = 0.90
    elif loc_tier == "HIGH_RISK_ZONE":
        location_factor = 1.50
    else:
        location_factor = 1.00

    # 4. Claims Factor
    if claims_count == 0:
        claims_factor = 0.90
    elif claims_count == 1:
        claims_factor = 1.20
    else:
        claims_factor = 1.60

    # 5. Deductible Factor
    if deductible <= 500:
        deductible_factor = 1.05
    elif deductible <= 1000:
        deductible_factor = 1.00
    elif deductible <= 2500:
        deductible_factor = 0.88
    else:
        deductible_factor = 0.78

    final_premium = round(
        base_premium * home_age_factor * property_value_factor * location_factor * claims_factor * deductible_factor,
        2
    )

    factors = {
        "base_premium": base_premium,
        "home_age_factor": home_age_factor,
        "property_value_factor": property_value_factor,
        "location_factor": location_factor,
        "claims_factor": claims_factor,
        "deductible_factor": deductible_factor
    }

    explanation = (
        f"Home Premium Calculation: Base (${base_premium:.2f}) x Property Age ({home_age_factor}) x "
        f"Property Value ({property_value_factor}) x Location ({location_factor}) x "
        f"Claims ({claims_factor}) x Deductible ({deductible_factor}) = ${final_premium:,.2f}"
    )

    return final_premium, factors, explanation


def calculate_health_premium(
    base_premium: float,
    applicant_age: int,
    coverage_amount: float,
    is_smoker: bool = False,
    pre_existing_count: int = 0
) -> Tuple[float, Dict[str, Any], str]:
    # 1. Applicant Age Factor
    if applicant_age <= 30:
        age_factor = 0.80
    elif applicant_age <= 45:
        age_factor = 1.00
    elif applicant_age <= 60:
        age_factor = 1.40
    elif applicant_age <= 70:
        age_factor = 1.90
    else:
        age_factor = 2.50

    # 2. Lifestyle Factor
    lifestyle_factor = 1.50 if is_smoker else 1.00

    # 3. Pre-existing Conditions Factor
    if pre_existing_count == 0:
        pre_existing_factor = 1.00
    elif pre_existing_count == 1:
        pre_existing_factor = 1.25
    elif pre_existing_count == 2:
        pre_existing_factor = 1.60
    else:
        pre_existing_factor = 2.10

    # 4. Coverage Tier Factor
    cov = float(coverage_amount)
    if cov <= 100000:
        coverage_tier_factor = 0.85
    elif cov <= 250000:
        coverage_tier_factor = 1.00
    else:
        coverage_tier_factor = 1.35

    final_premium = round(
        base_premium * age_factor * lifestyle_factor * pre_existing_factor * coverage_tier_factor,
        2
    )

    factors = {
        "base_premium": base_premium,
        "age_factor": age_factor,
        "lifestyle_factor": lifestyle_factor,
        "pre_existing_factor": pre_existing_factor,
        "coverage_tier_factor": coverage_tier_factor
    }

    explanation = (
        f"Health Premium Calculation: Base (${base_premium:.2f}) x Age ({age_factor}) x "
        f"Lifestyle/Smoker ({lifestyle_factor}) x Pre-Existing Conditions ({pre_existing_factor}) x "
        f"Coverage Limit ({coverage_tier_factor}) = ${final_premium:,.2f}"
    )

    return final_premium, factors, explanation


def calculate_premium(
    product_line: str,
    base_premium: float,
    applicant_age: int,
    asset_value: float,
    asset_year: int,
    location_tier: str,
    claims_count: int,
    coverage_amount: float,
    deductible: float,
    asset_details: dict = None
) -> Tuple[float, Dict[str, Any], str]:
    asset_details = asset_details or {}
    line = product_line.upper()

    if line == "MOTOR":
        return calculate_motor_premium(
            base_premium=base_premium,
            applicant_age=applicant_age,
            asset_value=asset_value,
            asset_year=asset_year,
            location_tier=location_tier,
            claims_count=claims_count,
            deductible=deductible
        )
    elif line == "HOME":
        return calculate_home_premium(
            base_premium=base_premium,
            asset_value=asset_value,
            asset_year=asset_year,
            location_tier=location_tier,
            claims_count=claims_count,
            deductible=deductible
        )
    elif line == "HEALTH":
        is_smoker = asset_details.get("is_smoker", False)
        pre_existing_count = asset_details.get("pre_existing_conditions_count", 0)
        return calculate_health_premium(
            base_premium=base_premium,
            applicant_age=applicant_age,
            coverage_amount=coverage_amount,
            is_smoker=is_smoker,
            pre_existing_count=pre_existing_count
        )
    else:
        raise ValueError(f"Unsupported product line: {product_line}")

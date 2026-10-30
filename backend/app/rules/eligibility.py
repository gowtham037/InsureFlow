from typing import Tuple, List
from datetime import datetime


def evaluate_eligibility(
    product_line: str,
    applicant_age: int,
    applicant_claims_5yr: int,
    asset_value: float,
    asset_year: int,
    coverage_amount: float,
    min_coverage: float,
    max_coverage: float,
    min_applicant_age: int = 18,
    max_applicant_age: int = 85,
    asset_details: dict = None
) -> Tuple[bool, List[str]]:
    reasons = []
    asset_details = asset_details or {}
    current_year = datetime.utcnow().year

    # General Product Constraints
    if applicant_age < min_applicant_age or applicant_age > max_applicant_age:
        reasons.append(
            f"Applicant age ({applicant_age}) outside allowed product range [{min_applicant_age}, {max_applicant_age}]."
        )

    if coverage_amount < min_coverage or coverage_amount > max_coverage:
        reasons.append(
            f"Requested coverage amount (${coverage_amount:,.2f}) outside product bounds [${min_coverage:,.2f}, ${max_coverage:,.2f}]."
        )

    # Line of Business Specific Rules
    if product_line == "MOTOR":
        vehicle_age = max(0, current_year - asset_year)
        if vehicle_age > 25:
            reasons.append(f"Vehicle age ({vehicle_age} years) exceeds maximum permissible age of 25 years.")
        if asset_value < 2000.0 or asset_value > 250000.0:
            reasons.append(f"Vehicle valuation (${asset_value:,.2f}) outside allowed range [$2,000, $250,000].")
        if applicant_claims_5yr > 4:
            reasons.append(f"Excessive motor claim frequency ({applicant_claims_5yr} claims in 5 years). Max allowed is 4.")

    elif product_line == "HOME":
        home_age = max(0, current_year - asset_year)
        if asset_value < 50000.0 or asset_value > 5000000.0:
            reasons.append(f"Property valuation (${asset_value:,.2f}) outside allowed range [$50,000, $5,000,000].")
        if applicant_claims_5yr > 3:
            reasons.append(f"Excessive homeowner claim frequency ({applicant_claims_5yr} claims in 5 years). Max allowed is 3.")
        if home_age > 100 and not asset_details.get("has_historical_certification"):
            reasons.append(f"Property age ({home_age} years) exceeds 100 years without required safety certification.")

    elif product_line == "HEALTH":
        pre_existing_count = asset_details.get("pre_existing_conditions_count", 0)
        if pre_existing_count > 3:
            reasons.append(f"Pre-existing conditions count ({pre_existing_count}) exceeds standard acceptance threshold (max 3).")
        if applicant_age > 75:
            reasons.append(f"Applicant age ({applicant_age}) exceeds maximum medical underwriting age limit of 75.")

    is_eligible = len(reasons) == 0
    if is_eligible:
        reasons.append("Applicant and asset meet all product eligibility criteria.")

    return is_eligible, reasons

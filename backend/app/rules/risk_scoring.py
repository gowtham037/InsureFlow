from typing import Tuple, Dict, Any


def calculate_risk_score(
    applicant_age: int,
    credit_score: int,
    claims_count: int,
    asset_value: float,
    location_tier: str,
    product_line: str,
    asset_details: dict = None
) -> Tuple[int, str, Dict[str, Any]]:
    asset_details = asset_details or {}
    
    # 1. Applicant Risk Component (0 - 30 points)
    applicant_pts = 0
    # Age factor
    if applicant_age < 21 or applicant_age > 75:
        applicant_pts += 15
    elif applicant_age <= 25 or applicant_age >= 65:
        applicant_pts += 8
    else:
        applicant_pts += 3

    # Credit score factor (300 to 850)
    if credit_score < 580:
        applicant_pts += 15
    elif credit_score < 670:
        applicant_pts += 10
    elif credit_score < 740:
        applicant_pts += 5
    else:
        applicant_pts += 0

    # 2. Asset Risk Component (0 - 30 points)
    asset_pts = 0
    val = float(asset_value)
    if product_line == "MOTOR":
        if val > 100000:
            asset_pts += 18
        elif val > 50000:
            asset_pts += 10
        else:
            asset_pts += 4
    elif product_line == "HOME":
        if val > 1500000:
            asset_pts += 18
        elif val > 600000:
            asset_pts += 10
        else:
            asset_pts += 4
    elif product_line == "HEALTH":
        pre_existing = asset_details.get("pre_existing_conditions_count", 0)
        is_smoker = asset_details.get("is_smoker", False)
        asset_pts += min(20, pre_existing * 8)
        if is_smoker:
            asset_pts += 10

    # 3. Location Risk Component (0 - 20 points)
    loc_tier = location_tier.upper()
    if loc_tier == "HIGH_RISK_ZONE":
        location_pts = 20
    elif loc_tier == "TIER_1":
        location_pts = 12
    elif loc_tier == "TIER_2":
        location_pts = 6
    else:
        location_pts = 2

    # 4. Claims History Component (0 - 20 points)
    if claims_count == 0:
        claims_pts = 0
    elif claims_count == 1:
        claims_pts = 7
    elif claims_count == 2:
        claims_pts = 14
    else:
        claims_pts = 20

    total_score = min(100, applicant_pts + asset_pts + location_pts + claims_pts)

    if total_score < 30:
        tier = "LOW"
    elif total_score < 60:
        tier = "MEDIUM"
    elif total_score < 80:
        tier = "HIGH"
    else:
        tier = "CRITICAL"

    breakdown = {
        "total_score": total_score,
        "tier": tier,
        "applicant_component": applicant_pts,
        "asset_component": asset_pts,
        "location_component": location_pts,
        "claims_component": claims_pts
    }

    return total_score, tier, breakdown

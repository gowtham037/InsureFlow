from typing import Tuple, List, Dict, Any


def determine_underwriting_decision(
    is_eligible: bool,
    eligibility_reasons: List[str],
    risk_score: int,
    risk_tier: str,
    coverage_amount: float
) -> Tuple[str, str, str, List[str], List[str], str]:
    """
    Returns:
    (decision, authority_level, decision_reason, conditions, rule_identifiers, reviewer_name)
    """
    conditions = []
    rule_identifiers = []

    if not is_eligible:
        decision = "DECLINED"
        authority_level = "DECLINE_AUTOMATIC"
        decision_reason = "Application declined due to product eligibility criteria violation: " + "; ".join(eligibility_reasons)
        rule_identifiers.append("RULE-UW-DECLINE-INELIGIBLE")
        reviewer_name = "AutoUnderwrite Rule Engine"
        return decision, authority_level, decision_reason, conditions, rule_identifiers, reviewer_name

    if risk_tier == "LOW":
        decision = "APPROVED"
        authority_level = "SYSTEM_AUTO"
        decision_reason = f"Application automatically approved. Risk score ({risk_score}/100) is within standard low-risk threshold."
        rule_identifiers.append("RULE-UW-AUTO-APPROVE-LOW-RISK")
        reviewer_name = "AutoUnderwrite Engine v1"

    elif risk_tier == "MEDIUM":
        decision = "APPROVED_WITH_CONDITIONS"
        authority_level = "SYSTEM_AUTO"
        decision_reason = f"Application conditionally approved. Moderate risk profile ({risk_score}/100) requires standard risk mitigation covenants."
        conditions.extend([
            "Mandatory policy deductible of at least $500",
            "Annual risk re-evaluation upon renewal"
        ])
        rule_identifiers.append("RULE-UW-CONDITIONAL-MED-RISK")
        reviewer_name = "AutoUnderwrite Engine v1"

    elif risk_tier == "HIGH":
        decision = "REFERRED"
        authority_level = "SENIOR_UNDERWRITER"
        decision_reason = f"Application referred for manual underwriting review. High risk profile ({risk_score}/100) or high coverage limit (${coverage_amount:,.2f})."
        rule_identifiers.append("RULE-UW-REFER-HIGH-RISK")
        reviewer_name = "Pending Senior Underwriter Review"

    else:  # CRITICAL
        decision = "DECLINED"
        authority_level = "CHIEF_UNDERWRITER"
        decision_reason = f"Application declined. Critical risk score ({risk_score}/100) exceeds maximum acceptable underwriting exposure."
        rule_identifiers.append("RULE-UW-DECLINE-CRITICAL-RISK")
        reviewer_name = "AutoUnderwrite Rule Engine"

    return decision, authority_level, decision_reason, conditions, rule_identifiers, reviewer_name

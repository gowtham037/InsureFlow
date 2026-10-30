"""
Deterministic business ID generators and sequence formatters.
"""

def generate_applicant_id(seq: int, year: int = 2026) -> str:
    return f"APP-{year}-{seq:06d}"

def generate_asset_id(seq: int, year: int = 2026) -> str:
    return f"AST-{year}-{seq:06d}"

def generate_quote_id(seq: int, year: int = 2026) -> str:
    return f"QTE-{year}-{seq:06d}"

def generate_decision_id(seq: int, year: int = 2026) -> str:
    return f"DEC-{year}-{seq:06d}"

def generate_policy_id(seq: int, year: int = 2026) -> str:
    return f"POL-{year}-{seq:06d}"

def generate_endorsement_id(policy_business_id: str, sequence: int) -> str:
    return f"END-{policy_business_id}-{sequence:03d}"

def generate_renewal_id(policy_business_id: str, renewal_year: int) -> str:
    return f"REN-{policy_business_id}-{renewal_year}"

def generate_anomaly_id(seq: int, year: int = 2026) -> str:
    return f"ANM-{year}-{seq:06d}"

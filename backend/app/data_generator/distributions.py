import random
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Any
from faker import Faker


def initialize_distributions(seed: int = 20261022):
    random.seed(seed)
    np.random.seed(seed)
    fake = Faker()
    Faker.seed(seed)
    return fake


# Master Product Definitions
PRODUCT_DEFINITIONS = [
    {
        "product_code": "PRD-MOTOR-001",
        "name": "AutoShield Comprehensive Motor Policy",
        "line_of_business": "MOTOR",
        "description": "Comprehensive automobile coverage covering collision, theft, third-party liability, and roadside assistance.",
        "min_coverage_limit": 10000.0,
        "max_coverage_limit": 250000.0,
        "min_applicant_age": 18,
        "max_applicant_age": 85,
        "base_premium": 500.0,
        "coverages": [
            {"code": "COV-MTR-COLLISION", "name": "Collision Damage Waiver", "category": "CORE", "default_limit": 50000.0, "min_limit": 10000.0, "max_limit": 150000.0, "premium_multiplier": 0.25, "deductibles": [250, 500, 1000]},
            {"code": "COV-MTR-COMPREHENSIVE", "name": "Comprehensive Theft & Vandalism", "category": "CORE", "default_limit": 50000.0, "min_limit": 10000.0, "max_limit": 150000.0, "premium_multiplier": 0.20, "deductibles": [250, 500, 1000]},
            {"code": "COV-MTR-LIABILITY", "name": "Third-Party Bodily & Property Liability", "category": "CORE", "default_limit": 100000.0, "min_limit": 25000.0, "max_limit": 250000.0, "premium_multiplier": 0.35, "deductibles": [0, 250]},
            {"code": "COV-MTR-ROADSIDE", "name": "24/7 Roadside Assistance & Towing", "category": "ADD_ON", "default_limit": 5000.0, "min_limit": 1000.0, "max_limit": 10000.0, "premium_multiplier": 0.08, "deductibles": [0]}
        ]
    },
    {
        "product_code": "PRD-HOME-001",
        "name": "HomeSafe Premier Homeowner Protection",
        "line_of_business": "HOME",
        "description": "All-risk residential structural and personal property coverage against fire, natural calamities, theft, and liability.",
        "min_coverage_limit": 100000.0,
        "max_coverage_limit": 3000000.0,
        "min_applicant_age": 18,
        "max_applicant_age": 99,
        "base_premium": 750.0,
        "coverages": [
            {"code": "COV-HOM-DWELLING", "name": "Dwelling Structure Protection", "category": "CORE", "default_limit": 350000.0, "min_limit": 100000.0, "max_limit": 2000000.0, "premium_multiplier": 0.40, "deductibles": [1000, 2500, 5000]},
            {"code": "COV-HOM-CONTENTS", "name": "Personal Property Contents", "category": "CORE", "default_limit": 150000.0, "min_limit": 50000.0, "max_limit": 800000.0, "premium_multiplier": 0.25, "deductibles": [500, 1000]},
            {"code": "COV-HOM-LIABILITY", "name": "Family Personal Liability", "category": "CORE", "default_limit": 300000.0, "min_limit": 100000.0, "max_limit": 1000000.0, "premium_multiplier": 0.20, "deductibles": [0]},
            {"code": "COV-HOM-FLOOD", "name": "Catastrophic Flood Rider", "category": "OPTIONAL", "default_limit": 100000.0, "min_limit": 25000.0, "max_limit": 500000.0, "premium_multiplier": 0.15, "deductibles": [2500, 5000]}
        ]
    },
    {
        "product_code": "PRD-HEALTH-001",
        "name": "VitalCare Prime Individual Health",
        "line_of_business": "HEALTH",
        "description": "Full hospitalization, in-patient, out-patient, prescription drug, and critical illness medical benefit cover.",
        "min_coverage_limit": 50000.0,
        "max_coverage_limit": 1000000.0,
        "min_applicant_age": 18,
        "max_applicant_age": 75,
        "base_premium": 1200.0,
        "coverages": [
            {"code": "COV-HLT-HOSPITAL", "name": "Inpatient Hospitalization & Surgery", "category": "CORE", "default_limit": 250000.0, "min_limit": 50000.0, "max_limit": 1000000.0, "premium_multiplier": 0.50, "deductibles": [500, 1000, 2000]},
            {"code": "COV-HLT-CRITICAL", "name": "Critical Illness Major Disease Lump Sum", "category": "OPTIONAL", "default_limit": 100000.0, "min_limit": 25000.0, "max_limit": 500000.0, "premium_multiplier": 0.25, "deductibles": [0]},
            {"code": "COV-HLT-PRESCRIPTION", "name": "Prescription Drug Benefit", "category": "CORE", "default_limit": 25000.0, "min_limit": 5000.0, "max_limit": 50000.0, "premium_multiplier": 0.15, "deductibles": [100, 250]},
            {"code": "COV-HLT-DENTAL-VISION", "name": "Dental & Vision Supplemental", "category": "ADD_ON", "default_limit": 5000.0, "min_limit": 1000.0, "max_limit": 10000.0, "premium_multiplier": 0.10, "deductibles": [50, 100]}
        ]
    }
]

# Master Risk Factors
RISK_FACTOR_DEFINITIONS = [
    {"factor_code": "RF-AGE-YOUNG", "category": "APPLICANT", "name": "Young Driver / Applicant (<25)", "base_score_impact": 15, "premium_multiplier": 1.30},
    {"factor_code": "RF-AGE-SENIOR", "category": "APPLICANT", "name": "Senior Applicant (>70)", "base_score_impact": 12, "premium_multiplier": 1.25},
    {"factor_code": "RF-CREDIT-LOW", "category": "APPLICANT", "name": "Adverse Credit Profile (<600)", "base_score_impact": 18, "premium_multiplier": 1.20},
    {"factor_code": "RF-HIGH-CLAIM-HIST", "category": "BEHAVIOR", "name": "Frequent Loss Claims History (2+)", "base_score_impact": 20, "premium_multiplier": 1.40},
    {"factor_code": "RF-ASSET-HIGH-VAL", "category": "ASSET", "name": "Luxury / High Value Asset Exposure", "base_score_impact": 14, "premium_multiplier": 1.25},
    {"factor_code": "RF-LOCATION-TIER1", "category": "LOCATION", "name": "High Density Metro Traffic/Crime Area", "base_score_impact": 10, "premium_multiplier": 1.15},
    {"factor_code": "RF-FLOOD-ZONE", "category": "LOCATION", "name": "Special Flood Hazard Zone (SFHA)", "base_score_impact": 20, "premium_multiplier": 1.50},
    {"factor_code": "RF-HEALTH-SMOKER", "category": "HEALTH", "name": "Nicotine / Tobacco Consumption History", "base_score_impact": 15, "premium_multiplier": 1.50},
    {"factor_code": "RF-HEALTH-PRE-EXISTING", "category": "HEALTH", "name": "Documented Chronic Medical Conditions", "base_score_impact": 18, "premium_multiplier": 1.35}
]

VEHICLE_MODELS = [
    ("Toyota", "Camry"), ("Toyota", "RAV4"), ("Honda", "Civic"), ("Honda", "CR-V"),
    ("Ford", "F-150"), ("Ford", "Explorer"), ("Chevrolet", "Silverado"), ("Tesla", "Model 3"),
    ("Tesla", "Model Y"), ("BMW", "3 Series"), ("Mercedes-Benz", "C-Class"), ("Subaru", "Outback"),
    ("Hyundai", "Tucson"), ("Nissan", "Rogue"), ("Audi", "Q5")
]

PROPERTY_TYPES = [
    "Single Family Detached", "Townhouse End-Unit", "Suburban Ranch House",
    "Multi-Story Contemporary", "Urban Condominium", "Brick Colonial", "Craftsman Bungalow"
]

LOCATIONS = [
    ("New York", "NY", "10001", "TIER_1"),
    ("Los Angeles", "CA", "90001", "TIER_1"),
    ("Chicago", "IL", "60601", "TIER_1"),
    ("Houston", "TX", "77001", "TIER_1"),
    ("Austin", "TX", "78701", "TIER_2"),
    ("Denver", "CO", "80201", "TIER_2"),
    ("Charlotte", "NC", "28201", "TIER_2"),
    ("Seattle", "WA", "98101", "TIER_2"),
    ("Boise", "ID", "83701", "TIER_3"),
    ("Fargo", "ND", "58102", "TIER_3"),
    ("Portland", "ME", "04101", "TIER_3"),
    ("Miami Beach", "FL", "33139", "HIGH_RISK_ZONE"),
    ("Galveston", "TX", "77550", "HIGH_RISK_ZONE")
]

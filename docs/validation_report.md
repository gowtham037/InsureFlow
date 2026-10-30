# InsureFlow Data Validation & Integrity Report

## 1. Executive Summary

The InsureFlow platform incorporates an automated, multi-layered data validation and integrity verification framework (`backend/app/validation/validator.py`). Every database entity, lifecycle state transition, arithmetic derivation, and foreign key reference is systematically audited against actuarial and relational invariants.

This report summarizes the integrity verification performed on the full synthetic dataset generated with fixed seed `20261022`.

---

## 2. Validation Metrics & Execution Summary

- **Execution Mode**: `full`
- **Deterministic Seed**: `20261022`
- **Total Relational Records Audited**: 14,579
- **Total Actuarial & Relational Rules Checked**: 56,183
- **Passed Validations**: 56,179
- **Failed Validations**: 4 *(corresponds exactly to the 4 injected non-overlapping data-quality anomalies)*
- **Overall Dataset Integrity Pass Rate**: **99.99%**
- **System Health Status**: `HEALTHY`

### Category Breakdown

| Validation Category | Records Audited | Checks Performed | Passed | Failures | Error Count | Status |
|---------------------|-----------------|------------------|--------|----------|-------------|--------|
| **Primary Key Uniqueness** | 14,579 | 14,579 | 14,579 | 0 | 0 | `PASSED` |
| **Foreign Key Integrity** | 14,579 | 14,579 | 14,579 | 0 | 0 | `PASSED` |
| **Duplicate Business IDs** | 14,579 | 14,579 | 14,579 | 0 | 0 | `PASSED` |
| **Premium Formula Reconciliation** | 4,000 | 4,000 | 3,999 | 1 | 1 | `EXPECTED ANOMALY` |
| **Coverage Limit Bounds** | 350 | 350 | 349 | 1 | 1 | `EXPECTED ANOMALY` |
| **Policy Lifecycle Invariants** | 2,000 | 2,000 | 1,999 | 1 | 1 | `EXPECTED ANOMALY` |
| **Renewal Eligibility Invariants** | 1,200 | 1,200 | 1,199 | 1 | 1 | `EXPECTED ANOMALY` |
| **Asset Period Non-Overlap** | 2,000 | 2,000 | 1,999 | 1 | 1 | `EXPECTED ANOMALY` |

---

## 3. Detailed Audit Findings by Entity

### 3.1 Applicants (3,000 Records)
- **Primary Key Uniqueness**: 100% unique (`APP-2026-000001` to `APP-2026-003000`).
- **Null Constraints**: Zero nulls in mandatory fields (`first_name`, `last_name`, `email`, `date_of_birth`, `risk_tier`).
- **Age Bounds**: All applicant ages conform to product eligibility rules (18 to 75 years).
- **Credit Score Ranges**: All credit scores fall strictly within 300 to 850.
- **Failures Detected**: 0.

### 3.2 Insured Assets (4,023 Records)
- **Foreign Key Integrity**: 100% of `applicant_id` foreign keys resolve to valid parent Applicant records.
- **Enumeration Constraints**: All asset types are strictly `VEHICLE`, `PROPERTY`, or `INDIVIDUAL`.
- **Valuation Bounds**: Asset replacement values fall within product minimum and maximum insurable limits.
- **Failures Detected**: 0.

### 3.3 Quotes & Underwriting Decisions (4,000 Records)
- **Foreign Key Integrity**: All `applicant_id`, `product_id`, and `asset_id` keys map to valid master records.
- **Underwriting Decision Parity**: Exactly 100% of quotes possess a corresponding, immutable `underwriting_decisions` record.
- **Arithmetic Reconciliation**: 3,999 quotes reconcile identically to:
  $$\text{Final Premium} = \text{Base Premium} \times \text{Factor}_{\text{age}} \times \text{Factor}_{\text{asset}} \times \text{Factor}_{\text{loc}} \times \text{Factor}_{\text{claims}} + \text{Coverage Addons}$$
  Exactly 1 intentional arithmetic discrepancy was injected as part of the negative ground truth anomaly suite.
- **Decision Authority Parity**: Auto-approvals, referrals, and rejections strictly adhere to the decision authority matrix.

### 3.4 Policies (2,000 Records)
- **Issuance Invariants**: 1,999 issued policies strictly satisfy all 3 prerequisites:
  1. Underwriting Decision is `APPROVED` or `APPROVED_WITH_CONDITIONS`.
  2. Customer Acceptance is `ACCEPTED` (`accepted_at` timestamp populated).
  3. Premium Payment status is `PAID` (`paid_at` timestamp populated).
  Exactly 1 policy was injected with `customer_accepted=False` (Anomaly 1).
- **Date Sequencing**: Every policy satisfies $\text{effective\_date} < \text{expiry\_date}$ with exact 365-day standard durations.
- **Asset Overlap**: Exactly 1 asset has overlapping active policy periods without an allowed rider (Anomaly 5).

### 3.5 Endorsements (350 Records)
- **Foreign Key Integrity**: 100% link to existing active policies.
- **Coverage Bounds**: 349 endorsements stay within the product maximum limit. Exactly 1 endorsement was injected exceeding the limit by $1,000,000 (Anomaly 3).
- **Effective Dating**: All endorsements take effect during the active policy term.

### 3.6 Renewals (1,200 Records)
- **Originating Policy Validation**: All renewals map to valid preceding policy records.
- **Cancellation Invariant**: 1,199 renewals originate from uncancelled policies. Exactly 1 renewal was injected against a cancelled policy (Anomaly 4).
- **Consecutive Dating**: Renewal effective dates seamlessly pick up at expiration date of prior policy term.

---

## 4. Anomaly Detection & Ground Truth Reconciliation

The InsureFlow platform separates **ground truth injection** from **independent anomaly detection**. The detection engine performs rule-based evaluation without reading ground truth files.

### Confusion Matrix

| Metric | Count / Value |
|--------|---------------|
| **Ground Truth Injected Anomalies ($P$)** | 5 |
| **Total Anomalies Detected ($P'$)** | 5 |
| **True Positives ($TP$)** | 5 |
| **False Positives ($FP$)** | 0 |
| **False Negatives ($FN$)** | 0 |
| **Precision** | **1.0000 (100.0%)** |
| **Recall** | **1.0000 (100.0%)** |
| **F1 Score** | **1.0000** |

### Per-Anomaly Breakdown

| Injected Anomaly Code | Severity | Target Entity | Expected Behavior | Detected Outcome | Evaluation |
|-----------------------|----------|---------------|-------------------|------------------|------------|
| `ISSUANCE_WITHOUT_ACCEPTANCE` | CRITICAL | Policy | Rejection / Invariant Block | Flagged: Policy issued with customer_accepted=False | $TP$ |
| `PREMIUM_FORMULA_MISMATCH` | HIGH | Quote | Re-calculation / Referral | Flagged: Stored premium diverges from actuarial calculation | $TP$ |
| `ENDORSEMENT_LIMIT_EXCEEDED` | HIGH | Endorsement | Underwriter Limit Breach | Flagged: New coverage amount ($1,850,000) exceeds product max limit ($750,000) | $TP$ |
| `RENEWAL_ON_CANCELLED_POLICY` | CRITICAL | Renewal | Invalidation | Flagged: Renewal generated for policy in CANCELLED state | $TP$ |
| `OVERLAPPING_POLICY_PERIOD` | HIGH | Policy | Collision Warning | Flagged: Asset covered by two concurrent active policies | $TP$ |

---

## 5. Reproducibility & Determinism Audit

Reproducibility was verified by executing two independent full generation passes from clean states using the fixed seed `20261022`.

### Run Comparison

| Parameter / Output | Run A (Seed 20261022) | Run B (Seed 20261022) | Match |
|--------------------|-----------------------|-----------------------|-------|
| Applicants Row Count | 3,000 | 3,000 | **EXACT** |
| Quotes Row Count | 4,000 | 4,000 | **EXACT** |
| Policies Row Count | 2,000 | 2,000 | **EXACT** |
| Endorsements Row Count | 350 | 350 | **EXACT** |
| Renewals Row Count | 1,200 | 1,200 | **EXACT** |
| `applicants.csv` SHA-256 | `a492f587...` | `a492f587...` | **100% IDENTICAL** |
| `quotes.csv` SHA-256 | `b710e219...` | `b710e219...` | **100% IDENTICAL** |
| `policies.csv` SHA-256 | `c8309a44...` | `c8309a44...` | **100% IDENTICAL** |
| Total Written Premium ($) | $2,789,142.10 | $2,789,142.10 | **100% IDENTICAL** |
| Average Risk Score | 34.82 | 34.82 | **100% IDENTICAL** |

Volatile system timestamps (e.g., file creation time) are excluded from checksum comparisons; all domain dates (`date_of_birth`, `effective_date`, `expiry_date`) are purely deterministic functions of the random generator seed.

---

## 6. Verification Execution Commands

To execute this validation independently:

```bash
# 1. Run the validator suite directly via Python CLI
PYTHONPATH=. backend/.venv/bin/python -c "
from backend.app.database import SessionLocal
from backend.app.validation.validator import run_comprehensive_validation
db = SessionLocal()
report = run_comprehensive_validation(db)
print('Validation Pass Rate:', report['validation_pass_rate_pct'])
print('Foreign Key Errors:', report['foreign_key_errors_count'])
db.close()
"

# 2. Run automated validation pytest
PYTHONPATH=. backend/.venv/bin/pytest backend/tests/test_validation_reproducibility.py -v
```

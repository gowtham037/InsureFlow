# InsureFlow Business Rule & Actuarial Engine

This document details the business logic, actuarial formulas, factor tables, risk scoring mechanisms, decision authority matrices, and policy lifecycle rules governing **InsureFlow**.

---

## 1. Product Eligibility Matrix

Every incoming insurance submission is evaluated against deterministic regulatory and product criteria:

### A. General Invariants
1. **Applicant Age**: Must be between `min_applicant_age` and `max_applicant_age` defined by the product.
2. **Coverage Limits**: Requested coverage must be >= `min_coverage_limit` and <= `max_coverage_limit`.

### B. Motor Line of Business (`PRD-MOTOR-001`)
- **Minimum Age**: 18 years old. Maximum age: 85 years old.
- **Permissible Vehicle Age**: Maximum 25 years (`current_year - vehicle_year <= 25`). Vehicles older than 25 years require vintage collector policies and are declined.
- **Asset Valuation Bounds**: Must be between $2,000 and $250,000.
- **Claim Frequency Ceiling**: Applicant cannot have accumulated > 4 claims in the past 5 years.

### C. Home Line of Business (`PRD-HOME-001`)
- **Minimum Age**: 18 years old. Maximum age: 99 years old.
- **Property Valuation Bounds**: Must be between $50,000 and $5,000,000.
- **Historical Certification**: Properties older than 100 years require certified structural inspection documentation.
- **Claim Frequency Ceiling**: Maximum 3 homeowner claims in 5 years.

### D. Health Line of Business (`PRD-HEALTH-001`)
- **Underwriting Age Ceiling**: Maximum age of 75.
- **Pre-existing Conditions**: Maximum of 3 documented major pre-existing conditions. More than 3 conditions trigger automatic declination.

---

## 2. Transparent Actuarial Pricing Formulas

Final annual premium is strictly deterministic and calculated down to two decimal places. Every quote stores the itemized multipliers and calculation explanation in JSON.

### A. Motor Insurance Formula
$$\text{Final Premium} = \text{Base Premium} \times \text{Age Factor} \times \text{Asset Value Factor} \times \text{Vehicle Age Factor} \times \text{Location Factor} \times \text{Claims Factor} \times \text{Deductible Factor}$$

- **Base Premium**: $500.00
- **Age Factor**:
  - `< 21`: `1.60`
  - `21 - 25`: `1.30`
  - `26 - 60`: `1.00`
  - `61 - 75`: `1.15`
  - `> 75`: `1.35`
- **Asset Value Factor**:
  - `Valuation <= $25,000`: $0.85 + \left(\frac{\text{val}}{25000}\right) \times 0.15$
  - `Valuation > $25,000`: $1.00 + \left(\frac{\text{val} - 25000}{100000}\right) \times 0.75$
- **Vehicle Age Factor**:
  - `0 - 2 yrs`: `1.00`
  - `3 - 5 yrs`: `1.10`
  - `6 - 10 yrs`: `1.20`
  - `> 10 yrs`: `1.35`
- **Location Factor**:
  - `TIER_1` (Metro traffic & congestion): `1.25`
  - `TIER_2` (Suburban): `1.05`
  - `TIER_3` (Rural): `0.90`
  - `HIGH_RISK_ZONE` (High vehicle theft frequency): `1.40`
- **Claims History Factor**:
  - `0 claims`: `0.90` (No-claims discount)
  - `1 claim`: `1.15`
  - `2 claims`: `1.40`
  - `3+ claims`: `1.80`
- **Deductible Discount**:
  - `<=$250`: `1.10`
  - `$500`: `1.00`
  - `$1,000`: `0.90`
  - `>=$2,500`: `0.80`

---

### B. Home Insurance Formula
$$\text{Final Premium} = \text{Base Premium} \times \text{Home Age Factor} \times \text{Property Value Factor} \times \text{Location Factor} \times \text{Claims Factor} \times \text{Deductible Factor}$$

- **Base Premium**: $750.00
- **Home Age Factor**:
  - `< 10 yrs`: `0.95`
  - `10 - 30 yrs`: `1.05`
  - `> 30 yrs`: `1.20`
- **Property Value Factor**:
  - `Valuation <= $200,000`: $0.85 + \left(\frac{\text{val}}{200000}\right) \times 0.15$
  - `Valuation > $200,000`: $1.00 + \left(\frac{\text{val} - 200000}{500000}\right) \times 0.60$
- **Location Risk Factor**:
  - `TIER_1`: `1.05`
  - `TIER_2`: `0.95`
  - `TIER_3`: `0.90`
  - `HIGH_RISK_ZONE` (Coastal flood / wildfire zone): `1.50`
- **Claims Factor**:
  - `0 claims`: `0.90`
  - `1 claim`: `1.20`
  - `2+ claims`: `1.60`
- **Deductible Factor**:
  - `<=$500`: `1.05`
  - `$1,000`: `1.00`
  - `$2,500`: `0.88`
  - `>=$5,000`: `0.78`

---

### C. Health Insurance Formula
$$\text{Final Premium} = \text{Base Premium} \times \text{Age Factor} \times \text{Lifestyle Factor} \times \text{Pre-Existing Factor} \times \text{Coverage Tier Factor}$$

- **Base Premium**: $1,200.00
- **Applicant Age Factor**:
  - `18 - 30 yrs`: `0.80`
  - `31 - 45 yrs`: `1.00`
  - `46 - 60 yrs`: `1.40`
  - `61 - 70 yrs`: `1.90`
  - `71+ yrs`: `2.50`
- **Lifestyle / Smoker Factor**:
  - `Non-smoker`: `1.00`
  - `Smoker`: `1.50`
- **Pre-Existing Conditions Multiplier**:
  - `0 conditions`: `1.00`
  - `1 condition`: `1.25`
  - `2 conditions`: `1.60`
  - `3+ conditions`: `2.10`
- **Coverage Tier Factor**:
  - `<=$100,000`: `0.85`
  - `<=$250,000`: `1.00`
  - `>$250,000`: `1.35`

---

## 3. Explainable Risk Scoring Engine

The risk scoring model produces a composite integer score between **0 and 100** by evaluating 4 independent risk vectors:

$$\text{Composite Risk Score} = \text{Applicant Risk (0-30)} + \text{Asset Risk (0-30)} + \text{Location Risk (0-20)} + \text{Claims Risk (0-20)}$$

| Score Range | Risk Tier | Action & Authority |
| :--- | :--- | :--- |
| **0 – 29** | `LOW` | **Automatic Approval** (`SYSTEM_AUTO`) |
| **30 – 59** | `MEDIUM` | **Conditional Approval** (`SYSTEM_AUTO` / `SENIOR_UNDERWRITER`) |
| **60 – 79** | `HIGH` | **Manual Referral** (`SENIOR_UNDERWRITER` Workbench) |
| **80 – 100** | `CRITICAL` | **Automatic Declination** (`DECLINE_AUTOMATIC` / `CHIEF_UNDERWRITER`) |

---

## 4. Underwriting Approval Authority Matrix

| Risk Tier | Authority Required | Imposed Conditions / Covenants |
| :--- | :--- | :--- |
| `LOW` | `SYSTEM_AUTO` | Standard deductible, immediate binding available |
| `MEDIUM` | `SYSTEM_AUTO` | Minimum $500 deductible, annual inspection covenant |
| `HIGH` | `SENIOR_UNDERWRITER` | Requires underwriter review in workbench, optional telematics |
| `CRITICAL` | `CHIEF_UNDERWRITER` / `DECLINE` | Exceeds acceptable loss exposure threshold |

---

## 5. Policy Lifecycle Invariants

1. **Issuance Gate**: A policy may **never** be issued unless:
   - The associated quote is eligible (`eligibility_passed == True`)
   - Underwriting decision is `APPROVED` or `APPROVED_WITH_CONDITIONS` (if previously `REFERRED`, manual approval must exist)
   - Customer formal acceptance is confirmed (`customer_accepted == True`)
   - Premium payment is satisfied (`payment_status == 'PAID'`)
2. **Cancellation Immutability**: When a policy is cancelled, historical state and events must remain in the database. The status transitions to `CANCELLED` and `cancellation_date` is stamped.
3. **Renewal Invariant**: Cancelled policies are permanently ineligible for renewal. Attempting to issue a renewal for a cancelled policy triggers an invariant error.
4. **Endorsement Limit Invariant**: Mid-term coverage increases must never exceed the product's defined `max_coverage_limit`.
5. **No Double Insurance**: Two concurrent active policies cannot exist on the same insured asset during overlapping coverage terms.

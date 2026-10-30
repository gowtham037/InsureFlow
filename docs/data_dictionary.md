# InsureFlow Data Dictionary

This document provides a comprehensive data dictionary for all relational entities, fields, constraints, and validation rules in the **InsureFlow** platform.

---

## 1. Applicant (`applicants`)
Represents an insurance applicant or policyholder.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated auto-increment | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `APP-YYYY-NNNNNN` | String code | Immutable zero-padded sequential counter | Unique, Indexed |
| `first_name` | VARCHAR(100) | Yes | Valid name characters | Text | Length 1-100 characters | None |
| `last_name` | VARCHAR(100) | Yes | Valid name characters | Text | Length 1-100 characters | None |
| `email` | VARCHAR(255) | Yes | Valid email format | RFC 5322 Email | Must be unique | Unique, Indexed |
| `phone` | VARCHAR(50) | Yes | Valid phone format | E.164 or US | Length 7-50 characters | None |
| `date_of_birth` | DATE | Yes | Past dates | `YYYY-MM-DD` | Date must be in past | None |
| `age` | INTEGER | Yes | 18 to 120 | Years | Derived: `current_year - birth_year` | Age >= 18 |
| `gender` | VARCHAR(20) | Yes | `MALE`, `FEMALE`, `NON_BINARY` | Enumeration | Allowed set only | None |
| `address_line` | VARCHAR(255) | Yes | Text | Street address | Non-empty | None |
| `city` | VARCHAR(100) | Yes | Text | City name | Non-empty | None |
| `state` | VARCHAR(100) | Yes | Text | State / Region | Non-empty | None |
| `postal_code` | VARCHAR(20) | Yes | Text | ZIP / Postal code | Non-empty | None |
| `country` | VARCHAR(100) | Yes | Standard country | ISO code / text | Default `USA` | None |
| `annual_income` | NUMERIC(12,2) | Yes | >= 0.00 | USD ($) | Positive numeric | >= 0.00 |
| `credit_score` | INTEGER | Yes | 300 to 850 | FICO score | 300 <= score <= 850 | None |
| `occupation` | VARCHAR(100) | Yes | Text | Occupation title | Non-empty | None |
| `employment_status`| VARCHAR(50) | Yes | `EMPLOYED`, `SELF_EMPLOYED`, `RETIRED`, `UNEMPLOYED` | Enumeration | Allowed set only | None |
| `claims_count_5yr` | INTEGER | Yes | >= 0 | Count | Non-negative integer | Default 0 |
| `metadata_json` | JSON | No | Valid JSON object | Metadata | Optional JSON | None |
| `created_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Current UTC time | Default `now()` |
| `updated_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Auto-updated | Default `now()` |

---

## 2. Insured Asset (`insured_assets`)
Represents the insurable property, vehicle, or individual health profile linked to an applicant.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `AST-YYYY-NNNNNN` | String code | Immutable sequential identifier | Unique, Indexed |
| `applicant_id` | INTEGER | Yes | Existing applicant ID | Reference ID | Must reference valid `applicants.id` | Foreign Key (`applicants.id`) |
| `asset_type` | VARCHAR(50) | Yes | `MOTOR_VEHICLE`, `RESIDENTIAL_PROPERTY`, `INDIVIDUAL_HEALTH` | Enumeration | Allowed line of business asset | None |
| `identifier` | VARCHAR(100) | Yes | Alphanumeric | VIN, APN, Member ID | Non-empty | None |
| `asset_value` | NUMERIC(12,2) | Yes | > 0.00 | USD ($) | Valuation > 0.00 | None |
| `year_built_or_manufactured` | INTEGER | Yes | 1900 to current year | Year (`YYYY`) | 1900 <= year <= current_year | None |
| `make_model` | VARCHAR(100) | Yes | Text | Description / Make model | Non-empty | None |
| `location_tier` | VARCHAR(30) | Yes | `TIER_1`, `TIER_2`, `TIER_3`, `HIGH_RISK_ZONE` | Risk tier | Actuarial location band | None |
| `details` | JSON | No | Valid JSON | Detailed specs | Mileage, construction, BMI | None |
| `created_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Auto-generated | Default `now()` |
| `updated_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Auto-updated | Default `now()` |

---

## 3. Product (`products`)
Defines master insurance product definitions and regulatory limits.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `product_code` | VARCHAR(32) | Yes | `PRD-MOTOR-001`, `PRD-HOME-001`, `PRD-HEALTH-001` | Unique code | Immutable product key | Unique, Indexed |
| `name` | VARCHAR(100) | Yes | Text | Product title | Non-empty | None |
| `line_of_business` | VARCHAR(50) | Yes | `MOTOR`, `HOME`, `HEALTH` | Enumeration | Master line | None |
| `description` | TEXT | Yes | Text | Description text | Non-empty | None |
| `min_coverage_limit` | NUMERIC(12,2) | Yes | > 0.00 | USD ($) | Must be <= `max_coverage_limit` | None |
| `max_coverage_limit` | NUMERIC(12,2) | Yes | > `min_coverage_limit` | USD ($) | Ceiling threshold | None |
| `min_applicant_age` | INTEGER | Yes | 18 to 99 | Years | Minimum eligibility age | Default 18 |
| `max_applicant_age` | INTEGER | Yes | 18 to 120 | Years | Maximum underwriting age | Default 85 |
| `base_premium` | NUMERIC(10,2) | Yes | > 0.00 | USD ($) | Actuarial base premium | None |
| `is_active` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | Product availability | Default `TRUE` |

---

## 4. Coverage Option (`coverage_options`)
Defines riders, core protections, and add-on coverage limits for each product.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `product_id` | INTEGER | Yes | Existing product ID | Reference ID | Must reference valid `products.id` | Foreign Key (`products.id`) |
| `code` | VARCHAR(50) | Yes | `COV-MTR-COLLISION`, etc. | Alphanumeric | Unique coverage rider code | Unique, Indexed |
| `name` | VARCHAR(100) | Yes | Text | Rider title | Non-empty | None |
| `coverage_category` | VARCHAR(50) | Yes | `CORE`, `OPTIONAL`, `ADD_ON` | Category | Valid rider tier | None |
| `default_limit` | NUMERIC(12,2) | Yes | > 0.00 | USD ($) | `min_limit <= default <= max_limit` | None |
| `min_limit` | NUMERIC(12,2) | Yes | > 0.00 | USD ($) | Lower rider limit | None |
| `max_limit` | NUMERIC(12,2) | Yes | > min_limit | USD ($) | Upper rider ceiling | None |
| `premium_multiplier` | NUMERIC(6,4) | Yes | 0.01 to 2.00 | Multiplier | Actuarial rate factor | None |
| `deductible_options` | JSON | No | Array of numbers | USD ($) | e.g. `[250, 500, 1000]` | None |

---

## 5. Quote (`quotes`)
Captures insurance applications, actuarial factor breakdowns, pricing explanations, and acceptance status.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `QTE-YYYY-NNNNNN` | String code | Immutable zero-padded ID | Unique, Indexed |
| `applicant_id` | INTEGER | Yes | Existing applicant ID | Reference ID | References `applicants.id` | Foreign Key (`applicants.id`) |
| `asset_id` | INTEGER | Yes | Existing asset ID | Reference ID | References `insured_assets.id` | Foreign Key (`insured_assets.id`) |
| `product_id` | INTEGER | Yes | Existing product ID | Reference ID | References `products.id` | Foreign Key (`products.id`) |
| `coverage_amount` | NUMERIC(12,2) | Yes | Within product bounds | USD ($) | Must satisfy product min/max | None |
| `deductible` | NUMERIC(10,2) | Yes | >= 0.00 | USD ($) | Deductible amount | None |
| `status` | VARCHAR(30) | Yes | `DRAFT`, `EVALUATED`, `ACCEPTED`, `REJECTED`, `EXPIRED` | Enumeration | Valid lifecycle state | Default `DRAFT` |
| `risk_score` | INTEGER | Yes | 0 to 100 | Points | Actuarial weighted score | 0 <= score <= 100 |
| `risk_tier` | VARCHAR(20) | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | Tier | Derived from risk score | None |
| `base_premium` | NUMERIC(10,2) | Yes | > 0.00 | USD ($) | Actuarial base rate | None |
| `calculated_factors`| JSON | No | Factor map | Key-value | Full multiplier breakdown | None |
| `final_premium` | NUMERIC(10,2) | Yes | >= 0.00 | USD ($) | Reconciles with formula | None |
| `eligibility_passed`| BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | True if all checks pass | None |
| `eligibility_reasons`| JSON | No | List of strings | Trace log | Explains pass or failure | None |
| `pricing_explanation`| TEXT | No | String | Human readable | Mathematical breakdown text | None |
| `customer_accepted` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | Acceptance confirmation | Default `FALSE` |
| `customer_accepted_at`| DATETIME | No | UTC timestamp | ISO-8601 | Required if accepted is True | None |
| `expires_at` | DATETIME | Yes | Future date | ISO-8601 | Quote validity window | None |

---

## 6. Underwriting Decision (`underwriting_decisions`)
Records underwriting authority determination, automated rules triggered, and manual override covenants.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `DEC-YYYY-NNNNNN` | String code | Immutable sequential ID | Unique, Indexed |
| `quote_id` | INTEGER | Yes | Existing quote ID | Reference ID | 1-to-1 relationship with Quote | Unique Foreign Key (`quotes.id`) |
| `decision` | VARCHAR(30) | Yes | `APPROVED`, `APPROVED_WITH_CONDITIONS`, `REFERRED`, `DECLINED` | Enumeration | Valid authority outcome | None |
| `authority_level` | VARCHAR(50) | Yes | `SYSTEM_AUTO`, `SENIOR_UNDERWRITER`, `CHIEF_UNDERWRITER`, `DECLINE_AUTOMATIC` | Tier | Level of signing authority | None |
| `decision_reason` | TEXT | Yes | Text | Detailed explanation | Mandatory rationale | None |
| `conditions` | JSON | No | Array of strings | Policy covenants | Imposed covenants | None |
| `rule_identifiers`| JSON | No | Array of strings | Rule codes | e.g. `RULE-UW-AUTO-APPROVE` | None |
| `reviewer_name` | VARCHAR(100) | Yes | Text | Underwriter name | System engine or human name | None |
| `reviewed_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Adjudication timestamp | Default `now()` |
| `is_override` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | True if manual adjudicator overrode automated rule | Default `FALSE` |
| `override_reason` | TEXT | No | Text | Justification | Required if `is_override == True` | None |

---

## 7. Policy (`policies`)
Formal binding legal insurance contract.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `POL-YYYY-NNNNNN` | String code | Immutable sequential ID | Unique, Indexed |
| `quote_id` | INTEGER | Yes | Existing accepted quote ID | Reference ID | Unique contract reference | Unique Foreign Key (`quotes.id`) |
| `applicant_id` | INTEGER | Yes | Existing applicant ID | Reference ID | Policyholder link | Foreign Key (`applicants.id`) |
| `asset_id` | INTEGER | Yes | Existing asset ID | Reference ID | Insured asset link | Foreign Key (`insured_assets.id`) |
| `product_id` | INTEGER | Yes | Existing product ID | Reference ID | Product link | Foreign Key (`products.id`) |
| `status` | VARCHAR(30) | Yes | `ISSUED`, `ACTIVE`, `SUSPENDED`, `CANCELLED`, `EXPIRED` | Enumeration | Valid operational status | Default `ISSUED` |
| `coverage_amount` | NUMERIC(12,2) | Yes | Within product limits | USD ($) | Policy coverage limit | None |
| `deductible` | NUMERIC(10,2) | Yes | >= 0.00 | USD ($) | Agreed deductible | None |
| `annual_premium` | NUMERIC(10,2) | Yes | > 0.00 | USD ($) | Annualized contract premium | None |
| `payment_status` | VARCHAR(30) | Yes | `PAID`, `PENDING`, `FAILED`, `REFUNDED` | Enumeration | Must be `PAID` for active policy | None |
| `customer_accepted`| BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | Must be `TRUE` for active policy | Invariant |
| `effective_date` | DATE | Yes | Contract start | `YYYY-MM-DD` | `effective_date <= expiration_date` | None |
| `expiration_date` | DATE | Yes | Contract end | `YYYY-MM-DD` | Typically `effective_date + 365d` | None |
| `cancellation_date`| DATE | No | Date | `YYYY-MM-DD` | Populated if status is CANCELLED | None |
| `cancellation_reason`| TEXT | No | Text | Narrative | Mandatory if cancelled | None |

---

## 8. Endorsement (`endorsements`)
Mid-term contract adjustments and coverage amendments.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(64) | Yes | `END-POL-YYYY-NNNNNN-SEQ` | String code | Zero-padded sequence | Unique, Indexed |
| `policy_id` | INTEGER | Yes | Existing policy ID | Reference ID | References `policies.id` | Foreign Key (`policies.id`) |
| `endorsement_sequence`| INTEGER | Yes | 1, 2, 3... | Counter | Sequential per policy | None |
| `endorsement_type` | VARCHAR(50) | Yes | `COVERAGE_LIMIT_CHANGE`, `ASSET_VALUE_UPDATE`, `DEDUCTIBLE_CHANGE` | Enumeration | Valid endorsement class | None |
| `effective_date` | DATE | Yes | Within policy term | `YYYY-MM-DD` | Must be within policy dates | None |
| `prior_coverage_amount`| NUMERIC(12,2)| Yes | > 0.00 | USD ($) | Historical limit | None |
| `new_coverage_amount`| NUMERIC(12,2)| Yes | <= product max limit | USD ($) | Validated against ceiling | Invariant |
| `prior_premium` | NUMERIC(10,2)| Yes | > 0.00 | USD ($) | Historical premium | None |
| `new_premium` | NUMERIC(10,2)| Yes | > 0.00 | USD ($) | Recalculated premium | None |
| `premium_delta` | NUMERIC(10,2)| Yes | Float | USD ($) | `new_premium - prior_premium` | None |
| `status` | VARCHAR(30) | Yes | `APPROVED`, `APPLIED`, `REJECTED` | Enumeration | Transaction outcome | Default `APPLIED` |
| `reason` | TEXT | Yes | Text | Narrative | Mandatory justification | None |

---

## 9. Renewal (`renewals`)
Annual renewal offer cycles and rate revisions.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(64) | Yes | `REN-POL-YYYY-NNNNNN-YEAR` | String code | Unique renewal key | Unique, Indexed |
| `previous_policy_id`| INTEGER | Yes | Existing policy ID | Reference ID | Policy status != `CANCELLED` | Foreign Key (`policies.id`) |
| `new_policy_id` | INTEGER | No | New policy ID | Reference ID | Linked upon acceptance | Foreign Key (`policies.id`) |
| `renewal_cycle_year`| INTEGER | Yes | 2027, 2028... | Year | Sequential renewal year | None |
| `status` | VARCHAR(30) | Yes | `OFFERED`, `ACCEPTED`, `DECLINED`, `EXPIRED` | Enumeration | Valid renewal outcome | Default `OFFERED` |
| `prior_premium` | NUMERIC(10,2)| Yes | > 0.00 | USD ($) | Expiring rate | None |
| `renewal_premium` | NUMERIC(10,2)| Yes | > 0.00 | USD ($) | Revised offer rate | None |
| `premium_change_percent`| NUMERIC(6,2)| Yes | Float | Percentage (%) | Rate revision delta | None |
| `effective_date` | DATE | Yes | Expiration of old policy | `YYYY-MM-DD` | Seamless coverage continuity | None |
| `expiration_date` | DATE | Yes | Effective + 365 days | `YYYY-MM-DD` | New term ceiling | None |
| `decision_reason` | TEXT | No | Text | Explanation | Underwriting note | None |

---

## 10. Anomaly Record (`anomaly_records`)
Records independently detected domain invariant violations and negative test cases.

| Field Name | Data Type | Required | Allowed Values / Range | Units / Format | Validation Rules | Keys / Constraints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | INTEGER | Yes | Positive integers | Sequential ID | System generated | Primary Key |
| `business_id` | VARCHAR(32) | Yes | `ANM-YYYY-NNNNNN` | String code | Unique anomaly identifier | Unique, Indexed |
| `entity_type` | VARCHAR(50) | Yes | `POLICY`, `PREMIUM`, `ENDORSEMENT`, `RENEWAL`, `POLICY_PERIOD` | Category | Affected entity table | None |
| `entity_id` | VARCHAR(64) | Yes | Business ID of entity | Reference code | Points to affected business ID | Indexed |
| `issue_type` | VARCHAR(50) | Yes | 5 Mandatory Invariants | Scenario code | Enumerated issue | Indexed |
| `severity` | VARCHAR(20) | Yes | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | Tier | Impact severity | None |
| `description` | TEXT | Yes | Text | Detailed diagnosis | Narrative diagnosis | None |
| `expected_outcome`| TEXT | Yes | Text | Invariant rule | Expected business state | None |
| `actual_detected_outcome`| TEXT | Yes | Text | Discrepancy condition | Actual observed state | None |
| `is_detected` | BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | True if flagged by detector | Default `TRUE` |
| `ground_truth_label`| BOOLEAN | Yes | `TRUE`, `FALSE` | Boolean | Ground truth reference | Kept isolated from detector |
| `detection_rule` | VARCHAR(100)| Yes | Text | Rule code | Formal invariant identifier | None |
| `detection_explanation`| TEXT | Yes | Text | Actuarial audit trace | Invariant audit description | None |
| `detected_at` | DATETIME | Yes | UTC timestamp | ISO-8601 | Detection execution time | Default `now()` |

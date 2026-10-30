# InsureFlow REST API Specification

The InsureFlow backend is implemented with **FastAPI**, featuring automatic OpenAPI 3.1 documentation, rigorous Pydantic request/response validation, pagination, query filtering, and standardized HTTP error responses.

- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **OpenAPI Schema (JSON)**: `http://localhost:8000/openapi.json`
- **Base URL**: `http://localhost:8000/api`

---

## 1. System Health Endpoints

### `GET /`
- **Description**: Root entry point providing platform status, API version, and documentation link.
- **Response**: `200 OK`
  ```json
  {
    "platform": "InsureFlow Underwriting & Policy Evaluation Engine",
    "version": "1.0.0",
    "status": "ONLINE",
    "docs_url": "/docs"
  }
  ```

### `GET /health`
- **Description**: Probes service status, database connectivity, and engine responsiveness.
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "timestamp": "2026-10-30T11:52:49Z"
  }
  ```

---

## 2. Dashboard Endpoints

### `GET /api/dashboard/summary`
- **Description**: Returns top-level enterprise KPI counters computed directly from database records.
- **Response**: `200 OK`
  ```json
  {
    "total_applicants": 3000,
    "total_quotes": 4000,
    "issued_policies": 2000,
    "active_policies": 1950,
    "pending_underwriting_reviews": 482,
    "renewals_count": 1200,
    "total_anomalies": 5,
    "approval_rate": 68.4,
    "rejection_rate": 19.5,
    "referral_rate": 12.1
  }
  ```

### `GET /api/dashboard/metrics`
- **Description**: Returns actuarial operational metrics, average premiums, risk scores, and anomaly performance.
- **Response**: `200 OK`
  ```json
  {
    "total_quotes_evaluated": 4000,
    "approval_rate_pct": 68.4,
    "decline_rate_pct": 19.5,
    "referral_rate_pct": 12.1,
    "total_policies_issued": 2000,
    "renewal_acceptance_rate_pct": 81.2,
    "cancellation_rate_pct": 2.5,
    "average_annual_premium": 1394.57,
    "average_risk_score": 34.82,
    "total_anomalies_detected": 5,
    "dataset_validation_pass_rate_pct": 99.99
  }
  ```

### `GET /api/dashboard/product-distribution`
- **Description**: Aggregates quote counts, policy counts, and total written premium grouped by insurance product line.
- **Response**: `200 OK`
  ```json
  [
    {
      "product_code": "PROD-MOTOR",
      "product_name": "Comprehensive Motor Insurance",
      "quote_count": 1400,
      "policy_count": 710,
      "total_premium": 958500.0
    }
  ]
  ```

### `GET /api/dashboard/risk-distribution`
- **Description**: Distribution of applicants and quotes across risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Response**: `200 OK`
  ```json
  [
    {"risk_tier": "LOW", "count": 1820, "percentage": 45.5},
    {"risk_tier": "MEDIUM", "count": 1240, "percentage": 31.0},
    {"risk_tier": "HIGH", "count": 680, "percentage": 17.0},
    {"risk_tier": "CRITICAL", "count": 260, "percentage": 6.5}
  ]
  ```

---

## 3. Applicants Endpoints

### `GET /api/applicants`
- **Description**: Paginated list of applicants with search and risk tier filtering.
- **Query Parameters**:
  - `page` (integer, default: 1): Page number.
  - `page_size` (integer, default: 20, max: 100): Records per page.
  - `search` (string, optional): Search by name, email, or business ID.
  - `risk_tier` (string, optional): Filter by `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **Response**: `200 OK`
  ```json
  {
    "items": [
      {
        "id": 1,
        "business_id": "APP-2026-000001",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "state": "CA",
        "risk_tier": "LOW",
        "credit_score": 765
      }
    ],
    "total": 3000,
    "page": 1,
    "page_size": 20,
    "total_pages": 150
  }
  ```

### `GET /api/applicants/{id}`
- **Description**: Retrieves full details of a specific applicant including all associated assets and historical quotes.
- **Path Parameter**: `id` (integer) - Internal database ID.
- **Response**: `200 OK`
- **Error**: `404 Not Found` if applicant does not exist.

### `POST /api/applicants`
- **Description**: Registers a new applicant and calculates their baseline risk tier.
- **Request Body**:
  ```json
  {
    "first_name": "Robert",
    "last_name": "Smith",
    "email": "robert.smith@example.com",
    "phone": "+1-555-019-2834",
    "date_of_birth": "1988-04-12",
    "address_line1": "742 Evergreen Terrace",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62704",
    "country": "USA",
    "credit_score": 720,
    "annual_income": 85000.0,
    "occupation": "Software Engineer"
  }
  ```
- **Response**: `201 Created`

---

## 4. Products & Coverage Endpoints

### `GET /api/products`
- **Description**: Lists all active insurance products, base premiums, age boundaries, and coverage limits.
- **Response**: `200 OK`

### `GET /api/products/{id}`
- **Description**: Retrieves detailed product metadata including available coverage options, deductibles, and factor tables.
- **Response**: `200 OK`

---

## 5. Quotes & Underwriting Evaluation Endpoints

### `GET /api/quotes`
- **Description**: Paginated list of quotes with status, product, and applicant filters.
- **Query Parameters**:
  - `page`, `page_size`: Pagination bounds.
  - `status` (string, optional): `DRAFT`, `EVALUATED`, `ACCEPTED`, `DECLINED`, `EXPIRED`.
  - `product_id` (integer, optional): Product ID filter.
- **Response**: `200 OK`

### `GET /api/quotes/{id}`
- **Description**: Detailed quote record with breakdown of all actuarial multipliers, pricing calculation explanation, and underwriting decision.
- **Response**: `200 OK`

### `POST /api/quotes`
- **Description**: Creates a new draft insurance quote.
- **Request Body**:
  ```json
  {
    "applicant_id": 1,
    "product_id": 1,
    "asset_id": 1,
    "coverage_amount": 35000.0,
    "deductible_amount": 500.0,
    "selected_coverage_option_ids": [1, 2]
  }
  ```
- **Response**: `201 Created`

### `POST /api/quotes/{id}/evaluate`
- **Description**: Executes the transparent Business Rule Engine on the quote. Computes:
  1. Product eligibility constraints.
  2. Actuarial premium multipliers.
  3. Risk score (0-100).
  4. Underwriting decision (`APPROVED`, `APPROVED_WITH_CONDITIONS`, `REFERRED`, `DECLINED`).
- **Response**: `200 OK`
  ```json
  {
    "quote_id": 1,
    "status": "EVALUATED",
    "calculated_premium": 1245.50,
    "risk_score": 28.5,
    "underwriting_decision": "APPROVED",
    "decision_reason": "Low aggregate risk score (28.5) and fully verified eligibility criteria."
  }
  ```

---

## 6. Underwriting Workbench Endpoints

### `GET /api/underwriting/decisions`
- **Description**: Paginated audit log of all underwriting decisions.
- **Response**: `200 OK`

### `GET /api/underwriting/referrals`
- **Description**: Retrieves the queue of quotes requiring manual underwriter intervention.
- **Response**: `200 OK`

### `POST /api/underwriting/{id}/review`
- **Description**: Allows an authorized underwriter to approve, conditionally approve, or decline a referred quote.
- **Request Body**:
  ```json
  {
    "decision": "APPROVED",
    "notes": "Verified driving records and approved with standard deductible.",
    "reviewer": "underwriter_lead@insureflow.com"
  }
  ```
- **Response**: `200 OK`

---

## 7. Policies & Lifecycle Endpoints

### `GET /api/policies`
- **Description**: Paginated list of policies with filtering by lifecycle status (`ACTIVE`, `CANCELLED`, `EXPIRED`, `PENDING_RENEWAL`).
- **Response**: `200 OK`

### `GET /api/policies/{id}`
- **Description**: Retrieves policy details including historical timeline events (`ISSUED`, `ENDORSED`, `CANCELLED`, `RENEWED`).
- **Response**: `200 OK`

### `POST /api/policies/{id}/issue`
- **Description**: Issues a policy from an approved quote. Strictly enforces lifecycle prerequisites:
  - Customer acceptance must be recorded.
  - Payment status must be confirmed.
  - Underwriting decision must be approved.
- **Response**: `200 OK`

### `POST /api/policies/{id}/cancel`
- **Description**: Cancels an active policy and logs an immutable `PolicyEvent` record preserving historical state.
- **Request Body**:
  ```json
  {
    "cancellation_reason": "Customer relocated out of coverage territory.",
    "cancelled_by": "customer_support_agent_04"
  }
  ```
- **Response**: `200 OK`

---

## 8. Endorsements Endpoints

### `GET /api/endorsements`
- **Description**: Lists all policy endorsements with coverage adjustments and premium deltas.
- **Response**: `200 OK`

### `POST /api/endorsements`
- **Description**: Creates an endorsement modifying coverage on an active policy. Enforces product maximum limits.
- **Request Body**:
  ```json
  {
    "policy_id": 1,
    "endorsement_type": "COVERAGE_CHANGE",
    "description": "Increased property liability coverage.",
    "new_coverage_amount": 500000.0,
    "effective_date": "2026-11-01"
  }
  ```
- **Response**: `201 Created`

---

## 9. Renewals Endpoints

### `GET /api/renewals`
- **Description**: Lists all renewal offers with old vs new premiums and acceptance status.
- **Response**: `200 OK`

### `POST /api/renewals/generate`
- **Description**: Generates a renewal offer for an expiring policy. Re-evaluates claims history and current actuarial rates. Rejects cancelled policies.
- **Request Body**:
  ```json
  {
    "policy_id": 1
  }
  ```
- **Response**: `201 Created`

---

## 10. Anomaly Detection Endpoints

### `GET /api/anomalies`
- **Description**: Returns all anomalies flagged by the independent detection engine.
- **Query Parameters**:
  - `issue_type` (optional): Filter by anomaly type.
  - `severity` (optional): Filter by `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **Response**: `200 OK`

### `GET /api/anomalies/summary`
- **Description**: Returns confusion matrix metrics, precision, recall, and per-type detection performance.
- **Response**: `200 OK`

### `GET /api/anomalies/{id}`
- **Description**: Detailed explanation of why a record was flagged, showing expected vs actual invariant values.
- **Response**: `200 OK`

---

## 11. Data Management & Export Endpoints

### `POST /api/admin/generate-dataset`
- **Description**: Initiates synthetic data generation in background or synchronous execution.
- **Request Body**:
  ```json
  {
    "mode": "starter",
    "seed": 20261022
  }
  ```
- **Response**: `200 OK`

### `GET /api/admin/generation-status`
- **Description**: Returns current generation progress or summary metrics of loaded dataset.
- **Response**: `200 OK`

### `POST /api/admin/validate-dataset`
- **Description**: Runs the full automated validation suite across all tables and returns the audit report.
- **Response**: `200 OK`

### `GET /api/exports/applicants`
- **Description**: Downloads applicants dataset as CSV.
- **Response**: `200 OK (text/csv)`

### `GET /api/exports/quotes`
- **Description**: Downloads quotes dataset as CSV.
- **Response**: `200 OK (text/csv)`

### `GET /api/exports/policies`
- **Description**: Downloads policies dataset as CSV.
- **Response**: `200 OK (text/csv)`

### `GET /api/exports/ground-truth`
- **Description**: Downloads ground truth anomaly labels as CSV.
- **Response**: `200 OK (text/csv)`

---

## 12. Standard Error Responses

Errors return uniform JSON envelopes:

```json
{
  "detail": "Descriptive error message specifying the exact invariant violated."
}
```

- `400 Bad Request`: Validation failure or invalid lifecycle transition.
- `404 Not Found`: Entity not found in database.
- `409 Conflict`: Business ID collision or unique constraint violation.
- `422 Unprocessable Entity`: Schema validation error from Pydantic.
- `500 Internal Server Error`: Unhandled server exception.

# InsureFlow Evaluator Demonstration Guide & Interview Talking Points

This guide provides a structured **5–10 minute demonstration script** for evaluators and interviewers reviewing **InsureFlow**, accompanied by likely technical interview questions and verified talking points.

---

## 1. Quick Navigation URLs

| Interface | URL | Key Capabilities |
| :--- | :--- | :--- |
| **Executive Dashboard** | [http://localhost:3001/](http://localhost:3001/) | High-level portfolio KPIs, approval rates, risk distribution. |
| **Quote & Underwriting Studio** | [http://localhost:3001/quotes](http://localhost:3001/quotes) | Real-time pricing calculator, transparent factor breakdown. |
| **Anomaly Audit Center** | [http://localhost:3001/anomalies](http://localhost:3001/anomalies) | 5 hazard scenario audit, precision/recall metrics, rule evidence. |
| **Data Management & Exports** | [http://localhost:3001/data-management](http://localhost:3001/data-management) | Live entity counters, 15-dataset CSV/JSON download catalog. |
| **Interactive API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Complete Swagger UI with interactive OpenAPI endpoints. |

---

## 2. 5–10 Minute Walkthrough Script

### Minute 1–2: System Overview & Executive Dashboard
* **Action**: Open [http://localhost:3001/](http://localhost:3001/).
* **Narrative**:
  > *"InsureFlow is an end-to-end insurance underwriting and policy evaluation engine. Notice the portfolio KPIs at the top: 3,000 baseline applicants, 4,000 quotes, 2,000 active policies, and \$2.8M in written premium across Motor, Home, and Individual Health lines. Everything you see here is generated deterministically using seed `20261022`, ensuring 100% mathematical reproducibility."*
* **Highlight**: Point out the Underwriting Decision distribution (Auto-Approve, Underwriter Review, Senior Underwriter Review, Reject).

### Minute 3–4: Explainable Actuarial Pricing & Underwriting Decision
* **Action**: Click into the **Quote & Underwriting Studio** or inspect a Quote detail modal.
* **Narrative**:
  > *"Unlike black-box insurance software, InsureFlow provides 100% mathematical transparency. When an applicant requests a quote for a 2022 Honda Accord, our actuarial engine applies explicit rating factors: Age tier multiplier, Credit Score tier, Annual Mileage, Prior Claims, and Location rating. Underwriters and regulatory auditors see the exact formula trail: Base Rate × Factor Multipliers = Final Premium."*
* **Highlight**: Show the automated underwriting authority determination. A quote with a low risk score ($<30$) is auto-approved, while higher scores or negative claim history require Senior Underwriter sign-off.

### Minute 5–6: Policy Lifecycle Governance (Issuance, Endorsements, Renewals)
* **Action**: Navigate to the Policies view and inspect a Policy lifecycle event timeline.
* **Narrative**:
  > *"InsureFlow strictly enforces policy state invariants. A quote cannot be bound into a policy without payment acceptance. Mid-term endorsements dynamically calculate premium deltas and record an immutable audit event. Renewals are automatically linked to active parent policies, and the system prohibits renewals on cancelled or lapsed contracts."*

### Minute 7–8: The Anomaly Audit Center (100% Precision & Recall)
* **Action**: Open [http://localhost:3001/anomalies](http://localhost:3001/anomalies).
* **Narrative**:
  > *"Here is the Anomaly Audit Center. We have injected five mandatory negative operational hazards: Issuance without Acceptance, Premium Arithmetic Misalignment, Renewal on Cancelled Policy, Overlapping Coverage Period, and Unexplained Limit Spike. Our independent invariant detection engine audits the entire database and achieves exactly 100% Precision, 100% Recall, and 1.0 F1 score. Crucially, all negative cases are partitioned using `is_baseline = False`, leaving the 2,000 clean baseline issued policies pristine."*

### Minute 9–10: Data Management & 15-Dataset Export Catalog
* **Action**: Open [http://localhost:3001/data-management](http://localhost:3001/data-management).
* **Narrative**:
  > *"Finally, in the Data Management Center, evaluators can monitor exact entity counts, trigger clean deterministic regenerations, and download all 15 relational datasets in both CSV and JSON formats, as well as the full SQL seed script. Furthermore, if an underwriter creates a custom applicant via the UI, our cascading delete rules preserve user records across subsequent regenerations."*

---

## 3. Likely Interviewer Questions & Technical Talking Points

### Q1: *"Why did you use deterministic synthetic data generation rather than an open public dataset?"*
* **Talking Point**: Real insurance policyholder data contains sensitive PII and confidential actuarial rate filings that cannot be published. Public datasets (like Kaggle claims datasets) are static tabular snapshots that lack relational lifecycle linkages (Quotes $\rightarrow$ Policies $\rightarrow$ Endorsements $\rightarrow$ Renewals). By building a synthetic generator with fixed seed `20261022`, we guarantee realistic demographic distributions, complete relational graph integrity, and deterministic reproducibility across any evaluator's laptop.

### Q2: *"How do you guarantee that anomaly detection doesn't overfit to the injected scenarios?"*
* **Talking Point**: The anomaly detection engine does **not** check the `record_source` or `is_baseline` labels during its scan. Instead, it executes independent SQL and relational invariant rules (e.g., verifying interval overlaps on dates, comparing line-item coverage sums against `total_premium`, and checking policy status transitions). The labels are only consulted during the final metric computation stage to benchmark True Positives, False Positives, and False Negatives against known ground truth.

### Q3: *"How does the system ensure user-created records survive synthetic dataset re-generation?"*
* **Talking Point**: Every entity implements a `RecordSourceMixin` with an indexed `record_source` column (`GENERATED`, `USER`, `INJECTED`). When regeneration is triggered, the cleanup logic selectively deletes `record_source != RecordSource.USER`. Furthermore, any generated asset or applicant that is referenced by a surviving user quote is flagged and spared from deletion to preserve foreign key constraints.

### Q4: *"How did you address cross-platform compatibility across Windows, macOS, and Linux?"*
* **Talking Point**: We diagnosed real-world edge cases: host Python version divergence (such as Python 3.8 failing on `pandas>=2.2.1`), Windows named pipe behavior (`dockerDesktopLinuxEngine`), CRLF line-ending corruption, and file-permission shadowing caused by host bind-mounts. We resolved this by establishing single-command Docker Compose as the universal evaluator runtime, baking all application code into multi-architecture container images (`python:3.12-slim`, `node:20-alpine`, `nginx:alpine`, and `postgres:16-alpine`), providing safe defaults so no `.env` copying is needed, and implementing dialect-agnostic column inspections in SQLAlchemy.

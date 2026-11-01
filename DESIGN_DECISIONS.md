# Architectural Design Decisions & Trade-Off Analysis (InsureFlow)

This document records the foundational architectural decisions, actuarial models, engineering trade-offs, and design rationales made during the construction of **InsureFlow**.

---

## 1. Trade-Off Analysis & Key Design Decisions

### Decision 1: Dual-Database Persistence (PostgreSQL + Automatic SQLite Fallback)
* **Context**: External evaluators may run the platform in diverse environments—from high-performance Docker workstations to resource-constrained developer laptops or air-gapped evaluation environments.
* **Decision**: Implement PostgreSQL 16 as the primary production container database in Docker Compose, paired with an automatic, zero-configuration SQLite fallback (`insureflow.db`).
* **Rationale**:
  * PostgreSQL provides strict foreign key enforcement, multi-threaded connection concurrency, and production-grade indexing.
  * SQLite guarantees that the application can run in standalone mode with zero external services installed on the host machine.
  * Connection initialization implements exponential backoff retry logic (up to 10 attempts), falling back to SQLite only if PostgreSQL is genuinely unreachable.

### Decision 2: Container Image Isolation vs. Host Directory Bind-Mounts
* **Context**: Earlier iterations utilized host bind-mounts (`- ./backend:/app/backend`) to support live development reload.
* **Problem**: In cross-platform evaluation (especially Windows WSL2 and macOS), bind-mounting host directories created permission errors, CRLF line-ending mismatches, and shadowed container binaries with empty host folders.
* **Decision**: **Remove host application code bind-mounts**. Container images bake all tested application code inside during the build stage (`COPY backend /app/backend`). Only the output directory (`./data/runtime_exports`) is mounted so evaluators can inspect exported CSVs and JSONs on their host desktop.
* **Benefit**: Guarantees identical execution across Windows, macOS, and Linux, completely immune to host file permissions or line-ending variations.

### Decision 3: Deterministic Data Generation with Fixed Seed (`20261022`)
* **Context**: Regulated insurance systems require reproducible auditing. If data generation is stochastic, test assertions become flaky and audit trails cannot be verified.
* **Decision**: Enforce pseudo-random reproducibility by seeding both Python's `random` module, `Faker`, and NumPy's random generators with fixed seed `20261022`.
* **Verification**: Across all platforms, seed `20261022` produces the exact same cryptographic hashes for export files (e.g., `applicants.csv` SHA-256: `970a6dfdace5571286100bb85d51e6ff36f7081090623ac4c20088f986fbd543`).

### Decision 4: Rule-Based Explainable Actuarial Pricing vs. Black-Box ML
* **Context**: Insurance regulators (e.g., NAIC, state insurance commissioners) require mathematical transparency and actuarial justification for every rating factor.
* **Decision**: Implement an explicit, deterministic factor-based pricing engine rather than a black-box regression or neural network model.
* **Formulas**:
  $$\text{Motor Premium} = \text{Base} \times F_{\text{age}} \times F_{\text{credit}} \times F_{\text{vehicle}} \times F_{\text{mileage}} \times F_{\text{claims}} \times F_{\text{location}}$$
  $$\text{Home Premium} = \text{Base} \times F_{\text{prop\_type}} \times F_{\text{sqft}} \times F_{\text{age}} \times F_{\text{security}} \times F_{\text{credit}} \times F_{\text{location}}$$
  $$\text{Health Premium} = \text{Base} \times F_{\text{age}} \times F_{\text{bmi}} \times F_{\text{smoker}} \times F_{\text{pre\_existing}} \times F_{\text{credit}}$$
* **Benefit**: Every quote response delivers an itemized audit trail detailing the exact multiplier applied for each factor, enabling 100% explainability for underwriters and auditors.

### Decision 5: Ground Truth Partitioning for Anomaly Detection
* **Context**: Requirement 3 mandates generating 2,000 valid issued baseline policies while also injecting 5 negative operational anomaly scenarios for evaluation.
* **Problem**: In naive systems, injecting anomalies corrupts the clean baseline dataset, invalidating baseline portfolio metrics.
* **Decision**: Implement explicit record attribution:
  * Baseline policies: `is_baseline = True`, `record_source = 'GENERATED'`.
  * Negative anomaly records: `is_baseline = False`, `record_source = 'INJECTED'`.
  * User-created UI records: `record_source = 'USER'`.
* **Benefit**: Invariant scans audit the full database without corrupting baseline reporting, enabling independent benchmarking with **100% precision and 100% recall**.

### Decision 6: Cascade Cleanup with User Record Preservation
* **Context**: When an underwriter creates a custom applicant, vehicle, and policy through the UI, and later triggers "Re-generate Dataset" from the Data Management console, their custom records must not be deleted.
* **Decision**: In `generator.py`, the cleanup routine explicitly filters deletion queries by `record_source != RecordSource.USER`. Parent applicants and assets referenced by surviving user quotes or policies are automatically protected from foreign-key cascade deletion.

### Decision 7: Single Universal Docker Compose Evaluation Method (Zero Host Runtimes)
* **Context**: External evaluators run diverse operating systems (Windows 10/11, macOS Intel & Apple Silicon, Linux). Testing demonstrated that standalone host execution frequently breaks due to host environment inconsistencies (e.g. host Python 3.8 failing with `ERROR: No matching distribution found for pandas>=2.2.1`).
* **Decision**: Establish Docker Compose as the **single universal installation method** for all external evaluators.
* **Rationale**:
  * Guarantees identical execution across all platforms by bundling Python 3.12, pandas 2.2+, FastAPI, Node.js 20, React 19, and PostgreSQL 16 directly inside containers.
  * Embedded default environment values (`${VAR:-default}`) eliminate the error-prone `.env` file copying step.
  * Evaluators require only three standard commands (`git clone`, `cd InsureFlow`, `docker compose up --build -d`), with zero host programming languages or databases required.

---

## 2. Five Mandatory Negative Anomaly Scenarios

InsureFlow implements deterministic negative scenario injection and independent invariant detection for five operational hazards:

| Scenario Code | Operational Hazard | Broken Business Invariant | Detection Mechanism |
| :--- | :--- | :--- | :--- |
| **`ISSUANCE_WITHOUT_ACCEPTANCE`** | Policy issued without recorded quote acceptance or payment. | A policy must never transition to `ISSUED` or `ACTIVE` if the originating quote status is `PENDING_REVIEW` or `REJECTED`. | Scans `policies` joined to `quotes`; flags any policy where `quotes.status != 'ACCEPTED'`. |
| **`PREMIUM_ARITHMETIC_MISALIGNMENT`** | Billed policy premium does not match the sum of coverage line items. | The policy's `total_premium` must equal the sum of its associated `policy_coverages.premium` within \$0.05 rounding tolerance. | Sums line-item coverages per policy; flags arithmetic divergence greater than \$0.05. |
| **`RENEWAL_ON_CANCELLED_POLICY`** | Renewal policy generated for a terminated or cancelled policy. | Renewals can only be initiated on policies with status `ACTIVE` or `EXPIRED`, never `CANCELLED` or `LAPSED`. | Cross-references `renewals` against parent policy status; flags renewals pointing to `status = 'CANCELLED'`. |
| **`OVERLAPPING_COVERAGE_PERIOD`** | Two active policies simultaneously insure the exact same vehicle/property asset for the same line of business. | An asset cannot have two concurrent active policy coverage windows with overlapping `[start_date, end_date]` intervals. | Performs interval overlap detection on active policies grouped by `asset_id` and `product_id`. |
| **`UNEXPLAINED_LIMIT_SPIKE`** | Mid-term endorsement spikes coverage limit by >200% without required underwriter review. | Endorsement limit increases exceeding 100% of prior limit mandate senior underwriter approval (`status = 'APPROVED'`). | Evaluates `endorsements` where `(new_coverage_amount - prior_coverage_amount) / prior_coverage_amount > 2.0` with status `APPLIED` without review. |

---

## 3. Assumptions & Limitations

1. **Synthetic Data Realism**: All applicant names, Social Security numbers, vehicle VINs, and addresses are synthetically generated using Faker and NumPy; they do not represent real-world entities.
2. **Currency**: All financial figures are denominated in United States Dollars (\$ USD).
3. **Product Scope**: Motor, Home, and Individual Health lines are fully modeled. Commercial liability and marine cargo are reserved for future architectural expansion.
4. **Payment Gateway**: Simulated deterministically (`PAID`, `PENDING`) within the quote-to-issuance workflow rather than integrating with live banking APIs.

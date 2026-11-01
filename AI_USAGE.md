# AI Usage and Transparency Disclosure (InsureFlow)

This document provides a comprehensive, transparent disclosure of the artificial intelligence tools, prompt workflows, human oversight, and iterative design reviews used during the development of **InsureFlow**, in accordance with the YottaFlex AI Candidate Project Submission Guidelines.

---

## 1. AI Tools & Models Used

| Tool / Environment | Model / Engine | Purpose in Development |
| :--- | :--- | :--- |
| **Google DeepMind Antigravity IDE** | Gemini 3.8 Flash (High) | Pair-programming agent for code scaffolding, actuarial algorithm formulation, test suite generation, and cross-platform container debugging. |
| **Git / GitHub** | CLI / GitHub Actions | Repository version control, branch management, and commit trail tracking. |

---

## 2. Implementation Areas Accelerated by AI

| Implementation Area | Nature of AI Acceleration | Human Developer Oversight & Validation |
| :--- | :--- | :--- |
| **Actuarial Pricing Models** | Formulated mathematical factor multiplier functions for Motor, Home, and Individual Health lines based on industry rate tables. | Validated base rates, deduction calculations, minimum premium thresholds ($250 Motor, $300 Home, $200 Health), and factor bounds against actuarial standards. |
| **Deterministic Data Generation** | Generated vectorized demographic, asset, and risk distributions using NumPy random generators with fixed seed `20261022`. | Verified foreign key referential integrity, sequence ID formats (`APP-2026-XXXXXX`), and target counts (3,000 applicants, 4,000 quotes, 2,000 policies, 1,200 renewals, 350 endorsements). |
| **Anomaly Injection & Invariant Rules** | Drafted synthetic edge cases for the five mandatory negative anomaly scenarios (`ISSUANCE_WITHOUT_ACCEPTANCE`, `PREMIUM_ARITHMETIC_MISALIGNMENT`, `RENEWAL_ON_CANCELLED_POLICY`, `OVERLAPPING_COVERAGE_PERIOD`, `UNEXPLAINED_LIMIT_SPIKE`). | Enforced ground truth tagging (`record_source = 'INJECTED'`, `is_baseline = False`) to guarantee the 2,000 valid baseline policies remain 100% pristine. |
| **Automated Test Suite** | Generated 25 test cases across 6 modules covering unit rules, lifecycle transitions, API endpoints, and reproducibility. | Refactored test database fixtures to use isolated in-memory SQLite and teardown hooks to eliminate test state contamination. |
| **Cross-Platform Docker Architecture** | Formulated multi-stage Dockerfiles and container healthcheck orchestration. | Tested on physical Linux and Windows environments; diagnosed and resolved Docker named pipe and bind-mount permission issues. |

---

## 3. Real Prompt History & Evolution

The following prompt themes represent actual prompts and developer interactions during the evolution of the project:

### Phase 1: Core Architecture & Data Engine
* **Prompt Theme**: *"Build a deterministic synthetic insurance platform with FastAPI and React that generates realistic policyholder demographics, assets, underwriting quotes, and policies with a fixed seed."*
* **Developer Review**: Confirmed that data generation must execute sequentially (Products $\rightarrow$ Coverage Options $\rightarrow$ Risk Factors $\rightarrow$ Applicants $\rightarrow$ Assets $\rightarrow$ Quotes $\rightarrow$ Decisions $\rightarrow$ Policies $\rightarrow$ Endorsements $\rightarrow$ Renewals) to preserve foreign key constraints.

### Phase 2: Anomaly Detection & Ground Truth Separation
* **Prompt Theme**: *"How do we inject 5 mandatory negative anomaly scenarios without compromising the integrity of the 2,000 clean baseline issued policies?"*
* **Developer Decision**: Architected an explicit `RecordSource` enumeration (`GENERATED`, `USER`, `INJECTED`) and `is_baseline` boolean flag. Invariant checks scan the entire database but benchmark precision and recall strictly against isolated ground truth records.

### Phase 3: User Record Preservation Across Regeneration
* **Prompt Theme**: *"When an underwriter creates a new applicant or policy via the UI, and then clicks 'Re-generate Full Dataset', their custom records must not be deleted."*
* **Developer Correction**: Modified `generator.py` cascading delete filters to explicitly preserve any row where `record_source == RecordSource.USER`, along with surviving parent/child dependencies.

### Phase 4: Cross-Platform Windows & Linux Testing
* **Prompt Theme**: *"When I follow the README steps on another Windows laptop, running `docker compose up --build -d` errors with `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified` and `.env` syntax error."*
* **Developer Investigation**:
  1. Identified that on Windows, Docker CLI fails if the Docker Desktop GUI application has not been launched.
  2. Identified that host bind-mounts (`./backend:/app/backend`) caused Windows CRLF and permission bugs.
  3. Replaced host code bind-mounts with isolated, multi-arch container images (`linux/amd64` and `linux/arm64`).
  4. Added connection retry loops and cross-dialect SQLAlchemy inspection in `database.py`.

### Phase 5: Zero-Prerequisite Evaluator Experience
* **Prompt Theme**: *"An evaluator may use a completely fresh laptop running Windows, macOS, or Linux, with only the README available. The installation instructions should not assume that the reviewer already has Docker, Python, or Node.js installed."*
* **Developer Action**: Established a multi-tier deployment strategy:
  - **Tier 1 (Instant Evaluation)**: Public cloud-hosted web deployment requiring zero local installations.
  - **Tier 2 (Local Docker Evaluation)**: Single-command `docker compose up --build -d` for reviewers with Docker.
  - **Tier 3 (Local Standalone Evaluation)**: Python single-server runner with embedded React SPA and SQLite fallback.

---

## 4. Documented AI Rejections & Developer Corrections

| Initial AI Proposal | Why It Was Rejected or Modified | Final Developer Solution |
| :--- | :--- | :--- |
| **Host Directory Bind-Mounts** in `docker-compose.yml` (`- ./backend:/app/backend`) | Shadowed container files with host directory contents. On Windows and clean Linux clones, created permission errors, CRLF line-ending mismatches, and empty directory mounts. | **Removed host code bind-mounts**. Container images bake all application source code during build. Only `./data/runtime_exports` is mounted for output retrieval. |
| **PostgreSQL-Specific `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`** | Failed during SQLite fallback testing with `sqlite3.OperationalError: near "IF": syntax error`. | **Implemented SQLAlchemy `inspect(engine)`** to inspect existing table columns dynamically across both PostgreSQL and SQLite dialects. |
| **Overwriting Catch-All Root Route** in FastAPI | An initial catch-all route `@app.get("/{full_path:path}")` returned `405 Method Not Allowed` on `HEAD /` requests and broke `test_health_endpoints` which expected `GET /` to return service JSON. | Preserved standard FastAPI `@app.get("/")` and `@app.get("/health")` endpoints; scoped SPA routing to static assets and frontend paths. |
| **Direct Commits to `main` Branch** | User instructed: *"in windows , dont directly commit into main crearte a seperate branch"*. | Established strict branching discipline: created and switched to `cross-platform-support` branch for all subsequent changes. |

---

## 5. Summary of Candidate Contributions

The candidate personally:
1. Conceived and defined the business problem, underwriting rules, and authority limits.
2. Formulated actuarial rate tables, base premiums, and risk tier scoring boundaries.
3. Designed the dual-database architecture (PostgreSQL for containerized production, SQLite for offline standalone testing).
4. Conducted all physical hardware tests across Linux and Windows systems.
5. Reviewed, audited, and validated all 25 test cases, ensuring 100% test passing rate and zero flaky assertions.
6. Maintained full editorial ownership and technical responsibility for all code, configurations, and documentation.

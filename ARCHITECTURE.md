# InsureFlow System Architecture & Engineering Design

This document details the architectural blueprints, component interactions, data flows, and technical designs powering **InsureFlow: Enterprise Insurance Underwriting, Policy Evaluation & Anomaly Detection Platform**.

---

## 1. Business Problem & System Objectives

Traditional insurance carriers struggle with operational fragmentation across pricing, underwriting, and policy servicing:
* **Black-Box Actuarial Calculations**: Opaque premium determinations erode customer trust and complicate regulatory rate filing compliance.
* **Inconsistent Underwriting Governance**: Subjective underwriter discretion introduces unmodeled portfolio risk and breaks audit trails.
* **Flawed Policy Lifecycle Transitions**: Coverage active before payment confirmation, renewals issued on cancelled policies, and unmonitored overlapping coverage periods create statutory solvency liabilities.
* **Data Corruption & Undetected Fraud**: Actuarial reserves are distorted when anomalies (e.g., unexplained coverage limit spikes or arithmetic discrepancies) remain undetected.

### System Objectives:
1. **Explainability**: Every premium calculation produces an itemized breakdown of base rates, factor multipliers, and discount/surcharge trails.
2. **Determinism**: The entire dataset is reproducibly generated using fixed pseudo-random seed `20261022`.
3. **Rigorous Invariant Enforcement**: Anomaly detection audits five mandatory operational hazards with 100% precision and recall.
4. **Data Isolation**: Synthetically injected negative cases are strictly tagged and separated from pristine baseline issued policies.
5. **Zero-Friction Accessibility**: The platform deploys seamlessly via Docker Compose, standalone Python/SQLite, or public cloud hosting.

---

## 2. High-Level System Architecture Diagram

```mermaid
graph TB
    subgraph Client Layer
        Browser["Web Browser / Client (Chrome, Edge, Safari, Firefox)"]
    end

    subgraph Presentation & Ingress Layer
        Nginx["Nginx Reverse Proxy (:3001 / :80)<br/>• SPA Static Hosting<br/>• API Reverse Proxy (/api/)<br/>• Swagger Proxy (/docs)"]
        ReactApp["React 19 + TypeScript SPA<br/>• Executive Dashboard<br/>• Quote & Underwriting Studio<br/>• Anomaly Audit Center<br/>• Data Management & Exports"]
    end

    subgraph Application & Business Logic Layer
        FastAPI["FastAPI Application (:8000)<br/>• OpenAPI / Swagger Docs<br/>• REST API Routers<br/>• Health Probes (/health)"]
        PricingEngine["Actuarial Pricing Engine<br/>• Motor, Home, Health Models<br/>• Transparent Factor Trails"]
        UWEngine["Underwriting Decision Engine<br/>• Rules & Eligibility Checks<br/>• Multi-tier Authority Bounds"]
        DataGen["Synthetic Generator Engine<br/>• Seed 20261022 Determinism<br/>• 3,000 Applicants / 2,000 Policies<br/>• User Record Protection"]
        AnomalyEngine["Anomaly Detection & Invariant Engine<br/>• 5 Hazard Detectors<br/>• Ground Truth Benchmarking"]
        ExportEngine["Runtime Exporter<br/>• 15 Datasets (CSV & JSON)<br/>• seed_data.sql Generator"]
    end

    subgraph Data & Persistence Layer
        PostgreSQL[("PostgreSQL 16 Alpine (:5432)<br/>• Primary Container Database<br/>• ACID Compliant Relational Schema<br/>• Named Volume: insureflow_postgres_data")]
        SQLite[("SQLite 3 Fallback (insureflow.db)<br/>• Offline / Standalone Fallback<br/>• Zero-Docker Portability")]
    end

    Browser -->|HTTP :3001| Nginx
    Browser -->|HTTP :8000| FastAPI
    Nginx -->|Serves Static Dist| ReactApp
    Nginx -->|Reverse Proxy /api/| FastAPI
    FastAPI --> PricingEngine
    FastAPI --> UWEngine
    FastAPI --> DataGen
    FastAPI --> AnomalyEngine
    FastAPI --> ExportEngine
    DataGen --> PostgreSQL
    DataGen --> SQLite
    FastAPI -->|SQLAlchemy 2.0 ORM| PostgreSQL
    FastAPI -.->|Automatic Fallback| SQLite
```

---

## 3. Core Component Descriptions

### 3.1 Presentation Layer (Frontend)
* **Framework**: React 19, TypeScript, Vite, Tailwind CSS.
* **State & Networking**: Native React Hooks with Axios API clients targeting relative `/api/` endpoints (proxied by Nginx in Docker or served directly by FastAPI in standalone mode).
* **Key Modules**:
  * `DashboardPage.tsx`: Key performance indicators (Total Applicants, Active Policies, Written Premium, Loss Ratios, Underwriting Approval Distribution).
  * `QuoteUnderwritingPage.tsx`: Interactive applicant quote evaluation, real-time risk score calculation, factor transparency breakdown, and one-click policy issuance.
  * `AnomalyCenterPage.tsx`: Independent evaluation matrix displaying True Positives, False Positives, False Negatives, Precision (100%), Recall (100%), and interactive drill-down.
  * `DataManagementPage.tsx`: Live entity count monitor, clean dataset re-generation trigger, and 15-dataset export downloader.

### 3.2 Application Layer (FastAPI Backend)
* **Framework**: FastAPI (Python 3.12) running under Uvicorn ASGI server.
* **Database Abstraction**: SQLAlchemy 2.0 Declarative ORM with connection pooling (`pool_pre_ping=True`) and exponential retry logic on startup.
* **Modular Routing Structure**:
  * `/api/dashboard`: Summary counts, line-of-business distributions, approval ratios.
  * `/api/applicants`: Applicant demographic CRUD, asset association, risk factor mappings.
  * `/api/products`: Master catalog of insurance lines and coverage options.
  * `/api/quotes`: Pricing calculations, underwriting authority evaluations, quote conversions.
  * `/api/policies`: Policy lifecycle management (active, endorsement, cancellation, renewal).
  * `/api/anomalies`: Invariant evaluation metrics, ground truth comparisons, detected anomalies list.
  * `/api/exports`: Download endpoints for all 15 relational datasets in CSV/JSON and SQL seed script.

### 3.3 Persistence Layer
* **PostgreSQL 16 (Containerized Production)**: Default database utilized by Docker Compose. Managed with healthcheck probes (`pg_isready`) and named volume persistence (`insureflow_postgres_data`).
* **SQLite 3 Fallback (`insureflow.db`)**: Activated automatically if PostgreSQL is unreachable or during standalone local execution, providing complete zero-configuration operational capability.

---

## 4. End-to-End Entity Relationship Diagram

```mermaid
erDiagram
    PRODUCTS ||--|{ COVERAGE_OPTIONS : offers
    PRODUCTS ||--|{ QUOTES : prices
    APPLICANTS ||--|{ INSURED_ASSETS : owns
    APPLICANTS ||--|{ APPLICANT_RISK_FACTORS : has
    APPLICANTS ||--|{ QUOTES : requests
    INSURED_ASSETS ||--|{ ASSET_RISK_FACTORS : carries
    INSURED_ASSETS ||--|{ QUOTES : covers
    QUOTES ||--|{ QUOTE_COVERAGES : includes
    QUOTES ||--|| UNDERWRITING_DECISIONS : triggers
    QUOTES ||--o| POLICIES : binds_into
    POLICIES ||--|{ POLICY_COVERAGES : specifies
    POLICIES ||--|{ POLICY_EVENTS : records
    POLICIES ||--|{ ENDORSEMENTS : modifies
    POLICIES ||--|{ RENEWALS : extends
    POLICIES ||--o| ANOMALY_RECORDS : flags

    PRODUCTS {
        int id PK
        string code UK
        string name
        string line_of_business
        numeric base_premium
    }

    COVERAGE_OPTIONS {
        int id PK
        int product_id FK
        string code
        string name
        numeric default_limit
        numeric default_deductible
    }

    APPLICANTS {
        int id PK
        string business_id UK
        string first_name
        string last_name
        string email UK
        int age
        numeric annual_income
        int credit_score
        string record_source
    }

    INSURED_ASSETS {
        int id PK
        string business_id UK
        int applicant_id FK
        string asset_type
        numeric declared_value
        string risk_tier
        string record_source
    }

    QUOTES {
        int id PK
        string business_id UK
        int applicant_id FK
        int asset_id FK
        int product_id FK
        numeric base_premium
        numeric final_premium
        string status
        string record_source
    }

    UNDERWRITING_DECISIONS {
        int id PK
        string business_id UK
        int quote_id FK
        string decision
        numeric risk_score
        string required_authority
        string record_source
    }

    POLICIES {
        int id PK
        string business_id UK
        int quote_id FK
        int asset_id FK
        date start_date
        date end_date
        numeric total_premium
        string status
        boolean is_baseline
        string record_source
    }

    ENDORSEMENTS {
        int id PK
        string business_id UK
        int policy_id FK
        string endorsement_type
        numeric prior_premium
        numeric new_premium
        numeric premium_delta
        string record_source
    }

    RENEWALS {
        int id PK
        string business_id UK
        int policy_id FK
        date renewal_effective_date
        numeric proposed_premium
        string status
        string record_source
    }

    ANOMALY_RECORDS {
        int id PK
        string anomaly_id UK
        string anomaly_type
        string entity_type
        int entity_id
        string severity
        string invariant_broken
        string record_source
    }
```

---

## 5. Security & Isolation Model

1. **Non-Root Execution**: Container processes run securely within their respective runtime environments.
2. **Network Isolation**: Docker Compose provisions a dedicated bridge network (`insureflow-network`). The database port (5432) is isolated within the internal network and only accessed by the backend service.
3. **Ground Truth Separation**: Injected negative testing scenarios are strictly partitioned using `is_baseline = False` and `record_source = 'INJECTED'`, preventing contamination of the 2,000 clean baseline policies.
4. **User Data Protection**: All entities implement `RecordSourceMixin`. When automated regeneration is executed, a cascade protection filter preserves all rows marked `RecordSource.USER`.

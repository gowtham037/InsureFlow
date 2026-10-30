# InsureFlow Synthetic Data Generation Methodology

This document details the generation architecture, random seed determinism, realistic demographic distributions, generation sequence, and export mechanisms of the **InsureFlow Synthetic Data Generator**.

---

## 1. Generation Architecture & Determinism

The InsureFlow generator utilizes a fixed pseudo-random seed:
$$\mathbf{Seed = 20261022}$$

By fixing the seed across Python's `random`, `numpy.random`, and `faker.Faker`, the engine produces identical synthetic insurance populations, actuarial factors, and tabular outputs on any compatible operating system.

### Verification of Reproducibility
Running the generator twice with the specified seed yields identical row counts, field values, and cryptographic hashes:
- `applicants.csv`: `5616b741c55ec0b9126c1314e0b1d2858e1ef4ff4f75ad3a4372592e9309014b`
- `quotes.csv`: `8a630d3433b65e316f96c9d57b8e60dfc6d317cf50a5380fc37c6490dda32d13`
- `policies.csv`: `398ab820f40639eae4a4503569488fe36bc743b9f6e29ccaa027ea0153ae2e86`

---

## 2. Dataset Targets & Scale Modes

| Metric | Starter Mode (`--mode starter`) | Full Mode (`--mode full`) | Description |
| :--- | :--- | :--- | :--- |
| **Applicants** | 300 | 3,000 | Primary policyholders |
| **Insured Assets** | ~400 | 4,000 | Vehicles, properties, health profiles |
| **Insurance Quotes** | 400 | 4,000 | Submissions with actuarial factor breakdown |
| **Underwriting Decisions** | 400 | 4,000 | Adjudication decisions (1-to-1 with quotes) |
| **Issued Policies** | 200 | 2,000 | Active binding legal contracts |
| **Endorsements** | 50 | 350 | Mid-term amendments |
| **Renewals** | 120 | 1,200 | Expiration renewal offer cycles |
| **Products** | 3 | 3 | Motor, Home, Health |
| **Negative Anomalies** | 5 | 5 | Injected domain invariant tests |

---

## 3. Strict Generation Order (Parent before Dependent)

To guarantee zero foreign key errors and preserve referential integrity, records are generated in a strict topographical dependency order:

1. **`Product`**: Master lines of business (Motor, Home, Health) with regulatory bounds.
2. **`CoverageOption`**: Core, optional, and rider add-on definitions linked to products.
3. **`RiskFactor`**: Actuarial risk classification vectors (age, location, health, behavior).
4. **`Applicant`**: Demographic profiles, credit scores, historical claims.
5. **`InsuredAsset`**: Linked to applicants (1 to 2 assets per applicant).
6. **`Quote`**: Product + Applicant + Asset combined through the business rule engine.
7. **`UnderwritingDecision`**: Created for every quote, determining approval authority.
8. **`Policy`**: Created strictly from accepted, approved, paid quotes.
9. **`Endorsement`**: Applied to active policies with product ceiling validation.
10. **`Renewal`**: Generated for active or expiring policies (never cancelled policies).

---

## 4. Realistic Demographic & Actuarial Distributions

- **Applicant Ages**: Modeled via a clipped Gaussian distribution centered at age 42 ($\mu = 42, \sigma = 14$), bounded between 19 and 82 years old.
- **Credit Scores**: Modeled via Gaussian distribution centered at 690 ($\mu = 690, \sigma = 70$), bounded between 500 and 840 (FICO standard).
- **Claims History (5-Year)**:
  - 0 claims: 65% of applicants
  - 1 claim: 22% of applicants
  - 2 claims: 9% of applicants
  - 3+ claims: 4% of applicants
- **Location Tiers**:
  - `TIER_1` (Metro traffic & dense risk): 35%
  - `TIER_2` (Suburban standard): 40%
  - `TIER_3` (Rural / low density): 20%
  - `HIGH_RISK_ZONE` (Coastal flood, wildfire zone): 5%
- **Asset Valuations**:
  - Motor Vehicles: $\mu = \$32,000, \sigma = \$15,000$ (bounded $\$6,000$ to $\$110,000$)
  - Residential Real Estate: $\mu = \$450,000, \sigma = \$200,000$ (bounded $\$120,000$ to $\$2,200,000$)
  - Health Benefit Limits: Standard tiers $\$100,000$, $\$250,000$, $\$500,000$.

---

## 5. Execution Commands

### Run Starter Mode:
```bash
python -m app.data_generator --mode starter --seed 20261022
```

### Run Full Scale Mode:
```bash
python -m app.data_generator --mode full --seed 20261022
```
Outputs are automatically committed to the database and exported to `data/exports/` in CSV and JSON formats.

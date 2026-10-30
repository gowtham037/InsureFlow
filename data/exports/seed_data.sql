-- InsureFlow Relational Seed Data Script
-- Deterministically generated from active database records

BEGIN TRANSACTION;

INSERT INTO products (product_code, name, line_of_business, description, base_premium, min_coverage_limit, max_coverage_limit, min_applicant_age, max_applicant_age, is_active) VALUES ('PRD-MOTOR-001', 'AutoShield Comprehensive Motor Policy', 'MOTOR', 'Comprehensive automobile coverage covering collision, theft, third-party liability, and roadside assistance.', 500.0, 10000.0, 250000.0, 18, 85, True) ON CONFLICT (product_code) DO NOTHING;
INSERT INTO products (product_code, name, line_of_business, description, base_premium, min_coverage_limit, max_coverage_limit, min_applicant_age, max_applicant_age, is_active) VALUES ('PRD-HOME-001', 'HomeSafe Premier Homeowner Protection', 'HOME', 'All-risk residential structural and personal property coverage against fire, natural calamities, theft, and liability.', 750.0, 100000.0, 3000000.0, 18, 99, True) ON CONFLICT (product_code) DO NOTHING;
INSERT INTO products (product_code, name, line_of_business, description, base_premium, min_coverage_limit, max_coverage_limit, min_applicant_age, max_applicant_age, is_active) VALUES ('PRD-HEALTH-001', 'VitalCare Prime Individual Health', 'HEALTH', 'Full hospitalization, in-patient, out-patient, prescription drug, and critical illness medical benefit cover.', 1200.0, 50000.0, 1000000.0, 18, 75, True) ON CONFLICT (product_code) DO NOTHING;

COMMIT;

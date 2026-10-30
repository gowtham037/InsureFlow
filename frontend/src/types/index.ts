export interface InsuredAsset {
  id: number;
  business_id: string;
  applicant_id: number;
  asset_type: string;
  identifier: string;
  asset_value: number;
  year_built_or_manufactured: number;
  make_model: string;
  location_tier: string;
  details?: Record<string, any>;
  created_at: string;
}

export interface Applicant {
  id: number;
  business_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  age: number;
  gender: string;
  address_line: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  annual_income: number;
  credit_score: number;
  occupation: string;
  employment_status: string;
  claims_count_5yr: number;
  created_at: string;
  assets?: InsuredAsset[];
}

export interface CoverageOption {
  id: number;
  code: string;
  name: string;
  description?: string;
  coverage_category: string;
  default_limit: number;
  min_limit: number;
  max_limit: number;
  premium_multiplier: number;
  deductible_options?: number[];
}

export interface Product {
  id: number;
  product_code: string;
  name: string;
  line_of_business: 'MOTOR' | 'HOME' | 'HEALTH';
  description: string;
  min_coverage_limit: number;
  max_coverage_limit: number;
  min_applicant_age: number;
  max_applicant_age: number;
  base_premium: number;
  is_active: boolean;
  created_at: string;
  coverage_options: CoverageOption[];
}

export interface Quote {
  id: number;
  business_id: string;
  applicant_id: number;
  asset_id: number;
  product_id: number;
  coverage_amount: number;
  deductible: number;
  status: string;
  risk_score: number;
  risk_tier: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  base_premium: number;
  calculated_factors?: Record<string, any>;
  final_premium: number;
  eligibility_passed: boolean;
  eligibility_reasons?: string[];
  pricing_explanation?: string;
  customer_accepted: boolean;
  customer_accepted_at?: string;
  created_at: string;
  expires_at: string;
}

export interface UnderwritingDecision {
  id: number;
  business_id: string;
  quote_id: number;
  decision: 'APPROVED' | 'APPROVED_WITH_CONDITIONS' | 'REFERRED' | 'DECLINED';
  authority_level: string;
  decision_reason: string;
  conditions?: string[];
  rule_identifiers?: string[];
  reviewer_name: string;
  reviewed_at: string;
  is_override: boolean;
  override_reason?: string;
}

export interface PolicyEvent {
  id: number;
  event_type: string;
  event_description: string;
  actor: string;
  metadata_json?: any;
  created_at: string;
}

export interface Policy {
  id: number;
  business_id: string;
  quote_id: number;
  applicant_id: number;
  asset_id: number;
  product_id: number;
  status: 'ISSUED' | 'ACTIVE' | 'SUSPENDED' | 'CANCELLED' | 'EXPIRED';
  coverage_amount: number;
  deductible: number;
  annual_premium: number;
  payment_status: 'PAID' | 'PENDING' | 'FAILED' | 'REFUNDED';
  customer_accepted: boolean;
  effective_date: string;
  expiration_date: string;
  cancellation_date?: string;
  cancellation_reason?: string;
  created_at: string;
  events?: PolicyEvent[];
}

export interface Endorsement {
  id: number;
  business_id: string;
  policy_id: number;
  endorsement_sequence: number;
  endorsement_type: string;
  effective_date: string;
  prior_coverage_amount: number;
  new_coverage_amount: number;
  prior_premium: number;
  new_premium: number;
  premium_delta: number;
  status: string;
  reason: string;
  created_at: string;
}

export interface Renewal {
  id: number;
  business_id: string;
  previous_policy_id: number;
  new_policy_id?: number;
  renewal_cycle_year: number;
  status: 'OFFERED' | 'ACCEPTED' | 'DECLINED' | 'EXPIRED';
  prior_premium: number;
  renewal_premium: number;
  premium_change_percent: number;
  effective_date: string;
  expiration_date: string;
  decision_reason?: string;
  created_at: string;
}

export interface Anomaly {
  id: number;
  business_id: string;
  entity_type: string;
  entity_id: string;
  issue_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  expected_outcome: string;
  actual_detected_outcome: string;
  is_detected: boolean;
  ground_truth_label: boolean;
  detection_rule: string;
  detection_explanation: string;
  detected_at: string;
}

export interface DashboardSummary {
  total_applicants: number;
  total_quotes: number;
  issued_policies: number;
  active_policies: number;
  pending_underwriting_reviews: number;
  renewals: number;
  total_anomalies: number;
  approval_rate: number;
  rejection_rate: number;
  referral_rate: number;
}

export interface DashboardMetrics {
  total_quotes_evaluated: number;
  approval_rate: number;
  decline_rate: number;
  referral_rate: number;
  total_policies_issued: number;
  renewal_acceptance_rate: number;
  cancellation_rate: number;
  average_premium: number;
  average_risk_score: number;
  total_anomalies: number;
  true_positives: number;
  false_positives: number;
  false_negatives: number;
  precision: number;
  recall: number;
  f1_score: number;
  dataset_validation_pass_rate: number;
}

export interface ProductDistributionItem {
  product_code: string;
  product_name: string;
  line_of_business: string;
  policy_count: number;
  quote_count: number;
  total_premium: number;
}

export interface RiskDistributionItem {
  risk_tier: string;
  quote_count: number;
  policy_count: number;
  average_score: number;
}

export interface ValidationReport {
  total_records_evaluated: number;
  total_rules_checked: number;
  passed_validations: number;
  failed_validations: number;
  validation_pass_rate_pct: number;
  foreign_key_errors_count: number;
  foreign_key_errors: string[];
  duplicate_records_count: number;
  duplicate_records: string[];
  arithmetic_errors_count: number;
  arithmetic_errors: string[];
  lifecycle_errors_count: number;
  lifecycle_errors: string[];
  constraint_errors_count: number;
  constraint_errors: string[];
  anomalies_detected_count: number;
  status: string;
}

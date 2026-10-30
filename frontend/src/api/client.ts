import axios from 'axios';
import {
  Applicant,
  Product,
  Quote,
  Policy,
  Endorsement,
  Renewal,
  Anomaly,
  DashboardSummary,
  DashboardMetrics,
  ProductDistributionItem,
  RiskDistributionItem,
  ValidationReport
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiClient = {
  // Dashboard
  getDashboardSummary: () => api.get<DashboardSummary>('/dashboard/summary').then(res => res.data),
  getDashboardMetrics: () => api.get<DashboardMetrics>('/dashboard/metrics').then(res => res.data),
  getProductDistribution: () => api.get<ProductDistributionItem[]>('/dashboard/product-distribution').then(res => res.data),
  getRiskDistribution: () => api.get<RiskDistributionItem[]>('/dashboard/risk-distribution').then(res => res.data),
  getLifecycleDistribution: () => api.get<{ status: string; count: number }[]>('/dashboard/policy-lifecycle').then(res => res.data),
  getRenewalOutcomes: () => api.get<{ status: string; count: number }[]>('/dashboard/renewal-outcomes').then(res => res.data),

  // Applicants
  getApplicants: (page = 1, pageSize = 20, search = '') =>
    api.get<{ total: number; page: number; page_size: number; items: Applicant[] }>(
      `/applicants?page=${page}&page_size=${pageSize}${search ? `&search=${encodeURIComponent(search)}` : ''}`
    ).then(res => res.data),
  getApplicant: (id: number) => api.get<Applicant>(`/applicants/${id}`).then(res => res.data),
  createApplicant: (data: Partial<Applicant>) => api.post<Applicant>('/applicants', data).then(res => res.data),

  // Products
  getProducts: () => api.get<Product[]>('/products').then(res => res.data),
  getProduct: (id: number) => api.get<Product>(`/products/${id}`).then(res => res.data),

  // Quotes
  getQuotes: (page = 1, pageSize = 20, status?: string, riskTier?: string, search?: string) => {
    let url = `/quotes?page=${page}&page_size=${pageSize}`;
    if (status) url += `&status=${status}`;
    if (riskTier) url += `&risk_tier=${riskTier}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return api.get<{ total: number; page: number; page_size: number; items: Quote[] }>(url).then(res => res.data);
  },
  getQuote: (id: number) => api.get<Quote>(`/quotes/${id}`).then(res => res.data),
  createQuote: (data: { applicant_id: number; asset_id: number; product_id: number; coverage_amount: number; deductible: number }) =>
    api.post<Quote>('/quotes', data).then(res => res.data),
  evaluateQuote: (id: number) => api.post<Quote>(`/quotes/${id}/evaluate`).then(res => res.data),
  acceptQuote: (id: number) => api.post<Quote>(`/quotes/${id}/accept`).then(res => res.data),

  // Underwriting
  getDecisions: (limit = 50) => api.get<any[]>(`/underwriting/decisions?limit=${limit}`).then(res => res.data),
  getReferrals: () => api.get<any[]>('/underwriting/referrals').then(res => res.data),
  reviewDecision: (id: number, data: { decision: string; reviewer_name: string; override_reason?: string; conditions?: string[] }) =>
    api.post<any>(`/underwriting/${id}/review`, data).then(res => res.data),

  // Policies
  getPolicies: (page = 1, pageSize = 20, status?: string, search?: string) => {
    let url = `/policies?page=${page}&page_size=${pageSize}`;
    if (status) url += `&status=${status}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return api.get<{ total: number; page: number; page_size: number; items: Policy[] }>(url).then(res => res.data);
  },
  getPolicy: (id: number) => api.get<Policy>(`/policies/${id}`).then(res => res.data),
  issuePolicy: (quoteId: number, paymentStatus = 'PAID') =>
    api.post<Policy>(`/policies/${quoteId}/issue`, { payment_status: paymentStatus }).then(res => res.data),
  cancelPolicy: (id: number, cancellationReason: string) =>
    api.post<Policy>(`/policies/${id}/cancel`, { cancellation_reason: cancellationReason }).then(res => res.data),

  // Endorsements
  getEndorsements: (limit = 50) => api.get<Endorsement[]>(`/endorsements?limit=${limit}`).then(res => res.data),
  createEndorsement: (data: { policy_id: number; endorsement_type: string; new_coverage_amount: number; effective_date: string; reason: string }) =>
    api.post<Endorsement>('/endorsements', data).then(res => res.data),

  // Renewals
  getRenewals: (limit = 50, status?: string) =>
    api.get<Renewal[]>(`/renewals?limit=${limit}${status ? `&status=${status}` : ''}`).then(res => res.data),
  generateRenewal: (policyId: number) =>
    api.post<Renewal>('/renewals/generate', { policy_id: policyId }).then(res => res.data),
  actOnRenewal: (id: number, action: 'ACCEPT' | 'DECLINE') =>
    api.post<Renewal>(`/renewals/${id}/action?action=${action}`).then(res => res.data),

  // Anomalies
  getAnomalies: (severity?: string, issueType?: string) => {
    let url = '/anomalies?';
    if (severity) url += `severity=${severity}&`;
    if (issueType) url += `issue_type=${issueType}&`;
    return api.get<Anomaly[]>(url).then(res => res.data);
  },
  getAnomalySummary: () => api.get<any>('/anomalies/summary').then(res => res.data),
  getAnomaly: (id: number) => api.get<Anomaly>(`/anomalies/${id}`).then(res => res.data),
  detectAnomalies: () => api.post<Anomaly[]>('/anomalies/detect').then(res => res.data),

  // Admin & Data Management
  getGenerationStatus: () => api.get<Record<string, number>>('/admin/generation-status').then(res => res.data),
  generateDataset: (mode: 'starter' | 'full' = 'starter', seed = 20261022) =>
    api.post<any>('/admin/generate-dataset', { mode, seed }).then(res => res.data),
  validateDataset: () => api.post<ValidationReport>('/admin/validate-dataset').then(res => res.data),
  getReproducibilityCheck: () => api.get<any>('/admin/reproducibility-check').then(res => res.data),

  // Exports URLs & Catalog
  getExportsList: () => api.get<any>('/exports').then(res => res.data),
  getExportUrl: (datasetName: string, format: 'csv' | 'json' = 'csv') => `${API_BASE_URL}/exports/${datasetName}?format=${format}`,
  exportApplicantsUrl: `${API_BASE_URL}/exports/applicants?format=csv`,
  exportQuotesUrl: `${API_BASE_URL}/exports/quotes?format=csv`,
  exportPoliciesUrl: `${API_BASE_URL}/exports/policies?format=csv`,
  exportGroundTruthUrl: `${API_BASE_URL}/exports/ground_truth?format=csv`,
  exportSqlSeedUrl: `${API_BASE_URL}/exports/sql-seed`,
};

export default api;

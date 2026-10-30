import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import {
  DashboardSummary,
  DashboardMetrics,
  ProductDistributionItem,
  RiskDistributionItem
} from '../types';
import {
  Users,
  FileSpreadsheet,
  ShieldCheck,
  Activity,
  AlertTriangle,
  RotateCw,
  TrendingUp,
  Percent,
  CheckCircle2,
  XCircle,
  Clock
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

const RISK_COLORS: Record<string, string> = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f97316',
  CRITICAL: '#ef4444'
};

const LIFECYCLE_COLORS: Record<string, string> = {
  ISSUED: '#38bdf8',
  ACTIVE: '#10b981',
  CANCELLED: '#f43f5e',
  EXPIRED: '#94a3b8'
};

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [productDist, setProductDist] = useState<ProductDistributionItem[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistributionItem[]>([]);
  const [lifecycleDist, setLifecycleDist] = useState<{ status: string; count: number }[]>([]);
  const [renewalDist, setRenewalDist] = useState<{ status: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [sum, met, prod, risk, life, ren] = await Promise.all([
        apiClient.getDashboardSummary(),
        apiClient.getDashboardMetrics(),
        apiClient.getProductDistribution(),
        apiClient.getRiskDistribution(),
        apiClient.getLifecycleDistribution(),
        apiClient.getRenewalOutcomes(),
      ]);
      setSummary(sum);
      setMetrics(met);
      setProductDist(prod);
      setRiskDist(risk);
      setLifecycleDist(life);
      setRenewalDist(ren);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Operations Dashboard" subtitle="Enterprise Insurance Underwriting & Policy Telemetry" />
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="flex flex-col items-center gap-3">
            <Activity className="w-8 h-8 text-brand-600 animate-spin" />
            <p className="text-sm font-medium text-slate-500">Loading system metrics and telemetry...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Operations Dashboard"
        subtitle="Real-time Underwriting Intelligence, Portfolio Health & Integrity Metrics"
        onRefresh={handleRefresh}
        isRefreshing={refreshing}
      />

      <div className="p-8 space-y-8">
        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Applicants</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.total_applicants.toLocaleString()}</h3>
              <p className="text-xs text-slate-500 mt-1">Insured individuals & assets</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Users className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Evaluated Quotes</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.total_quotes.toLocaleString()}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs font-semibold text-emerald-600">{summary?.approval_rate}% Approved</span>
              </div>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Policies</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.active_policies.toLocaleString()}</h3>
              <p className="text-xs text-slate-500 mt-1">{summary?.issued_policies} Total Issued</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Detected Anomalies</p>
              <h3 className="text-2xl font-bold text-rose-600 mt-1">{summary?.total_anomalies}</h3>
              <p className="text-xs text-slate-500 mt-1">
                F1 Score: <span className="font-semibold text-slate-800">{(metrics?.f1_score ?? 1) * 100}%</span>
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Secondary KPI Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs text-center">
          <div className="p-2 border-r border-slate-100 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Approval Rate</span>
            <span className="text-base font-bold text-emerald-600">{metrics?.approval_rate}%</span>
          </div>
          <div className="p-2 border-r border-slate-100 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Decline Rate</span>
            <span className="text-base font-bold text-rose-600">{metrics?.decline_rate}%</span>
          </div>
          <div className="p-2 border-r border-slate-100 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Referral Rate</span>
            <span className="text-base font-bold text-amber-600">{metrics?.referral_rate}%</span>
          </div>
          <div className="p-2 border-r border-slate-100 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Renewal Acceptance</span>
            <span className="text-base font-bold text-brand-600">{metrics?.renewal_acceptance_rate}%</span>
          </div>
          <div className="p-2 border-r border-slate-100 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Average Premium</span>
            <span className="text-base font-bold text-slate-900">${metrics?.average_premium?.toLocaleString()}</span>
          </div>
          <div className="p-2 last:border-none">
            <span className="text-xs font-medium text-slate-500 block">Validation Pass Rate</span>
            <span className="text-base font-bold text-emerald-600">{metrics?.dataset_validation_pass_rate}%</span>
          </div>
        </div>

        {/* Charts Row 1: Product Distribution & Risk Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Product Portfolio Breakdown</h3>
                <p className="text-xs text-slate-500">Active policies and cumulative premium per line of business</p>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={productDist} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="line_of_business" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(val: any) => [`${val}`, 'Policies']}
                  />
                  <Bar dataKey="policy_count" name="Policies" fill="#026bc9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Risk Profile Distribution</h3>
                <p className="text-xs text-slate-500">Actuarial risk scoring categorization (LOW, MED, HIGH, CRIT)</p>
              </div>
            </div>
            <div className="h-64 flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskDist}
                    dataKey="quote_count"
                    nameKey="risk_tier"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={45}
                    paddingAngle={3}
                  >
                    {riskDist.map((entry) => (
                      <Cell key={entry.risk_tier} fill={RISK_COLORS[entry.risk_tier] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                    formatter={(val: any, name: any) => [`${val} quotes`, name]}
                  />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Charts Row 2: Policy Lifecycle & Renewal Outcomes */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Policy Lifecycle Statuses</h3>
                <p className="text-xs text-slate-500">Distribution of policies across formal operational states</p>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={lifecycleDist} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="status" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                    formatter={(val: any) => [`${val}`, 'Policies']}
                  />
                  <Bar dataKey="count" name="Count" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200/80 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Renewal Cycle Outcomes</h3>
                <p className="text-xs text-slate-500">Policy renewal offer acceptance, pending and declination rates</p>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={renewalDist} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="status" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                    formatter={(val: any) => [`${val}`, 'Renewals']}
                  />
                  <Bar dataKey="count" name="Renewals" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

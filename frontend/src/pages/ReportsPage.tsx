import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { DashboardMetrics, ProductDistributionItem, RiskDistributionItem } from '../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend
} from 'recharts';
import {
  BarChart3,
  TrendingUp,
  ShieldAlert,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Layers,
  Activity
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [productDist, setProductDist] = useState<ProductDistributionItem[]>([]);
  const [riskDist, setRiskDist] = useState<RiskDistributionItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [m, p, r] = await Promise.all([
          apiClient.getDashboardMetrics(),
          apiClient.getProductDistribution(),
          apiClient.getRiskDistribution()
        ]);
        setMetrics(m);
        setProductDist(p);
        setRiskDist(r);
      } catch (err) {
        console.error('Failed to load reports data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Actuarial & Underwriting Reports"
        subtitle="Comprehensive operational reports, portfolio pricing distribution and data quality audit scorecards"
      />

      <div className="p-8 space-y-8">
        {/* Underwriting Performance Scorecard */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-brand-600" />
            Underwriting Authority & Decision Breakdown
          </h3>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="p-4 bg-slate-50 rounded-lg text-center">
              <span className="text-xs text-slate-500 font-medium block">Total Evaluated</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{metrics?.total_quotes_evaluated?.toLocaleString()}</span>
            </div>
            <div className="p-4 bg-emerald-50 rounded-lg text-center border border-emerald-100">
              <span className="text-xs text-emerald-700 font-medium block">Approval Rate</span>
              <span className="text-xl font-bold text-emerald-700 mt-1 block">{metrics?.approval_rate}%</span>
            </div>
            <div className="p-4 bg-rose-50 rounded-lg text-center border border-rose-100">
              <span className="text-xs text-rose-700 font-medium block">Decline Rate</span>
              <span className="text-xl font-bold text-rose-700 mt-1 block">{metrics?.decline_rate}%</span>
            </div>
            <div className="p-4 bg-amber-50 rounded-lg text-center border border-amber-100">
              <span className="text-xs text-amber-700 font-medium block">Referral Rate</span>
              <span className="text-xl font-bold text-amber-700 mt-1 block">{metrics?.referral_rate}%</span>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={riskDist} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="risk_tier" stroke="#64748b" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={12} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }}
                  formatter={(val: any, name: any) => [`${val}`, name === 'quote_count' ? 'Quotes' : 'Policies']}
                />
                <Legend verticalAlign="top" height={36} />
                <Bar dataKey="quote_count" name="Evaluated Quotes" fill="#026bc9" radius={[4, 4, 0, 0]} />
                <Bar dataKey="policy_count" name="Issued Policies" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Anomaly Detection Matrix */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-2 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-600" />
            Anomaly Detection Confusion Matrix & Quality Scorecard
          </h3>
          <p className="text-xs text-slate-500 mb-6">
            Evaluates independent anomaly rule detections against strictly isolated synthetic ground truth labels
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 text-center">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-xs text-slate-500 block">True Positives</span>
              <span className="text-lg font-bold text-emerald-600 mt-1 block">{metrics?.true_positives}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-xs text-slate-500 block">False Positives</span>
              <span className="text-lg font-bold text-slate-700 mt-1 block">{metrics?.false_positives}</span>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
              <span className="text-xs text-slate-500 block">False Negatives</span>
              <span className="text-lg font-bold text-slate-700 mt-1 block">{metrics?.false_negatives}</span>
            </div>
            <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
              <span className="text-xs text-emerald-700 block font-semibold">Precision</span>
              <span className="text-lg font-bold text-emerald-700 mt-1 block">{((metrics?.precision ?? 1) * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-xs text-blue-700 block font-semibold">Recall</span>
              <span className="text-lg font-bold text-blue-700 mt-1 block">{((metrics?.recall ?? 1) * 100).toFixed(1)}%</span>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
              <span className="text-xs text-purple-700 block font-semibold">F1 Score</span>
              <span className="text-lg font-bold text-purple-700 mt-1 block">{((metrics?.f1_score ?? 1) * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Portfolio Premium Production */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-600" />
            Product Portfolio Revenue Performance
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Product Code</th>
                  <th className="py-3 px-4">Line of Business</th>
                  <th className="py-3 px-4">Product Name</th>
                  <th className="py-3 px-4">Policies Written</th>
                  <th className="py-3 px-4">Quotes Evaluated</th>
                  <th className="py-3 px-4 text-right">Written Premium</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {productDist.map((p) => (
                  <tr key={p.product_code} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                      {p.product_code}
                    </td>
                    <td className="py-3.5 px-4 text-xs font-semibold text-slate-800">
                      {p.line_of_business}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      {p.product_name}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      {p.policy_count.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-slate-600">
                      {p.quote_count.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 font-bold text-slate-900 text-sm text-right">
                      ${p.total_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

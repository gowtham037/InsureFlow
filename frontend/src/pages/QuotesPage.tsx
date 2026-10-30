import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Quote, Applicant, Product } from '../types';
import { Modal } from '../components/Modal';
import { RiskBadge, StatusBadge } from '../components/Badge';
import {
  Search,
  Plus,
  Eye,
  CheckCircle2,
  XCircle,
  FileSpreadsheet,
  Calculator,
  ChevronLeft,
  ChevronRight,
  Activity,
  AlertCircle
} from 'lucide-react';

export const QuotesPage: React.FC = () => {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Detail Modal
  const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  // Create Modal
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [applicantsList, setApplicantsList] = useState<Applicant[]>([]);
  const [productsList, setProductsList] = useState<Product[]>([]);
  const [formData, setFormData] = useState({
    applicant_id: 0,
    asset_id: 0,
    product_id: 0,
    coverage_amount: 50000,
    deductible: 500
  });

  const fetchQuotes = async (p = page) => {
    setLoading(true);
    try {
      const data = await apiClient.getQuotes(p, pageSize, statusFilter, riskFilter, search);
      setQuotes(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch quotes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotes(page);
  }, [page, statusFilter, riskFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchQuotes(1);
  };

  const handleOpenCreate = async () => {
    try {
      const [apps, prods] = await Promise.all([
        apiClient.getApplicants(1, 100),
        apiClient.getProducts()
      ]);
      setApplicantsList(apps.items);
      setProductsList(prods);
      if (apps.items.length > 0 && prods.length > 0) {
        const firstApp = apps.items[0];
        const firstAssetId = firstApp.assets && firstApp.assets.length > 0 ? firstApp.assets[0].id : 1;
        setFormData({
          applicant_id: firstApp.id,
          asset_id: firstAssetId,
          product_id: prods[0].id,
          coverage_amount: 50000,
          deductible: 500
        });
      }
      setIsCreateOpen(true);
    } catch (err) {
      console.error('Failed to prepare quote form:', err);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const created = await apiClient.createQuote(formData);
      setIsCreateOpen(false);
      setSelectedQuote(created);
      setIsDetailOpen(true);
      fetchQuotes(1);
    } catch (err: any) {
      alert(`Quote Creation Failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const handleAcceptQuote = async (id: number) => {
    try {
      const updated = await apiClient.acceptQuote(id);
      setSelectedQuote(updated);
      fetchQuotes(page);
    } catch (err: any) {
      alert(`Failed to accept quote: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Quotes & Submissions"
        subtitle="Automated product eligibility, transparent actuarial pricing breakdowns and customer acceptance"
        onRefresh={() => fetchQuotes(page)}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        {/* Filter & Action Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Quote ID..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </form>

            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="text-sm p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="">All Statuses</option>
              <option value="EVALUATED">EVALUATED</option>
              <option value="ACCEPTED">ACCEPTED</option>
              <option value="REJECTED">REJECTED</option>
            </select>

            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
              className="text-sm p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="">All Risk Tiers</option>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>

          <button
            onClick={handleOpenCreate}
            className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-xs transition-colors shrink-0"
          >
            <Calculator className="w-4 h-4" />
            Create & Evaluate Quote
          </button>
        </div>

        {/* Quotes Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Quote ID</th>
                  <th className="py-3 px-4">Coverage Amount</th>
                  <th className="py-3 px-4">Deductible</th>
                  <th className="py-3 px-4">Risk Tier (Score)</th>
                  <th className="py-3 px-4">Annual Premium</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Accepted?</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && quotes.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Loading quotes...
                    </td>
                  </tr>
                ) : quotes.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      No quotes found matching criteria.
                    </td>
                  </tr>
                ) : (
                  quotes.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {q.business_id}
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-slate-900">
                        ${q.coverage_amount?.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-slate-600">
                        ${q.deductible?.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5">
                          <RiskBadge tier={q.risk_tier} />
                          <span className="text-xs text-slate-400">({q.risk_score}/100)</span>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-bold text-slate-900 text-sm">
                          ${q.final_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={q.status} />
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        {q.customer_accepted ? (
                          <span className="inline-flex items-center gap-1 text-emerald-600 font-semibold">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Accepted
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-slate-400">
                            <XCircle className="w-3.5 h-3.5" /> Pending
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => { setSelectedQuote(q); setIsDetailOpen(true); }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-brand-600 hover:bg-slate-100 rounded-md transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between px-4 py-3 bg-slate-50/80 border-t border-slate-200 text-xs text-slate-500">
            <div>
              Showing <span className="font-semibold text-slate-700">{(page - 1) * pageSize + 1}</span> to{' '}
              <span className="font-semibold text-slate-700">{Math.min(page * pageSize, total)}</span> of{' '}
              <span className="font-semibold text-slate-700">{total}</span> quotes
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
                className="p-1 rounded-md border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="px-2">Page {page} of {totalPages || 1}</span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                className="p-1 rounded-md border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Quote Detail Modal */}
      <Modal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        title={`Quote Actuarial Breakdown: ${selectedQuote?.business_id}`}
        maxWidth="max-w-3xl"
      >
        {selectedQuote && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
              <div>
                <span className="text-slate-400 block font-medium">Final Annual Premium</span>
                <span className="text-lg font-bold text-slate-900 leading-tight">
                  ${selectedQuote.final_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Risk Tier & Score</span>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <RiskBadge tier={selectedQuote.risk_tier} />
                  <span className="font-bold text-slate-800">{selectedQuote.risk_score}/100</span>
                </div>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Eligibility Outcome</span>
                <span className={`font-bold mt-0.5 inline-block ${selectedQuote.eligibility_passed ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {selectedQuote.eligibility_passed ? 'ELIGIBLE' : 'INELIGIBLE'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Customer Acceptance</span>
                <span className="font-semibold text-slate-700 mt-0.5 inline-block">
                  {selectedQuote.customer_accepted ? 'ACCEPTED' : 'PENDING'}
                </span>
              </div>
            </div>

            {/* Actuarial Factor Breakdown */}
            <div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Calculator className="w-4 h-4 text-brand-600" />
                Transparent Pricing Multipliers
              </h4>
              <div className="bg-white border border-slate-200 rounded-lg overflow-hidden text-xs">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                    <tr>
                      <th className="p-2.5">Actuarial Variable</th>
                      <th className="p-2.5 text-right">Multiplier / Value</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {selectedQuote.calculated_factors && Object.entries(selectedQuote.calculated_factors).map(([k, v]) => (
                      <tr key={k}>
                        <td className="p-2.5 font-medium text-slate-700 capitalize">{k.replace(/_/g, ' ')}</td>
                        <td className="p-2.5 text-right font-mono font-bold text-slate-900">{typeof v === 'number' ? v : String(v)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Explanation Note */}
            {selectedQuote.pricing_explanation && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-900">
                <span className="font-bold block mb-1">Actuarial Explanation:</span>
                {selectedQuote.pricing_explanation}
              </div>
            )}

            {/* Eligibility Reasons */}
            {selectedQuote.eligibility_reasons && selectedQuote.eligibility_reasons.length > 0 && (
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Rule Evaluation Trace:</h4>
                <ul className="space-y-1 text-xs text-slate-600">
                  {selectedQuote.eligibility_reasons.map((r, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Action Bar */}
            <div className="flex justify-between items-center pt-4 border-t border-slate-100">
              <span className="text-xs text-slate-400">Expires: {new Date(selectedQuote.expires_at).toLocaleDateString()}</span>
              {!selectedQuote.customer_accepted && selectedQuote.eligibility_passed && (
                <button
                  onClick={() => handleAcceptQuote(selectedQuote.id)}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Record Customer Acceptance
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Create Quote Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create & Evaluate New Insurance Quote"
        maxWidth="max-w-xl"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Select Applicant</label>
            <select
              required
              value={formData.applicant_id}
              onChange={(e) => {
                const appId = parseInt(e.target.value);
                const app = applicantsList.find(a => a.id === appId);
                const assetId = app?.assets && app.assets.length > 0 ? app.assets[0].id : 1;
                setFormData({ ...formData, applicant_id: appId, asset_id: assetId });
              }}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {applicantsList.map(a => (
                <option key={a.id} value={a.id}>
                  {a.business_id} – {a.first_name} {a.last_name} ({a.city}, {a.state})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Select Insured Asset</label>
            <select
              required
              value={formData.asset_id}
              onChange={(e) => setFormData({ ...formData, asset_id: parseInt(e.target.value) })}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {applicantsList.find(a => a.id === formData.applicant_id)?.assets?.map(ast => (
                <option key={ast.id} value={ast.id}>
                  {ast.business_id} – {ast.make_model} (${ast.asset_value?.toLocaleString()})
                </option>
              )) || <option value={1}>Asset 1</option>}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Select Insurance Product</label>
            <select
              required
              value={formData.product_id}
              onChange={(e) => setFormData({ ...formData, product_id: parseInt(e.target.value) })}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {productsList.map(p => (
                <option key={p.id} value={p.id}>
                  {p.product_code} – {p.name} (${p.min_coverage_limit?.toLocaleString()} - ${p.max_coverage_limit?.toLocaleString()})
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Requested Coverage ($)</label>
              <input
                required
                type="number"
                value={formData.coverage_amount}
                onChange={(e) => setFormData({ ...formData, coverage_amount: parseFloat(e.target.value) || 0 })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Deductible ($)</label>
              <input
                required
                type="number"
                value={formData.deductible}
                onChange={(e) => setFormData({ ...formData, deductible: parseFloat(e.target.value) || 0 })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsCreateOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 shadow-xs flex items-center gap-1.5"
            >
              <Calculator className="w-4 h-4" />
              Evaluate Quote
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

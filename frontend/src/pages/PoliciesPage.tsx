import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Policy } from '../types';
import { Modal } from '../components/Modal';
import { StatusBadge } from '../components/Badge';
import {
  Search,
  Eye,
  XCircle,
  FileCheck2,
  Calendar,
  DollarSign,
  ChevronLeft,
  ChevronRight,
  Activity,
  History,
  ShieldAlert
} from 'lucide-react';

export const PoliciesPage: React.FC = () => {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // Detail Modal
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  // Cancel Modal
  const [isCancelOpen, setIsCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('Customer policyholder cancellation request');

  const fetchPolicies = async (p = page) => {
    setLoading(true);
    try {
      const data = await apiClient.getPolicies(p, pageSize, statusFilter, search);
      setPolicies(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load policies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies(page);
  }, [page, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchPolicies(1);
  };

  const handleOpenDetail = async (id: number) => {
    try {
      const pol = await apiClient.getPolicy(id);
      setSelectedPolicy(pol);
      setIsDetailOpen(true);
    } catch (err) {
      console.error('Failed to load policy detail:', err);
    }
  };

  const handleCancelSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPolicy) return;

    try {
      await apiClient.cancelPolicy(selectedPolicy.id, cancelReason);
      setIsCancelOpen(false);
      setIsDetailOpen(false);
      fetchPolicies(page);
    } catch (err: any) {
      alert(`Cancellation failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Policy Administration"
        subtitle="Manage active insurance contracts, effective dates, premium accounting and lifecycle timeline events"
        onRefresh={() => fetchPolicies(page)}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        {/* Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
            <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search Policy ID..."
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
              <option value="ACTIVE">ACTIVE</option>
              <option value="ISSUED">ISSUED</option>
              <option value="CANCELLED">CANCELLED</option>
              <option value="EXPIRED">EXPIRED</option>
            </select>
          </div>
        </div>

        {/* Policies Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Policy ID</th>
                  <th className="py-3 px-4">Coverage Limit</th>
                  <th className="py-3 px-4">Annual Premium</th>
                  <th className="py-3 px-4">Effective Term</th>
                  <th className="py-3 px-4">Payment</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && policies.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Loading policies...
                    </td>
                  </tr>
                ) : policies.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      No policies found matching criteria.
                    </td>
                  </tr>
                ) : (
                  policies.map((p) => (
                    <tr key={p.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {p.business_id}
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-slate-900">
                        ${p.coverage_amount?.toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        ${p.annual_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600">
                        {p.effective_date} – {p.expiration_date}
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className="font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          {p.payment_status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={p.status} />
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => handleOpenDetail(p.id)}
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
              <span className="font-semibold text-slate-700">{total}</span> policies
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

      {/* Policy Detail Modal */}
      <Modal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        title={`Policy Contract: ${selectedPolicy?.business_id}`}
        maxWidth="max-w-3xl"
      >
        {selectedPolicy && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
              <div>
                <span className="text-slate-400 block font-medium">Policy Status</span>
                <div className="mt-1"><StatusBadge status={selectedPolicy.status} /></div>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Annual Premium</span>
                <span className="text-base font-bold text-slate-900 mt-0.5 block">
                  ${selectedPolicy.annual_premium?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Coverage Limit</span>
                <span className="text-base font-bold text-brand-700 mt-0.5 block">
                  ${selectedPolicy.coverage_amount?.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Effective Period</span>
                <span className="text-xs font-semibold text-slate-700 mt-1 block">
                  {selectedPolicy.effective_date} to {selectedPolicy.expiration_date}
                </span>
              </div>
            </div>

            {selectedPolicy.cancellation_reason && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-800">
                <span className="font-bold block mb-1">Cancellation Recorded:</span>
                Date: {selectedPolicy.cancellation_date} | Reason: {selectedPolicy.cancellation_reason}
              </div>
            )}

            {/* Lifecycle Timeline */}
            <div>
              <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <History className="w-4 h-4 text-brand-600" />
                Immutable Policy Lifecycle Timeline ({selectedPolicy.events?.length ?? 0} events)
              </h4>
              <div className="space-y-3 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-200">
                {selectedPolicy.events && selectedPolicy.events.length > 0 ? (
                  selectedPolicy.events.map((ev) => (
                    <div key={ev.id} className="relative flex items-start gap-4 ml-1">
                      <div className="w-5 h-5 rounded-full bg-brand-600 text-white flex items-center justify-center text-[10px] shrink-0 z-10">
                        •
                      </div>
                      <div className="flex-1 bg-white p-3 rounded-lg border border-slate-200 shadow-2xs text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-slate-900">{ev.event_type}</span>
                          <span className="text-[11px] text-slate-400">{new Date(ev.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-slate-600">{ev.event_description}</p>
                        <span className="text-[10px] text-slate-400 mt-1 block">Actor: {ev.actor}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400 pl-6">No historical events recorded yet.</p>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end items-center pt-4 border-t border-slate-100 gap-3">
              {selectedPolicy.status === 'ACTIVE' && (
                <button
                  onClick={() => setIsCancelOpen(true)}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold shadow-xs transition-colors flex items-center gap-1.5"
                >
                  <XCircle className="w-4 h-4" />
                  Cancel Policy Contract
                </button>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Cancel Confirmation Modal */}
      <Modal
        isOpen={isCancelOpen}
        onClose={() => setIsCancelOpen(false)}
        title="Cancel Policy Contract"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleCancelSubmit} className="space-y-4">
          <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-800 flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <span>
              This will transition the policy to CANCELLED and preserve this action in the immutable audit trail.
              Cancelled policies become permanently ineligible for renewals.
            </span>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Cancellation Reason</label>
            <textarea
              required
              rows={3}
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-rose-500"
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsCancelOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm font-semibold hover:bg-slate-50"
            >
              Back
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-rose-600 text-white rounded-lg text-sm font-semibold hover:bg-rose-700 shadow-xs"
            >
              Confirm Cancellation
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Renewal, Policy } from '../types';
import { Modal } from '../components/Modal';
import { StatusBadge } from '../components/Badge';
import {
  RotateCw,
  Plus,
  Activity,
  CheckCircle2,
  XCircle,
  Calendar,
  TrendingUp,
  Percent,
  AlertCircle
} from 'lucide-react';

export const RenewalsPage: React.FC = () => {
  const [renewals, setRenewals] = useState<Renewal[]>([]);
  const [activePolicies, setActivePolicies] = useState<Policy[]>([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  // Generate Renewal Modal
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  const [selectedPolicyId, setSelectedPolicyId] = useState<number>(0);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [rens, pols] = await Promise.all([
        apiClient.getRenewals(100, statusFilter),
        apiClient.getPolicies(1, 50, 'ACTIVE')
      ]);
      setRenewals(rens);
      setActivePolicies(pols.items);
      if (pols.items.length > 0) {
        setSelectedPolicyId(pols.items[0].id);
      }
    } catch (err) {
      console.error('Failed to load renewals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const handleGenerateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.generateRenewal(selectedPolicyId);
      setIsGenerateOpen(false);
      fetchData();
    } catch (err: any) {
      alert(`Renewal Generation Failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  const handleAction = async (id: number, action: 'ACCEPT' | 'DECLINE') => {
    try {
      await apiClient.actOnRenewal(id, action);
      fetchData();
    } catch (err: any) {
      alert(`Action failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Renewal Portfolio"
        subtitle="Automated policy expiration tracking, rate revisions, customer acceptance and renewal covenant enforcement"
        onRefresh={fetchData}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-sm p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="">All Renewal States</option>
              <option value="OFFERED">OFFERED (Pending Customer)</option>
              <option value="ACCEPTED">ACCEPTED (Renewed)</option>
              <option value="DECLINED">DECLINED</option>
            </select>
          </div>

          <button
            onClick={() => setIsGenerateOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-xs transition-colors shrink-0"
          >
            <RotateCw className="w-4 h-4" />
            Generate Renewal Offer
          </button>
        </div>

        {/* Renewals Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Renewal ID</th>
                  <th className="py-3 px-4">Cycle Year</th>
                  <th className="py-3 px-4">Prior Premium</th>
                  <th className="py-3 px-4">Renewal Premium</th>
                  <th className="py-3 px-4">Rate Change</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Term</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && renewals.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Loading renewals...
                    </td>
                  </tr>
                ) : renewals.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-slate-400">
                      No renewals found.
                    </td>
                  </tr>
                ) : (
                  renewals.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {r.business_id}
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-slate-800 text-xs">
                        Cycle {r.renewal_cycle_year}
                      </td>
                      <td className="py-3.5 px-4 text-slate-500 text-xs">
                        ${r.prior_premium?.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900 text-sm">
                        ${r.renewal_premium?.toFixed(2)}
                      </td>
                      <td className="py-3.5 px-4 text-xs font-semibold text-brand-700">
                        +{r.premium_change_percent}%
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={r.status} />
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500">
                        {r.effective_date} to {r.expiration_date}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {r.status === 'OFFERED' ? (
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => handleAction(r.id, 'ACCEPT')}
                              className="px-2 py-1 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 rounded text-xs font-semibold transition-colors"
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => handleAction(r.id, 'DECLINE')}
                              className="px-2 py-1 bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 rounded text-xs font-semibold transition-colors"
                            >
                              Decline
                            </button>
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400">Finalized</span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Generate Renewal Modal */}
      <Modal
        isOpen={isGenerateOpen}
        onClose={() => setIsGenerateOpen(false)}
        title="Generate Annual Renewal Offer"
        maxWidth="max-w-md"
      >
        <form onSubmit={handleGenerateSubmit} className="space-y-4">
          <p className="text-xs text-slate-500">
            Select an active policy to calculate the renewal premium based on claims history and product indexation.
            Policies in CANCELLED status will be rejected automatically.
          </p>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Eligible Policy Contract</label>
            <select
              required
              value={selectedPolicyId}
              onChange={(e) => setSelectedPolicyId(parseInt(e.target.value))}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {activePolicies.map(p => (
                <option key={p.id} value={p.id}>
                  {p.business_id} (Exp: {p.expiration_date})
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsGenerateOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 shadow-xs flex items-center gap-1.5"
            >
              <RotateCw className="w-4 h-4" />
              Generate Offer
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

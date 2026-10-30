import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Endorsement, Policy } from '../types';
import { Modal } from '../components/Modal';
import { StatusBadge } from '../components/Badge';
import {
  FileEdit,
  Plus,
  Activity,
  ArrowRight,
  TrendingUp,
  TrendingDown,
  Calendar,
  CheckCircle2
} from 'lucide-react';

export const EndorsementsPage: React.FC = () => {
  const [endorsements, setEndorsements] = useState<Endorsement[]>([]);
  const [activePolicies, setActivePolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);

  // Create Modal
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState({
    policy_id: 0,
    endorsement_type: 'COVERAGE_LIMIT_CHANGE',
    new_coverage_amount: 75000,
    effective_date: new Date().toISOString().split('T')[0],
    reason: 'Mid-term adjustment of declared coverage limits'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [ends, pols] = await Promise.all([
        apiClient.getEndorsements(100),
        apiClient.getPolicies(1, 50, 'ACTIVE')
      ]);
      setEndorsements(ends);
      setActivePolicies(pols.items);
      if (pols.items.length > 0) {
        setFormData(prev => ({ ...prev, policy_id: pols.items[0].id }));
      }
    } catch (err) {
      console.error('Failed to load endorsements:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createEndorsement(formData);
      setIsCreateOpen(false);
      fetchData();
    } catch (err: any) {
      alert(`Endorsement Failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Mid-Term Endorsements"
        subtitle="Coverage amendments, vehicle upgrades, deductible revisions and prorated premium delta tracking"
        onRefresh={fetchData}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Endorsement Records</span>
            <span className="text-sm font-bold text-slate-900">Total Processed: {endorsements.length}</span>
          </div>

          <button
            onClick={() => setIsCreateOpen(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4" />
            Issue Policy Endorsement
          </button>
        </div>

        {/* Endorsements Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Endorsement ID</th>
                  <th className="py-3 px-4">Endorsement Type</th>
                  <th className="py-3 px-4">Coverage Change</th>
                  <th className="py-3 px-4">Premium Delta</th>
                  <th className="py-3 px-4">Effective Date</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && endorsements.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Loading endorsements...
                    </td>
                  </tr>
                ) : endorsements.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      No endorsements issued yet.
                    </td>
                  </tr>
                ) : (
                  endorsements.map((end) => (
                    <tr key={end.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {end.business_id}
                      </td>
                      <td className="py-3.5 px-4 text-xs font-semibold text-slate-800">
                        {end.endorsement_type.replace(/_/g, ' ')}
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className="text-slate-400">${end.prior_coverage_amount?.toLocaleString()}</span>
                        <ArrowRight className="w-3 h-3 inline mx-1.5 text-slate-400" />
                        <span className="font-bold text-slate-900">${end.new_coverage_amount?.toLocaleString()}</span>
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className={`font-bold inline-flex items-center gap-1 ${
                          end.premium_delta >= 0 ? 'text-brand-600' : 'text-emerald-600'
                        }`}>
                          {end.premium_delta >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                          {end.premium_delta >= 0 ? '+' : ''}${end.premium_delta?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600">
                        {end.effective_date}
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={end.status} />
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500 max-w-xs truncate">
                        {end.reason}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Create Endorsement Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Execute Policy Endorsement"
        maxWidth="max-w-xl"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Target Active Policy</label>
            <select
              required
              value={formData.policy_id}
              onChange={(e) => setFormData({ ...formData, policy_id: parseInt(e.target.value) })}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              {activePolicies.map(p => (
                <option key={p.id} value={p.id}>
                  {p.business_id} – Current Limit: ${p.coverage_amount?.toLocaleString()} (Prem: ${p.annual_premium?.toFixed(2)})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Endorsement Type</label>
            <select
              value={formData.endorsement_type}
              onChange={(e) => setFormData({ ...formData, endorsement_type: e.target.value })}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              <option value="COVERAGE_LIMIT_CHANGE">COVERAGE_LIMIT_CHANGE (Adjust Total Limit)</option>
              <option value="ASSET_VALUE_UPDATE">ASSET_VALUE_UPDATE (Re-evaluation)</option>
              <option value="DEDUCTIBLE_CHANGE">DEDUCTIBLE_CHANGE (Increase/Decrease Excess)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">New Coverage Amount ($)</label>
              <input
                required
                type="number"
                value={formData.new_coverage_amount}
                onChange={(e) => setFormData({ ...formData, new_coverage_amount: parseFloat(e.target.value) || 0 })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Effective Date</label>
              <input
                required
                type="date"
                value={formData.effective_date}
                onChange={(e) => setFormData({ ...formData, effective_date: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Endorsement Reason</label>
            <textarea
              required
              rows={2}
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
            />
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
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 shadow-xs"
            >
              Apply Endorsement
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

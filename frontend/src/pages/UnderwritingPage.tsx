import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { UnderwritingDecision } from '../types';
import { Modal } from '../components/Modal';
import { RiskBadge, StatusBadge } from '../components/Badge';
import {
  Cpu,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  UserCheck,
  ShieldAlert,
  ArrowRight,
  Activity,
  History
} from 'lucide-react';

export const UnderwritingPage: React.FC = () => {
  const [decisions, setDecisions] = useState<UnderwritingDecision[]>([]);
  const [referrals, setReferrals] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'referrals' | 'history'>('referrals');
  const [loading, setLoading] = useState(true);

  // Review Modal
  const [selectedDecision, setSelectedDecision] = useState<UnderwritingDecision | null>(null);
  const [isReviewOpen, setIsReviewOpen] = useState(false);
  const [reviewAction, setReviewAction] = useState('APPROVED');
  const [reviewerName, setReviewerName] = useState('Senior Underwriter');
  const [overrideReason, setOverrideReason] = useState('Manual risk assessment verified acceptable exposure.');
  const [conditionInput, setConditionInput] = useState('$1,000 standard deductible and inspection verification');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [refs, decs] = await Promise.all([
        apiClient.getReferrals(),
        apiClient.getDecisions(100)
      ]);
      setReferrals(refs);
      setDecisions(decs);
    } catch (err) {
      console.error('Failed to load underwriting data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenReview = (dec: UnderwritingDecision) => {
    setSelectedDecision(dec);
    setReviewAction(dec.decision === 'REFERRED' ? 'APPROVED' : dec.decision);
    setIsReviewOpen(true);
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDecision) return;

    try {
      await apiClient.reviewDecision(selectedDecision.id, {
        decision: reviewAction,
        reviewer_name: reviewerName,
        override_reason: overrideReason,
        conditions: conditionInput ? [conditionInput] : []
      });
      setIsReviewOpen(false);
      fetchData();
    } catch (err: any) {
      alert(`Adjudication failed: ${err?.response?.data?.detail || err.message}`);
    }
  };

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Underwriting Workbench"
        subtitle="Adjudicate high-exposure risk referrals, enforce underwriting authority and condition covenants"
        onRefresh={fetchData}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        {/* Navigation Tabs */}
        <div className="flex items-center gap-3 border-b border-slate-200">
          <button
            onClick={() => setActiveTab('referrals')}
            className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'referrals'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            Pending Underwriter Referrals ({referrals.length})
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition-colors ${
              activeTab === 'history'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            }`}
          >
            <History className="w-4 h-4" />
            Decision Audit Trail ({decisions.length})
          </button>
        </div>

        {/* Tab 1: Pending Referrals */}
        {activeTab === 'referrals' && (
          <div className="space-y-4">
            {loading ? (
              <div className="flex items-center justify-center p-12 bg-white rounded-xl border border-slate-200">
                <Activity className="w-6 h-6 text-brand-600 animate-spin mr-2" />
                <span className="text-sm font-medium text-slate-500">Checking pending underwriting referrals...</span>
              </div>
            ) : referrals.length === 0 ? (
              <div className="bg-white p-12 rounded-xl border border-slate-200 text-center">
                <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
                <h3 className="text-base font-bold text-slate-900">Zero Pending Referrals</h3>
                <p className="text-xs text-slate-500 mt-1">
                  All insurance applications are either automated or already adjudicated.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {referrals.map((ref, idx) => {
                  const matchDec = decisions.find(d => d.quote_id === ref.quote_id);
                  return (
                    <div
                      key={idx}
                      className="bg-white rounded-xl border border-amber-200 shadow-xs p-5 flex flex-col justify-between hover:border-amber-400 transition-all"
                    >
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-mono text-xs font-bold text-brand-600">{ref.quote_business_id}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-50 text-amber-700 border border-amber-200">
                            REFERRED
                          </span>
                        </div>

                        <h4 className="text-sm font-bold text-slate-900">{ref.applicant_name}</h4>
                        <p className="text-xs text-slate-500 mb-3">{ref.product_name}</p>

                        <div className="bg-slate-50 p-3 rounded-lg space-y-1.5 text-xs mb-3">
                          <div className="flex justify-between">
                            <span className="text-slate-400 font-medium">Coverage Limit:</span>
                            <span className="font-bold text-slate-900">${ref.coverage_amount?.toLocaleString()}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400 font-medium">Risk Score:</span>
                            <span className="font-bold text-rose-600">{ref.risk_score} / 100 ({ref.risk_tier})</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400 font-medium">Calculated Premium:</span>
                            <span className="font-bold text-brand-700">${ref.final_premium?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                          </div>
                        </div>

                        <div className="text-xs text-slate-600 p-2.5 bg-amber-50/60 rounded-md border border-amber-100 mb-4">
                          <span className="font-bold text-amber-900 block mb-0.5">Referral Reason:</span>
                          {ref.decision_reason}
                        </div>
                      </div>

                      {matchDec && (
                        <button
                          onClick={() => handleOpenReview(matchDec)}
                          className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-semibold shadow-xs flex items-center justify-center gap-1.5 transition-colors"
                        >
                          <UserCheck className="w-3.5 h-3.5" />
                          Adjudicate & Override
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Decision History */}
        {activeTab === 'history' && (
          <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-700">
                <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                  <tr>
                    <th className="py-3 px-4">Decision ID</th>
                    <th className="py-3 px-4">Decision</th>
                    <th className="py-3 px-4">Authority Level</th>
                    <th className="py-3 px-4">Reviewer</th>
                    <th className="py-3 px-4">Decision Rationale</th>
                    <th className="py-3 px-4">Override?</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {decisions.map((dec) => (
                    <tr key={dec.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {dec.business_id}
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={dec.decision} />
                      </td>
                      <td className="py-3.5 px-4 text-xs font-semibold text-slate-700">
                        {dec.authority_level}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600">
                        {dec.reviewer_name}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500 max-w-xs truncate">
                        {dec.decision_reason}
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        {dec.is_override ? (
                          <span className="font-semibold text-amber-600">Yes (Override)</span>
                        ) : (
                          <span className="text-slate-400">Standard</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => handleOpenReview(dec)}
                          className="px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-brand-600 hover:bg-slate-100 rounded-md"
                        >
                          Review
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Review Modal */}
      <Modal
        isOpen={isReviewOpen}
        onClose={() => setIsReviewOpen(false)}
        title={`Underwriter Adjudication: ${selectedDecision?.business_id}`}
        maxWidth="max-w-xl"
      >
        <form onSubmit={handleReviewSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Underwriting Decision</label>
            <select
              value={reviewAction}
              onChange={(e) => setReviewAction(e.target.value)}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white"
            >
              <option value="APPROVED">APPROVED (Full Approval)</option>
              <option value="APPROVED_WITH_CONDITIONS">APPROVED_WITH_CONDITIONS (Conditional Approval)</option>
              <option value="DECLINED">DECLINED (Risk Exposure Rejection)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Underwriter Reviewer Name</label>
            <input
              required
              type="text"
              value={reviewerName}
              onChange={(e) => setReviewerName(e.target.value)}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Override Reason & Rationale</label>
            <textarea
              required
              rows={3}
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
            />
          </div>

          {reviewAction === 'APPROVED_WITH_CONDITIONS' && (
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Covenants / Imposed Conditions</label>
              <input
                type="text"
                value={conditionInput}
                onChange={(e) => setConditionInput(e.target.value)}
                placeholder="e.g. Mandatory telematics, $1,000 deductible"
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
            <button
              type="button"
              onClick={() => setIsReviewOpen(false)}
              className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 shadow-xs"
            >
              Confirm Adjudication
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

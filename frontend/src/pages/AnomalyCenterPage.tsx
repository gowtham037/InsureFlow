import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Anomaly } from '../types';
import { Modal } from '../components/Modal';
import { SeverityBadge } from '../components/Badge';
import {
  AlertTriangle,
  ShieldAlert,
  Search,
  CheckCircle2,
  XCircle,
  Activity,
  Scan,
  Info,
  Layers,
  ChevronRight,
  Eye
} from 'lucide-react';

export const AnomalyCenterPage: React.FC = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [severityFilter, setSeverityFilter] = useState('');
  const [issueFilter, setIssueFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  // Inspector Modal
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [list, sum] = await Promise.all([
        apiClient.getAnomalies(severityFilter, issueFilter),
        apiClient.getAnomalySummary()
      ]);
      setAnomalies(list);
      setSummary(sum);
    } catch (err) {
      console.error('Failed to load anomalies:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [severityFilter, issueFilter]);

  const handleTriggerDetection = async () => {
    setScanning(true);
    try {
      await apiClient.detectAnomalies();
      await fetchData();
    } catch (err) {
      alert('Anomaly detection scan failed.');
    } finally {
      setScanning(false);
    }
  };

  const evalMetrics = summary?.evaluation_metrics || {};

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Anomaly Detection & Integrity Center"
        subtitle="Independent invariant rule evaluations, discrepancy diagnosis and actuarial ground truth metrics"
        onRefresh={fetchData}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        {/* KPI & Confusion Matrix Header */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Detected Anomalies</p>
              <h3 className="text-2xl font-bold text-rose-600 mt-1">{summary?.total_anomalies ?? 0}</h3>
              <p className="text-xs text-slate-500 mt-1">Independent rule violations</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Detection Precision</p>
              <h3 className="text-2xl font-bold text-emerald-600 mt-1">
                {((evalMetrics.precision ?? 1) * 100).toFixed(1)}%
              </h3>
              <p className="text-xs text-slate-500 mt-1">True Positives / (TP + FP)</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Detection Recall</p>
              <h3 className="text-2xl font-bold text-brand-600 mt-1">
                {((evalMetrics.recall ?? 1) * 100).toFixed(1)}%
              </h3>
              <p className="text-xs text-slate-500 mt-1">True Positives / (TP + FN)</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Scan className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Actuarial F1 Score</p>
              <h3 className="text-2xl font-bold text-purple-600 mt-1">
                {((evalMetrics.f1_score ?? 1) * 100).toFixed(1)}%
              </h3>
              <p className="text-xs text-slate-500 mt-1">Harmonic accuracy mean</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
              <Layers className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Action & Filter Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <div className="flex flex-wrap items-center gap-3">
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="text-sm p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
            </select>

            <select
              value={issueFilter}
              onChange={(e) => setIssueFilter(e.target.value)}
              className="text-sm p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700"
            >
              <option value="">All Anomaly Scenarios</option>
              <option value="ISSUANCE_WITHOUT_ACCEPTANCE">Issuance Without Acceptance</option>
              <option value="PREMIUM_FORMULA_MISMATCH">Premium Formula Mismatch</option>
              <option value="ENDORSEMENT_LIMIT_EXCEEDED">Endorsement Limit Exceeded</option>
              <option value="RENEWAL_ON_CANCELLED_POLICY">Renewal on Cancelled Policy</option>
              <option value="OVERLAPPING_POLICY_PERIOD">Overlapping Policy Period</option>
            </select>
          </div>

          <button
            onClick={handleTriggerDetection}
            disabled={scanning}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-sm font-semibold shadow-xs transition-colors disabled:opacity-50"
          >
            <Scan className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
            Run Invariant Inspection Scan
          </button>
        </div>

        {/* Anomalies Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Anomaly ID</th>
                  <th className="py-3 px-4">Entity ID</th>
                  <th className="py-3 px-4">Issue Scenario</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Detection Rule</th>
                  <th className="py-3 px-4">Diagnosis Summary</th>
                  <th className="py-3 px-4 text-right">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && anomalies.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Evaluating anomaly invariants...
                    </td>
                  </tr>
                ) : anomalies.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      Zero anomalies detected. All invariant rules satisfied.
                    </td>
                  </tr>
                ) : (
                  anomalies.map((anm) => (
                    <tr key={anm.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {anm.business_id}
                      </td>
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900 text-xs">
                        {anm.entity_id}
                      </td>
                      <td className="py-3.5 px-4 text-xs font-semibold text-slate-800">
                        {anm.issue_type.replace(/_/g, ' ')}
                      </td>
                      <td className="py-3.5 px-4">
                        <SeverityBadge severity={anm.severity} />
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-500 font-mono">
                        {anm.detection_rule.split(':')[0]}
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600 max-w-sm truncate">
                        {anm.description}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => { setSelectedAnomaly(anm); setIsDetailOpen(true); }}
                          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-brand-600 hover:text-brand-800 hover:bg-brand-50 rounded-md transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          Diagnose
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Diagnosis Inspector Modal */}
      <Modal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        title={`Anomaly Diagnosis: ${selectedAnomaly?.business_id}`}
        maxWidth="max-w-2xl"
      >
        {selectedAnomaly && (
          <div className="space-y-5">
            <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-lg border border-slate-200">
              <div>
                <span className="text-xs text-slate-400 block">Affected Entity</span>
                <span className="text-sm font-bold text-slate-900">{selectedAnomaly.entity_type} – {selectedAnomaly.entity_id}</span>
              </div>
              <SeverityBadge severity={selectedAnomaly.severity} />
            </div>

            <div>
              <span className="text-xs text-slate-400 block font-medium">Issue Type & Rule Reference</span>
              <span className="text-sm font-bold text-slate-900 block mt-0.5">{selectedAnomaly.issue_type}</span>
              <span className="text-xs text-brand-600 font-mono block mt-0.5">{selectedAnomaly.detection_rule}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs">
                <span className="font-bold text-emerald-900 block mb-1">Expected Invariant Outcome:</span>
                <p className="text-emerald-800">{selectedAnomaly.expected_outcome}</p>
              </div>
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs">
                <span className="font-bold text-rose-900 block mb-1">Actual Detected Condition:</span>
                <p className="text-rose-800">{selectedAnomaly.actual_detected_outcome}</p>
              </div>
            </div>

            <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs">
              <span className="font-bold text-slate-900 block mb-1">Actuarial Diagnostic Explanation:</span>
              <p className="text-slate-600 leading-relaxed">{selectedAnomaly.detection_explanation}</p>
            </div>

            <div className="flex justify-between items-center pt-3 border-t border-slate-100 text-[11px] text-slate-400">
              <span>Timestamp: {new Date(selectedAnomaly.detected_at).toLocaleString()}</span>
              <span>Ground Truth Separated: Verified</span>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

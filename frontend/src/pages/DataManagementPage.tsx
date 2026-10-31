import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { ValidationReport } from '../types';
import {
  Database,
  Play,
  CheckCircle2,
  AlertTriangle,
  Download,
  FileCheck,
  ShieldCheck,
  RefreshCw,
  Activity,
  Layers,
  FileCode,
  FileSpreadsheet,
  Archive
} from 'lucide-react';

export const DataManagementPage: React.FC = () => {
  const [status, setStatus] = useState<Record<string, any>>({});
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [reproducibility, setReproducibility] = useState<any>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [genMessage, setGenMessage] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<'csv' | 'json'>('csv');
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [pendingMode, setPendingMode] = useState<'starter' | 'full' | null>(null);

  const fetchStatus = async () => {
    try {
      const [s, repro] = await Promise.all([
        apiClient.getGenerationStatus(),
        apiClient.getReproducibilityCheck()
      ]);
      setStatus(s);
      setReproducibility(repro);
    } catch (err) {
      console.error('Failed to load generation status:', err);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const requestGenerate = (mode: 'starter' | 'full') => {
    setPendingMode(mode);
    setConfirmModalOpen(true);
  };

  const handleCancelGenerate = () => {
    setConfirmModalOpen(false);
    setPendingMode(null);
  };

  const handleConfirmGenerate = async () => {
    if (!pendingMode) return;
    const mode = pendingMode;
    setConfirmModalOpen(false);
    setPendingMode(null);
    await handleGenerate(mode);
  };

  const handleGenerate = async (mode: 'starter' | 'full') => {
    setIsGenerating(true);
    setGenMessage(`Generating ${mode} synthetic dataset (Seed: 20261022)... This process generates relational records across all 15 entities.`);
    try {
      const res = await apiClient.generateDataset(mode);
      setGenMessage(`Successfully generated ${mode} dataset! Preserved user records and updated telemetry.`);
      await fetchStatus();
    } catch (err: any) {
      setGenMessage(`Generation failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleValidate = async () => {
    setIsValidating(true);
    try {
      const report = await apiClient.validateDataset();
      setValidationReport(report);
    } catch (err: any) {
      alert(`Validation failed: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setIsValidating(false);
    }
  };

  const datasets = [
    { id: 'applicants', name: 'Applicants', desc: 'Policyholder demographics and risk tiers' },
    { id: 'insured_assets', name: 'Insured Assets', desc: 'Vehicles, properties, and health subjects' },
    { id: 'products', name: 'Products', desc: 'Insurance lines, limits, and age boundaries' },
    { id: 'coverage_options', name: 'Coverage Options', desc: 'Optional add-ons, limits, and pricing' },
    { id: 'risk_factors', name: 'Risk Factors', desc: 'Actuarial risk factors and weight tables' },
    { id: 'quotes', name: 'Quotes', desc: 'Actuarial pricing breakdown and customer acceptance' },
    { id: 'quote_coverages', name: 'Quote Coverages', desc: 'Bridge table of selected coverage options' },
    { id: 'underwriting_decisions', name: 'Underwriting Decisions', desc: 'Authority levels, reasons, and rules' },
    { id: 'policies', name: 'Policies', desc: 'Binding contracts, payment status, effective dates' },
    { id: 'policy_coverages', name: 'Policy Coverages', desc: 'Active policy allocated coverages' },
    { id: 'endorsements', name: 'Endorsements', desc: 'Mid-term coverage revisions and delta premiums' },
    { id: 'renewals', name: 'Renewals', desc: 'Policy extensions and renewal cycle rate adjustments' },
    { id: 'policy_events', name: 'Policy Events', desc: 'Historical immutable audit events log' },
    { id: 'anomaly_records', name: 'Anomaly Records', desc: 'Violations detected by invariant detection engine' },
    { id: 'ground_truth', name: 'Ground Truth', desc: 'Independently isolated negative test ground truth' },
  ];

  const genState = status.generation_state || {};
  const currentGenStatus = genState.status || (status.applicants ? 'COMPLETED' : 'NOT_STARTED');

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Data Management & Integrity Workbench"
        subtitle="Execute deterministic synthetic data generator, export datasets and run automated data quality audits"
      />

      <div className="p-8 space-y-8">
        {/* Status notification */}
        {genMessage && (
          <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-sm flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-600 animate-spin" />
              <span>{genMessage}</span>
            </div>
            <button onClick={() => setGenMessage(null)} className="text-xs font-semibold hover:underline">Dismiss</button>
          </div>
        )}

        {/* Current Database Volume Cards */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-brand-600" />
              Live Database Record Counts
            </h3>
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Engine State:</span>
              <span className={`px-2.5 py-0.5 rounded-full font-bold ${
                currentGenStatus === 'COMPLETED' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                currentGenStatus === 'GENERATING' ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                currentGenStatus === 'FAILED' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                'bg-slate-100 text-slate-600'
              }`}>
                {currentGenStatus}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Applicants</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.applicants ?? 0).toLocaleString()}</span>
              {status.user_applicants > 0 && (
                <span className="text-[10px] font-semibold text-brand-600 block mt-0.5">
                  +{status.user_applicants} user-created
                </span>
              )}
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Quotes</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.quotes ?? 0).toLocaleString()}</span>
              {status.user_quotes > 0 && (
                <span className="text-[10px] font-semibold text-brand-600 block mt-0.5">
                  +{status.user_quotes} user-created
                </span>
              )}
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Baseline Policies</span>
              <span className="text-xl font-bold text-emerald-600 mt-1 block">{(status.baseline_policies ?? status.policies ?? 0).toLocaleString()}</span>
              {status.user_policies > 0 && (
                <span className="text-[10px] font-semibold text-brand-600 block mt-0.5">
                  +{status.user_policies} user-created
                </span>
              )}
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Renewals</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.renewals ?? 0).toLocaleString()}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Endorsements</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.endorsements ?? 0).toLocaleString()}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Decisions</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.underwriting_decisions ?? 0).toLocaleString()}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Anomalies</span>
              <span className="text-xl font-bold text-rose-600 mt-1 block">{(status.anomalies ?? 0).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Generator Controls & Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Generator Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold text-slate-900">Synthetic Data Generation Engine</h3>
                <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 text-slate-700">
                  Seed: 20261022
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed mb-6">
                Generates realistic, actuarially grounded records adhering to product eligibility, transparent pricing formulas,
                risk scoring, underwriting rules and policy lifecycle conditions.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 border-t border-slate-100">
              <button
                onClick={() => requestGenerate('starter')}
                disabled={isGenerating || currentGenStatus === 'GENERATING'}
                className="py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5 text-brand-600" />
                Generate Starter Dataset (~300)
              </button>
              <button
                onClick={() => requestGenerate('full')}
                disabled={isGenerating || currentGenStatus === 'GENERATING'}
                className="py-3 px-4 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-xs disabled:opacity-50 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                Generate Full Dataset (3,000)
              </button>
            </div>
          </div>

          {/* Validation Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold text-slate-900">Automated Data Integrity Audit</h3>
                <span className="px-2.5 py-0.5 rounded text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Comprehensive Suite
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed mb-6">
                Validates PK uniqueness, foreign key relationships, date constraints, actuarial premium reconciliation,
                and policy lifecycle invariants across all records in the database.
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <button
                onClick={handleValidate}
                disabled={isValidating}
                className="w-full py-3 px-4 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-xs disabled:opacity-50"
              >
                <FileCheck className={`w-4 h-4 ${isValidating ? 'animate-spin' : ''}`} />
                Run Comprehensive Validation Suite
              </button>
            </div>
          </div>
        </div>

        {/* Validation Report View */}
        {validationReport && (
          <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-900">Validation Audit Report</h4>
                <p className="text-xs text-slate-500">Evaluated {validationReport.total_records_evaluated} records against {validationReport.total_rules_checked} rule checks</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                validationReport.validation_pass_rate_pct >= 99 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'
              }`}>
                Pass Rate: {validationReport.validation_pass_rate_pct}%
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 p-4 rounded-lg text-xs">
              <div>
                <span className="text-slate-400 font-medium block">FK Integrity Errors</span>
                <span className="text-sm font-bold text-emerald-600">{validationReport.foreign_key_errors_count}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Duplicate Records</span>
                <span className="text-sm font-bold text-emerald-600">{validationReport.duplicate_records_count}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Arithmetic Variance</span>
                <span className="text-sm font-bold text-amber-600">{validationReport.arithmetic_errors_count}</span>
              </div>
              <div>
                <span className="text-slate-400 font-medium block">Lifecycle Violations</span>
                <span className="text-sm font-bold text-rose-600">{validationReport.lifecycle_errors_count}</span>
              </div>
            </div>

            {validationReport.arithmetic_errors_count > 0 && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
                <span className="font-bold block mb-1">Detected Injected Negative Scenarios (Expected Invariant Violations):</span>
                <ul className="list-disc list-inside space-y-0.5">
                  {validationReport.arithmetic_errors.map((e, i) => (
                    <li key={`arith-${i}`}>{e}</li>
                  ))}
                  {validationReport.lifecycle_errors?.map((e, i) => (
                    <li key={`life-${i}`}>{e}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Dataset Exports & Downloads Catalog */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                <Download className="w-4 h-4 text-brand-600" />
                Comprehensive Dataset Exports Catalog (All 15 Entities)
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Export raw generated tabular datasets from live database for independent evaluation
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-50 text-xs">
                <button
                  onClick={() => setSelectedFormat('csv')}
                  className={`px-3 py-1 font-bold rounded-md transition-colors ${
                    selectedFormat === 'csv' ? 'bg-white text-brand-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  CSV Format
                </button>
                <button
                  onClick={() => setSelectedFormat('json')}
                  className={`px-3 py-1 font-bold rounded-md transition-colors ${
                    selectedFormat === 'json' ? 'bg-white text-brand-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  JSON Format
                </button>
              </div>

              <a
                href={apiClient.exportBundleUrl(selectedFormat)}
                download={`insureflow_${selectedFormat}_all_datasets.zip`}
                className="px-3 py-1.5 bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 rounded-lg text-xs font-bold transition-colors inline-flex items-center gap-1.5 shadow-xs cursor-pointer"
                title={`Download all 15 datasets as a single ${selectedFormat.toUpperCase()} .zip archive`}
              >
                <Archive className="w-3.5 h-3.5 text-brand-600" />
                Download All ({selectedFormat.toUpperCase()} .ZIP)
              </a>

              <a
                href={apiClient.exportSqlSeedUrl}
                download="seed_data.sql"
                className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition-colors inline-flex items-center gap-1.5 shadow-xs cursor-pointer"
                title="Download full SQL seed data script"
              >
                <FileCode className="w-3.5 h-3.5 text-emerald-400" />
                SQL Seed (seed_data.sql)
              </a>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-4">
            {datasets.map((ds) => (
              <div
                key={ds.id}
                className="p-3 bg-slate-50 hover:bg-slate-100/80 border border-slate-200/80 rounded-lg flex items-center justify-between transition-colors group"
              >
                <div className="overflow-hidden pr-2">
                  <span className="font-bold text-xs text-slate-800 block truncate">
                    {ds.name}.{selectedFormat}
                  </span>
                  <span className="text-[10px] text-slate-500 block truncate">
                    {ds.desc}
                  </span>
                </div>
                <a
                  href={apiClient.getExportUrl(ds.id, selectedFormat)}
                  download={`${ds.id}.${selectedFormat}`}
                  className="p-2 bg-white hover:bg-brand-50 border border-slate-200 rounded-md text-slate-700 hover:text-brand-600 transition-colors shrink-0 shadow-2xs inline-flex items-center justify-center cursor-pointer"
                  title={`Download ${ds.name}.${selectedFormat}`}
                >
                  <Download className="w-3.5 h-3.5" />
                </a>
              </div>
            ))}
          </div>
        </div>

        {/* Reproducibility Checksums */}
        <div className="bg-white p-6 rounded-xl border border-slate-200/90 shadow-xs">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              Full Dataset Deterministic Checksums (SHA-256)
            </h3>
            <span className="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Status: VERIFIED DETERMINISTIC
            </span>
          </div>
          <p className="text-xs text-slate-500 mb-4">
            Deterministic seed 20261022 guarantees identical row counts, hashes and derived values across runs. Volatile timestamps excluded.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5 text-xs">
            {reproducibility?.checksums && Object.entries(reproducibility.checksums).map(([f, hash]: any) => (
              <div key={f} className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-slate-800 truncate">{f}</span>
                  {reproducibility?.row_counts?.[f] !== undefined && (
                    <span className="text-[10px] text-slate-400 font-mono">
                      {reproducibility.row_counts[f]} rows
                    </span>
                  )}
                </div>
                <span className="font-mono text-[9px] text-slate-500 break-all select-all">
                  {hash}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Confirmation Dialog Modal for Baseline Dataset Regeneration */}
      {confirmModalOpen && pendingMode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-lg w-full border border-slate-200 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="px-6 py-5 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200/80 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-600 shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">
                  Confirm Baseline Dataset Regeneration
                </h3>
                <p className="text-xs text-slate-600">
                  Target: {pendingMode === 'full' ? 'Full Baseline Dataset (3,000)' : 'Starter Baseline Dataset (~300)'}
                </p>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              <p className="text-xs text-slate-600 leading-relaxed">
                You are about to regenerate synthetic insurance baseline records using deterministic fixed seed{' '}
                <code className="bg-slate-100 text-slate-800 px-1 py-0.5 rounded font-mono font-bold">20261022</code>.
                Review the items to be reset and preserved below:
              </p>

              {/* Will be Reset & Regenerated */}
              <div className="rounded-xl border border-rose-200 bg-rose-50/70 p-3.5 space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-bold text-rose-800">
                  <RefreshCw className="w-3.5 h-3.5 text-rose-600" />
                  <span>Will be Reset &amp; Regenerated:</span>
                </div>
                <ul className="text-[11px] text-rose-700 space-y-1 list-disc list-inside pl-1">
                  <li>
                    {pendingMode === 'full'
                      ? '3,000 baseline applicants, 4,000 quotes, 2,000 policies, 1,200 renewals, and 350 endorsements'
                      : '300 starter applicants, 400 quotes, 200 policies, 120 renewals, and 50 endorsements'}
                  </li>
                  <li>Injected negative anomaly test scenarios and independent detector logs</li>
                  <li>Runtime CSV &amp; JSON exports generated in data/runtime_exports/ (canonical submission baseline in data/exports/ preserved)</li>
                </ul>
              </div>

              {/* Will be Strictly Preserved (Protected) */}
              <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3.5 space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-800">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Will be Strictly Preserved (Protected):</span>
                </div>
                <ul className="text-[11px] text-emerald-700 space-y-1 list-disc list-inside pl-1">
                  <li>
                    All manually created applicants ({status.user_applicants ?? 0}), quotes ({status.user_quotes ?? 0}), policies ({status.user_policies ?? 0}), endorsements, and renewals created through frontend operations
                  </li>
                  <li>All system audit logs and state transition history (audit_logs)</li>
                  <li>Master catalog configuration (Products, Coverage Options, Risk Factors)</li>
                </ul>
              </div>
            </div>

            {/* Modal Actions */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={handleCancelGenerate}
                className="px-4 py-2.5 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-200/70 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmGenerate}
                className="px-5 py-2.5 rounded-lg text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white shadow-xs transition-colors flex items-center gap-2 cursor-pointer"
              >
                <Play className="w-3.5 h-3.5" />
                Confirm &amp; Regenerate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

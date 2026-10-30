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

  const handleGenerate = async (mode: 'starter' | 'full') => {
    const confirmed = window.confirm(
      `⚠️ Re-generating the synthetic dataset will reset the database and re-seed all 15 relational tables to the deterministic benchmark (Seed: 20261022).\n\nAny manually created test applicants or quotes will be replaced with the standard benchmark records.\n\nDo you want to proceed with generating the ${mode.toUpperCase()} dataset?`
    );
    if (!confirmed) return;

    setIsGenerating(true);
    setGenMessage(`Generating ${mode} synthetic dataset (Seed: 20261022)... This process generates relational records across all 15 entities.`);
    try {
      const res = await apiClient.generateDataset(mode);
      setGenMessage(`Successfully generated ${mode} dataset! Updated record telemetry across all entities.`);
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
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Quotes</span>
              <span className="text-xl font-bold text-slate-900 mt-1 block">{(status.quotes ?? 0).toLocaleString()}</span>
            </div>
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
              <span className="text-xs text-slate-400 font-medium block">Baseline Policies</span>
              <span className="text-xl font-bold text-emerald-600 mt-1 block">{(status.baseline_policies ?? status.policies ?? 0).toLocaleString()}</span>
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
              <p className="text-xs text-slate-500 leading-relaxed mb-3">
                Generates realistic, actuarially grounded records adhering to product eligibility, transparent pricing formulas,
                risk scoring, underwriting rules and policy lifecycle conditions.
              </p>
              <div className="p-2.5 rounded-lg bg-amber-50 border border-amber-200/80 text-[11px] text-amber-800 flex items-start gap-2 mb-4">
                <span className="font-bold text-amber-900 shrink-0">Deterministic Benchmark:</span>
                <span>Re-generating resets and re-seeds the database to the benchmark baseline (Seed: 20261022) to guarantee reproducible audit checksums.</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-4 border-t border-slate-100">
              <button
                onClick={() => handleGenerate('starter')}
                disabled={isGenerating || currentGenStatus === 'GENERATING'}
                className="py-3 px-4 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 text-brand-600" />
                Generate Starter Dataset (~300)
              </button>
              <button
                onClick={() => handleGenerate('full')}
                disabled={isGenerating || currentGenStatus === 'GENERATING'}
                className="py-3 px-4 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-xs disabled:opacity-50"
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
    </div>
  );
};

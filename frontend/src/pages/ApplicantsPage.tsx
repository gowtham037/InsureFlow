import React, { useEffect, useState } from 'react';
import { Header } from '../components/Header';
import { apiClient } from '../api/client';
import { Applicant, InsuredAsset } from '../types';
import { Modal } from '../components/Modal';
import { Search, Plus, Eye, User, Home, Car, Heart, ChevronLeft, ChevronRight, Activity, ShieldCheck } from 'lucide-react';

export const ApplicantsPage: React.FC = () => {
  const [applicants, setApplicants] = useState<Applicant[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedApplicant, setSelectedApplicant] = useState<Applicant | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '1990-01-01',
    gender: 'FEMALE',
    address_line: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'USA',
    annual_income: 75000,
    credit_score: 720,
    occupation: 'Professional',
    employment_status: 'EMPLOYED',
    claims_count_5yr: 0
  });

  const fetchApplicants = async (p = page, q = search) => {
    setLoading(true);
    try {
      const data = await apiClient.getApplicants(p, pageSize, q);
      setApplicants(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch applicants:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplicants(page, search);
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchApplicants(1, search);
  };

  const handleViewDetail = async (id: number) => {
    try {
      const app = await apiClient.getApplicant(id);
      setSelectedApplicant(app);
      setIsDetailOpen(true);
    } catch (err) {
      console.error('Failed to get applicant detail:', err);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.createApplicant(formData);
      setIsCreateOpen(false);
      fetchApplicants(1, search);
    } catch (err) {
      alert('Failed to create applicant. Check field inputs.');
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="flex-1 flex flex-col pb-12">
      <Header
        title="Applicant Directory"
        subtitle="Manage master policyholders, insured profiles, credit telemetry and declared assets"
        onRefresh={() => fetchApplicants(page, search)}
        isRefreshing={loading}
      />

      <div className="p-8 space-y-6">
        {/* Controls Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
          <form onSubmit={handleSearchSubmit} className="relative w-full sm:w-96">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by name, ID, email, or city..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </form>

          <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
            <button
              onClick={() => setIsCreateOpen(true)}
              className="flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-xs transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Applicant
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 text-xs uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Business ID</th>
                  <th className="py-3 px-4">Applicant Name</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Age / Gender</th>
                  <th className="py-3 px-4">Credit Score</th>
                  <th className="py-3 px-4">5Yr Claims</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading && applicants.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      <Activity className="w-6 h-6 animate-spin mx-auto mb-2 text-brand-600" />
                      Loading applicants...
                    </td>
                  </tr>
                ) : applicants.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-8 text-center text-slate-400">
                      No applicants found matching criteria.
                    </td>
                  </tr>
                ) : (
                  applicants.map((app) => (
                    <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-medium text-brand-600 text-xs">
                        {app.business_id}
                      </td>
                      <td className="py-3.5 px-4">
                        <div className="font-semibold text-slate-900">{app.first_name} {app.last_name}</div>
                        <div className="text-xs text-slate-400">{app.email}</div>
                      </td>
                      <td className="py-3.5 px-4 text-xs text-slate-600">
                        {app.city}, {app.state}
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        {app.age} yrs <span className="text-slate-400">({app.gender})</span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${
                          app.credit_score >= 720 ? 'bg-emerald-50 text-emerald-700' :
                          app.credit_score >= 620 ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700'
                        }`}>
                          {app.credit_score}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-xs">
                        <span className={`font-medium ${app.claims_count_5yr > 1 ? 'text-rose-600' : 'text-slate-600'}`}>
                          {app.claims_count_5yr} claims
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => handleViewDetail(app.id)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-600 hover:text-brand-600 hover:bg-slate-100 rounded-md transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View
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
              <span className="font-semibold text-slate-700">{total}</span> applicants
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

      {/* Detail Modal */}
      <Modal
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        title={`Applicant Profile: ${selectedApplicant?.business_id}`}
        maxWidth="max-w-3xl"
      >
        {selectedApplicant && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div>
                <span className="text-xs text-slate-400 block">Full Name</span>
                <span className="text-sm font-bold text-slate-900">{selectedApplicant.first_name} {selectedApplicant.last_name}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Email Address</span>
                <span className="text-sm font-semibold text-slate-700">{selectedApplicant.email}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Phone</span>
                <span className="text-sm font-semibold text-slate-700">{selectedApplicant.phone}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Age & Birthdate</span>
                <span className="text-sm font-semibold text-slate-700">{selectedApplicant.age} yrs ({selectedApplicant.date_of_birth})</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Credit Score</span>
                <span className="text-sm font-bold text-brand-600">{selectedApplicant.credit_score}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Annual Income</span>
                <span className="text-sm font-bold text-slate-900">${selectedApplicant.annual_income?.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Occupation / Status</span>
                <span className="text-sm font-semibold text-slate-700">{selectedApplicant.occupation} ({selectedApplicant.employment_status})</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Residence Location</span>
                <span className="text-sm font-semibold text-slate-700">{selectedApplicant.city}, {selectedApplicant.state} {selectedApplicant.postal_code}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block">Historical 5Yr Claims</span>
                <span className="text-sm font-bold text-slate-900">{selectedApplicant.claims_count_5yr} claims</span>
              </div>
            </div>

            {/* Assets List */}
            <div>
              <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-brand-600" />
                Declared Insurable Assets ({selectedApplicant.assets?.length ?? 0})
              </h4>
              <div className="space-y-3">
                {selectedApplicant.assets && selectedApplicant.assets.length > 0 ? (
                  selectedApplicant.assets.map((asset) => (
                    <div key={asset.id} className="p-3.5 bg-white rounded-lg border border-slate-200 shadow-xs flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center text-slate-700">
                          {asset.asset_type === 'MOTOR_VEHICLE' && <Car className="w-5 h-5 text-blue-600" />}
                          {asset.asset_type === 'RESIDENTIAL_PROPERTY' && <Home className="w-5 h-5 text-emerald-600" />}
                          {asset.asset_type === 'INDIVIDUAL_HEALTH' && <Heart className="w-5 h-5 text-rose-600" />}
                        </div>
                        <div>
                          <div className="text-xs font-mono font-medium text-brand-600">{asset.business_id}</div>
                          <div className="text-sm font-bold text-slate-900">{asset.make_model} ({asset.year_built_or_manufactured})</div>
                          <div className="text-xs text-slate-500">Tier: {asset.location_tier}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-slate-400 block">Declared Value</span>
                        <span className="text-sm font-bold text-slate-900">${asset.asset_value?.toLocaleString()}</span>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-400">No assets registered for this applicant.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Create Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Register New Applicant"
        maxWidth="max-w-2xl"
      >
        <form onSubmit={handleCreateSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">First Name</label>
              <input
                required
                type="text"
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Last Name</label>
              <input
                required
                type="text"
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Email</label>
              <input
                required
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Phone</label>
              <input
                required
                type="text"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Date of Birth</label>
              <input
                required
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Credit Score (300-850)</label>
              <input
                required
                type="number"
                min="300"
                max="850"
                value={formData.credit_score}
                onChange={(e) => setFormData({ ...formData, credit_score: parseInt(e.target.value) || 300 })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">Annual Income ($)</label>
              <input
                required
                type="number"
                value={formData.annual_income}
                onChange={(e) => setFormData({ ...formData, annual_income: parseFloat(e.target.value) || 0 })}
                className="w-full text-sm p-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">City & State</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  required
                  placeholder="City"
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full text-sm p-2 border border-slate-200 rounded-lg"
                />
                <input
                  required
                  placeholder="State"
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full text-sm p-2 border border-slate-200 rounded-lg"
                />
              </div>
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
              className="px-4 py-2 bg-brand-600 text-white rounded-lg text-sm font-semibold hover:bg-brand-700 shadow-xs"
            >
              Save Applicant
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

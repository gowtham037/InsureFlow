import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { ApplicantsPage } from './pages/ApplicantsPage';
import { ProductsPage } from './pages/ProductsPage';
import { QuotesPage } from './pages/QuotesPage';
import { UnderwritingPage } from './pages/UnderwritingPage';
import { PoliciesPage } from './pages/PoliciesPage';
import { EndorsementsPage } from './pages/EndorsementsPage';
import { RenewalsPage } from './pages/RenewalsPage';
import { AnomalyCenterPage } from './pages/AnomalyCenterPage';
import { DataManagementPage } from './pages/DataManagementPage';
import { ReportsPage } from './pages/ReportsPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex">
        <Sidebar />
        <main className="flex-1 pl-64 min-w-0 flex flex-col">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/applicants" element={<ApplicantsPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/quotes" element={<QuotesPage />} />
            <Route path="/underwriting" element={<UnderwritingPage />} />
            <Route path="/policies" element={<PoliciesPage />} />
            <Route path="/endorsements" element={<EndorsementsPage />} />
            <Route path="/renewals" element={<RenewalsPage />} />
            <Route path="/anomalies" element={<AnomalyCenterPage />} />
            <Route path="/data-management" element={<DataManagementPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;

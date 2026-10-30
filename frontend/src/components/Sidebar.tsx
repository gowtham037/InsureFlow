import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  ShieldCheck,
  FileSpreadsheet,
  Cpu,
  FileCheck2,
  FileEdit,
  RotateCw,
  AlertOctagon,
  Database,
  BarChart3,
  Shield
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Applicants', path: '/applicants', icon: Users },
  { name: 'Products', path: '/products', icon: ShieldCheck },
  { name: 'Quotes', path: '/quotes', icon: FileSpreadsheet },
  { name: 'Underwriting', path: '/underwriting', icon: Cpu },
  { name: 'Policies', path: '/policies', icon: FileCheck2 },
  { name: 'Endorsements', path: '/endorsements', icon: FileEdit },
  { name: 'Renewals', path: '/renewals', icon: RotateCw },
  { name: 'Anomaly Center', path: '/anomalies', icon: AlertOctagon },
  { name: 'Data Management', path: '/data-management', icon: Database },
  { name: 'Reports', path: '/reports', icon: BarChart3 },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen fixed left-0 top-0 text-slate-300 z-30 select-none">
      {/* Brand Logo & Title */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-600 to-brand-400 flex items-center justify-center shadow-lg shadow-brand-500/20 text-white">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-lg tracking-tight text-white block leading-tight">InsureFlow</span>
          <span className="text-xs text-brand-400 font-medium tracking-wide">ENTERPRISE CORE</span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          Operations & Underwriting
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-brand-600 text-white shadow-md shadow-brand-600/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span className="flex-1 truncate">{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40 text-xs text-slate-400 flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <span>Engine Seed</span>
          <span className="font-mono text-brand-400 font-semibold">20261022</span>
        </div>
        <div className="flex items-center justify-between">
          <span>System Status</span>
          <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Operational
          </span>
        </div>
      </div>
    </aside>
  );
};

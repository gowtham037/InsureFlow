import React from 'react';

interface BadgeProps {
  variant?: 'risk' | 'status' | 'default';
  value: string;
  className?: string;
}

export const RiskBadge: React.FC<{ tier: string }> = ({ tier }) => {
  const t = tier ? tier.toUpperCase() : 'LOW';
  let colorStyles = 'bg-emerald-50 text-emerald-700 border-emerald-200';

  if (t === 'MEDIUM') {
    colorStyles = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (t === 'HIGH') {
    colorStyles = 'bg-orange-50 text-orange-700 border-orange-200';
  } else if (t === 'CRITICAL') {
    colorStyles = 'bg-rose-50 text-rose-700 border-rose-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${colorStyles}`}>
      {t}
    </span>
  );
};

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const s = status ? status.toUpperCase() : 'DRAFT';
  let styles = 'bg-slate-100 text-slate-700 border-slate-200';

  if (['ACTIVE', 'ACCEPTED', 'APPROVED'].includes(s)) {
    styles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (['APPROVED_WITH_CONDITIONS', 'OFFERED', 'EVALUATED'].includes(s)) {
    styles = 'bg-blue-50 text-blue-700 border-blue-200';
  } else if (['REFERRED', 'PENDING', 'SUSPENDED'].includes(s)) {
    styles = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (['DECLINED', 'REJECTED', 'CANCELLED', 'FAILED'].includes(s)) {
    styles = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (['EXPIRED'].includes(s)) {
    styles = 'bg-slate-100 text-slate-500 border-slate-200';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles}`}>
      {s.replace(/_/g, ' ')}
    </span>
  );
};

export const SeverityBadge: React.FC<{ severity: string }> = ({ severity }) => {
  const sev = severity ? severity.toUpperCase() : 'LOW';
  let styles = 'bg-blue-50 text-blue-700 border-blue-200';

  if (sev === 'MEDIUM') {
    styles = 'bg-amber-50 text-amber-700 border-amber-200';
  } else if (sev === 'HIGH') {
    styles = 'bg-orange-50 text-orange-700 border-orange-200';
  } else if (sev === 'CRITICAL') {
    styles = 'bg-rose-50 text-rose-700 border-rose-200';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold border ${styles}`}>
      {sev}
    </span>
  );
};

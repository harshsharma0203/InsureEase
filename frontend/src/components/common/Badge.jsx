import React from 'react';

const BADGE_VARIANTS = {
  // Green - Success
  ACTIVE: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  APPROVED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  SETTLED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  PAID: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  COMPLETED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  SUCCESS: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  LOW: 'bg-emerald-50 text-emerald-700 border-emerald-200',

  // Amber - Warning / Pending
  PENDING: 'bg-amber-50 text-amber-700 border-amber-200',
  UNDER_REVIEW: 'bg-amber-50 text-amber-700 border-amber-200',
  PARTIALLY_PAID: 'bg-amber-50 text-amber-700 border-amber-200',
  PENDING_RENEWAL: 'bg-amber-50 text-amber-700 border-amber-200',
  DOCUMENTS_REQUIRED: 'bg-amber-50 text-amber-700 border-amber-200',
  ADDITIONAL_INFO_REQUIRED: 'bg-amber-50 text-amber-700 border-amber-200',
  SETTLEMENT_PENDING: 'bg-amber-50 text-amber-700 border-amber-200',
  MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',

  // Red - Danger / Reject
  REJECTED: 'bg-rose-50 text-rose-700 border-rose-200',
  OVERDUE: 'bg-rose-50 text-rose-700 border-rose-200',
  CANCELLED: 'bg-rose-50 text-rose-700 border-rose-200',
  EXPIRED: 'bg-slate-100 text-slate-700 border-slate-300',
  TERMINATED: 'bg-rose-50 text-rose-700 border-rose-200',
  FAILED: 'bg-rose-50 text-rose-700 border-rose-200',
  HIGH: 'bg-orange-50 text-orange-700 border-orange-200',
  VERY_HIGH: 'bg-rose-50 text-rose-700 border-rose-200',

  // Blue / Slate - Info
  SUBMITTED: 'bg-blue-50 text-blue-700 border-blue-200',
  VERIFIED: 'bg-sky-50 text-sky-700 border-sky-200',
  ISSUED: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  UNPAID: 'bg-orange-50 text-orange-700 border-orange-200',
  DRAFT: 'bg-slate-100 text-slate-700 border-slate-200',
  INFO: 'bg-sky-50 text-sky-700 border-sky-200',
};

export const Badge = ({ status, text, className = '' }) => {
  const norm = (status || '').toUpperCase();
  const variant = BADGE_VARIANTS[norm] || 'bg-slate-100 text-slate-700 border-slate-200';
  const label = text || status?.replace(/_/g, ' ') || 'N/A';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize ${variant} ${className}`}
    >
      {label}
    </span>
  );
};

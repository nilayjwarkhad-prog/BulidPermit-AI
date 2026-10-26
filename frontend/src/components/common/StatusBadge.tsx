import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle2, Clock, HelpCircle, XCircle, ShieldCheck } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  type?: 'severity' | 'finding_status' | 'checklist' | 'job' | 'jurisdiction';
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type = 'severity', size = 'sm' }) => {
  const norm = (status || '').toLowerCase().trim();

  let bg = 'bg-slate-100 text-slate-700 border-slate-200';
  let Icon = HelpCircle;
  let label = status;

  if (type === 'severity') {
    if (norm === 'critical') {
      bg = 'bg-rose-50 text-rose-700 border-rose-200/80';
      Icon = AlertCircle;
      label = 'Critical';
    } else if (norm === 'warning') {
      bg = 'bg-amber-50 text-amber-800 border-amber-200/80';
      Icon = AlertTriangle;
      label = 'Warning';
    } else {
      bg = 'bg-blue-50 text-blue-700 border-blue-200/80';
      Icon = HelpCircle;
      label = 'Informational';
    }
  } else if (type === 'finding_status') {
    if (norm === 'open') {
      bg = 'bg-rose-50 text-rose-700 border-rose-200/80';
      Icon = AlertCircle;
      label = 'Open';
    } else if (norm === 'in_review') {
      bg = 'bg-amber-50 text-amber-800 border-amber-200/80';
      Icon = Clock;
      label = 'In Review';
    } else if (norm === 'resolved') {
      bg = 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
      Icon = CheckCircle2;
      label = 'Resolved';
    } else if (norm === 'dismissed') {
      bg = 'bg-slate-100 text-slate-600 border-slate-200';
      Icon = XCircle;
      label = 'Dismissed';
    }
  } else if (type === 'checklist') {
    if (norm === 'complete') {
      bg = 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
      Icon = CheckCircle2;
      label = 'Present';
    } else if (norm === 'missing') {
      bg = 'bg-rose-50 text-rose-700 border-rose-200/80';
      Icon = XCircle;
      label = 'Missing';
    } else if (norm === 'needs_verification') {
      bg = 'bg-amber-50 text-amber-800 border-amber-200/80';
      Icon = AlertTriangle;
      label = 'Needs Review';
    } else if (norm === 'not_applicable') {
      bg = 'bg-slate-100 text-slate-500 border-slate-200';
      Icon = HelpCircle;
      label = 'Not Applicable';
    } else {
      bg = 'bg-slate-100 text-slate-600 border-slate-200';
      Icon = HelpCircle;
      label = 'Unverified';
    }
  } else if (type === 'job') {
    if (norm === 'completed') {
      bg = 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
      Icon = CheckCircle2;
      label = 'Completed';
    } else if (norm === 'processing') {
      bg = 'bg-brand-50 text-brand-700 border-brand-200/80';
      Icon = Clock;
      label = 'Processing';
    } else if (norm === 'failed') {
      bg = 'bg-rose-50 text-rose-700 border-rose-200/80';
      Icon = AlertCircle;
      label = 'Failed';
    } else {
      bg = 'bg-slate-100 text-slate-600 border-slate-200';
      Icon = Clock;
      label = 'Queued';
    }
  } else if (type === 'jurisdiction') {
    if (norm === 'supported') {
      bg = 'bg-emerald-50 text-emerald-700 border-emerald-200/80';
      Icon = ShieldCheck;
      label = 'Checklist Verified';
    } else {
      bg = 'bg-slate-100 text-slate-600 border-slate-200';
      Icon = HelpCircle;
      label = 'General Standard';
    }
  }

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1 font-medium rounded-md border ${bg} ${px}`}>
      <Icon className={size === 'sm' ? 'w-3 h-3 shrink-0' : 'w-3.5 h-3.5 shrink-0'} />
      <span>{label}</span>
    </span>
  );
};

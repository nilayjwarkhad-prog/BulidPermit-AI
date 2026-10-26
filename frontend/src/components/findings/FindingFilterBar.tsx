import React from 'react';

interface FindingFilterBarProps {
  severity: string;
  category: string;
  status: string;
  onSeverityChange: (s: string) => void;
  onCategoryChange: (c: string) => void;
  onStatusChange: (st: string) => void;
  counts: {
    total: number;
    critical: number;
    warning: number;
    resolved: number;
  };
}

export const FindingFilterBar: React.FC<FindingFilterBarProps> = ({
  severity,
  category,
  status,
  onSeverityChange,
  onCategoryChange,
  onStatusChange,
  counts
}) => {
  return (
    <div className="saas-card p-3 sm:p-4 flex flex-wrap items-center justify-between gap-3">
      
      {/* Quick Filter Buttons */}
      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        <button
          type="button"
          onClick={() => { onSeverityChange(''); onStatusChange(''); }}
          className={`px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer border ${
            !severity && !status 
              ? 'bg-slate-900 text-white border-slate-900' 
              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
          }`}
        >
          All ({counts.total})
        </button>

        <button
          type="button"
          onClick={() => { onSeverityChange('critical'); onStatusChange(''); }}
          className={`px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer border ${
            severity === 'critical' 
              ? 'bg-rose-700 text-white border-rose-700' 
              : 'bg-white text-rose-800 border-rose-200 hover:bg-rose-50'
          }`}
        >
          Critical ({counts.critical})
        </button>

        <button
          type="button"
          onClick={() => { onSeverityChange('warning'); onStatusChange(''); }}
          className={`px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer border ${
            severity === 'warning' 
              ? 'bg-amber-700 text-white border-amber-700' 
              : 'bg-white text-amber-900 border-amber-200 hover:bg-amber-50'
          }`}
        >
          Warnings ({counts.warning})
        </button>

        <button
          type="button"
          onClick={() => { onSeverityChange(''); onStatusChange('resolved'); }}
          className={`px-3 py-1.5 rounded-md font-medium transition-colors cursor-pointer border ${
            status === 'resolved' 
              ? 'bg-emerald-700 text-white border-emerald-700' 
              : 'bg-white text-emerald-800 border-emerald-200 hover:bg-emerald-50'
          }`}
        >
          Resolved ({counts.resolved})
        </button>
      </div>

      {/* Category / Type Dropdown */}
      <div className="flex items-center gap-2 text-xs">
        <label className="text-slate-500 font-medium whitespace-nowrap">Filter by Type:</label>
        <select
          value={category}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="saas-select text-xs py-1.5 px-2.5 max-w-[210px] cursor-pointer"
        >
          <option value="">All Finding Types</option>
          <option value="Inconsistency">Document Inconsistency</option>
          <option value="Missing Document">Potentially Missing Document</option>
          <option value="Missing Field">Missing Annotation</option>
          <option value="Zoning & Setbacks">Zoning & Setbacks</option>
          <option value="Page Quality">Page Quality</option>
        </select>
      </div>

    </div>
  );
};

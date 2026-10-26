import React from 'react';
import { ShieldAlert } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white py-8 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
        
        {/* Compliance disclaimer */}
        <div className="flex items-start gap-3 p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            <strong className="font-semibold text-slate-800">Pre-Submission Preparation Notice:</strong> BuildPermit AI assists homeowners, architects, and builders with document organization, completeness checks, and potential inconsistency detection prior to permit filing. This software does not issue building permits, certify structural engineering safety, or guarantee approval by any municipal, county, or regional building department. All submittals must be reviewed by licensed design professionals according to applicable local building codes.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <p>© {new Date().getFullYear()} BuildPermit AI Platform. All rights reserved.</p>
          <div className="flex items-center gap-6 text-slate-600">
            <span>Jurisdiction Rulesets: Verified & Non-Regulatory Samples</span>
            <span>Local AI Model Integration: Gemma 4 (gemma4:e2b) / Ollama</span>
          </div>
        </div>

      </div>
    </footer>
  );
};

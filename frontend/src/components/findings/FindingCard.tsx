import React, { useState } from 'react';
import { Finding } from '../../types';
import { StatusBadge } from '../common/StatusBadge';
import { 
  FileText, 
  ArrowRight, 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  Check, 
  Info, 
  Eye, 
  Layers, 
  ShieldAlert, 
  CheckCircle2, 
  HelpCircle 
} from 'lucide-react';
import { api } from '../../services/api';

interface FindingCardProps {
  finding: Finding;
  onStatusChange: (updated: Finding) => void;
  onOpenDocument?: (documentId: string, pageNumber: number) => void;
}

interface ConflictPair {
  sourceA: string;
  valueA: string;
  pageA?: number;
  sourceB: string;
  valueB: string;
  pageB?: number;
}

// Parses evidence_text containing conflicting values (e.g., "Sheet A (Page 2): '124 Main' vs Sheet B (Page 4): '142 Main'")
function parseConflictEvidence(evidenceText?: string): ConflictPair | null {
  if (!evidenceText || !evidenceText.includes(' vs ')) return null;
  const parts = evidenceText.split(' vs ');
  if (parts.length !== 2) return null;

  const extractPage = (str: string): number | undefined => {
    const m = str.match(/Page(?:s)?\s*(\d+)/i);
    return m ? parseInt(m[1], 10) : undefined;
  };

  const cleanPart = (str: string) => {
    const colonIdx = str.indexOf(':');
    if (colonIdx !== -1) {
      const source = str.slice(0, colonIdx).trim();
      const val = str.slice(colonIdx + 1).trim().replace(/^['"]|['"]$/g, '');
      return { source, val };
    }
    return { source: 'Reference', val: str.trim() };
  };

  const partA = cleanPart(parts[0]);
  const partB = cleanPart(parts[1]);

  return {
    sourceA: partA.source,
    valueA: partA.val,
    pageA: extractPage(parts[0]),
    sourceB: partB.source,
    valueB: partB.val,
    pageB: extractPage(parts[1])
  };
}

// Separates the core finding explanation from AI-generated analysis notes
function splitExplanation(explanation: string): { coreText: string; aiNote?: string } {
  const marker = explanation.includes('\n\nAI Analysis:') 
    ? '\n\nAI Analysis:' 
    : (explanation.includes('\n\nAI Advisory Note:') ? '\n\nAI Advisory Note:' : null);

  if (!marker) {
    return { coreText: explanation.trim() };
  }

  const [main, ...rest] = explanation.split(marker);
  return {
    coreText: main.trim(),
    aiNote: rest.join(marker).trim()
  };
}

// Categorizes the finding into one of 4 distinct types (plus unverified sample guidance)
export function getFindingClassification(finding: Finding): {
  typeLabel: string;
  badgeStyle: string;
  isVerified: boolean;
  typeIcon: React.ReactNode;
} {
  const cat = (finding.category || '').toLowerCase();
  const ruleRef = (finding.rule_reference || '').toLowerCase();
  const ruleCode = (finding.rule_code || '').toLowerCase();

  // 1. Document Inconsistency
  if (cat.includes('inconsisten') || ruleCode.includes('mismatch') || ruleCode.includes('conflict')) {
    return {
      typeLabel: 'Document Inconsistency',
      badgeStyle: 'bg-purple-50 text-purple-800 border-purple-200',
      isVerified: false,
      typeIcon: <Layers className="w-3 h-3 text-purple-600" />
    };
  }

  // 2. Potentially Missing Document
  if (cat.includes('missing doc') || ruleCode.includes('missing-doc')) {
    return {
      typeLabel: 'Potentially Missing Document',
      badgeStyle: 'bg-amber-50 text-amber-900 border-amber-200',
      isVerified: false,
      typeIcon: <FileText className="w-3 h-3 text-amber-600" />
    };
  }

  // 3. Missing Annotation
  if (cat.includes('missing field') || cat.includes('annotation') || ruleCode.includes('north') || ruleCode.includes('scale')) {
    return {
      typeLabel: 'Missing Annotation',
      badgeStyle: 'bg-blue-50 text-blue-800 border-blue-200',
      isVerified: false,
      typeIcon: <Info className="w-3 h-3 text-blue-600" />
    };
  }

  // 4. Verified Jurisdiction Requirement
  if (ruleRef.includes('verified') || cat.includes('verified')) {
    return {
      typeLabel: 'Verified Jurisdiction Requirement',
      badgeStyle: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      isVerified: true,
      typeIcon: <CheckCircle2 className="w-3 h-3 text-emerald-600" />
    };
  }

  // 5. Sample Guidance (Unverified)
  return {
    typeLabel: 'Sample Guidance (Unverified)',
    badgeStyle: 'bg-slate-100 text-slate-700 border-slate-200',
    isVerified: false,
    typeIcon: <HelpCircle className="w-3 h-3 text-slate-500" />
  };
}

export const FindingCard: React.FC<FindingCardProps> = ({
  finding,
  onStatusChange,
  onOpenDocument
}) => {
  const [isDetailExpanded, setIsDetailExpanded] = useState<boolean>(false);
  const [isEditingStatus, setIsEditingStatus] = useState<boolean>(false);
  const [selectedStatus, setSelectedStatus] = useState<string>(finding.status);
  const [notes, setNotes] = useState<string>(finding.resolution_notes || '');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isRequestingAI, setIsRequestingAI] = useState<boolean>(false);

  const conflict = parseConflictEvidence(finding.evidence_text);
  const { coreText, aiNote } = splitExplanation(finding.explanation);
  const classification = getFindingClassification(finding);

  const isResolved = finding.status === 'resolved' || finding.status === 'dismissed';

  const handleStatusSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const updated = await api.updateFindingStatus(finding.id, selectedStatus, notes);
      onStatusChange(updated);
      setIsEditingStatus(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAIAdvice = async () => {
    setIsRequestingAI(true);
    try {
      const updated = await api.requestAIAdvice(finding.id);
      onStatusChange(updated);
    } finally {
      setIsRequestingAI(false);
    }
  };

  const triggerOpenSheet = (page?: number) => {
    if (!onOpenDocument) return;
    const targetPage = page || finding.page_number || 1;
    if (finding.document_id) {
      onOpenDocument(finding.document_id, targetPage);
    } else if (finding.document_name) {
      onOpenDocument(finding.document_name, targetPage);
    }
  };

  return (
    <div className={`
      saas-card p-5 transition-all space-y-3
      ${isResolved ? 'opacity-70 bg-slate-50/60' : 'bg-white hover:border-slate-300'}
    `}>
      {/* 1. Header: Classification Type, Severity, and Human Review Badge */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap items-center gap-2">
          {/* Distinct Classification Type Badge */}
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-semibold border ${classification.badgeStyle}`}>
            {classification.typeIcon}
            <span>{classification.typeLabel}</span>
          </span>

          {/* Severity Badge */}
          <StatusBadge status={finding.severity} type="severity" size="sm" />

          {/* Current Status Badge if resolved or in review */}
          {finding.status !== 'open' && (
            <StatusBadge status={finding.status} type="finding_status" size="sm" />
          )}
        </div>

        {/* Human Review Recommended Tag */}
        {finding.human_review_required && !isResolved && (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-800 bg-amber-50 border border-amber-200/90 px-2 py-0.5 rounded">
            <ShieldAlert className="w-3 h-3 text-amber-600" />
            <span>Human Review Advised</span>
          </span>
        )}
      </div>

      {/* 2. Finding Title */}
      <h3 className="text-sm sm:text-base font-bold text-slate-900 tracking-tight">
        {finding.title}
      </h3>

      {/* 3. Prominent Conflicting Values Display (if discrepancy detected) */}
      {conflict ? (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 my-2.5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
              Conflicting Values Across Sources
            </span>
            {finding.document_id && onOpenDocument && (
              <span className="text-[11px] text-slate-400">Click a sheet to view source</span>
            )}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
            {/* Side A */}
            <div className="bg-white border border-slate-200 rounded p-2.5 flex flex-col justify-between">
              <div>
                <span className="text-[11px] text-slate-500 font-medium block truncate">
                  {conflict.sourceA}
                </span>
                <span className="font-semibold text-slate-900 text-sm block mt-0.5">
                  {conflict.valueA}
                </span>
              </div>
              {conflict.pageA && onOpenDocument && (
                <button
                  type="button"
                  onClick={() => triggerOpenSheet(conflict.pageA)}
                  className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-brand-600 hover:text-brand-800 cursor-pointer self-start"
                >
                  <Eye className="w-3 h-3" />
                  <span>View Sheet (Page {conflict.pageA})</span>
                </button>
              )}
            </div>

            {/* Side B */}
            <div className="bg-white border border-rose-200 rounded p-2.5 flex flex-col justify-between">
              <div>
                <span className="text-[11px] text-slate-500 font-medium block truncate">
                  {conflict.sourceB}
                </span>
                <span className="font-semibold text-rose-900 text-sm block mt-0.5">
                  {conflict.valueB}
                </span>
              </div>
              {conflict.pageB && onOpenDocument && (
                <button
                  type="button"
                  onClick={() => triggerOpenSheet(conflict.pageB)}
                  className="mt-2 inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700 hover:text-rose-900 cursor-pointer self-start"
                >
                  <Eye className="w-3 h-3" />
                  <span>View Sheet (Page {conflict.pageB})</span>
                </button>
              )}
            </div>
          </div>
        </div>
      ) : finding.evidence_text && !isDetailExpanded && (
        <div className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-700 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2 truncate">
            <span className="font-bold text-slate-600 uppercase text-[10px] tracking-wide">Observed:</span>
            <span className="font-mono text-slate-800 truncate">{finding.evidence_text}</span>
          </div>
          {finding.document_id && onOpenDocument && (
            <button
              type="button"
              onClick={() => triggerOpenSheet(finding.page_number)}
              className="text-xs font-semibold text-brand-600 hover:text-brand-800 flex items-center gap-1 shrink-0 cursor-pointer"
            >
              <span>View Sheet {finding.page_number ? `(p. ${finding.page_number})` : ''}</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          )}
        </div>
      )}

      {/* 4. Core Concise Explanation (1-3 sentences) */}
      <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
        {coreText}
      </p>

      {/* 5. AI Advisory Explanation Panel (if generated) */}
      {aiNote && (
        <div className="p-3 bg-indigo-50/50 border border-indigo-100 rounded-lg text-xs space-y-1">
          <div className="flex items-center gap-1.5 font-semibold text-indigo-900">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>AI Pre-Check Analysis & Guidance</span>
          </div>
          <p className="text-indigo-950 leading-relaxed">{aiNote}</p>
          <p className="text-[10px] text-indigo-700/80 italic pt-0.5">
            Advisory notice: This automated guidance is non-binding. Consult your architect, engineer, or municipal building department for official code interpretations.
          </p>
        </div>
      )}

      {/* 6. Recommended Next Step */}
      {finding.recommended_action && (
        <div className="p-2.5 bg-blue-50/40 border border-blue-100 rounded-lg text-xs">
          <span className="font-semibold text-blue-950 block mb-0.5">Recommended Next Step:</span>
          <p className="text-blue-900 leading-relaxed">{finding.recommended_action}</p>
        </div>
      )}

      {/* 7. Collapsible Detail Drawer (Rule Reference, Confidence, Snippets) */}
      {isDetailExpanded && (
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs space-y-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <div>
              <span className="text-slate-500 text-[11px] block font-medium">Standard / Rule Reference:</span>
              <span className="font-semibold text-slate-800">
                {finding.rule_reference || 'Preliminary Architectural Practice Benchmark'}
              </span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block font-medium">Analysis Code & Confidence:</span>
              <span className="font-mono text-slate-700">
                {finding.rule_code || 'N/A'} • {Math.round((finding.confidence || 0) * 100)}% confidence
              </span>
            </div>
          </div>

          {finding.evidence_text && (
            <div>
              <span className="text-slate-500 text-[11px] block font-medium">Raw Extraction Evidence:</span>
              <p className="font-mono text-[11px] bg-white p-2 border border-slate-200 rounded text-slate-800 break-words mt-0.5">
                {finding.evidence_text}
              </p>
            </div>
          )}

          {finding.resolution_notes && (
            <div className="pt-1 border-t border-slate-200">
              <span className="text-emerald-800 font-semibold text-[11px] block">Resolution Notes:</span>
              <p className="text-slate-700 mt-0.5">{finding.resolution_notes}</p>
            </div>
          )}
        </div>
      )}

      {/* 8. Functional Actions Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-100 text-xs">
        
        {/* Left Action Group: View Sheet, View Detail, Explain with AI */}
        <div className="flex flex-wrap items-center gap-2">
          {/* View Sheet Action */}
          {finding.document_id && onOpenDocument && (
            <button
              type="button"
              onClick={() => triggerOpenSheet(finding.page_number)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-brand-700 bg-brand-50 hover:bg-brand-100 rounded-md font-medium border border-brand-200 transition-colors cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>View Sheet {finding.page_number ? `(Page ${finding.page_number})` : ''}</span>
            </button>
          )}

          {/* View Detail Action */}
          <button
            type="button"
            onClick={() => setIsDetailExpanded(!isDetailExpanded)}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-md font-medium transition-colors cursor-pointer border border-slate-200"
          >
            <span>{isDetailExpanded ? 'Hide Detail' : 'View Detail'}</span>
            {isDetailExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>

          {/* Explain with AI Action */}
          <button
            type="button"
            onClick={handleAIAdvice}
            disabled={isRequestingAI}
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-slate-700 hover:text-indigo-700 hover:bg-indigo-50 rounded-md font-medium transition-colors disabled:opacity-50 cursor-pointer border border-slate-200 hover:border-indigo-200"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>{isRequestingAI ? 'Generating Advice...' : (aiNote ? 'Re-Explain with AI' : 'Explain with AI')}</span>
          </button>
        </div>

        {/* Right Action Group: Mark Resolved, Re-open, Dismiss */}
        {!isEditingStatus ? (
          <div className="flex items-center gap-2">
            {!isResolved ? (
              <>
                <button
                  type="button"
                  onClick={() => { setSelectedStatus('resolved'); setIsEditingStatus(true); }}
                  className="inline-flex items-center gap-1 px-2.5 py-1 text-emerald-700 hover:bg-emerald-50 font-medium rounded border border-emerald-200 transition-colors cursor-pointer"
                >
                  <Check className="w-3 h-3" />
                  <span>Mark Resolved</span>
                </button>
                <button
                  type="button"
                  onClick={() => { setSelectedStatus('dismissed'); setIsEditingStatus(true); }}
                  className="text-slate-500 hover:text-slate-800 px-2 py-1 transition-colors cursor-pointer"
                >
                  Dismiss
                </button>
              </>
            ) : (
              <button
                type="button"
                onClick={() => { setSelectedStatus('open'); setIsEditingStatus(true); }}
                className="inline-flex items-center gap-1 px-2.5 py-1 text-slate-600 hover:bg-slate-100 font-medium rounded border border-slate-200 transition-colors cursor-pointer"
              >
                <span>Re-open Finding</span>
              </button>
            )}
          </div>
        ) : (
          <form onSubmit={handleStatusSubmit} className="w-full mt-2 pt-2 border-t border-slate-200 space-y-2">
            <div className="flex items-center gap-3">
              <label className="font-semibold text-slate-700">Update Finding Status:</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="saas-select text-xs py-1 px-2 cursor-pointer"
              >
                <option value="open">Open</option>
                <option value="in_review">In Review</option>
                <option value="resolved">Resolved</option>
                <option value="dismissed">Dismissed</option>
              </select>
            </div>
            <div>
              <input
                type="text"
                placeholder="Resolution reason (e.g. 'Architect revised Sheet A-101 to 124 Example Lane')..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="saas-input text-xs"
              />
            </div>
            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setIsEditingStatus(false)}
                className="px-2.5 py-1 text-slate-600 hover:bg-slate-100 rounded text-xs cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-3 py-1 bg-brand-600 text-white rounded text-xs font-semibold hover:bg-brand-700 cursor-pointer disabled:opacity-50"
              >
                {isSubmitting ? 'Saving...' : 'Save Resolution'}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
};

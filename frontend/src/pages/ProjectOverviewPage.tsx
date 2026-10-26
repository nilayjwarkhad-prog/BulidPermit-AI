import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, Play, CheckSquare, FileSpreadsheet, AlertTriangle, ArrowRight, CheckCircle2, Upload } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FindingCard } from '../components/findings/FindingCard';
import { DocumentViewerModal } from '../components/documents/DocumentViewerModal';
import { api } from '../services/api';
import { Project, Finding, DocumentItem, Checklist } from '../types';

export const ProjectOverviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [viewerPage, setViewerPage] = useState<number>(1);

  useEffect(() => {
    if (!id) return;
    async function loadData() {
      try {
        const [projData, findData, docsData, chkData] = await Promise.all([
          api.getProject(id!),
          api.getFindings(id!),
          api.getProjectDocuments(id!),
          api.getChecklist(id!).catch(() => null)
        ]);
        setProject(projData);
        setFindings(findData);
        setDocuments(docsData);
        setChecklist(chkData);
      } catch (err) {
        console.error('Error loading project overview:', err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [id]);

  const handleOpenDoc = (docId: string, page: number) => {
    const doc = documents.find(d => d.id === docId);
    if (doc) {
      setSelectedDoc(doc);
      setViewerPage(page);
    }
  };

  if (isLoading || !project) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-50">
        <Navbar />
        <div className="flex-1 flex items-center justify-center p-12">
          <LoadingSpinner size="lg" />
        </div>
        <Footer />
      </div>
    );
  }

  const openIssues = findings.filter(f => f.status === 'open' || f.status === 'in_review');
  const criticalCount = findings.filter(f => f.severity === 'critical' && f.status === 'open').length;
  const hasDocs = documents.length > 0;
  const chkStats = checklist?.completion_stats || { complete: 0, missing: 0, needs_verification: 0, total: 0, percentage: 0 };

  // Determine ONE clear next recommended action
  let nextAction: { title: string; desc: string; buttonLabel: string; buttonTo: string; icon: React.ReactNode };

  if (!hasDocs) {
    nextAction = {
      title: "Upload Submittal Documents",
      desc: "Add your architectural drawings, site plan, and permit application form to begin pre-check analysis.",
      buttonLabel: "Upload Documents",
      buttonTo: `/projects/${project.id}/documents`,
      icon: <Upload className="w-4 h-4" />
    };
  } else if (openIssues.length > 0) {
    nextAction = {
      title: `Review ${openIssues.length} Identified ${openIssues.length === 1 ? 'Discrepancy' : 'Discrepancies'}`,
      desc: criticalCount > 0 
        ? `${criticalCount} critical issue${criticalCount > 1 ? 's' : ''} flagged for correction or verification before submission.`
        : "Review flagged warnings and confirm drawing alignment across your plan sheets.",
      buttonLabel: "Review Findings",
      buttonTo: `/projects/${project.id}/findings`,
      icon: <AlertTriangle className="w-4 h-4" />
    };
  } else {
    nextAction = {
      title: "Submittal Package Ready for Summary Report",
      desc: "All uploaded sheets match preliminary identification standards. Generate an advisory pre-check summary.",
      buttonLabel: "Generate Report",
      buttonTo: `/projects/${project.id}/reports`,
      icon: <FileSpreadsheet className="w-4 h-4" />
    };
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <ProjectHeader project={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Next Recommended Action Banner */}
        <div className="saas-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6 border-l-4 border-l-brand-600">
          <div className="space-y-1">
            <span className="text-[11px] font-semibold text-brand-700 uppercase tracking-wider">
              Recommended Next Step
            </span>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              {nextAction.title}
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 max-w-2xl">
              {nextAction.desc}
            </p>
          </div>

          <Link
            to={nextAction.buttonTo}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-xs sm:text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 active:bg-brand-800 rounded-lg shadow-xs transition-colors shrink-0 cursor-pointer"
          >
            {nextAction.icon}
            <span>{nextAction.buttonLabel}</span>
          </Link>
        </div>

        {/* 3 Balanced Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          {/* Documents Status */}
          <div className="saas-card p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider">Submittal Documents</span>
                <FileText className="w-4 h-4 text-slate-400" />
              </div>
              <div className="text-2xl font-bold text-slate-900 mb-1">
                {documents.length} {documents.length === 1 ? 'Document' : 'Documents'}
              </div>
              <p className="text-xs text-slate-500 mb-3">
                {documents.length === 0 ? 'No files uploaded yet' : `${documents.reduce((acc, d) => acc + (d.page_count || 1), 0)} total drawing pages`}
              </p>
            </div>

            <Link
              to={`/projects/${project.id}/documents`}
              className="text-xs font-medium text-brand-600 hover:text-brand-700 inline-flex items-center gap-1 pt-2 border-t border-slate-100"
            >
              <span>Manage documents</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Checklist Completeness */}
          <div className="saas-card p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider">Checklist Completeness</span>
                <CheckSquare className="w-4 h-4 text-slate-400" />
              </div>
              <div className="text-2xl font-bold text-slate-900 mb-1">
                {chkStats.percentage}%
              </div>
              <div className="text-xs text-slate-500 space-x-2 mb-3">
                <span className="text-emerald-700 font-medium">{chkStats.complete} present</span>
                <span>•</span>
                <span className="text-rose-700 font-medium">{chkStats.missing} missing</span>
              </div>
            </div>

            <Link
              to={`/projects/${project.id}/checklist`}
              className="text-xs font-medium text-brand-600 hover:text-brand-700 inline-flex items-center gap-1 pt-2 border-t border-slate-100"
            >
              <span>View submittal checklist</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Review Findings */}
          <div className="saas-card p-5 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-slate-500 mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider">Pre-Check Findings</span>
                <AlertTriangle className={`w-4 h-4 ${openIssues.length > 0 ? 'text-amber-500' : 'text-slate-400'}`} />
              </div>
              <div className="text-2xl font-bold text-slate-900 mb-1">
                {openIssues.length}
              </div>
              <p className="text-xs text-slate-500 mb-3">
                {criticalCount > 0 ? (
                  <span className="text-rose-700 font-medium">{criticalCount} critical issues flagged</span>
                ) : openIssues.length === 0 ? (
                  <span className="text-emerald-700 font-medium">No open issues</span>
                ) : (
                  <span>Warnings requiring review</span>
                )}
              </p>
            </div>

            <Link
              to={`/projects/${project.id}/findings`}
              className="text-xs font-medium text-brand-600 hover:text-brand-700 inline-flex items-center gap-1 pt-2 border-t border-slate-100"
            >
              <span>Inspect findings & rerun</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

        </div>

        {/* Recent Open Findings Section */}
        {openIssues.length > 0 && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-900">High-Priority Findings Requiring Review</h3>
              <Link to={`/projects/${project.id}/findings`} className="text-xs font-medium text-brand-600 hover:underline">
                View all ({findings.length})
              </Link>
            </div>

            <div className="space-y-3">
              {openIssues.slice(0, 3).map((f) => (
                <FindingCard
                  key={f.id}
                  finding={f}
                  onStatusChange={(updated) => {
                    setFindings(findings.map(item => item.id === updated.id ? updated : item));
                  }}
                  onOpenDocument={handleOpenDoc}
                />
              ))}
            </div>
          </div>
        )}

      </main>

      <Footer />

      {/* Document Viewer Modal */}
      <DocumentViewerModal
        document={selectedDoc}
        initialPage={viewerPage}
        onClose={() => setSelectedDoc(null)}
      />
    </div>
  );
};

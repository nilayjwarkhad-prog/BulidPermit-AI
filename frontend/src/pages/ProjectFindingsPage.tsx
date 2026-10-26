import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Play, CheckCircle2, Search, RefreshCw, AlertTriangle, ChevronRight } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FindingCard } from '../components/findings/FindingCard';
import { FindingFilterBar } from '../components/findings/FindingFilterBar';
import { DocumentViewerModal } from '../components/documents/DocumentViewerModal';
import { api } from '../services/api';
import { Project, Finding, DocumentItem, AnalysisJob } from '../types';

export const ProjectFindingsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [currentJob, setCurrentJob] = useState<AnalysisJob | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isStartingAnalysis, setIsStartingAnalysis] = useState<boolean>(false);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Viewer Modal
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [viewerPage, setViewerPage] = useState<number>(1);

  useEffect(() => {
    if (!id) return;
    loadData();
  }, [id, severityFilter, categoryFilter, statusFilter]);

  // Polling if job is currently running
  useEffect(() => {
    if (!currentJob || (currentJob.status !== 'processing' && currentJob.status !== 'pending')) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await api.getAnalysisJob(currentJob.id);
        setCurrentJob(updated);
        if (updated.status === 'completed' || updated.status === 'failed') {
          // Re-fetch findings and project once completed
          if (id) {
            const [fList, p] = await Promise.all([
              api.getFindings(id),
              api.getProject(id)
            ]);
            setFindings(fList);
            setProject(p);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [currentJob, id]);

  const loadData = async () => {
    try {
      const [p, fList, docs, history] = await Promise.all([
        api.getProject(id!),
        api.getFindings(id!, {
          severity: severityFilter || undefined,
          category: categoryFilter || undefined,
          status: statusFilter || undefined
        }),
        api.getProjectDocuments(id!),
        api.getAnalysisHistory(id!).catch(() => [])
      ]);
      setProject(p);
      setFindings(fList);
      setDocuments(docs);
      if (history && history.length > 0) {
        setCurrentJob(history[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!id) return;
    setIsStartingAnalysis(true);
    try {
      const job = await api.startAnalysis(id);
      setCurrentJob(job);
    } catch (err: any) {
      alert(err.message || 'Failed to start pre-check analysis.');
    } finally {
      setIsStartingAnalysis(false);
    }
  };

  const handleOpenDocument = (docIdOrName: string, pageNumber: number) => {
    const doc = documents.find(d => d.id === docIdOrName || d.filename === docIdOrName);
    if (doc) {
      setSelectedDoc(doc);
      setViewerPage(pageNumber);
    }
  };

  const handleStatusChange = (updated: Finding) => {
    setFindings(findings.map(f => f.id === updated.id ? updated : f));
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

  const isRunning = currentJob?.status === 'processing' || currentJob?.status === 'pending';

  const filteredFindings = findings.filter(f => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase().trim();
    return (
      f.title.toLowerCase().includes(q) ||
      f.explanation.toLowerCase().includes(q) ||
      (f.rule_code && f.rule_code.toLowerCase().includes(q))
    );
  });

  const counts = {
    total: findings.length,
    critical: findings.filter(f => f.severity === 'critical').length,
    warning: findings.filter(f => f.severity === 'warning').length,
    resolved: findings.filter(f => f.status === 'resolved' || f.status === 'dismissed').length
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <ProjectHeader project={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Pre-Check Status & Execution Banner */}
        <div className="saas-card p-5 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                Pre-Check Review Engine
              </span>
              <span className="w-1 h-1 rounded-full bg-slate-300" />
              <span className="text-xs text-slate-600 font-medium">
                {isRunning ? 'Analysis in progress...' : currentJob?.status === 'completed' ? 'Latest analysis complete' : 'Ready to analyze'}
              </span>
            </div>

            <h2 className="text-base sm:text-lg font-bold text-slate-900 tracking-tight">
              {isRunning 
                ? `Running Review Pipeline (${currentJob?.progress_percentage}%)` 
                : counts.critical > 0 
                  ? `${counts.critical} Critical ${counts.critical === 1 ? 'Issue' : 'Issues'} Detected`
                  : counts.total > 0
                    ? `${counts.total} Findings Flagged for Review`
                    : 'All Submittal Documents Verified'
              }
            </h2>

            <p className="text-xs text-slate-500">
              Evaluates title block consistency, room labels, square footage variances, and municipal submittal completeness.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to={`/projects/${project.id}/analysis`}
              className="text-xs font-medium text-slate-600 hover:text-slate-900 px-3 py-2 rounded-lg hover:bg-slate-100 transition-colors"
            >
              Pipeline Details
            </Link>

            <button
              onClick={handleStartAnalysis}
              disabled={isStartingAnalysis || isRunning || (project.document_count || 0) === 0}
              className={`
                inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer
                ${isRunning
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  : 'bg-brand-600 hover:bg-brand-700 text-white'
                }
              `}
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Run Pre-Check</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Progress Bar during execution */}
        {isRunning && (
          <div className="saas-card p-4 space-y-1.5">
            <div className="flex items-center justify-between text-xs text-slate-600">
              <span>Stage: <strong className="text-slate-900">{currentJob?.current_step}</strong></span>
              <span className="font-mono">{currentJob?.progress_percentage}%</span>
            </div>
            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
              <div
                className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${currentJob?.progress_percentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Filter Bar */}
        <FindingFilterBar
          severity={severityFilter}
          category={categoryFilter}
          status={statusFilter}
          onSeverityChange={setSeverityFilter}
          onCategoryChange={setCategoryFilter}
          onStatusChange={setStatusFilter}
          counts={counts}
        />

        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search findings by keyword, address, or rule reference..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="saas-input pl-9"
          />
        </div>

        {/* Findings List */}
        {filteredFindings.length === 0 ? (
          <div className="text-center py-12 px-4 saas-card">
            <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto mb-2" />
            <h3 className="text-sm font-semibold text-slate-900">No findings matching your criteria</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 mb-3">
              All documents in this category are clear or no issues have been detected.
            </p>
            {(severityFilter || categoryFilter || statusFilter || searchQuery) && (
              <button
                onClick={() => { setSeverityFilter(''); setCategoryFilter(''); setStatusFilter(''); setSearchQuery(''); }}
                className="text-xs font-semibold text-brand-600 hover:underline cursor-pointer"
              >
                Clear all filters
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-3.5">
            {filteredFindings.map((f) => (
              <FindingCard
                key={f.id}
                finding={f}
                onStatusChange={handleStatusChange}
                onOpenDocument={handleOpenDocument}
              />
            ))}
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

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Play, CheckCircle2, AlertCircle, ArrowRight, RefreshCw, ChevronDown, ChevronUp, Terminal, FileText } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';
import { api } from '../services/api';
import { Project, AnalysisJob, AIHealthStatus } from '../types';

const PIPELINE_STEPS = [
  { step: 1, title: "File Validation", desc: "MIME types, signatures, file size & page limits" },
  { step: 2, title: "Text Extraction", desc: "PyMuPDF / pypdf text layout & page counts" },
  { step: 3, title: "Page Preview Rendering", desc: "High-resolution blueprint rendering for web inspection" },
  { step: 4, title: "Document Classification", desc: "Category mapping with Gemma 4 AI & architectural cues" },
  { step: 5, title: "Field & Measurement Extraction", desc: "Address, APN, setbacks, room labels, square footage" },
  { step: 6, title: "Checklist Verification", desc: "Submittal package mapping against municipal checklist" },
  { step: 7, title: "Cross-Document Integrity Checks", desc: "Deterministic address, area, and sheet consistency" },
  { step: 8, title: "Jurisdiction Rules Evaluation", desc: "Zoning setbacks & life safety dimensional thresholds" },
  { step: 9, title: "Pre-Check Compilation Ready", desc: "Findings compiled and pre-submission report available" },
];

export const ProjectAnalysisPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [currentJob, setCurrentJob] = useState<AnalysisJob | null>(null);
  const [aiHealth, setAiHealth] = useState<AIHealthStatus | null>(null);
  const [isStarting, setIsStarting] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    loadData();
    api.getAIHealth().then(setAiHealth).catch(console.error);
  }, [id]);

  useEffect(() => {
    if (!currentJob || (currentJob.status !== 'processing' && currentJob.status !== 'pending')) {
      return;
    }

    const interval = setInterval(async () => {
      try {
        const updated = await api.getAnalysisJob(currentJob.id);
        setCurrentJob(updated);
        if (updated.status === 'completed' || updated.status === 'failed') {
          if (id) {
            const p = await api.getProject(id);
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
      const [p, history] = await Promise.all([
        api.getProject(id!),
        api.getAnalysisHistory(id!).catch(() => [])
      ]);
      setProject(p);
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
    setIsStarting(true);
    try {
      const job = await api.startAnalysis(id);
      setCurrentJob(job);
    } catch (err: any) {
      alert(err.message || 'Failed to start analysis.');
    } finally {
      setIsStarting(false);
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

  const isRunning = currentJob?.status === 'processing' || currentJob?.status === 'pending';
  const isCompleted = currentJob?.status === 'completed';
  const activeStepNum = currentJob?.current_step_number || 0;

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <ProjectHeader project={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Main Status & Action Card */}
        <div className="saas-card p-6 space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  Pre-Check Pipeline Status
                </span>
                {currentJob && <StatusBadge status={currentJob.status} type="job" size="sm" />}
              </div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                Deterministic Cross-Document Verification
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Checks address title blocks, addition square footages, setbacks, and required submittal plans.
              </p>
            </div>

            <button
              onClick={handleStartAnalysis}
              disabled={isStarting || isRunning || (project.document_count || 0) === 0}
              className={`
                inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs sm:text-sm font-semibold shadow-xs transition-colors cursor-pointer shrink-0
                ${isRunning
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  : 'bg-brand-600 hover:bg-brand-700 text-white'
                }
              `}
            >
              {isRunning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-slate-400" />
                  <span>Running Analysis ({currentJob?.progress_percentage}%)</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white" />
                  <span>{currentJob ? 'Re-run Pre-Check' : 'Run Pre-Check'}</span>
                </>
              )}
            </button>
          </div>

          {/* Progress Indicator when running */}
          {isRunning && (
            <div className="space-y-2 py-2">
              <div className="flex items-center justify-between text-xs text-slate-600">
                <span>Executing: <strong className="text-slate-900">{currentJob?.current_step}</strong></span>
                <span className="font-mono font-medium">{currentJob?.progress_percentage}%</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-brand-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentJob?.progress_percentage}%` }}
                />
              </div>
            </div>
          )}

          {/* Completion Card */}
          {isCompleted && (
            <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <div>
                  <p className="text-xs font-semibold text-slate-900">
                    Pre-Check Analysis Complete
                  </p>
                  <p className="text-xs text-slate-500">
                    {project.open_findings_count || 0} findings flagged across uploaded sheets.
                  </p>
                </div>
              </div>

              <Link
                to={`/projects/${project.id}/findings`}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors shrink-0"
              >
                <span>Review Findings ({project.open_findings_count || 0})</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}

          {/* Toggle for Technical Details */}
          <div className="pt-2">
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 cursor-pointer"
            >
              <span>{showTechnicalDetails ? 'Hide Technical Diagnostics' : 'Show Technical Pipeline Diagnostics'}</span>
              {showTechnicalDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Collapsible Technical Pipeline Details */}
        {showTechnicalDetails && (
          <div className="saas-card p-6 space-y-6">
            <h3 className="text-sm font-bold text-slate-900">Pipeline Execution Steps</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {PIPELINE_STEPS.map((s) => {
                const isPast = currentJob && (currentJob.status === 'completed' || s.step < activeStepNum);
                const isCurrent = currentJob && isRunning && s.step === activeStepNum;

                return (
                  <div
                    key={s.step}
                    className={`
                      p-3.5 rounded-lg border text-xs flex flex-col justify-between transition-colors
                      ${isPast
                        ? 'bg-emerald-50/40 border-emerald-200'
                        : isCurrent
                          ? 'bg-brand-50/50 border-brand-300 ring-2 ring-brand-500/10'
                          : 'bg-slate-50/50 border-slate-200/80 opacity-60'
                      }
                    `}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-mono text-[10px] text-slate-500 font-semibold">Step {s.step}</span>
                        {isPast && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                        {isCurrent && <RefreshCw className="w-3.5 h-3.5 text-brand-600 animate-spin" />}
                      </div>
                      <h4 className="font-semibold text-slate-900">{s.title}</h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">{s.desc}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Execution Logs */}
            {currentJob?.logs && currentJob.logs.length > 0 && (
              <div className="pt-2">
                <span className="text-xs font-semibold text-slate-700 block mb-2">Diagnostic Logs</span>
                <div className="bg-slate-900 text-slate-200 font-mono text-[11px] p-4 rounded-xl max-h-48 overflow-y-auto space-y-1">
                  {currentJob.logs.map((log, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="text-slate-500 shrink-0">[{log.step}]</span>
                      <span className={log.level === 'error' ? 'text-rose-400' : log.level === 'warning' ? 'text-amber-400' : 'text-slate-300'}>
                        {log.message}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </main>

      <Footer />
    </div>
  );
};

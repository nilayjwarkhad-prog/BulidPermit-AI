import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileSpreadsheet, Download, Plus, FileText, Calendar, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { api } from '../services/api';
import { Project, ReportItem } from '../types';

export const ProjectReportsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [downloadingReportId, setDownloadingReportId] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [p, repList] = await Promise.all([
        api.getProject(id!),
        api.getProjectReports(id!)
      ]);
      setProject(p);
      setReports(repList);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!id) return;
    setIsGenerating(true);
    setSuccessMessage(null);
    setDownloadError(null);
    try {
      const newReport = await api.createReport(id);
      setReports([newReport, ...reports]);
      setSuccessMessage(`Report ${newReport.report_number} generated successfully.`);
    } catch (err: any) {
      alert(err.message || 'Failed to generate PDF report.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async (report: ReportItem) => {
    setDownloadingReportId(report.id);
    setDownloadError(null);
    try {
      const blob = await api.downloadReportBlob(report.id);
      const blobUrl = URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = blobUrl;
      a.download = `${report.report_number}.pdf`;
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to download report');
    } finally {
      setDownloadingReportId(null);
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

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <ProjectHeader project={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Top Report Generator Banner */}
        <div className="saas-card p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div className="space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Pre-Submission Documentation
            </span>
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">
              Compile Pre-Check Audit Report
            </h2>
            <p className="text-xs text-slate-500 max-w-xl">
              Generates a formal PDF summary documenting verified submittal sheets, checklist readiness, and flagged discrepancies.
            </p>
          </div>

          <button
            onClick={handleGenerateReport}
            disabled={isGenerating}
            className="inline-flex items-center justify-center gap-2 px-5 py-2.5 text-xs sm:text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 active:bg-brand-800 rounded-lg shadow-xs transition-colors shrink-0 cursor-pointer disabled:opacity-50"
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            <span>{isGenerating ? 'Compiling PDF...' : 'Generate New Report'}</span>
          </button>
        </div>

        {/* Feedback Alerts */}
        {successMessage && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2 text-xs text-emerald-800">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
        )}

        {downloadError && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{downloadError}</span>
          </div>
        )}

        {/* Reports Table Card */}
        <div className="saas-card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200/90 flex items-center justify-between bg-slate-50/50">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Generated Reports Archive</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {reports.length} {reports.length === 1 ? 'report' : 'reports'} on file for this project
              </p>
            </div>
          </div>

          {reports.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-xs">
              <FileSpreadsheet className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="font-semibold text-slate-700">No reports generated yet</p>
              <p className="text-slate-400 mt-1 max-w-sm mx-auto">
                Click "Generate New Report" above to compile your pre-submission summary PDF.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50/80 border-b border-slate-200/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-5 py-3">Report Number</th>
                    <th className="px-5 py-3">Generated Date</th>
                    <th className="px-5 py-3">Scope & Findings</th>
                    <th className="px-5 py-3 text-right">Download</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {reports.map((rep) => (
                    <tr key={rep.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-brand-600 shrink-0" />
                          <span className="font-semibold text-slate-900 font-mono text-xs">
                            {rep.report_number}
                          </span>
                        </div>
                      </td>

                      <td className="px-5 py-3.5 text-slate-600">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-slate-400" />
                          <span>{new Date(rep.created_at).toLocaleDateString()}</span>
                        </div>
                      </td>

                      <td className="px-5 py-3.5 text-slate-600">
                        <span className="bg-slate-100 px-2 py-0.5 rounded text-[11px] font-medium text-slate-700">
                          {rep.summary_data?.findings_count || 0} {(rep.summary_data?.findings_count || 0) === 1 ? 'finding' : 'findings'} documented
                        </span>
                      </td>

                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={() => handleDownloadReport(rep)}
                          disabled={downloadingReportId === rep.id}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors disabled:opacity-50 cursor-pointer"
                        >
                          {downloadingReportId === rep.id ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Download className="w-3.5 h-3.5 text-slate-500" />
                          )}
                          <span>Download PDF</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Compliance Disclaimer Notice */}
        <div className="p-4 bg-slate-100/70 border border-slate-200 rounded-xl text-xs text-slate-600 space-y-1">
          <p className="font-semibold text-slate-800">
            Legal & Regulatory Disclaimer
          </p>
          <p className="text-[11px] leading-relaxed text-slate-500">
            BuildPermit AI reports provide automated document review and discrepancy detection to assist with pre-submission submittal quality. 
            BuildPermit AI does not provide architectural or engineering certifications, legal interpretations of building codes, or guarantees of municipal permit approval. 
            Permit approval is subject exclusively to review by your local building department authority having jurisdiction.
          </p>
        </div>

      </main>

      <Footer />
    </div>
  );
};

import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Search, FolderKanban, MapPin, Building2, AlertTriangle, CheckCircle2, FileText, ArrowRight, Upload } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { StatusBadge } from '../components/common/StatusBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { EmptyState } from '../components/common/EmptyState';
import { api } from '../services/api';
import { DashboardStats, Project } from '../types';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'attention' | 'ready'>('all');

  useEffect(() => {
    async function fetchDashboard() {
      try {
        const [statsData, projsData] = await Promise.all([
          api.getDashboardStats(),
          api.getProjects()
        ]);
        setStats(statsData);
        setProjects(projsData);
      } catch (err) {
        console.error('Failed to load dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  const filteredProjects = useMemo(() => {
    return projects.filter((p) => {
      const q = searchQuery.toLowerCase().trim();
      const matchesSearch = !q || 
        p.name.toLowerCase().includes(q) ||
        p.address.toLowerCase().includes(q) ||
        p.city.toLowerCase().includes(q) ||
        p.project_type.toLowerCase().includes(q);

      if (!matchesSearch) return false;

      if (statusFilter === 'attention') {
        return (p.open_findings_count || 0) > 0;
      }
      if (statusFilter === 'ready') {
        return (p.document_count || 0) > 0 && (p.open_findings_count || 0) === 0;
      }
      return true;
    });
  }, [projects, searchQuery, statusFilter]);

  const attentionCount = projects.filter(p => (p.open_findings_count || 0) > 0).length;
  const readyCount = projects.filter(p => (p.document_count || 0) > 0 && (p.open_findings_count || 0) === 0).length;

  if (isLoading) {
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

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Page Heading & Primary Action */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">Permit Projects</h1>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              Review drawings, track missing documentation, and verify municipal submittal readiness.
            </p>
          </div>
          <Link
            to="/projects/new"
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2 bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white rounded-lg text-xs sm:text-sm font-semibold shadow-xs transition-colors cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>New Project</span>
          </Link>
        </div>

        {/* Compact Summary Strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <button
            onClick={() => setStatusFilter('all')}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              statusFilter === 'all' 
                ? 'bg-white border-brand-500 ring-2 ring-brand-500/10 shadow-xs' 
                : 'bg-white border-slate-200/90 hover:border-slate-300'
            }`}
          >
            <span className="text-xs font-medium text-slate-500 block">Total Active Projects</span>
            <span className="text-2xl font-bold text-slate-900 mt-1 block">{projects.length}</span>
          </button>

          <button
            onClick={() => setStatusFilter('attention')}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              statusFilter === 'attention' 
                ? 'bg-white border-amber-500 ring-2 ring-amber-500/10 shadow-xs' 
                : 'bg-white border-slate-200/90 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-amber-800">Needs Attention</span>
              <AlertTriangle className="w-4 h-4 text-amber-600" />
            </div>
            <span className="text-2xl font-bold text-slate-900 mt-1 block">{attentionCount}</span>
          </button>

          <button
            onClick={() => setStatusFilter('ready')}
            className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
              statusFilter === 'ready' 
                ? 'bg-white border-emerald-500 ring-2 ring-emerald-500/10 shadow-xs' 
                : 'bg-white border-slate-200/90 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-emerald-800">Ready for Submission</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </div>
            <span className="text-2xl font-bold text-slate-900 mt-1 block">{readyCount}</span>
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search projects by name, address, or project type..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="saas-input pl-9"
            />
          </div>

          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="text-xs text-slate-500 hover:text-slate-800 font-medium self-center cursor-pointer"
            >
              Clear search
            </button>
          )}
        </div>

        {/* Project List */}
        {projects.length === 0 ? (
          <EmptyState
            icon={FolderKanban}
            title="No permit projects yet"
            description="Create your first residential project to begin uploading architectural drawings, checklists, and permit applications."
            actionLabel="Create New Project"
            onAction={() => window.location.href = '/projects/new'}
          />
        ) : filteredProjects.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-slate-200">
            <p className="text-sm text-slate-600 font-medium">No projects match your filter criteria.</p>
            <button
              onClick={() => { setSearchQuery(''); setStatusFilter('all'); }}
              className="mt-2 text-xs font-semibold text-brand-600 hover:underline cursor-pointer"
            >
              Reset filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredProjects.map((proj) => {
              const hasDocs = (proj.document_count || 0) > 0;
              const hasIssues = (proj.open_findings_count || 0) > 0;

              return (
                <div
                  key={proj.id}
                  className="saas-card-interactive p-5 flex flex-col justify-between"
                >
                  <div>
                    {/* Top line: Name & jurisdiction */}
                    <div className="flex items-start justify-between gap-2 mb-1.5">
                      <Link
                        to={`/projects/${proj.id}`}
                        className="font-semibold text-slate-900 hover:text-brand-600 transition-colors text-base line-clamp-1"
                      >
                        {proj.name}
                      </Link>
                      <StatusBadge status={proj.jurisdiction_supported} type="jurisdiction" size="sm" />
                    </div>

                    {/* Address */}
                    <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{proj.address}, {proj.city}</span>
                    </div>

                    {/* Building specs */}
                    <div className="flex items-center gap-1.5 text-xs text-slate-500 mb-4">
                      <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>{proj.project_type}</span>
                    </div>
                  </div>

                  {/* Card Footer */}
                  <div className="pt-3.5 border-t border-slate-100 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 flex items-center gap-1">
                        <FileText className="w-3.5 h-3.5 text-slate-400" />
                        {proj.document_count || 0} documents
                      </span>

                      {hasIssues ? (
                        <span className="text-amber-800 font-medium flex items-center gap-1 bg-amber-50 px-2 py-0.5 rounded text-xs border border-amber-200/80">
                          <AlertTriangle className="w-3 h-3 text-amber-600 shrink-0" />
                          {proj.open_findings_count} {proj.open_findings_count === 1 ? 'issue' : 'issues'}
                        </span>
                      ) : hasDocs ? (
                        <span className="text-emerald-700 font-medium flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded text-xs border border-emerald-200/80">
                          <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                          Pre-check clear
                        </span>
                      ) : (
                        <span className="text-slate-500 text-xs bg-slate-100 px-2 py-0.5 rounded">
                          No documents
                        </span>
                      )}
                    </div>

                    {/* Next Action Link */}
                    <div className="pt-1">
                      {!hasDocs ? (
                        <Link
                          to={`/projects/${proj.id}/documents`}
                          className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors"
                        >
                          <Upload className="w-3.5 h-3.5 text-slate-500" />
                          <span>Upload Documents</span>
                        </Link>
                      ) : hasIssues ? (
                        <Link
                          to={`/projects/${proj.id}/findings`}
                          className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-amber-900 bg-amber-50 hover:bg-amber-100 border border-amber-200/80 rounded-md transition-colors"
                        >
                          <span>Review Findings</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      ) : (
                        <Link
                          to={`/projects/${proj.id}`}
                          className="w-full inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-md transition-colors"
                        >
                          <span>View Overview</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

      </main>

      <Footer />
    </div>
  );
};

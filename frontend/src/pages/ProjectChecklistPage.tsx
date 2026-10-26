import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CheckSquare, CheckCircle2, AlertTriangle, XCircle, FileText, Info } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';
import { api } from '../services/api';
import { Project, Checklist, ChecklistItem } from '../types';

export const ProjectChecklistPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [checklist, setChecklist] = useState<Checklist | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [editingItemId, setEditingItemId] = useState<string | null>(null);
  const [itemStatus, setItemStatus] = useState<string>('');
  const [itemNotes, setItemNotes] = useState<string>('');
  const [isSaving, setIsSaving] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    loadData();
  }, [id]);

  const loadData = async () => {
    try {
      const [p, chk] = await Promise.all([
        api.getProject(id!),
        api.getChecklist(id!)
      ]);
      setProject(p);
      setChecklist(chk);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditClick = (item: ChecklistItem) => {
    setEditingItemId(item.id);
    setItemStatus(item.status);
    setItemNotes(item.notes || '');
  };

  const handleSaveItem = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingItemId) return;
    setIsSaving(true);
    try {
      const updated = await api.updateChecklistItem(editingItemId, itemStatus, itemNotes);
      if (checklist) {
        setChecklist({
          ...checklist,
          items: checklist.items.map(i => i.id === updated.id ? updated : i)
        });
      }
      setEditingItemId(null);
    } catch (err) {
      console.error('Failed to update item:', err);
    } finally {
      setIsSaving(false);
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

  // Group items by category
  const categories: Record<string, ChecklistItem[]> = {};
  if (checklist?.items) {
    checklist.items.forEach(item => {
      categories[item.category] = categories[item.category] || [];
      categories[item.category].push(item);
    });
  }

  const stats = checklist?.completion_stats || { total: 0, complete: 0, missing: 0, needs_verification: 0, percentage: 0 };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <ProjectHeader project={project} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        
        {/* Header & Completeness Indicator Banner */}
        <div className="saas-card p-6 space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  Submittal Readiness Checklist
                </span>
                <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                <span className="text-xs font-mono text-slate-500">{project.jurisdiction_id}</span>
              </div>
              <h2 className="text-lg font-bold text-slate-900 tracking-tight">
                Pre-Submission Document Completeness
              </h2>
              <p className="text-xs text-slate-500 max-w-2xl">
                Tracks presence of required drawing sheets, site plan labels, and dimensioning standards before city intake.
              </p>
            </div>

            {/* Completeness Summary Block */}
            <div className="flex items-center gap-4 bg-slate-50 border border-slate-200/90 p-3 rounded-lg text-xs self-stretch sm:self-auto justify-between sm:justify-start">
              <div>
                <span className="block font-bold text-slate-900 text-base leading-none">{stats.percentage}%</span>
                <span className="text-[10px] text-slate-500 uppercase font-semibold">Completeness</span>
              </div>
              <div className="h-6 w-px bg-slate-200"></div>
              <div className="flex items-center gap-3 text-slate-700">
                <span className="flex items-center gap-1 text-emerald-700 font-medium">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  {stats.complete} Present
                </span>
                <span className="flex items-center gap-1 text-rose-700 font-medium">
                  <XCircle className="w-3.5 h-3.5 text-rose-600" />
                  {stats.missing} Missing
                </span>
                <span className="flex items-center gap-1 text-amber-800 font-medium">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                  {stats.needs_verification} Review
                </span>
              </div>
            </div>
          </div>

          {/* Completeness Bar */}
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="bg-brand-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${stats.percentage}%` }}
            />
          </div>

          <p className="text-[11px] text-slate-400 italic">
            * Advisory completeness guidance based on standard residential requirements. Official acceptance is determined exclusively by your local building department.
          </p>
        </div>

        {/* Grouped Checklist Categories */}
        <div className="space-y-5">
          {Object.entries(categories).map(([categoryName, items]) => (
            <div key={categoryName} className="saas-card overflow-hidden">
              <div className="px-5 py-3 bg-slate-50/70 border-b border-slate-200/90 flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">{categoryName}</h3>
                <span className="text-xs text-slate-500 font-medium">
                  {items.filter(i => i.status === 'complete').length} of {items.length} Present
                </span>
              </div>

              <div className="divide-y divide-slate-100">
                {items.map((item) => (
                  <div key={item.id} className="p-4 sm:p-5 hover:bg-slate-50/40 transition-colors">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 mb-1.5">
                      <div className="flex items-center gap-2">
                        <StatusBadge status={item.status} type="checklist" size="sm" />
                        <h4 className="font-semibold text-slate-900 text-sm">{item.title}</h4>
                      </div>
                      <span className="text-[11px] font-mono text-slate-400">
                        {item.requirement_code}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed mb-2.5">
                      {item.description}
                    </p>

                    {/* Evidence & Action Row */}
                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 pt-2 border-t border-slate-100">
                      <div className="flex flex-wrap items-center gap-2.5">
                        {item.evidence_document_name && (
                          <div className="flex items-center gap-1.5 font-medium text-slate-700 bg-slate-100 px-2 py-0.5 rounded text-[11px]">
                            <FileText className="w-3.5 h-3.5 text-slate-400" />
                            <span>{item.evidence_document_name}</span>
                          </div>
                        )}
                        {item.notes && (
                          <span className="text-slate-600 italic">
                            {item.notes}
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => handleEditClick(item)}
                        className="text-xs font-medium text-brand-600 hover:text-brand-700 hover:underline cursor-pointer"
                      >
                        Update Status
                      </button>
                    </div>

                    {/* Inline Status Editor */}
                    {editingItemId === item.id && (
                      <form onSubmit={handleSaveItem} className="mt-3 p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-2.5 text-xs">
                        <div className="flex items-center gap-3">
                          <label className="font-semibold text-slate-700">Status:</label>
                          <select
                            value={itemStatus}
                            onChange={(e) => setItemStatus(e.target.value)}
                            className="rounded border border-slate-300 text-xs px-2 py-1 text-slate-800 cursor-pointer"
                          >
                            <option value="complete">Present</option>
                            <option value="missing">Missing</option>
                            <option value="needs_verification">Needs Review</option>
                            <option value="not_applicable">Not Applicable</option>
                          </select>
                        </div>
                        <div>
                          <input
                            type="text"
                            placeholder="Verification note (e.g. 'Sheet A-1 verified with stamp')..."
                            value={itemNotes}
                            onChange={(e) => setItemNotes(e.target.value)}
                            className="saas-input text-xs"
                          />
                        </div>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => setEditingItemId(null)}
                            className="px-2.5 py-1 text-slate-600 hover:bg-slate-200 rounded text-xs cursor-pointer"
                          >
                            Cancel
                          </button>
                          <button
                            type="submit"
                            disabled={isSaving}
                            className="px-3 py-1 bg-brand-600 text-white rounded font-medium text-xs hover:bg-brand-700 shadow-xs cursor-pointer disabled:opacity-50"
                          >
                            {isSaving ? 'Saving...' : 'Save'}
                          </button>
                        </div>
                      </form>
                    )}

                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

      </main>

      <Footer />
    </div>
  );
};

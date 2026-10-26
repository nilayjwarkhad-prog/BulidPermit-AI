import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileText, Download, Trash2, Eye, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { Navbar } from '../components/layout/Navbar';
import { Footer } from '../components/layout/Footer';
import { ProjectHeader } from '../components/layout/ProjectHeader';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { UploadDropzone } from '../components/documents/UploadDropzone';
import { DocumentViewerModal } from '../components/documents/DocumentViewerModal';
import { api } from '../services/api';
import { Project, DocumentItem } from '../types';

const CATEGORIES = [
  "Permit Application",
  "Site Plan",
  "Property Survey",
  "Floor Plan",
  "Elevation Drawing",
  "Building Sections",
  "Structural Plans",
  "Structural Calculations",
  "Energy Documentation",
  "Electrical Plans",
  "Plumbing Plans",
  "Mechanical Plans",
  "Drainage and Grading",
  "Geotechnical Report",
  "Professional Signatures & Seals",
  "Other Supporting Document"
];

export const ProjectDocumentsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [downloadingDocId, setDownloadingDocId] = useState<string | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    loadProjectAndDocs();
  }, [id]);

  const loadProjectAndDocs = async () => {
    try {
      const [p, docs] = await Promise.all([
        api.getProject(id!),
        api.getProjectDocuments(id!)
      ]);
      setProject(p);
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadSuccess = (newDocs: DocumentItem[]) => {
    setDocuments([...newDocs, ...documents]);
    if (project) {
      setProject({ ...project, document_count: (project.document_count || 0) + newDocs.length });
    }
  };

  const handleSeedSampleDocs = async () => {
    if (!id) return;
    setIsSeeding(true);
    setDownloadError(null);
    try {
      const seeded = await api.seedSampleDocuments(id, true);
      setDocuments([...seeded, ...documents]);
      if (project) {
        setProject({ ...project, document_count: (project.document_count || 0) + seeded.length });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to load sample documents.');
    } finally {
      setIsSeeding(false);
    }
  };

  const handleCategoryChange = async (docId: string, newCategory: string) => {
    try {
      const updated = await api.updateDocumentCategory(docId, newCategory);
      setDocuments(documents.map(d => d.id === docId ? updated : d));
    } catch (err) {
      console.error('Failed to update category:', err);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm('Remove this document from the submittal set?')) return;
    try {
      await api.deleteDocument(docId);
      setDocuments(documents.filter(d => d.id !== docId));
      if (project) {
        setProject({ ...project, document_count: Math.max(0, (project.document_count || 1) - 1) });
      }
    } catch (err: any) {
      alert(err.message || 'Failed to delete document');
    }
  };

  const handleDownload = async (doc: DocumentItem) => {
    setDownloadingDocId(doc.id);
    setDownloadError(null);
    try {
      const blob = await api.downloadDocumentBlob(doc.id);
      const blobUrl = URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = blobUrl;
      a.download = doc.original_filename || `${doc.filename}.pdf`;
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to download document');
    } finally {
      setDownloadingDocId(null);
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
        
        {/* Top Section: Upload Area & Sample Seeder */}
        <div className="saas-card p-6 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">Upload Submittal Documents</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Upload PDFs or drawings to extract title blocks, square footage, and setback evidence.
              </p>
            </div>

            <button
              onClick={handleSeedSampleDocs}
              disabled={isSeeding}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-50 cursor-pointer self-start sm:self-center"
              title="Loads realistic sample documents for local testing"
            >
              {isSeeding ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-brand-600" />}
              <span>{isSeeding ? 'Loading Samples...' : 'Load Sample Set'}</span>
            </button>
          </div>

          <UploadDropzone projectId={project.id} onUploadSuccess={handleUploadSuccess} />
        </div>

        {downloadError && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2 text-xs text-rose-800">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
            <span>{downloadError}</span>
          </div>
        )}

        {/* Document List Table */}
        <div className="saas-card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200/90 flex items-center justify-between bg-slate-50/50">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Submittal Document Set</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                {documents.length} {documents.length === 1 ? 'document' : 'documents'} ready for pre-check
              </p>
            </div>
          </div>

          {documents.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-xs">
              <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="font-medium text-slate-700">No documents uploaded yet</p>
              <p className="text-slate-400 mt-1">Upload plan sheets above or load sample documents to test.</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50/80 border-b border-slate-200/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                  <tr>
                    <th className="px-5 py-3">Document Name</th>
                    <th className="px-5 py-3">Category</th>
                    <th className="px-5 py-3 text-center">Pages</th>
                    <th className="px-5 py-3">Status</th>
                    <th className="px-5 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {documents.map((doc) => (
                    <tr key={doc.id} className="hover:bg-slate-50/60 transition-colors">
                      {/* Name */}
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2.5">
                          <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                          <div>
                            <span className="font-semibold text-slate-900 block truncate max-w-xs sm:max-w-md">
                              {doc.original_filename || doc.filename}
                            </span>
                            <span className="text-[11px] text-slate-400 font-mono">
                              {(doc.file_size / 1024).toFixed(0)} KB
                            </span>
                          </div>
                        </div>
                      </td>

                      {/* Category Selector */}
                      <td className="px-5 py-3.5">
                        <select
                          value={doc.category}
                          onChange={(e) => handleCategoryChange(doc.id, e.target.value)}
                          className="text-xs rounded border border-slate-200 bg-white px-2 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-brand-500 cursor-pointer"
                        >
                          {CATEGORIES.map((cat) => (
                            <option key={cat} value={cat}>
                              {cat}
                            </option>
                          ))}
                        </select>
                      </td>

                      {/* Pages */}
                      <td className="px-5 py-3.5 text-center font-medium">
                        {doc.page_count || 1}
                      </td>

                      {/* Status */}
                      <td className="px-5 py-3.5">
                        <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200/70">
                          {doc.status}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-5 py-3.5 text-right">
                        <div className="inline-flex items-center gap-1.5 justify-end">
                          <button
                            onClick={() => setSelectedDoc(doc)}
                            className="p-1.5 rounded-md text-slate-600 hover:text-brand-600 hover:bg-slate-100 transition-colors cursor-pointer"
                            title="Inspect page previews & extracted fields"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          <button
                            onClick={() => handleDownload(doc)}
                            disabled={downloadingDocId === doc.id}
                            className="p-1.5 rounded-md text-slate-600 hover:text-brand-600 hover:bg-slate-100 transition-colors disabled:opacity-40 cursor-pointer"
                            title="Download original document"
                          >
                            {downloadingDocId === doc.id ? (
                              <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
                            ) : (
                              <Download className="w-4 h-4" />
                            )}
                          </button>

                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="p-1.5 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                            title="Remove document"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </main>

      <Footer />

      {/* Document Inspector Modal */}
      <DocumentViewerModal
        document={selectedDoc}
        onClose={() => setSelectedDoc(null)}
        onCategoryChange={(newCat) => {
          if (selectedDoc) {
            handleCategoryChange(selectedDoc.id, newCat);
          }
        }}
      />
    </div>
  );
};

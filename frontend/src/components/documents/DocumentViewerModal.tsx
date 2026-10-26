import React, { useState, useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Download, FileText, CheckCircle2, Tag, Loader2, AlertCircle } from 'lucide-react';
import { DocumentItem } from '../../types';
import { api } from '../../services/api';

interface DocumentViewerModalProps {
  document: DocumentItem | null;
  initialPage?: number;
  onClose: () => void;
  onCategoryChange?: (newCategory: string) => void;
}

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

const FIELD_LABELS: Record<string, string> = {
  property_address: "Property Address",
  stated_building_area: "Stated Building Area",
  addition_area: "Proposed Addition Area",
  parcel_number: "Assessor Parcel Number (APN)",
  applicant_name: "Applicant / Owner Name",
  license_number: "Contractor / Architect License",
  setback_front: "Front Yard Setback",
  setback_rear: "Rear Yard Setback",
  setback_side: "Side Yard Setback",
  scale_annotation: "Drawing Scale",
  has_north_arrow: "North Arrow Present",
  has_professional_stamp: "Professional Stamp / Seal",
  identified_rooms: "Identified Rooms",
  sheet_number: "Sheet Number"
};

export const DocumentViewerModal: React.FC<DocumentViewerModalProps> = ({
  document,
  initialPage = 1,
  onClose,
  onCategoryChange
}) => {
  const [currentPage, setCurrentPage] = useState<number>(initialPage);
  const [zoom, setZoom] = useState<number>(100);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [isUpdatingCategory, setIsUpdatingCategory] = useState<boolean>(false);
  const [imageError, setImageError] = useState<boolean>(false);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isOpeningOriginal, setIsOpeningOriginal] = useState<boolean>(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    if (document) {
      setCurrentPage(initialPage || 1);
      setSelectedCategory(document.category);
      setImageError(false);
      setZoom(100);
      setDownloadError(null);
    }
  }, [document, initialPage]);

  if (!document) return null;

  const totalPages = document.page_count || 1;
  const previewUrl = api.getDocumentPreviewUrl(document.id, currentPage);

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      setImageError(false);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
      setImageError(false);
    }
  };

  const handleCategorySave = async (newCat: string) => {
    setSelectedCategory(newCat);
    setIsUpdatingCategory(true);
    try {
      await api.updateDocumentCategory(document.id, newCat);
      if (onCategoryChange) {
        onCategoryChange(newCat);
      }
    } finally {
      setIsUpdatingCategory(false);
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);
    try {
      const blob = await api.downloadDocumentBlob(document.id);
      const blobUrl = URL.createObjectURL(blob);
      const a = window.document.createElement('a');
      a.href = blobUrl;
      a.download = document.original_filename || `${document.filename}.pdf`;
      window.document.body.appendChild(a);
      a.click();
      window.document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 10000);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to download document');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleOpenOriginal = async () => {
    setIsOpeningOriginal(true);
    setDownloadError(null);
    try {
      const blob = await api.downloadDocumentBlob(document.id);
      const blobUrl = URL.createObjectURL(blob);
      const newWin = window.open(blobUrl, '_blank');
      if (!newWin) {
        const a = window.document.createElement('a');
        a.href = blobUrl;
        a.download = document.original_filename || `${document.filename}.pdf`;
        window.document.body.appendChild(a);
        a.click();
        window.document.body.removeChild(a);
      }
      setTimeout(() => URL.revokeObjectURL(blobUrl), 15000);
    } catch (err: any) {
      setDownloadError(err.message || 'Failed to open document');
    } finally {
      setIsOpeningOriginal(false);
    }
  };

  // Safe field extraction parsing
  const extracted = document.extracted_fields || {};
  const pageFieldsList: any[] = Array.isArray(extracted._page_fields) ? extracted._page_fields : [];
  const fieldPagesMap: Record<string, any> = (extracted._field_pages && typeof extracted._field_pages === 'object') ? extracted._field_pages : {};
  const fieldAllPagesMap: Record<string, any> = (extracted._field_all_pages && typeof extracted._field_all_pages === 'object') ? extracted._field_all_pages : {};

  // Find fields specifically detected on the currently selected sheet
  const currentPageData = pageFieldsList.find(p => p.page_number === currentPage);

  // Filter clean document-level fields (ignore internal _ prefixed keys)
  const cleanDocFields = Object.entries(extracted).filter(([k, v]) => {
    if (k.startsWith('_')) return false;
    if (v === null || v === undefined || v === '') return false;
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 animate-fadeIn">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-6xl h-[92vh] flex flex-col border border-slate-200 overflow-hidden">
        
        {/* Top Header Bar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-200 bg-white">
          <div className="flex items-center gap-2.5 min-w-0">
            <FileText className="w-4 h-4 text-slate-500 shrink-0" />
            <span className="font-semibold text-slate-900 text-sm truncate max-w-md">
              {document.original_filename || document.filename}
            </span>
            <span className="text-xs text-slate-400 font-mono hidden sm:inline">
              ({document.page_count || 1} {document.page_count === 1 ? 'page' : 'pages'})
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-md transition-colors disabled:opacity-50 cursor-pointer"
              title="Download original file"
            >
              {isDownloading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
              <span className="hidden sm:inline">Download</span>
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer"
              title="Close viewer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Main Body */}
        <div className="flex-1 flex flex-col lg:flex-row overflow-hidden bg-slate-100">
          
          {/* Left Canvas: Preview + Zoom & Page Navigation */}
          <div className="flex-1 flex flex-col overflow-hidden relative">
            
            {/* Toolbar */}
            <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-slate-200 text-xs">
              
              {/* Page Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={handlePrevPage}
                  disabled={currentPage <= 1}
                  className="p-1 rounded hover:bg-slate-100 disabled:opacity-30 transition-colors cursor-pointer"
                  title="Previous page"
                >
                  <ChevronLeft className="w-4 h-4 text-slate-700" />
                </button>
                <span className="font-medium text-slate-800">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={handleNextPage}
                  disabled={currentPage >= totalPages}
                  className="p-1 rounded hover:bg-slate-100 disabled:opacity-30 transition-colors cursor-pointer"
                  title="Next page"
                >
                  <ChevronRight className="w-4 h-4 text-slate-700" />
                </button>
              </div>

              {/* Zoom Controls */}
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setZoom(Math.max(50, zoom - 25))}
                  className="p-1 rounded hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                  title="Zoom Out"
                >
                  <ZoomOut className="w-4 h-4" />
                </button>
                <span className="w-10 text-center font-mono text-slate-700 text-xs">{zoom}%</span>
                <button
                  onClick={() => setZoom(Math.min(200, zoom + 25))}
                  className="p-1 rounded hover:bg-slate-100 text-slate-600 transition-colors cursor-pointer"
                  title="Zoom In"
                >
                  <ZoomIn className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setZoom(100)}
                  className="text-slate-500 hover:text-slate-800 px-1.5 py-0.5 text-[11px] rounded hover:bg-slate-100 cursor-pointer"
                >
                  Reset
                </button>
              </div>

            </div>

            {/* Preview Image Render Area */}
            <div className="flex-1 overflow-auto p-6 flex items-center justify-center">
              {!imageError ? (
                <div
                  style={{ width: `${zoom}%` }}
                  className="transition-all duration-150 flex items-center justify-center"
                >
                  <img
                    src={previewUrl}
                    alt={`Sheet page ${currentPage}`}
                    onError={() => setImageError(true)}
                    className="max-w-full rounded shadow-sm border border-slate-300 bg-white object-contain"
                  />
                </div>
              ) : (
                <div className="text-center p-8 bg-white rounded-xl shadow-xs border border-slate-200 max-w-sm">
                  <FileText className="w-10 h-10 text-slate-400 mx-auto mb-2" />
                  <p className="font-semibold text-slate-800 text-sm">Direct Page Preview</p>
                  <p className="text-xs text-slate-500 mt-1 mb-4">
                    Vector PDF sheet is ready. Open with the authenticated viewer.
                  </p>
                  <button
                    onClick={handleOpenOriginal}
                    disabled={isOpeningOriginal}
                    className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors cursor-pointer"
                  >
                    {isOpeningOriginal ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                    <span>{isOpeningOriginal ? 'Opening...' : 'Open Original PDF'}</span>
                  </button>
                  {downloadError && (
                    <p className="mt-2 text-xs text-rose-600">{downloadError}</p>
                  )}
                </div>
              )}
            </div>

          </div>

          {/* Right Inspector Panel */}
          <div className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-slate-200 bg-white p-5 flex flex-col overflow-y-auto space-y-5">
            
            {/* Category Selector */}
            <div>
              <label className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                <Tag className="w-3.5 h-3.5 text-slate-400" />
                <span>Document Category</span>
              </label>
              <select
                value={selectedCategory}
                onChange={(e) => handleCategorySave(e.target.value)}
                disabled={isUpdatingCategory}
                className="saas-select text-xs"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            {/* Current Page Extraction */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Page {currentPage} Extracted Data
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">Sheet-specific</span>
              </div>

              {currentPageData && (currentPageData.property_address || currentPageData.addition_area || currentPageData.stated_building_area || currentPageData.sheet_number) ? (
                <div className="space-y-2 text-xs">
                  {currentPageData.property_address && (
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="block text-[10px] font-semibold text-slate-500 uppercase">Address on Sheet</span>
                      <span className="block font-medium text-slate-900 mt-0.5">{currentPageData.property_address}</span>
                    </div>
                  )}
                  {currentPageData.addition_area !== null && currentPageData.addition_area !== undefined && (
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="block text-[10px] font-semibold text-slate-500 uppercase">Addition Area</span>
                      <span className="block font-medium text-slate-900 mt-0.5">{currentPageData.addition_area.toLocaleString()} sq ft</span>
                    </div>
                  )}
                  {currentPageData.stated_building_area !== null && currentPageData.stated_building_area !== undefined && (
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="block text-[10px] font-semibold text-slate-500 uppercase">Building Area</span>
                      <span className="block font-medium text-slate-900 mt-0.5">{currentPageData.stated_building_area.toLocaleString()} sq ft</span>
                    </div>
                  )}
                  {currentPageData.sheet_number && (
                    <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="block text-[10px] font-semibold text-slate-500 uppercase">Sheet Number</span>
                      <span className="block font-medium text-slate-900 mt-0.5">{currentPageData.sheet_number}</span>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic bg-slate-50 p-3 rounded-lg border border-slate-100">
                  No sheet-specific address or area overrides on page {currentPage}.
                </p>
              )}
            </div>

            {/* Document-Level Verified Fields */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Document-Level Fields
                </h3>
                <span className="text-[11px] text-slate-400 font-mono">Aggregated</span>
              </div>

              {cleanDocFields.length > 0 ? (
                <div className="space-y-2 text-xs">
                  {cleanDocFields.map(([k, v]) => {
                    const label = FIELD_LABELS[k] || k.replace(/_/g, ' ');
                    const sourcePage = fieldPagesMap[k];
                    const allPages = fieldAllPagesMap[k];

                    let displayVal = String(v);
                    if (typeof v === 'boolean') {
                      displayVal = v ? 'Verified Present' : 'Not Detected';
                    } else if (Array.isArray(v)) {
                      displayVal = v.join(', ');
                    } else if (typeof v === 'number' && (k.includes('area') || k.includes('footage'))) {
                      displayVal = `${v.toLocaleString()} sq ft`;
                    }

                    return (
                      <div key={k} className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                        <div className="flex items-center justify-between gap-1">
                          <span className="text-[10px] font-semibold text-slate-500 uppercase">{label}</span>
                          {sourcePage && (
                            <button
                              onClick={() => {
                                setCurrentPage(sourcePage);
                                setImageError(false);
                              }}
                              className="text-[10px] font-medium text-brand-600 hover:underline cursor-pointer"
                              title={`Jump to Page ${sourcePage}`}
                            >
                              Page {sourcePage}
                            </button>
                          )}
                        </div>
                        <span className="block font-medium text-slate-900 mt-0.5 break-words">
                          {displayVal}
                        </span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No structured fields extracted yet.</p>
              )}
            </div>

            {/* Pre-Check Guidance */}
            <div className="mt-auto p-3 bg-blue-50/60 border border-blue-200/80 rounded-lg text-xs text-blue-900 space-y-1">
              <p className="font-semibold flex items-center gap-1.5 text-blue-950">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                <span>Pre-Check Tip</span>
              </p>
              <p className="text-[11px] leading-relaxed text-blue-800">
                Make sure title block addresses and declared square footage match across all uploaded sheets before municipal filing.
              </p>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
};

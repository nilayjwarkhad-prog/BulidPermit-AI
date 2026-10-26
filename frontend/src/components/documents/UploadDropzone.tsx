import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../../services/api';
import { DocumentItem } from '../../types';

interface UploadDropzoneProps {
  projectId: string;
  onUploadSuccess: (newDocs: DocumentItem[]) => void;
}

const CATEGORIES = [
  "Other Supporting Document",
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
  "Professional Signatures & Seals"
];

export const UploadDropzone: React.FC<UploadDropzoneProps> = ({ projectId, onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>("Other Supporting Document");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFiles(Array.from(e.target.files));
    }
  };

  const processFiles = async (files: File[]) => {
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsUploading(true);
    setUploadProgress(15);

    const uploadedResults: DocumentItem[] = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        if (file.size > 50 * 1024 * 1024) {
          throw new Error(`File '${file.name}' exceeds the 50 MB limit.`);
        }
        const ext = file.name.split('.').pop()?.toLowerCase();
        if (!['pdf', 'png', 'jpg', 'jpeg'].includes(ext || '')) {
          throw new Error(`Unsupported file format '${ext}'. Please upload PDF, PNG, or JPEG.`);
        }

        const uploaded = await api.uploadDocument(projectId, file, selectedCategory);
        uploadedResults.push(uploaded);
        setUploadProgress(Math.round(((i + 1) / files.length) * 100));
      }

      setSuccessMessage(`Uploaded ${uploadedResults.length} document${uploadedResults.length > 1 ? 's' : ''} successfully.`);
      onUploadSuccess(uploadedResults);
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed. Please check file format.');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="space-y-3">
      {/* Category selector row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <label className="text-xs font-semibold text-slate-700">
          Target Category for Upload:
        </label>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="saas-select max-w-xs text-xs"
        >
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Dropzone Container */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`
          border border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center
          ${isDragging 
            ? 'border-brand-500 bg-brand-50/50' 
            : 'border-slate-300 bg-white hover:border-slate-400 hover:bg-slate-50/50'
          }
        `}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          onChange={handleFileSelect}
          className="hidden"
        />

        <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 mb-2">
          {isUploading ? (
            <Loader2 className="w-5 h-5 animate-spin text-brand-600" />
          ) : (
            <UploadCloud className="w-5 h-5" />
          )}
        </div>

        <p className="text-xs sm:text-sm font-semibold text-slate-900">
          Click to upload or drag and drop plan sheets
        </p>
        <p className="text-[11px] text-slate-500 mt-1">
          Supported formats: PDF, PNG, JPG (up to 50 MB per file)
        </p>

        {isUploading && (
          <div className="w-full max-w-xs mt-4 space-y-1">
            <div className="flex items-center justify-between text-[11px] text-slate-600">
              <span>Uploading & extracting...</span>
              <span className="font-mono">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
              <div 
                className="bg-brand-600 h-1.5 rounded-full transition-all duration-200"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      {errorMessage && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg flex items-center gap-2 text-xs text-rose-800">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}

      {successMessage && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center gap-2 text-xs text-emerald-800">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
          <span>{successMessage}</span>
        </div>
      )}
    </div>
  );
};

import {
  User,
  AuthResponse,
  Project,
  DocumentItem,
  Finding,
  Checklist,
  ChecklistItem,
  AnalysisJob,
  ReportItem,
  Jurisdiction,
  DashboardStats,
  AIHealthStatus
} from '../types';

const API_BASE = '/api/v1';

function getAuthHeaders(isFormData: boolean = false): HeadersInit {
  const token = localStorage.getItem('buildpermit_token');
  const headers: Record<string, string> = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem('buildpermit_token');
      localStorage.removeItem('buildpermit_user');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register' && window.location.pathname !== '/') {
        window.location.href = '/login';
      }
    }
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Request failed with status ${res.status}`);
  }
  if (res.status === 204) {
    return {} as T;
  }
  return res.json();
}

export const api = {
  // Auth
  async register(data: { email: string; password: string; full_name?: string; role?: string }): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return handleResponse<AuthResponse>(res);
  },

  async login(data: { email: string; password: string }): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return handleResponse<AuthResponse>(res);
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders()
    });
    return handleResponse<User>(res);
  },

  // Health
  async getAIHealth(): Promise<AIHealthStatus> {
    const res = await fetch('/health/ai');
    return handleResponse<AIHealthStatus>(res);
  },

  // Dashboard
  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: getAuthHeaders()
    });
    return handleResponse<DashboardStats>(res);
  },

  // Projects
  async getProjects(): Promise<Project[]> {
    const res = await fetch(`${API_BASE}/projects`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Project[]>(res);
  },

  async getProject(id: string): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Project>(res);
  },

  async createProject(data: Partial<Project>): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Project>(res);
  },

  async updateProject(id: string, data: Partial<Project>): Promise<Project> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    return handleResponse<Project>(res);
  },

  async deleteProject(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/projects/${id}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return handleResponse<void>(res);
  },

  // Jurisdictions
  async getJurisdictions(): Promise<Jurisdiction[]> {
    const res = await fetch(`${API_BASE}/jurisdictions`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Jurisdiction[]>(res);
  },

  // Documents
  async getProjectDocuments(projectId: string): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
      headers: getAuthHeaders()
    });
    return handleResponse<DocumentItem[]>(res);
  },

  async uploadDocument(projectId: string, file: File, category: string = 'Other Supporting Document'): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);

    const res = await fetch(`${API_BASE}/projects/${projectId}/documents`, {
      method: 'POST',
      headers: getAuthHeaders(true),
      body: formData
    });
    return handleResponse<DocumentItem>(res);
  },

  async seedSampleDocuments(projectId: string, includeInconsistency: boolean = true): Promise<DocumentItem[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/seed_sample_documents?include_inconsistency=${includeInconsistency}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<DocumentItem[]>(res);
  },

  async updateDocumentCategory(docId: string, category: string): Promise<DocumentItem> {
    const res = await fetch(`${API_BASE}/documents/${docId}/category`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ category })
    });
    return handleResponse<DocumentItem>(res);
  },

  async deleteDocument(docId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/documents/${docId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return handleResponse<void>(res);
  },

  getDocumentPreviewUrl(docId: string, pageNumber: number = 1): string {
    const token = localStorage.getItem('buildpermit_token');
    const query = token ? `?token=${encodeURIComponent(token)}` : '';
    return `${API_BASE}/documents/${docId}/preview/${pageNumber}${query}`;
  },

  getDocumentDownloadUrl(docId: string): string {
    const token = localStorage.getItem('buildpermit_token');
    const query = token ? `?token=${encodeURIComponent(token)}` : '';
    return `${API_BASE}/documents/${docId}/download${query}`;
  },

  async downloadDocumentBlob(docId: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/documents/${docId}/download`, {
      headers: getAuthHeaders(true)
    });
    if (!res.ok) {
      if (res.status === 401) {
        throw new Error('Authentication required. Please log in to download this document.');
      }
      if (res.status === 403) {
        throw new Error('Access denied. You do not have permission to download this document.');
      }
      if (res.status === 404) {
        throw new Error('Document file not found on server.');
      }
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Download failed with status ${res.status}`);
    }
    return res.blob();
  },

  // Analysis
  async startAnalysis(projectId: string): Promise<AnalysisJob> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/analysis`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<AnalysisJob>(res);
  },

  async getAnalysisJob(jobId: string): Promise<AnalysisJob> {
    const res = await fetch(`${API_BASE}/analysis/${jobId}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<AnalysisJob>(res);
  },

  async getAnalysisHistory(projectId: string): Promise<AnalysisJob[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/analysis/history`, {
      headers: getAuthHeaders()
    });
    return handleResponse<AnalysisJob[]>(res);
  },

  // Findings
  async getFindings(projectId: string, filters: { severity?: string; category?: string; status?: string; document_id?: string } = {}): Promise<Finding[]> {
    const query = new URLSearchParams();
    if (filters.severity) query.append('severity', filters.severity);
    if (filters.category) query.append('category', filters.category);
    if (filters.status) query.append('status', filters.status);
    if (filters.document_id) query.append('document_id', filters.document_id);

    const res = await fetch(`${API_BASE}/projects/${projectId}/findings?${query.toString()}`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Finding[]>(res);
  },

  async updateFindingStatus(findingId: string, status: string, resolution_notes?: string): Promise<Finding> {
    const res = await fetch(`${API_BASE}/findings/${findingId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status, resolution_notes })
    });
    return handleResponse<Finding>(res);
  },

  async requestAIAdvice(findingId: string): Promise<Finding> {
    const res = await fetch(`${API_BASE}/findings/${findingId}/ai_advice`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<Finding>(res);
  },

  // Checklist
  async getChecklist(projectId: string): Promise<Checklist> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/checklist`, {
      headers: getAuthHeaders()
    });
    return handleResponse<Checklist>(res);
  },

  async updateChecklistItem(itemId: string, status: string, notes?: string): Promise<ChecklistItem> {
    const res = await fetch(`${API_BASE}/checklist/items/${itemId}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status, notes })
    });
    return handleResponse<ChecklistItem>(res);
  },

  // Reports
  async createReport(projectId: string): Promise<ReportItem> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/reports`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return handleResponse<ReportItem>(res);
  },

  async getProjectReports(projectId: string): Promise<ReportItem[]> {
    const res = await fetch(`${API_BASE}/projects/${projectId}/reports`, {
      headers: getAuthHeaders()
    });
    return handleResponse<ReportItem[]>(res);
  },

  getReportDownloadUrl(reportId: string): string {
    const token = localStorage.getItem('buildpermit_token');
    const query = token ? `?token=${encodeURIComponent(token)}` : '';
    return `${API_BASE}/reports/${reportId}/download${query}`;
  },

  async downloadReportBlob(reportId: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/download`, {
      headers: getAuthHeaders(true)
    });
    if (!res.ok) {
      if (res.status === 401) {
        throw new Error('Authentication required. Please log in to download this report.');
      }
      if (res.status === 403) {
        throw new Error('Access denied. You do not have permission to download this report.');
      }
      if (res.status === 404) {
        throw new Error('Report file not found on server.');
      }
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Download failed with status ${res.status}`);
    }
    return res.blob();
  }
};

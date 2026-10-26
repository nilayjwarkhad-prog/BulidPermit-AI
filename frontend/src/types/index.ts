export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  country: string;
  state_region: string;
  city: string;
  address: string;
  project_type: string;
  building_type: string;
  num_floors: number;
  area?: number;
  area_unit: string;
  stage: string;
  jurisdiction_id: string;
  jurisdiction_supported: 'supported' | 'partial' | 'unsupported';
  created_at: string;
  updated_at: string;
  document_count?: number;
  open_findings_count?: number;
  checklist_completion_percent?: number;
  latest_job_status?: string;
}

export interface DocumentItem {
  id: string;
  project_id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  page_count: number;
  category: string;
  suggested_category?: string;
  category_confidence?: number;
  manual_category_override: boolean;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
  extracted_fields?: Record<string, any>;
  preview_pages?: string[];
}

export interface Finding {
  id: string;
  project_id: string;
  document_id?: string;
  document_name?: string;
  rule_code?: string;
  title: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  status: 'open' | 'in_review' | 'resolved' | 'dismissed';
  explanation: string;
  page_number?: number;
  evidence_text?: string;
  rule_reference?: string;
  recommended_action?: string;
  confidence: number;
  human_review_required: boolean;
  resolution_notes?: string;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ChecklistItem {
  id: string;
  checklist_id: string;
  category: string;
  requirement_code: string;
  title: string;
  description: string;
  status: 'complete' | 'missing' | 'needs_verification' | 'not_applicable' | 'unsupported';
  notes?: string;
  evidence_document_id?: string;
  evidence_document_name?: string;
  evidence_page_number?: number;
  rule_reference?: string;
  document_references?: string[];
  created_at: string;
  updated_at: string;
}

export interface Checklist {
  id: string;
  project_id: string;
  jurisdiction_id: string;
  ruleset_version: string;
  items: ChecklistItem[];
  completion_stats: {
    total: number;
    complete: number;
    missing: number;
    needs_verification: number;
    percentage: number;
  };
  created_at: string;
  updated_at: string;
}

export interface AnalysisJob {
  id: string;
  project_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  current_step: string;
  current_step_number: number;
  total_steps: number;
  progress_percentage: number;
  logs: Array<{
    timestamp: string;
    step: string;
    message: string;
    level: string;
  }>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
}

export interface ReportItem {
  id: string;
  project_id: string;
  report_number: string;
  file_path: string;
  file_size: number;
  summary_data?: {
    documents_count: number;
    findings_count: number;
    checklist_items_count: number;
    critical_count: number;
    warning_count: number;
  };
  created_at: string;
}

export interface Jurisdiction {
  id: string;
  name: string;
  country: string;
  state_region: string;
  city: string;
  authority_name: string;
  is_supported: boolean;
  is_sample_ruleset: boolean;
  notes?: string;
}

export interface DashboardStats {
  total_projects: number;
  documents_awaiting_review: number;
  issues_requiring_attention: number;
  completed_reviews: number;
  recent_projects: Project[];
  recent_jobs: Array<{
    id: string;
    project_id: string;
    status: string;
    current_step: string;
    progress_percentage: number;
    started_at: string;
    completed_at?: string;
  }>;
}

export interface AIHealthStatus {
  available: boolean;
  ai_enabled: boolean;
  model: string;
  model_ready?: boolean;
  message: string;
  installed_models: string[];
}

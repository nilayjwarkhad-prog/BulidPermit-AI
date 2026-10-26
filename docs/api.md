# BuildPermit AI — API v1 Reference

All API routes are served under `/api/v1`. Interactive Swagger documentation is automatically available at `http://localhost:8000/docs`.

## 1. Authentication
- `POST /api/v1/auth/register`: Create user account (`email`, `password`, `full_name`, `role`).
- `POST /api/v1/auth/login`: Authenticate and receive JWT access token.
- `GET /api/v1/auth/me`: Retrieve current user profile.

## 2. Dashboard
- `GET /api/v1/dashboard/stats`: Returns project counts, open issues, document totals, and recent pipeline jobs.

## 3. Projects
- `POST /api/v1/projects`: Create a new building project with jurisdiction and property details.
- `GET /api/v1/projects`: List user's projects with progress and open finding metrics.
- `GET /api/v1/projects/{id}`: Retrieve project details.
- `PATCH /api/v1/projects/{id}`: Update project details.
- `DELETE /api/v1/projects/{id}`: Delete project and associated records.

## 4. Documents
- `POST /api/v1/projects/{id}/documents`: Upload document (PDF, PNG, JPG).
- `POST /api/v1/projects/{id}/seed_sample_documents`: 1-Click test seeder loading sample architectural set.
- `GET /api/v1/projects/{id}/documents`: List uploaded documents with category classifications.
- `GET /api/v1/documents/{id}`: Get document metadata.
- `PATCH /api/v1/documents/{id}/category`: Manually override classified category.
- `GET /api/v1/documents/{id}/preview/{page}`: Rendered PNG preview image.
- `GET /api/v1/documents/{id}/download`: Download raw uploaded document.
- `DELETE /api/v1/documents/{id}`: Soft delete document.

## 5. Analysis
- `POST /api/v1/projects/{id}/analysis`: Trigger the 9-step analysis pipeline.
- `GET /api/v1/analysis/{job_id}`: Poll status, current step, progress percentage, and execution logs.
- `GET /api/v1/projects/{id}/analysis/history`: List recent analysis jobs for this project.

## 6. Findings
- `GET /api/v1/projects/{id}/findings`: List findings with filters (`severity`, `category`, `status`, `document_id`).
- `PATCH /api/v1/findings/{id}`: Update finding status (`open`, `in_review`, `resolved`, `dismissed`) with resolution notes.
- `POST /api/v1/findings/{id}/ai_advice`: Consult local Qwen AI for non-technical resolution advice.

## 7. Checklist
- `GET /api/v1/projects/{id}/checklist`: Retrieve checklist items grouped by category with completion statistics.
- `PATCH /api/v1/checklist/items/{id}`: Update status and notes.

## 8. Reports
- `POST /api/v1/projects/{id}/reports`: Generate formal ReportLab PDF audit report.
- `GET /api/v1/projects/{id}/reports`: List generated reports.
- `GET /api/v1/reports/{id}/download`: Download compiled PDF report.

## 9. Jurisdictions & System Health
- `GET /api/v1/jurisdictions`: List supported permitting jurisdictions.
- `GET /health`: Overall API service health.
- `GET /health/ai`: Local Ollama & Qwen model connectivity and model health check.

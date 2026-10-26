# BuildPermit AI — System Architecture & Design

## 1. Executive Summary

**BuildPermit AI** is a pre-submission review and compliance preparation platform for residential building permit applications. It bridges the gap between homeowners/architects and municipal building departments by detecting missing documents, contradictory measurements, and zoning setback risks prior to formal municipal submittal.

## 2. Core Architectural Principles

1. **Non-Regulatory Safety Guarantee**: The system operates as a preparation and risk-detection assistant. It never guarantees permit approval or certifies structural safety.
2. **Deterministic Rules Over AI Hallucination**: Regulatory thresholds (e.g., minimum setback distances, address matching, required sheet presence) are evaluated deterministically in Python. Open-weight LLMs (Qwen 2.5 via Ollama) are utilized strictly for semantic explanation, categorization suggestions, and user-friendly recommendation summaries.
3. **Graceful Fallback**: If local AI/Ollama is offline or disabled, 100% of the project management, document upload, layout extraction, deterministic checklist checks, and PDF report generation features remain fully functional.
4. **Data Isolation & Privacy**: Uploaded CAD drawings and permit documents are stored in secure local paths and never transmitted to third-party paid AI APIs for training.

## 3. High-Level Architecture Diagram

```
+--------------------------------------------------------------------------+
|                        Client Layer (React 19 + Vite)                     |
|  - Modern Light-Neutral Theme with Dark Navy Typography                  |
|  - Real-Time 9-Step Pipeline Visualizer                                  |
|  - High-Resolution Document Page Viewer & Canvas Zoom                    |
|  - Pre-Submission Checklist & Finding Resolution Workflows               |
+------------------------------------+-------------------------------------+
                                     | (REST API via /api/v1)
+------------------------------------v-------------------------------------+
|                     FastAPI Backend Services Layer                       |
|  - JWT Bearer Security & Project Ownership Verification                  |
|  - Asynchronous Analysis Pipeline Coordinator                            |
|  - ReportLab PDF Report Generator                                        |
+-------------------+--------------------+-------------------+-------------+
                    |                    |                   |
+-------------------v---+  +-------------v----+  +-----------v-------------+
| Document Processing   |  | Compliance Engine |  | AI Integration Layer    |
| - File Validation     |  | - Cross-Doc Match |  | - Ollama Adapter        |
| - Dual-Engine PDF:    |  | - Setback Rules   |  | - Qwen 2.5-Coder Model  |
|   PyMuPDF & pypdf     |  | - Checklist Engine|  | - Structured JSON Output|
| - Field Extraction    |  | - Sample Registry |  | - Health & Fallback     |
+-----------------------+  +-------------------+  +-------------------------+
                    |                    |
+-------------------v--------------------v---------------------------------+
|                   Data Persistence (SQLAlchemy ORM)                      |
| - SQLite (Zero-config local dev) or PostgreSQL (Production)              |
| - Users, Projects, Documents, Versions, Findings, Checklists, Reports    |
+--------------------------------------------------------------------------+
```

## 4. The 9-Step Pre-Check Pipeline

1. **File Validation**: MIME verification, magic byte checks (`%PDF`, PNG, JPG), size validation (50MB max), and path traversal prevention.
2. **Text Extraction**: PyMuPDF / pure-Python `pypdf` extraction of text and page bounds.
3. **Page Preview Rendering**: High-res PNG previews generated per page for web inspection.
4. **Document Classification**: Keywords, title block cues, and AI suggestions.
5. **Field & Measurement Extraction**: Address, APN, setbacks, rooms, and square footages.
6. **Checklist Verification**: Mapping uploaded sheets to municipal requirements.
7. **Cross-Document Integrity Checks**: Detects address mismatches and square footage contradictions between sheets.
8. **Jurisdiction Rules Evaluation**: Setbacks and dimensional compliance checks.
9. **Pre-Check Compilation Ready**: Generates findings with evidence quotes and prepares the audit report.

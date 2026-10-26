# BuildPermit AI — Pre-Submission Assistant for Building Permits

> **AI Pre-Submission Review Platform — Not an Official Permit Approval**  
> An intelligent pre-submission assistant helping homeowners, architects, and builders inspect permit documents, detect cross-sheet inconsistencies, evaluate setback thresholds, and compile audit-ready packages before filing with municipal building departments.

---

## 🌟 Key Features

1. **Project & Jurisdiction Profiling**: Configure residential projects with country, state/region, city, and permitting authority with real-time jurisdiction support indicators.
2. **Secure Document Workspace**: Upload architectural plans, site surveys, structural calculations, and permit application forms (PDF, PNG, JPG) with magic byte validation, page count checks, and path traversal protection.
3. **9-Step Asynchronous Analysis Pipeline**:
   - File validation & geometry checking
   - PyMuPDF / pure-Python dual-engine PDF extraction
   - High-resolution page preview rendering for web inspection
   - Document classification (Permit Application, Site Plan, Floor Plan, Structural, etc.)
   - Structured field extraction (Address, APN, setbacks, rooms, square footage)
   - Pre-submission checklist mapping
   - Deterministic cross-document consistency checks (detects address typos and conflicting square footages across sheets)
   - Zoning & setback rules evaluation
   - Pre-check audit report compilation
4. **Interactive Document Viewer**: Inspect high-resolution blueprint pages with zoom, page navigation, direct download, and extracted fields breakdown.
5. **Audited Findings & AI Explanations**: Review flagged items with sheet page links, evidence quotes, and plain-language resolution guidance powered by local Qwen 2.5 AI.
6. **Pre-Submission Checklist**: Grouped municipal requirements with completion tracking and linked document references.
7. **ReportLab PDF Generation**: Generates and downloads official pre-submission review reports labeled *"AI Pre-Submission Review Report — Not an Official Permit Approval"*.
8. **1-Click Test Seeder**: Populate any project with realistic architectural drawings and permit applications to test the complete pre-check workflow instantly.

---

## 🏗️ Project Structure

```
Hecktober/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & startup lifecycle
│   │   ├── config.py                   # Pydantic BaseSettings & env configuration
│   │   ├── api/v1/                     # Versioned REST API endpoints
│   │   │   ├── auth.py                 # Registration, login, profile
│   │   │   ├── projects.py             # Project CRUD & dashboard statistics
│   │   │   ├── documents.py            # Upload, preview, download, sample seeder
│   │   │   ├── analysis.py             # 9-step pipeline execution & polling
│   │   │   ├── findings.py             # Findings listing, filtering, AI advice
│   │   │   ├── checklist.py            # Requirements checklist management
│   │   │   ├── reports.py              # ReportLab PDF report generation & download
│   │   │   └── jurisdictions.py        # Supported jurisdictions registry
│   │   ├── core/                       # Security, password hashing, sanitized logging
│   │   ├── db/                         # SQLAlchemy engine & session management
│   │   ├── models/                     # SQLAlchemy declarative models
│   │   ├── schemas/                    # Pydantic v2 validation schemas
│   │   ├── document_processing/        # PDF loaders, classifiers, field extractors
│   │   ├── compliance/                 # Rule engine, cross-doc checks, checklist engine
│   │   ├── ai/                         # Ollama adapter, Qwen model client, fallbacks
│   │   └── reports/                    # ReportLab PDF generator
│   ├── tests/                          # 10 automated test suites with 100% pass rate
│   ├── scripts/                        # Sample document generation scripts
│   ├── storage/                        # Uploads, page previews, generated PDF reports
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                 # Reusable layout, document, and finding components
│   │   ├── pages/                      # Landing, Auth, Dashboard, Workspace, Analysis
│   │   ├── context/                    # AuthContext with 1-click quick demo login
│   │   ├── services/                   # Typed API service client
│   │   ├── types/                      # TypeScript schemas
│   │   └── App.tsx                     # React Router v7 routes
│   ├── Dockerfile
│   └── package.json
├── data/
│   └── sample_documents/               # Realistic sample PDFs for instant testing
├── docs/                               # Architecture, API, Security, Jurisdiction guides
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Local Setup

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend starts at `http://127.0.0.1:8000`.  
Interactive Swagger docs: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend starts at `http://localhost:5173`.

---

## 🤖 Local AI Model Setup (Optional but Recommended)

BuildPermit AI integrates with open-weight instruction models via **Ollama** running locally on your workstation.

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai).
2. **Pull the Qwen Model**:
   ```bash
   ollama pull qwen2.5-coder:7b
   ```
3. **Verify Connectivity**:
   ```bash
   curl http://localhost:11434/api/tags
   ```

> **Note**: If Ollama or the model is not installed or offline, BuildPermit AI **automatically operates in deterministic fallback mode**. All document parsing, cross-document checks, checklist reviews, and PDF report downloads continue to function seamlessly.

---

## 🧪 Running Automated Tests

Run the test suite using `pytest`:

```bash
cd backend
.\.venv\Scripts\pytest.exe -v
```

**Test Coverage Highlights**:
- User registration, login, and JWT decoding
- Project ownership isolation (access control between users)
- File validation (rejecting corrupt, oversized, and disallowed files)
- Address normalization and cross-sheet inconsistency detection
- Stated square footage conflict detection
- Setback rule threshold evaluation
- ReportLab PDF compilation and download
- End-to-end 9-step analysis pipeline execution

---

## 🎯 Instant Walkthrough with Demo Account

1. Navigate to `http://localhost:5173/login`.
2. Click **"1-Click Sign In with Demo Account (Alex Builder)"**.
3. In the Dashboard, click **"Create New Project"** or open an existing project.
4. In the **Documents** tab, click **"Load Sample Architectural Set"** to seed realistic permit applications, site plans, floor plans, and structural notes.
5. In the **AI Pre-Check** tab, click **"Run AI Pre-Check"** to watch the real-time 9-step pipeline progress.
6. In the **Findings** tab, review flagged items (e.g. address typos between sheets, conflicting stated square footages), inspect the referenced sheets in the viewer, and click **"Explain with AI Advice"**.
7. In the **Reports** tab, click **"Generate New PDF Report"** and download your compiled PDF audit report!

---

## ⚖️ Disclaimer

BuildPermit AI is a pre-submission review tool designed to assist applicants in identifying common documentation errors prior to formal permit filing. It is not an official permit-issuing authority and does not replace the professional judgment of licensed architects, engineers, or municipal plan examiners.

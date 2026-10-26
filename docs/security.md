# BuildPermit AI — Security & Privacy Architecture

## 1. Authentication & Session Management
- **Password Security**: Passwords are encrypted using salted `bcrypt` hashes. Plaintext passwords are never stored or logged.
- **JWT Authorization**: Requests utilize signed JSON Web Tokens (HS256) with configurable expiration (`ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Strict Ownership Checks**: Every endpoint accessing projects, documents, or reports validates that `project.user_id == current_user.id`. Frontend assumptions are never trusted for authorization.

## 2. File Upload & Document Pipeline Security
- **Magic Byte Verification**: Uploads are validated against magic byte signatures (`%PDF` for PDFs, PNG headers, and JPEG markers) rather than trusting client-provided filenames or MIME headers.
- **Path Traversal Protection**: Filenames containing `..`, `/`, or `\` are rejected. Internal storage uses UUID-derived filenames stored outside the public web root.
- **Resource Constraints**: Uploads are capped at 50 MB and 150 pages per document to prevent memory exhaustion and DoS attacks.
- **Private File Downloads**: Document and report download endpoints require Bearer authentication. Uploaded documents are never exposed through guessable public URLs.

## 3. Data Privacy & Sanitized Logging
- **Model Privacy**: Documents are processed locally via open-weight models running on Ollama. Files are never shared with cloud LLM providers or used for public training.
- **Sanitized Logging**: Loggers employ regex masking to redact passwords, JWT tokens, and sensitive personal parameters.

## 4. Production Deployment Checklist
- Enable HTTPS with automatic TLS certificates (e.g., Let's Encrypt / Caddy).
- Configure production PostgreSQL with daily automated database backups.
- Place the document storage directory on an encrypted volume (EBS / dm-crypt).
- Enable rate limiting on authentication routes (e.g. 5 attempts/minute).

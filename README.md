# Studyio

AI-powered study assistant for working with documents, summarization, and document-based question answering.

## Overview

Studyio is an AI study assistant that allows users to upload documents and interact with their content using AI.

The current system focuses on:

* Document upload and processing
* AI-powered document summarization
* Document-based question answering
* Relevance-based document retrieval
* Multiple AI providers through a central AI router
* Persian and English responses
* React/Vite frontend
* Python backend

The application is designed so that AI provider credentials remain on the backend and are never exposed to the frontend.

---

## Architecture

```text
Studyio
│
├── frontend/                 # React + Vite frontend
│
├── app/
│   └── services/
│       ├── ai_router.py      # Central AI provider router
│       ├── document_ai_service.py
│       ├── kilo_provider.py
│       └── gapgpt_provider.py
│
├── run.py                    # Backend entry point
│
└── .env                     # Local/server secrets (NOT committed)
```

### Main components

#### Frontend

The frontend is built with:

* React
* Vite
* CSS

The frontend communicates with the backend API and does not contain AI API keys.

#### Backend

The backend is responsible for:

* Document processing
* AI requests
* Provider selection
* Summarization
* Question answering
* Relevance detection

#### AI Router

`app/services/ai_router.py`

The AI router provides a single interface for sending requests to the configured AI provider.

This allows the application to switch between providers without changing the document-processing logic.

#### Document AI Service

`app/services/document_ai_service.py`

This service handles:

* Large-document summarization
* Batch creation based on character limits
* Progressive summary reduction
* Final summary compression
* Document question answering
* Keyword-based relevance retrieval
* Persian/English response handling

---

# Requirements

Recommended development environment:

* Python 3.10+
* Node.js 18+
* npm
* Git

For production:

* Ubuntu VPS
* Python 3.10+
* Node.js 18+
* Nginx
* systemd or another process manager
* HTTPS-enabled domain

---

# Clone the project

```bash
git clone git@github.com:Nyctorn1/Studyio.git
cd Studyio
```

---

# Backend setup

Create a Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

If the project does not currently contain a `requirements.txt`, create/update it before deployment.

---

# Environment variables

Create a `.env` file in the project root.

Example:

```env
AI_PROVIDER=kilo

KILO_API_KEY=your_api_key_here
GAPGPT_API_KEY=your_api_key_here
```

Use the actual variables required by the configured providers.

### Important

Never commit `.env` to Git.

Check:

```bash
git status
```

and make sure `.env` is ignored.

A recommended `.gitignore` entry:

```gitignore
.env
.env.*
!.env.example
.venv/
__pycache__/
node_modules/
dist/
```

For development, create an example environment file:

```bash
cp .env.example .env
```

The example file must contain placeholders only.

Never put real API keys in:

* GitHub
* frontend source code
* React environment variables
* screenshots
* README files
* public configuration files

---

# Run the backend

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Then run:

```bash
python run.py
```

The exact host and port depend on the backend configuration.

For local development, the backend should normally be available on:

```text
http://127.0.0.1:<PORT>
```

---

# Frontend setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Vite development server:

```bash
npm run dev
```

Vite will print the local URL in the terminal.

---

# Frontend production build

Create a production build:

```bash
cd frontend
npm run build
```

The generated production files will normally be placed in:

```text
frontend/dist/
```

The `dist/` directory should not normally be committed to Git.

---

# Local development

A typical local setup uses two terminals.

### Terminal 1 — Backend

```bash
cd ~/projects/ai-study-assistant

source .venv/bin/activate

python run.py
```

### Terminal 2 — Frontend

```bash
cd ~/projects/ai-study-assistant/frontend

npm run dev
```

Then open the URL shown by Vite.

---

# Document summarization

Studyio summarizes large documents progressively rather than sending the entire document to the AI in one request.

The process is approximately:

```text
Original document
       │
       ▼
Document chunks
       │
       ▼
Character-based batches
       │
       ▼
Intermediate summaries
       │
       ▼
Progressive reduction
       │
       ▼
Final compression
       │
       ▼
Final document summary
```

The summary system uses character limits instead of assuming that every chunk has the same size.

Important configuration values are defined in:

```text
app/services/document_ai_service.py
```

For example:

```python
MAX_CHARS_PER_BATCH = 12000
FINAL_SUMMARY_RATIO = 0.20
MAX_CHARS_PER_REDUCTION_BATCH = 16000
```

The final summary target is approximately 20% of the original document size.

---

# Document question answering

The question-answering system does not send the entire document to the AI for every question.

Instead:

```text
User question
      │
      ▼
Keyword extraction
      │
      ▼
Chunk relevance scoring
      │
      ▼
Relevant chunks
      │
      ▼
AI provider
      │
      ▼
Answer
```

The system attempts to:

* Select relevant document sections
* Preserve the original document order
* Limit the amount of context sent to the AI
* Prevent unsupported answers
* Answer only from the provided document
* Support Persian and English

If the document does not contain enough information, the model is instructed to say so instead of using outside knowledge.

---

# AI Providers

AI providers are accessed through:

```text
app/services/ai_router.py
```

Current provider implementations include:

```text
app/services/kilo_provider.py
app/services/gapgpt_provider.py
```

The router allows the rest of the application to remain independent from a specific AI provider.

When changing providers, avoid putting provider-specific logic inside:

```text
document_ai_service.py
```

Provider-specific authentication and request handling should remain inside the provider implementation.

---

# Language support

The document AI service currently supports:

```text
fa
en
```

Persian mode returns Persian responses.

English mode returns English responses.

Unsupported languages should raise a validation error rather than silently falling back to another language.

---

# Git workflow

Check the current state:

```bash
git status
```

Review changes:

```bash
git diff
```

Stage changes:

```bash
git add .
```

Commit:

```bash
git commit -m "Describe the change"
```

Push:

```bash
git push origin master
```

Check recent commits:

```bash
git log --oneline -5
```

---

# Production deployment

The recommended production architecture is:

```text
                    Internet
                       │
                       ▼
                  Domain / HTTPS
                       │
                       ▼
                     Nginx
                  ┌────┴────┐
                  │         │
                  ▼         ▼
             Frontend    Backend
              static       API
               files        │
                            ▼
                       AI Provider
```

The AI API keys remain on the VPS.

Testers only access the application through the browser.

They should not need:

* Python
* Node.js
* `.env`
* API keys
* Git
* terminal access

---

# VPS deployment

Recommended production environment:

```text
Ubuntu
Python
Node.js
Nginx
Git
HTTPS
```

Clone the repository on the VPS:

```bash
git clone git@github.com:Nyctorn1/Studyio.git
cd Studyio
```

Create the Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the server-side environment file:

```bash
nano .env
```

Add the required provider configuration.

Do not commit this file.

---

# Updating the production server

After pushing new code to GitHub:

```bash
cd /path/to/Studyio
git pull origin master
```

If Python dependencies changed:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

If frontend dependencies changed:

```bash
cd frontend
npm install
npm run build
```

Then restart the backend service according to the production process manager.

---

# Security

Never expose AI provider credentials to the browser.

Do not use secret API keys in:

```text
VITE_*
```

environment variables.

Vite variables prefixed with `VITE_` are intended to be available to frontend code and can therefore become public.

AI credentials must remain backend-only.

Before every production deployment, verify:

```bash
git status
```

and make sure no secret files are staged.

You can also check tracked files with:

```bash
git ls-files | grep -E '(^|/)\.env($|\.)|\.pem$|credentials|secret|api[_-]?key'
```

This command should not return real secret files.

---

# Testing checklist

Before giving the application to testers, verify:

* [ ] Frontend loads successfully
* [ ] Backend is running
* [ ] Document upload works
* [ ] Document processing works
* [ ] Summary generation works
* [ ] Persian summary works
* [ ] English summary works
* [ ] Question answering works
* [ ] Irrelevant questions are rejected appropriately
* [ ] AI provider credentials are available only on the server
* [ ] No API key is present in frontend code
* [ ] HTTPS works
* [ ] Application works from a different device/network

---

# Current development status

The application currently uses a backend-controlled AI architecture.

The immediate deployment goal is to provide testers with a normal user experience where they only need to open the application and use it.

Server-side configuration, API credentials, AI provider selection, and application infrastructure should remain invisible to testers.

---

# Project

Repository:

```text
git@github.com:Nyctorn1/Studyio.git
```

Main branch:

```text
master
```

The project is currently being prepared for remote testing and VPS deployment.

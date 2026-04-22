# Resume Navigator

Resume Navigator is a Chinese-first resume diagnosis system focused on:

- deterministic ATS checks
- structured JD parsing
- explainable resume-to-JD matching
- early beta feedback collection
- safe rewrite assistance
- future resume-to-interview continuity

This repository currently contains two layers:

- the original Streamlit prototype in `app.py`
- the new backend-oriented architecture under `backend/` and `apps/`

## Current Status

The project is in active refactor.

The goal of the refactor is to move core logic out of the Streamlit monolith and into reusable services that are easier to test, document, and deploy.

## What Is Already Implemented In The New Architecture

- modular configuration layer
- structured domain schemas
- resume parsing service for PDF and DOCX
- deterministic ATS rule engine
- deterministic JD parser
- deterministic matching engine with must-have coverage, impact signals, experience signals, and confidence scoring
- analysis orchestration pipeline
- browser-based FastAPI demo entrypoint with Simplified Chinese default and English switch
- local history and beta feedback collection
- unit-testable deterministic core

## Quick Start

### 1. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `python` is not on your `PATH`, use your installed Python executable directly.

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in the values you need.

At minimum, the deterministic analysis path works without model keys.

Model keys are only needed for future LLM-powered explanation and rewrite stages.

### 4. Run the new API

```powershell
uvicorn apps.web.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/history`
- `http://127.0.0.1:8000/feedback`
- `http://127.0.0.1:8000/docs`

### 5. Run the old Streamlit prototype

```powershell
streamlit run app.py
```

### 6. Run a local deterministic analysis from the terminal

```powershell
python scripts\run_local_analysis.py --resume "your_resume.pdf" --jd-file "target_jd.txt"
```

## Repository Structure

```text
apps/
  web/
backend/
  api/
  core/
  providers/
  services/
docs/
tests/
```

## Collaboration And Feedback

This repository now includes:

- CI workflow
- issue templates
- pull request template
- contribution guide
- security policy

These files are there on purpose so we can start collecting structured feedback during development instead of waiting until the product is "done."

## Growth And Release Docs

- `docs/GROWTH_PLAYBOOK_ZH.md`
- `docs/GITHUB_UPLOAD_GUIDE_ZH.md`
- `docs/LOCAL_VALIDATION_GUIDE_ZH.md`
- `docs/COMMUNITY_PUBLISHING_GUIDE_ZH.md`
- `docs/LLM_INTEGRATION_DECISION_ZH.md`
- `docs/SEARCH_INTERVIEW_GTM_STRATEGY_ZH.md`
- `docs/BETA_TESTER_OPERATIONS_ZH.md`

## Validation

### Quick validation

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1
```

### Validation with a real resume and a JD file

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate_project.ps1 -ResumePath "your_resume.pdf" -JdFile "data\samples\sample_supply_chain_jd.txt"
```

### Check GitHub publish readiness

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_publish_readiness.ps1
```

## Compliance Note

The open-source default product is designed to be useful without relying on unauthorized scraping of protected job platforms.

Private research connectors can exist as optional local-only adapters, but they should never be the foundation of the public product.

## Next Milestones

1. complete repository cleanup
2. migrate more logic out of `app.py`
3. add rewrite service and export flow
4. add evidence cards and interview prep

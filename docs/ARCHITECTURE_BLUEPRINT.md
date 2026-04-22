# Resume Navigator Code Design Blueprint

Version: v0.1
Date: 2026-04-21
Status: Draft

## 1. Architecture Goals

- modularize the current Streamlit monolith
- keep deployment cost low
- support local single-user mode and future hosted multi-user mode
- support deterministic analysis first and LLM enrichment second
- support optional background tasks without forcing heavy infrastructure on day one

## 2. Recommended Technical Direction

### Default stack

- backend: `FastAPI`
- frontend: server-rendered `Jinja2` + `HTMX` + `Alpine.js`
- style layer: custom CSS design system
- database: `SQLite` for local development, `PostgreSQL` for hosted deployment
- file storage: local filesystem in dev, object storage optional later
- background jobs: FastAPI background tasks for MVP, `RQ + Redis` as an upgrade path
- PDF/DOCX parsing: `pdfplumber`, `python-docx`, optional OCR fallback later
- LLM provider layer: provider abstraction with `Gemini` first, optional `OpenAI` support later

### Why this direction

- easier for a Python-first beginner to maintain
- lower ops cost than a multi-service Java or Node-heavy stack
- cleaner long-term structure than the current Streamlit monolith
- enough frontend flexibility for a polished product without forcing a full SPA immediately

## 3. Migration Strategy

### Stage 1

- keep the current Streamlit app as a prototype reference only
- stop adding new core logic into `app.py`
- move parsing, scoring, rewriting, and ingestion into reusable service modules

### Stage 2

- build FastAPI routes and background task endpoints
- add new web UI over the service layer

### Stage 3

- optionally keep a hidden developer/demo Streamlit page if helpful
- production path uses the new app architecture

## 4. High-Level System Diagram

```text
User
  -> Web UI
  -> API Router
  -> Orchestration Service
  -> Resume Parser
  -> JD Parser
  -> ATS Rule Engine
  -> Match Engine
  -> Evidence Engine
  -> Rewrite Engine
  -> Interview Engine
  -> Storage Layer
  -> Export Layer
```

## 5. Proposed Repository Layout

```text
Resume_ATS_Project/
  apps/
    web/
      main.py
      templates/
      static/
  backend/
    api/
      routes/
      schemas/
    core/
      config.py
      logging.py
      security.py
    db/
      base.py
      models/
      repositories/
    services/
      resume/
      jd/
      ats/
      matching/
      evidence/
      rewrite/
      interview/
      history/
      export/
    providers/
      llm/
      storage/
      search/
    workers/
      tasks.py
  docs/
  tests/
    unit/
    integration/
    fixtures/
  scripts/
  data/
    samples/
```

## 6. Core Domain Objects

### ResumeAsset

- original uploaded file metadata
- file hash
- storage path
- source type

### ResumeDocument

- normalized text
- extracted sections
- extracted entities
- parsing warnings

### ResumeSection

- section type
- raw text
- normalized text
- time range
- bullet list

### JobDescription

- raw JD text
- normalized JD text
- company name
- role name
- industry hints
- structured requirement groups

### MatchReport

- overall score
- component scores
- matched items
- missing items
- risky items
- explanation summary

### EvidenceCard

- title
- summary
- source URL
- source type
- capture date
- confidence
- scope tag

### RewriteDraft

- source version
- target section
- original text
- suggested text
- rationale
- status

### InterviewPack

- target role
- question list
- answer framework
- weak-point reminders

## 7. Processing Pipeline

### 7.1 Resume ingestion

1. upload file
2. validate type and size
3. save asset metadata
4. parse text
5. segment sections
6. extract structured signals
7. store normalized document

### 7.2 JD ingestion

1. accept pasted JD or imported text
2. normalize formatting
3. extract company and role
4. classify requirements
5. map skills into taxonomy
6. store structured JD

### 7.3 Diagnosis pipeline

1. run ATS format engine
2. run structural completeness checks
3. run JD-resume match engine
4. optionally request evidence enrichment
5. request LLM explanation and rewrite hints
6. persist report and render result view

### 7.4 Rewrite pipeline

1. select sections or full document
2. generate section-safe rewrites
3. mark unsupported claims as user-confirmation-needed
4. allow human edits
5. save as new draft version
6. export

### 7.5 Interview pipeline

1. read latest JD and match report
2. identify gap topics
3. generate likely questions
4. generate answer skeletons
5. store practice package

## 8. Engine Design

## 8.1 ATS Rule Engine

This engine should be fully deterministic.

Suggested checks:

- page count
- image count
- table count
- scan-only PDF risk
- extractability score
- suspicious layout density
- missing essential sections

Output:

- finding code
- severity
- affected section
- user-facing explanation
- remediation hint

## 8.2 JD Parser Engine

Responsibilities:

- extract role metadata
- identify must-have and nice-to-have requirements
- map terminology to normalized taxonomy
- score requirement confidence

Implementation idea:

- regex and dictionary extraction first
- LLM only for structured fallback and ambiguity resolution

## 8.3 Match Engine

The match engine should use weighted deterministic signals.

Candidate score components:

- ATS format score
- hard skill coverage score
- tool stack coverage score
- experience relevance score
- quantified impact score
- section completeness score
- timeline consistency score
- keyword stuffing penalty

This is the main originality layer of the product.

## 8.4 Evidence Engine

Responsibilities:

- collect optional market signals from approved sources
- deduplicate similar findings
- store citations
- distinguish evidence certainty levels

Evidence types:

- official company recruiting page
- official company IR or recruiting articles
- public hiring report
- manually imported job posting set
- optional research connector result

Rules:

- external evidence never silently changes deterministic score rules
- evidence can adjust suggestions and risk notes
- every evidence-derived statement must have provenance

## 8.5 Rewrite Engine

Responsibilities:

- rewrite section by section
- preserve facts
- avoid unsupported additions
- expose rationale for each edit

Safety rules:

- no invented metrics
- no invented companies, projects, titles, or dates
- any missing proof becomes a "suggestion template", not a committed fact

## 8.6 Interview Engine

Responsibilities:

- convert resume and JD gaps into interview topics
- generate questions with follow-up intent
- provide answer structure and reminders

## 9. LLM Provider Abstraction

Create a unified interface:

```text
LLMProvider
  -> analyze_structured_json()
  -> explain_findings()
  -> rewrite_section()
  -> generate_interview_pack()
```

Benefits:

- avoid hard-coding one provider into every module
- allow future Gemini and OpenAI switching
- make tests easier with mocked providers

## 10. Data Source Connector Strategy

Design all external data ingestion behind adapters:

```text
SourceAdapter
  -> fetch()
  -> normalize()
  -> validate()
  -> to_evidence_cards()
```

Examples:

- `UserImportedJDAdapter`
- `OfficialCareerSiteAdapter`
- `PublicReportAdapter`
- `ManualCorpusAdapter`
- `ResearchConnectorAdapter`

## 11. BOSS直聘 Connector Policy

### Default open-source behavior

- no built-in unauthorized crawler enabled by default
- no dependency on BOSS-specific scraping for core product value
- no browser profile artifacts in repository

### If a future connector is added

- place it under `providers/search/research_connectors/`
- mark it experimental
- disable by default
- require explicit environment flag
- never let it bypass source citation requirements

### Reason

The reviewed public agreement material indicates restrictions on unauthorized spider, crawler, anthropomorphic automation, and abnormal browsing for data acquisition. Therefore the architecture must treat such sources as optional and high-risk, not foundational.

## 12. Storage Design

### Tables or model groups

- users
- resume_assets
- resume_documents
- job_descriptions
- match_reports
- report_components
- evidence_cards
- rewrite_drafts
- interview_packs
- task_runs

### Local-first policy

- local mode should run with SQLite and local files
- hosted mode can switch to PostgreSQL and object storage without code rewrite

## 13. Background Task Design

### MVP

- synchronous parsing
- background explanation and rewrite generation

### Upgrade path

- `task_runs` table records state
- states: `PENDING`, `RUNNING`, `FAILED`, `COMPLETED`
- UI polls task state
- retry only idempotent tasks

## 14. API Design

### Suggested route groups

- `POST /api/resumes`
- `POST /api/job-descriptions`
- `POST /api/analysis`
- `GET /api/analysis/{id}`
- `POST /api/rewrite-drafts`
- `PATCH /api/rewrite-drafts/{id}`
- `POST /api/exports/pdf`
- `POST /api/interview-packs`

## 15. UI Design Blueprint

### Main pages

- landing page
- new diagnosis page
- analysis detail page
- rewrite workspace page
- history page
- interview prep page

### UX requirements

- show "what failed", not only "score"
- show priority labels like `must fix`, `important`, `optional`
- show evidence sources when external insight is used
- show diff view for rewrite suggestions
- keep language simple for beginners

## 16. Evaluation and Testing

### Unit tests

- parser behavior
- ATS rules
- JD normalization
- match score calculation
- rewrite safety guards

### Integration tests

- upload -> parse -> analyze -> rewrite flow
- background task status flow
- export flow

### Golden dataset

- create sample resumes and JDs
- preserve expected structured outputs
- compare scoring stability after refactors

## 17. Security and Privacy

- no user API keys stored in plain text unless explicitly chosen for local mode
- secrets in environment variables only
- uploaded resumes excluded from Git tracking
- clear deletion controls for local history
- redact personal data in debug logs

## 18. Repository Hygiene Rules

- remove `.tmp`
- remove browser profiles and cache directories
- expand `.gitignore`
- add `README.md`
- add `.env.example`
- add `LICENSE`
- add automated checks

## 19. Recommended First Refactor Tasks

1. clean repository artifacts and tighten `.gitignore`
2. extract parser layer from current `utils/parser.py`
3. design structured data schemas
4. implement deterministic ATS engine
5. implement structured JD parser
6. implement deterministic match engine
7. wrap Gemini calls behind a provider interface
8. move history from JSON blobs toward a database-backed repository
9. create analysis API and a minimal UI shell

## 20. Definition of Done For The New Core

The new architecture is successful when:

- a fresh machine can run the project from documented steps
- the diagnosis result is mostly derived from auditable logic
- LLM output is constrained and replaceable
- the app remains useful even with external enrichment disabled
- the repository is clean enough for public GitHub release

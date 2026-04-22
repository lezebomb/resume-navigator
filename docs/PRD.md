# Resume Navigator PRD

Version: v0.1
Date: 2026-04-21
Status: Draft

## 1. Product Positioning

`Resume Navigator` is a resume diagnosis and job-targeting system for Chinese job seekers.

It is not just a "resume scoring tool".

It is a complete job application copilot that helps users:

- understand whether their resume can pass ATS
- understand why they do or do not match a target JD
- get evidence-backed optimization suggestions
- generate editable improvement drafts without fabricating experience
- continue into interview preparation after resume optimization

## 2. Why This Product Should Exist

Current job seekers usually face five problems:

- they do not know whether their resume fails because of formatting, keyword mismatch, weak experience framing, or lack of quantified results
- they receive generic AI suggestions that sound good but are not actionable
- they cannot tell which recommendations are trustworthy and which are hallucinated
- they do not want full auto-generated resumes that may create fake content
- after optimizing a resume, they still do not know how to prepare for the actual interview

Our product should solve these with a more practical workflow:

- deterministic ATS checks
- structured JD matching
- source-backed market insight cards
- safe rewrite assistance
- resume-to-interview continuity

## 3. Product Goals

### Core goals

- help users improve resume pass-through probability for real target roles
- keep usage low-cost and easy to deploy
- preserve originality and avoid code plagiarism
- provide clear explanations instead of opaque model scores
- support privacy-first local deployment and lightweight public deployment

### Business and open-source goals

- become a GitHub-ready, documented, reproducible project
- be useful for individual job seekers, counselors, and student communities
- support community contributions without exposing risky scraping defaults

## 4. Target Users

### Primary users

- fresh graduates
- early-career candidates switching jobs
- non-technical job seekers who need guided resume optimization
- Chinese job seekers applying through ATS-heavy channels

### Secondary users

- career coaches
- university就业指导老师
- communities that want a deployable open-source resume tool

## 5. Core Differentiators

- Chinese resume optimization first, not generic English-only ATS scoring
- dual-engine analysis: deterministic rule engine first, LLM explanation second
- evidence cards for external market insight, instead of hidden prompt stuffing
- anti-fabrication rewrite policy: optimize expression, never invent achievements
- resume diagnosis linked to interview preparation
- privacy mode for local use, not only cloud SaaS thinking

## 6. Lessons Borrowed From Other Projects Without Copying Code

We will borrow product mechanisms, not implementation code.

### From `interview-guide`

- async analysis pipeline
- task status tracking
- history, retry, and reanalysis workflow
- linking resume analysis with later interview preparation

### From `careerlyze`

- persistent analysis records
- asynchronous rewrite generation
- editable improved resume draft
- exportable result flow

### From `Resume-Optimization`

- editable intermediate representation
- markdown-style content transformation pipeline
- emphasis on editable output rather than black-box output

### From `AI-Mock-Interview-Platform`

- transition from resume stage to interview stage
- question generation and targeted feedback loop

### From our current project

- ATS format checks already exist
- Chinese job-market orientation already exists
- job ecosystem and community data ingestion direction already exists

## 7. Product Principles

- explanation before decoration
- evidence before confidence
- editability before automation
- originality before imitation
- low-cost deployment before heavy infrastructure
- compliance before aggressive data acquisition

## 8. Scope Definition

### MVP scope

- resume upload and parsing for PDF and DOCX
- ATS format diagnosis
- structured JD parsing
- resume-to-JD match scoring with deterministic metrics
- safe AI explanation layer
- actionable optimization suggestions
- editable rewritten draft
- export to Markdown and PDF
- analysis history

### V1 scope

- multi-target comparison for one resume against multiple JDs
- evidence-backed external insight cards
- company and industry preference summaries
- user feedback loop on suggestion quality
- interview question pack generated from resume gaps and target JD

### V2 scope

- multiple resume versions per user
- role-specific optimization presets
- collaboration mode for counselors or mentors
- benchmark dataset and evaluation dashboard
- optional recruiter-side matching view

## 9. Core User Flows

### Flow A: First-time diagnosis

1. User uploads resume.
2. User pastes or imports a target JD.
3. System parses resume and JD into structured objects.
4. System runs deterministic ATS checks and match scoring.
5. System optionally enriches analysis with evidence cards from allowed data sources.
6. System generates a diagnosis report with scores, explanations, and fix priority.
7. User reviews detailed suggestions.

### Flow B: Resume improvement

1. User chooses which sections to optimize.
2. System generates section-level rewrite suggestions.
3. User sees "original vs suggestion vs reason".
4. User accepts or edits suggestions manually.
5. System saves a new draft version.
6. User exports the final resume.

### Flow C: Interview continuation

1. User clicks "prepare interview".
2. System derives likely interview questions from JD, resume strengths, and weak points.
3. System creates answer frameworks and warning points.
4. User practices and reviews feedback.

## 10. Functional Requirements

### 10.1 Resume parsing

- support PDF and DOCX
- extract raw text and preserve section boundaries when possible
- detect education, work experience, projects, skills, awards, certifications, self-summary
- extract time ranges, numbers, tools, responsibilities, and outcomes

### 10.2 ATS format engine

- detect tables, images, multi-column risk, scan-only PDFs, page count issues
- detect ATS-unfriendly visual constructs
- produce severity-tagged findings

### 10.3 JD parser

- identify job title, company, function, industry hints, seniority, location
- classify requirements into must-have, preferred, soft skills, tools, experience, education
- normalize skills into a canonical taxonomy

### 10.4 Matching engine

- compute keyword coverage
- compute hard skill coverage
- compute experience relevance
- compute quantified achievement density
- compute section completeness
- compute timeline consistency
- compute anti-keyword-stuffing signals
- provide weighted overall score with role-specific weights

### 10.5 Explanation engine

- translate structured scoring into human-readable suggestions
- never override deterministic findings silently
- flag uncertain or inferred judgments explicitly

### 10.6 Rewrite engine

- section-level rewrite only
- preserve factual truth
- ask user to confirm any content that needs missing evidence
- provide safe templates for STAR/CAR framing

### 10.7 Evidence card engine

- show title, summary, source URL, source type, capture date, confidence
- separate "company-specific" from "industry-generic" insights
- allow disabling external enrichment

### 10.8 Interview prep engine

- generate role-specific question sets
- tie questions to weak spots in the resume
- provide answer framework and follow-up risk notes

## 11. Data Strategy

### Tier A: user-provided data

- pasted JD
- uploaded resume
- manually imported job text
- user-confirmed notes and edits

This is the safest and most reliable default data source.

### Tier B: public and low-risk knowledge sources

- public hiring reports
- official company recruitment pages
- official investor relations pages
- user-uploaded or manually reviewed public job postings

### Tier C: research connectors

- controlled source adapters for public web pages
- disabled by default in the open-source product
- only enabled after explicit user configuration and legal review

## 12. BOSS直聘 and Similar Platform Data Strategy

### Product decision

We can design a connector layer that is technically capable of ingesting job-market data, but we should not make unauthorized crawling of `BOSS直聘` or similar platforms the default foundation of the product.

### Why

- public evidence of an official public open API is not clear from the sources reviewed
- the `BOSS直聘` user agreement explicitly restricts unauthorized use of spider, crawler, anthropomorphic automation, or other abnormal browsing methods to obtain platform data
- relying on unauthorized scraping would create legal, operational, and repository-distribution risks

### What we should do instead

- treat `BOSS直聘` as a potential future connector only if official authorization or a compliant channel is obtained
- keep all such connectors behind an interface, not hardwired into core scoring
- make the open-source default product work well with user-provided JD text and public low-risk sources
- support a user-operated research mode in private environments only after explicit warning and local configuration

### Practical compromise

Our system should be optimized to gain value even without any risky platform scraping:

- better JD parsing
- better resume structuring
- better deterministic scoring
- stronger rewrite workflow
- better evidence cards from compliant sources

This makes the product useful on day one and robust enough for GitHub release.

## 13. Originality Strategy

To maximize usefulness while staying original:

- we will not copy code, prompts, schemas, or UI from reference projects
- we will design our own scoring formula and data structures
- we will create our own Chinese-first skill taxonomy and rewrite policy
- we will build our own evidence-card workflow and anti-fabrication constraints
- we will preserve your existing research-agent direction, but redesign it into a more trustworthy ingestion system

## 14. Success Metrics

### Product quality metrics

- percentage of resumes successfully parsed
- percentage of JDs successfully structured
- percentage of suggestions accepted by users
- export completion rate
- interview-prep continuation rate

### Model quality metrics

- keyword coverage precision
- section extraction accuracy
- hallucination incident rate in rewrite suggestions
- evidence-card citation coverage

### Engineering metrics

- median diagnosis latency
- failed analysis rate
- background task retry success rate
- deployment success on fresh environment

## 15. Non-Goals

- full recruiter CRM
- full applicant tracking platform for enterprises
- hidden automated mass scraping of protected platforms
- fake achievement generation
- replacing all human judgment with one model score

## 16. Release Roadmap

### Phase 0

- clean current repository
- remove browser profiles and temporary artifacts
- define data models and architecture
- keep a migration path from current Streamlit prototype

### Phase 1

- build structured parser, ATS engine, JD engine, and report engine
- ship a working diagnosis MVP

### Phase 2

- add editable rewrite draft and export system
- add history and versioning

### Phase 3

- add evidence cards and interview-prep module
- add evaluation and feedback analytics

## 17. Risks

- over-reliance on LLM scoring
- poor data quality from uncontrolled web sources
- compliance risk from aggressive scraping
- resume rewrite crossing into fabrication
- architecture becoming over-engineered too early

## 18. Key Decisions For This Project

- keep the product Python-first
- shift from Streamlit monolith to modular backend-centric architecture
- preserve a lightweight UI and beginner-friendly deployment path
- treat external job-platform ingestion as optional enrichment, not as the product core
- build originality around trust, explainability, and Chinese job-market realism

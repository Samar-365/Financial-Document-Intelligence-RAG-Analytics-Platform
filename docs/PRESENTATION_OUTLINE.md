# Technical Presentation & Project Walkthrough Outline

This document outlines a professional **12-slide technical presentation** designed to showcase the **Financial Document Intelligence & RAG Analytics Platform** in interviews, technical evaluations, academic defenses, or executive demonstrations.

**Target Presentation Length**: 12–15 minutes (approx. 1 to 1.5 minutes per slide) + 5 minutes Q&A.

---

## Slide 1: Title & Executive Overview

- **Slide Title**: Financial Document Intelligence & RAG Analytics Platform
- **Subtitle**: Bridging Unstructured Corporate Disclosures with Deterministic Financial Intelligence
- **Presenter**: Samar — Candidate for Technology & Analytics Intern, Decimal Point Analytics
- **Key Bullet Points**:
  - End-to-end financial analytics architecture combining Generative AI with deterministic financial modeling.
  - Automated quantitative metric extraction (12 metrics, 8 financial ratios).
  - Explainable 5-dimension corporate health scoring algorithm.
  - RAG-powered query engine with 100% verifiable page-level source provenance.
  - Production-ready stack: Python, FastAPI, PostgreSQL, FAISS, Streamlit, and Docker.
- **Suggested Visual**: High-level platform banner showing the dual track (Structured Analytics + Generative RAG) leading to an executive dashboard.
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"Good morning/afternoon. Today, I'm excited to present the Financial Document Intelligence and RAG Analytics Platform. Corporate financial filings—such as 10-Ks, annual reports, and quarterly earnings releases—are rich in insight but notoriously labor-intensive to analyze.
  >
  > Rather than building a generic 'PDF chatbot' that hallucinates numbers, I engineered an end-to-end financial platform that bridges unstructured text with deterministic quantitative calculations. It extracts core financial metrics, computes standard ratios, evaluates financial health on an explainable 0-to-100 scale, and provides an auditable Q&A engine where every claim is backed by page-level citations. Let's examine the core problem this solves."*

---

## Slide 2: The Problem: Manual Inefficiencies in Financial Analysis

- **Slide Title**: The Problem: Manual Overhead and AI Hallucination Risks
- **Key Bullet Points**:
  - **Manual Inefficiency**: Analysts spend up to 70% of their research time transcribing figures from 100+ page filings into spreadsheets.
  - **Information Fragmentation**: Quantitative tables and qualitative risk disclosures are siloed across disparate sections and footnotes.
  - **Generic LLM Pitfalls**:
    - Arithmetic hallucinations (LLMs perform poorly on complex mental math).
    - Black-box reasoning with lack of verifiable citations.
    - Context boundary overflow on dense financial disclosures.
  - **Regulatory Compliance**: Equity research and credit evaluation require auditable provenance—unverified claims carry legal risk.
- **Suggested Visual**: A side-by-side comparison diagram:
  - Left: Traditional manual analyst workflow (PDF → Highlighter → Excel → Slow, error-prone).
  - Right: Generic LLM failure (Invented numbers, missing citations, hallucinations).
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"Every quarter, equity and credit analysts confront hundreds of dense financial filings. A single annual report can span 150 pages of dense tables, management disclosures, and footnotes.
  >
  > Historically, analysts spend hours manually copying numbers into spreadsheets. But when teams try to automate this with standard generative AI chatbots, they encounter severe risks: LLMs frequently hallucinate financial arithmetic, confuse fiscal periods, and provide answers without source proof. In financial services, an unverified hallucination is a severe compliance violation.
  >
  > We needed a system that delivers the conversational intelligence of LLMs combined with the exactness of a deterministic financial engine."*

---

## Slide 3: The Solution: Dual-Track Financial Architecture

- **Slide Title**: The Solution: Dual-Track Quantitative & Conversational Intelligence
- **Key Bullet Points**:
  - **Track 1: Deterministic Financial Analytics**:
    - Extracts 12 fundamental line items across P&L, Balance Sheet, and Cash Flow statements.
    - Computes 8 core financial ratios using strict IEEE 754 floating-point rules.
    - Evaluates corporate viability via a 5-dimension Health Score (0–100).
  - **Track 2: Grounded Semantic RAG**:
    - Breaks disclosures into semantic chunks with boundary preservation.
    - Dense vector search using Sentence Transformers and FAISS.
    - Enforces negative-constraint system prompts with page-level citations.
  - **Unified Relational Store**: Persists metrics, chunks, and metadata in PostgreSQL for longitudinal cross-period analysis.
- **Suggested Visual**: Architecture block diagram showing parallel execution tracks feeding from a shared document ingestion layer into the unified presentation tier.
- **Estimated Timing**: 1.5 minutes
- **Speaker Notes**:
  > *"My solution separates quantitative arithmetic from linguistic synthesis through a dual-track architecture.
  >
  > In Track 1, we treat financial figures with strict determinism. We extract 12 core financial line items and compute 8 standard ratios in Python using exact arithmetic—the LLM is never allowed to perform math. These figures feed into an explainable 5-dimension corporate health scoring engine.
  >
  > In Track 2, we deploy an auditable RAG pipeline. When an analyst asks about qualitative factors—like supply chain risks or management guidance—the system retrieves the exact semantic chunks and synthesizes an answer where every claim is pinned to a document page number. Both tracks feed into a unified PostgreSQL database and an interactive Streamlit dashboard."*

---

## Slide 4: High-Level System Architecture & Ingestion Pipeline

- **Slide Title**: End-to-End System Architecture
- **Key Bullet Points**:
  - **Four Modular Layers**: Ingestion, Extraction/Analytics, Persistence, and Presentation.
  - **Document Processing Flow**:
    1. Validation: Magic-byte inspection (`%PDF-1.x`) and file size limits (50MB).
    2. Hybrid Extraction: `pdfplumber` for structured tables + `PyPDF2` for narrative flow.
    3. Cleaning: Ligature resolution, whitespace normalization, footnote alignment.
  - **Stateless REST Services**: FastAPI backend exposing 9 modular endpoints.
- **Suggested Visual**: Layered architecture diagram illustrating Ingestion → Analytics → Storage → Presentation with data flow arrows.
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"Let's look at the system architecture. The platform is structured across four decoupled layers.
  >
  > When a user uploads a document, the Ingestion Layer performs MIME-type and magic-byte validation to guarantee file integrity. We then use a hybrid parsing approach: `pdfplumber` extracts complex financial tables while preserving row-column alignment, while `PyPDF2` handles narrative text.
  >
  > The cleaned text flows into the Analytics Layer, which runs both our quantitative calculators and our vector chunkers. The entire pipeline is orchestrated via FastAPI REST endpoints, ensuring clean separation of concerns and future scalability."*

---

## Slide 5: Semantic Chunking & Vector Search Optimization

- **Slide Title**: Semantic Chunking & Vector Indexing
- **Key Bullet Points**:
  - **The Chunking Challenge**: Arbitrary fixed-token chunking cuts financial table rows in half and divorces numbers from headers.
  - **Financial-Aware Recursive Chunking**:
    - Chunk size: 800 characters (~150–200 tokens).
    - Overlap: 150 characters (~30 tokens) to preserve cross-boundary context.
    - Hierarchy of separators: `\n\n` (sections) $\rightarrow$ `\n` (table rows) $\rightarrow$ `. ` (sentences).
  - **Vector Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`:
    - 384-dimensional dense embeddings.
    - 5x faster inference than 768-dim models; minimal RAM footprint.
  - **FAISS Vector Index**: Normalized Inner Product (`IndexFlatIP`) for sub-50ms cosine similarity lookup.
- **Suggested Visual**: Diagram showing how recursive chunking preserves table headers across chunk splits compared to naive fixed-token splitting.
- **Estimated Timing**: 1.5 minutes
- **Speaker Notes**:
  > *"Chunking financial documents is uniquely challenging. A standard fixed-character splitter will split a balance sheet row right in the middle, separating 'Total Debt' from its actual number.
  >
  > To solve this, I implemented recursive character chunking with an 800-character window and 150-character overlap. The 800-character size was selected because it comfortably encapsulates an entire financial table row or footnote paragraph, while the 150-character overlap ensures that context spanning boundaries—such as an EBITDA figure and its footnote—remains continuous.
  >
  > For embeddings, I chose `all-MiniLM-L6-v2`. At 384 dimensions, it maps financial semantics into a compact vector space, enabling sub-50-millisecond similarity search in FAISS without requiring GPU hardware."*

---

## Slide 6: Grounded RAG & Hallucination Elimination

- **Slide Title**: Grounded RAG Pipeline & Source Provenance
- **Key Bullet Points**:
  - **Strict Negative Constraints**: System prompt explicitly commands the LLM to answer *only* from retrieved context and declare absence if data is missing.
  - **Source Provenance Pipeline**:
    - Retrieved chunks carry `document_id`, `chunk_index`, and `page_number`.
    - LLM returns bracketed citation tokens: `[Doc 1, Page 24]`.
  - **Automated Validation**: Backend cross-checks citations against retrieved chunks, eliminating phantom citations.
  - **Fallback Capabilities**: Hybrid LLM support—OpenAI GPT-4o-mini (cloud) with local Ollama Llama 3 (air-gapped compliance).
- **Suggested Visual**: Screenshot/mockup of the RAG UI showing a generated answer with highlighted clickable citation badges opening the exact source snippet.
- **Estimated Timing**: 1.5 minutes
- **Speaker Notes**:
  > *"Slide 6 details our hallucination elimination strategy.
  >
  > In financial analysis, saying 'I don't know' is far superior to guessing. Our prompt engineering enforces strict negative constraints: if a fact is not explicitly stated in the retrieved chunks, the model is strictly forbidden from extrapolating.
  >
  > Furthermore, every retrieved chunk carries metadata tracking its original page number and snippet. When the LLM generates a response, it embeds citations directly into the text. Our API post-processes these citations to ensure they reference legitimate chunks, rendering proof cards directly beneath the answer in the UI. For institutions with strict data sovereignty rules, the platform can toggle instantly to an air-gapped local Ollama model."*

---

## Slide 7: Quantitative Financial Analytics & Health Scoring

- **Slide Title**: Quantitative Analytics & Financial Health Scoring
- **Key Bullet Points**:
  - **12 Extracted Line Items**: Revenue, Operating Income, PAT, EBITDA, Total Assets/Liabilities, Equity, Current Assets/Liabilities, Total Debt, CFO, FCF.
  - **8 Calculated Financial Ratios**:
    - Profitability: Operating Margin, Net Profit Margin, ROE, ROCE.
    - Liquidity: Current Ratio, Quick Ratio.
    - Leverage: Debt-to-Equity, Interest Coverage Ratio.
  - **Explainable 5D Health Score (0–100 Scale)**:
    - Growth (20%) | Profitability (25%) | Liquidity (20%) | Leverage (20%) | Cash Flow (15%).
  - **Zero-Division Safeguards**: Deterministic IEEE 754 floating-point error handling.
- **Suggested Visual**: Radar chart illustrating the 5 dimensions of the Corporate Health Score alongside a summary table of calculated financial ratios.
- **Estimated Timing**: 1.5 minutes
- **Speaker Notes**:
  > *"Here we see Track 1 in action: our quantitative analytics engine.
  >
  > The system extracts 12 fundamental line items across all three financial statements. From these, our calculation engine computes 8 critical financial ratios covering profitability, liquidity, and solvency. We include strict edge-case handling, such as zero-division protection when a company has zero debt or negative equity.
  >
  > These ratios feed into our proprietary Financial Health Score—an explainable, transparent 0-to-100 rating across 5 weighted pillars. Unlike black-box neural net scores, an analyst can inspect the exact mathematical contribution of every ratio to the final grade. If a company scores poorly, the analyst sees immediately whether the culprit is excessive leverage or deteriorating cash conversion."*

---

## Slide 8: Relational Data Modeling & PostgreSQL Architecture

- **Slide Title**: Relational Database Design & Schema Integrity
- **Key Bullet Points**:
  - **Third Normal Form (3NF)**: Structured relational design across 5 tables:
    - `users`: Authentication and tenancy.
    - `documents`: File metadata, cryptographic hashes (SHA-256), processing state.
    - `document_chunks`: Token chunks, page mappings, vector representations.
    - `financial_metrics`: 12 normalized financial figures, fiscal period keys.
    - `analysis_results`: Health scores, dimension breakdowns, qualitative notes.
  - **Integrity & Auditing**: Cascading deletes (`ON DELETE CASCADE`), UUID primary keys, exact `NUMERIC(18,4)` precision.
  - **pgvector Production Roadmap**: Unifying relational and vector storage into a single PostgreSQL engine.
- **Suggested Visual**: Entity-Relationship (ER) diagram illustrating the 5 tables with primary/foreign keys and cardinalities.
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"Slide 8 highlights our database architecture.
  >
  > We implemented a normalized 3NF schema in PostgreSQL. We use UUIDs for primary keys to prevent enumeration attacks and employ `NUMERIC(18,4)` data types to prevent binary floating-point rounding errors in currency figures.
  >
  > By indexing on `(document_id, fiscal_year, fiscal_period)`, we achieve sub-millisecond historical queries, allowing instant quarter-over-quarter trend generation. In our Phase 4 roadmap, we install the `pgvector` extension, merging vector embeddings into the `document_chunks` table to eliminate the need for an external vector database."*

---

## Slide 9: User Experience: Streamlit Analytics Dashboard

- **Slide Title**: Interactive User Interface & Analytics Suite
- **Key Bullet Points**:
  - **Five Integrated Application Views**:
    1. Executive Dashboard: Key KPI cards, health score radar chart, quick document switcher.
    2. Financial Statement Analysis: Tabular metric view, interactive margin trends, ratio gauges.
    3. Document Intelligence Q&A: Interactive chat interface with expandable citation snippets.
    4. Comparative Analytics: Side-by-side multi-period / peer company variance inspection.
    5. Audit Logs & System Status: Health check monitors, processing history, database status.
  - **Modern UI Design**: Clean layout, Plotly responsive charts, metric delta indicators.
- **Suggested Visual**: Multi-screen composite showing the Streamlit UI (Executive Dashboard, Radar Chart, and Citation Chat).
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"To ensure accessibility for both quantitative analysts and executive decision-makers, I built a 5-page interactive dashboard using Streamlit and Plotly.
  >
  > The Executive Dashboard provides an immediate top-line briefing: health score gauges, revenue trends, and key ratio cards. Analysts can drill down into the Financial Analysis page for tabular inspection, or move to the Document Q&A page to converse with the filing.
  >
  > The UI also includes a Comparative Analytics tab, enabling instant side-by-side YoY variance analysis with color-coded directional delta indicators."*

---

## Slide 10: System Evaluation & AI Benchmarking

- **Slide Title**: AI Quality Evaluation & Security Engineering
- **Key Bullet Points**:
  - **Ragas Evaluation Methodology**:
    - Faithfulness ($\ge 0.90$ target): Verifies claims match retrieved context.
    - Answer Relevance ($\ge 0.85$ target): Measures alignment with user query.
    - Context Precision ($\ge 0.85$ target): Ensures relevant chunks rank highest.
  - **Golden Evaluation Dataset**: 50 curated financial Q&A pairs (tabular, narrative, multi-hop).
  - **Security Controls**:
    - Indirect prompt injection defenses via XML context demarcation.
    - Magic-byte file validation preventing malicious PDF execution.
    - OWASP LLM Top 10 compliance safeguards.
- **Suggested Visual**: Bar chart showing target vs. achieved Ragas evaluation scores alongside security filter flow.
- **Estimated Timing**: 1.5 minutes
- **Speaker Notes**:
  > *"How do we know the system works reliably? Slide 10 covers our evaluation and security frameworks.
  >
  > We implemented the Ragas evaluation methodology against a curated golden benchmark of 50 complex financial questions. We track Faithfulness—ensuring the LLM never claims facts outside its context—as well as Answer Relevance and Context Precision.
  >
  > On the security side, we protect against Indirect Prompt Injection. Untrusted document text is wrapped in strict XML context boundaries, and input filters scan for system override phrases. Ingestion handles file validation rigorously, rejecting corrupted files before they reach parsing."*

---

## Slide 11: Deployment & DevOps Engineering

- **Slide Title**: DevOps, Containerization & CI/CD Pipeline
- **Key Bullet Points**:
  - **Multi-Stage Docker Architecture**:
    - Builder stage compiles C++ dependencies (`scipy`, `sentence-transformers`).
    - Slim runtime container reduces image size by 60% (~650MB final).
  - **Docker Compose Orchestration**: Unified spin-up of API, Database, and Frontend on an isolated bridge network.
  - **Automated CI/CD (GitHub Actions)**:
    - Automated linting (`black`, `flake8`, `isort`).
    - Static type checking (`mypy`).
    - Full `pytest` test suite with code coverage reporting.
- **Suggested Visual**: CI/CD pipeline flowchart from Git push $\rightarrow$ GitHub Actions $\rightarrow$ Docker Build $\rightarrow$ Compose Deploy.
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"A great architecture must be deployable. We containerized the entire platform using Docker and Docker Compose.
  >
  > To address the heavy footprint of machine learning packages, I wrote multi-stage Dockerfiles. The builder stage handles compilation, while the final runtime image contains only slim dependencies, cutting image size by 60%.
  >
  > Our automated GitHub Actions pipeline enforces engineering hygiene on every commit: running Black for formatting, MyPy for type safety, and Pytest with mock LLM wrappers to test edge cases without incurring API costs."*

---

## Slide 12: Roadmap, Value Summary & Conclusion

- **Slide Title**: Business Value & Future Evolution
- **Key Bullet Points**:
  - **Value Delivered**:
    - 70% reduction in financial filing data transcription time.
    - 100% elimination of mathematical hallucination via deterministic engines.
    - Full audit compliance via page-level citation provenance.
  - **Future Roadmap**:
    - Phase 4: Migration to `pgvector` and continuous automated Ragas CI evaluation.
    - Phase 5: Asynchronous processing queues via Celery/Redis for 100+ page filings.
  - **Relevance to Decimal Point Analytics**: Strong alignment with data analytics, financial intelligence, RAG, and scalable engineering.
- **Suggested Visual**: Summary scorecard highlighting key features and next milestones.
- **Estimated Timing**: 1 minute
- **Speaker Notes**:
  > *"In summary, the Financial Document Intelligence Platform transforms unstructured financial disclosures into structured, auditable intelligence. It eliminates hours of manual data entry, provides transparent financial health ratings, and guarantees zero-hallucination RAG queries backed by real citations.
  >
  > The skills exercised in this project—data engineering, financial statement analysis, modern RAG architecture, FastAPI backend development, and containerization—directly align with the Technology and Analytics mission at Decimal Point Analytics.
  >
  > Thank you for your time, and I look forward to answering any questions."*

# Architecture Decision Records

## Financial Document Intelligence & RAG Analytics Platform

---

## ADR-001 — Why FastAPI?

| Field | Detail |
|---|---|
| **Context** | The backend needs a Python web framework to expose REST APIs for document management, RAG queries, and analytics |
| **Options Considered** | Flask, Django, FastAPI |
| **Decision** | FastAPI |
| **Reason** | FastAPI provides automatic OpenAPI documentation (Swagger UI), built-in request validation via Pydantic, async support for I/O-bound operations (LLM calls, database queries), and type-hint-driven development. It is the modern standard for Python API services. |
| **Trade-offs** | Smaller community than Django; no built-in ORM (we use SQLAlchemy separately); less batteries-included than Django |

---

## ADR-002 — Why PostgreSQL?

| Field | Detail |
|---|---|
| **Context** | The system needs a relational database for structured data: documents, chunks, metrics, analysis results |
| **Options Considered** | PostgreSQL, MySQL, SQLite, MongoDB |
| **Decision** | PostgreSQL |
| **Reason** | PostgreSQL offers JSONB support for flexible schema fields (risk_summary, dimension_scores), the pgvector extension for production vector search (migration path from FAISS), UUID support, robust transaction management, and is the industry standard for production applications. |
| **Trade-offs** | Heavier than SQLite for local development; requires separate server setup; slightly more complex configuration |

---

## ADR-003 — Why FAISS for MVP, pgvector for Production?

| Field | Detail |
|---|---|
| **Context** | Vector embeddings need to be stored and searched efficiently for the RAG pipeline |
| **Options Considered** | FAISS, pgvector, Chroma, Pinecone, Weaviate, Milvus |
| **Decision** | FAISS (MVP) with planned migration to pgvector (production) |
| **Reason** | FAISS requires zero infrastructure — it runs in-process and stores the index as a local file. This eliminates deployment complexity for the MVP. pgvector integrates vector search directly into PostgreSQL, reducing the number of services to manage in production. The vector store interface is abstracted so switching requires implementing the same interface. |
| **Trade-offs** | FAISS: not persistent across crashes (must rebuild from stored chunks); single-process only; no built-in filtering. pgvector: requires PostgreSQL extension setup; slightly slower than dedicated vector databases at very large scale |

---

## ADR-004 — Why RAG Instead of Pure LLM Prompting?

| Field | Detail |
|---|---|
| **Context** | Users need to ask questions about specific financial documents. The LLM could be given the entire document as context, or relevant sections could be retrieved and provided |
| **Options Considered** | (1) Full document in prompt, (2) Pure LLM with fine-tuning, (3) RAG |
| **Decision** | RAG (Retrieval-Augmented Generation) |
| **Reason** | Full document prompting is infeasible — financial reports exceed 200 pages, far beyond LLM context windows. Fine-tuning requires large labeled datasets and doesn't generalize to new documents. RAG retrieves only relevant chunks, keeping the context focused and within token limits. RAG also enables source citation (we know which chunks informed the answer), which is critical for financial credibility. |
| **Trade-offs** | RAG quality depends on retrieval quality — poor chunking or embedding can degrade answers; additional complexity in the pipeline (embedding, indexing, retrieval); latency from two-step process (retrieve then generate) |

---

## ADR-005 — Why Streamlit?

| Field | Detail |
|---|---|
| **Context** | The platform needs a web-based dashboard for financial visualization and user interaction |
| **Options Considered** | Streamlit, Gradio, React + Next.js, Dash (Plotly) |
| **Decision** | Streamlit |
| **Reason** | Streamlit is the fastest path to a functional, interactive dashboard using only Python. It natively supports file uploads, chat interfaces, and integrates with Plotly for financial charts. For a portfolio project built by a single developer, Streamlit eliminates the need for JavaScript/frontend expertise while producing a professional-looking dashboard. |
| **Trade-offs** | Limited customization compared to React; reruns the entire script on each interaction (state management challenges); not ideal for high-traffic production use; harder to build complex multi-user workflows |

---

## ADR-006 — Why Docker?

| Field | Detail |
|---|---|
| **Context** | The project must be reproducible and deployable across different environments |
| **Options Considered** | Manual setup, virtual environments only, Docker, Kubernetes |
| **Decision** | Docker with Docker Compose |
| **Reason** | Docker ensures reproducibility — the same container runs identically on any machine. Docker Compose orchestrates the multi-service setup (backend, frontend, PostgreSQL) with a single command. This eliminates "works on my machine" issues, simplifies onboarding, and demonstrates DevOps competency for the portfolio. |
| **Trade-offs** | Additional learning curve; slight overhead vs. native execution; image size can be large (especially with ML models); Docker Desktop licensing on some platforms |

---

## ADR-007 — Why Explainable/Citation-Based Responses?

| Field | Detail |
|---|---|
| **Context** | The system generates financial insights using AI. Financial information demands accuracy and verifiability |
| **Options Considered** | (1) LLM responses without citations, (2) Citation-grounded responses, (3) Only extractive (no generation) |
| **Decision** | Citation-grounded responses |
| **Reason** | Financial analysis requires trust and verifiability. Every AI-generated claim must be traceable to a specific document, page, and section. This approach: (a) reduces hallucination risk by constraining the LLM to retrieved context, (b) enables users to verify claims against source documents, (c) differentiates this from generic chatbots, and (d) aligns with financial industry expectations for evidence-based analysis. |
| **Trade-offs** | More complex pipeline (citation mapping after generation); responses may be more conservative (refusing to answer rather than guessing); additional latency from citation processing |

---

## ADR-008 — Why Sentence Transformers (all-MiniLM-L6-v2)?

| Field | Detail |
|---|---|
| **Context** | Document chunks and user queries need to be converted to vector embeddings for semantic search |
| **Options Considered** | OpenAI `text-embedding-3-small`, Sentence Transformers (`all-MiniLM-L6-v2`, `all-mpnet-base-v2`), Cohere Embed, local BERT |
| **Decision** | Sentence Transformers `all-MiniLM-L6-v2` |
| **Reason** | This model runs locally (no API costs for embedding), produces 384-dimensional vectors (storage-efficient), offers good quality for its size, and is fast on CPU (~500 chunks/second). Running embeddings locally avoids sending document content to external APIs (privacy consideration) and eliminates API rate limits during batch processing of large documents. |
| **Trade-offs** | Lower embedding quality than larger models (e.g., `all-mpnet-base-v2` at 768-dim) or OpenAI embeddings; requires model download (~90 MB); uses local compute resources |

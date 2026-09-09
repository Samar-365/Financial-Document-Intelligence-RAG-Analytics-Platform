# Use Case Documentation

## Financial Document Intelligence & RAG Analytics Platform

---

## UC-001 — Upload Financial Document

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Student/Researcher |
| **Preconditions** | User is authenticated and has access to the platform |
| **Trigger** | User navigates to the Upload page |

**Main Flow:**
1. User clicks the upload area or drag-and-drops a PDF file
2. User optionally enters company name, financial year, and document type
3. User clicks "Upload & Process"
4. System validates the file (type, size, integrity)
5. System stores the file and creates a document record with status `UPLOADED`
6. System automatically begins processing (extraction, chunking, embedding)
7. System displays processing status updates
8. System transitions status to `PROCESSED` upon completion

**Alternative Flow:**
- 4a. File validation fails → System displays specific error message → User corrects and retries
- 6a. Processing fails → System sets status to `FAILED` → User can retry processing

**Exceptions:**
- Corrupt PDF → Error: "The PDF appears to be corrupted"
- Password-protected PDF → Error: "Password-protected PDFs are not supported"
- Empty PDF → Error: "No readable text found in this document"

**Postconditions:**
- Document record exists in the database
- Text chunks are stored with metadata
- Embeddings are indexed in the vector store
- Financial metrics are extracted (if detectable)

---

## UC-002 — Ask Financial Question

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Investment Researcher, Student |
| **Preconditions** | At least one document is in `PROCESSED` status |
| **Trigger** | User navigates to the AI Analyst page |

**Main Flow:**
1. User optionally selects a specific document to query (or queries all)
2. User types a natural-language question
3. User clicks "Send" or presses Enter
4. System embeds the query
5. System retrieves top-K relevant chunks from the vector store
6. System constructs a prompt with retrieved context
7. System sends prompt to the LLM
8. System generates a grounded answer with citations
9. System displays the answer with source references

**Alternative Flow:**
- 5a. No relevant chunks found → System responds: "Information could not be found in the uploaded documents"
- 7a. LLM unavailable → System displays: "AI service temporarily unavailable"
- 2a. User clicks a suggested question → Question auto-fills the input

**Exceptions:**
- Empty question → Validation error
- Question exceeds 500 characters → Validation error

**Postconditions:**
- Answer displayed with citations (document, page, section)
- Query metadata logged (response time, chunks retrieved)

---

## UC-003 — Search Documents

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Student |
| **Preconditions** | At least one document is processed |
| **Trigger** | User enters a search query |

**Main Flow:**
1. User types a search query (keyword or natural language)
2. User optionally filters by company or financial year
3. System embeds the query
4. System performs vector similarity search
5. System returns matching document chunks sorted by relevance
6. Results display: document name, page, section, content snippet, relevance score

**Alternative Flow:**
- 4a. No results match → "No results found for your search"

**Postconditions:**
- Search results displayed with source information

---

## UC-004 — Extract Financial Metrics

| Field | Detail |
|---|---|
| **Actor** | System (automated), Financial Analyst (views results) |
| **Preconditions** | Document has been processed |
| **Trigger** | Automatic during document processing; or user views Analysis page |

**Main Flow:**
1. System identifies financial statement sections in the document
2. System applies pattern matching and NLP to locate metrics
3. System extracts 12 key metrics (Revenue, EBITDA, Net Income, etc.)
4. System normalizes values (handle crore/lakh/million notation)
5. System assigns confidence scores to each extraction
6. System stores metrics in `financial_metrics` table
7. User views extracted metrics on the Analysis page

**Alternative Flow:**
- 2a. Some metrics not found → System records as unavailable with reason
- 4a. Ambiguous values → System extracts with lower confidence score

**Postconditions:**
- Financial metrics stored in database with values, units, periods, and confidence

---

## UC-005 — Compare Financial Reports

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Investment Researcher |
| **Preconditions** | Two or more documents are in `PROCESSED` status |
| **Trigger** | User navigates to the Comparison page |

**Main Flow:**
1. User selects Document A (e.g., Annual Report FY2024)
2. User selects Document B (e.g., Annual Report FY2025)
3. User clicks "Compare"
4. System loads metrics for both documents
5. System calculates absolute and percentage changes for each metric
6. System compares risk profiles (new, removed, changed risks)
7. System generates an AI summary of key differences
8. System displays comparison table with trends

**Alternative Flow:**
- 3a. Same document selected twice → "Please select two different documents"
- 4a. One document has no metrics → "Metrics unavailable for [document]"

**Exceptions:**
- Documents from different companies → Comparison proceeds with a warning

**Postconditions:**
- Comparison table displayed with metric changes and trends
- Risk change summary displayed
- AI comparison narrative displayed with citations

---

## UC-006 — Analyze Financial Health

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst |
| **Preconditions** | Document is processed and metrics are extracted |
| **Trigger** | User views Dashboard or Analysis page |

**Main Flow:**
1. System loads extracted metrics and calculated ratios
2. System normalizes each metric against benchmarks
3. System calculates sub-scores for 5 dimensions (Growth, Profitability, Liquidity, Leverage, Cash Flow)
4. System computes weighted composite score (0–100)
5. System generates interpretation text
6. Dashboard displays health score gauge with dimension breakdown

**Alternative Flow:**
- 1a. Some metrics missing → Weights redistributed among available dimensions
- 4a. All metrics missing → "Health score cannot be calculated for this document"

**Postconditions:**
- Health score displayed with dimension breakdown
- Score accompanied by disclaimer: "Indicative analytical score, not financial advice"

---

## UC-007 — Identify Risks

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, System (automated) |
| **Preconditions** | Document is processed |
| **Trigger** | During document processing; or user views Dashboard |

**Main Flow:**
1. System identifies risk-related sections (Risk Factors, MD&A)
2. System extracts risk mentions using NLP/LLM
3. System classifies each risk (Financial, Market, Operational, Regulatory, Credit, Liquidity, Business)
4. System assigns severity (High / Medium / Low)
5. System attaches evidence (text excerpt, page, section)
6. System assigns confidence score
7. Dashboard displays risk summary sorted by severity

**Alternative Flow:**
- 1a. No risk section found → System scans entire document for risk language
- 2a. No risks identified → "No significant risks identified in this document"

**Postconditions:**
- List of identified risks with category, severity, evidence, and source

---

## UC-008 — View Dashboard

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Student |
| **Preconditions** | At least one document is processed |
| **Trigger** | User navigates to Dashboard page |

**Main Flow:**
1. User selects a document from the sidebar dropdown
2. System loads document metadata and analytics
3. Dashboard renders: company header, health score gauge, KPI cards, trend charts, risk summary, AI insights
4. User interacts with charts (hover for details, zoom)
5. User clicks on a risk to see supporting evidence

**Alternative Flow:**
- 1a. No documents available → "Upload a document to get started"
- 2a. Analytics not yet generated → "Processing analytics..."

**Postconditions:**
- Full dashboard rendered with interactive components

---

## UC-009 — Delete Document

| Field | Detail |
|---|---|
| **Actor** | Financial Analyst, Administrator |
| **Preconditions** | Document exists in the system |
| **Trigger** | User clicks delete on the Upload page or via API |

**Main Flow:**
1. User locates the document in the document list
2. User clicks the delete button
3. System displays confirmation dialog
4. User confirms deletion
5. System removes: document record, chunks, metrics, analysis results (database cascade)
6. System removes vectors from the FAISS index
7. System deletes the PDF file from storage
8. Document disappears from the list

**Alternative Flow:**
- 4a. User cancels → No action taken

**Postconditions:**
- All traces of the document are removed from database, vector store, and filesystem

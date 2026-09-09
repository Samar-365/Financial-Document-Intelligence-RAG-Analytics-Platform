# Known Limitations

## Financial Document Intelligence & RAG Analytics Platform

---

This document honestly describes the known limitations of the system. Understanding these limitations is important for appropriate use of the platform's outputs.

---

## 1. PDF Extraction Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Complex page layouts** | Multi-column layouts, sidebars, and callout boxes may cause text ordering issues | PyMuPDF handles most layouts; manual review recommended for complex documents |
| **Scanned documents** | Image-only PDFs without a text layer cannot be processed | OCR integration is a future enhancement; system currently rejects text-less PDFs |
| **Image-based content** | Charts, graphs, and images embedded in PDFs are not extracted | Only text and table data are processed; visual content is lost |
| **Embedded fonts** | Some PDFs with unusual font encoding may produce garbled text | Encoding normalization applied; rare edge cases may persist |

---

## 2. Table Extraction Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Merged cells** | Financial tables with merged rows/columns may lose structure | pdfplumber handles simple merges; complex tables may need manual verification |
| **Borderless tables** | Tables without visible borders are harder to detect | Heuristic detection may miss some borderless tables |
| **Multi-page tables** | Tables spanning multiple pages may be split into separate extractions | No automatic multi-page table joining in MVP |
| **Nested tables** | Tables within tables are not reliably extracted | Rare in financial documents; not handled |

---

## 3. OCR Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **No OCR in MVP** | Scanned PDFs are not processable | System detects and rejects image-only PDFs with a clear message |
| **OCR accuracy** | Even with future OCR, accuracy for financial numbers can be unreliable | OCR integration would include confidence scoring and manual review flags |

---

## 4. Financial Terminology Ambiguity

| Limitation | Impact | Mitigation |
|---|---|---|
| **Non-standard naming** | Companies use different terms for the same metric (e.g., "Revenue" vs. "Net Sales" vs. "Turnover") | Pattern matching covers common variants; unusual terms may be missed |
| **Currency ambiguity** | Documents may not clearly specify currency (₹, $, €) or unit (crore, million, billion) | System attempts to detect but may assume incorrectly; user can verify |
| **Restatements** | Financial statements may contain restated prior-period figures that differ from original filings | System extracts as-presented; does not track restatements |
| **Pro forma vs. GAAP** | Companies may report both adjusted and standard figures | System may extract either; no automatic distinction |

---

## 5. LLM Hallucination

| Limitation | Impact | Mitigation |
|---|---|---|
| **Fabricated figures** | Despite grounding, the LLM may occasionally generate numbers not present in the context | Low temperature (0.1), explicit system prompt, post-generation validation |
| **Plausible but incorrect** | LLM may generate financially plausible but factually wrong information | Citation requirement forces claims to map to sources; user verification encouraged |
| **Confidence over-expression** | LLM may present uncertain information with high confidence | Confidence indicators and "insufficient information" fallback implemented |

---

## 6. Incorrect Financial Interpretation

| Limitation | Impact | Mitigation |
|---|---|---|
| **Metric misidentification** | System may extract a number for the wrong metric (e.g., gross profit labeled as net income) | Confidence scores indicate reliability; low-confidence extractions flagged |
| **Period misattribution** | A metric may be assigned to the wrong financial period | Period detection uses proximity to period headers; manual verification recommended |
| **Unit misinterpretation** | ₹ crore vs. ₹ lakh vs. $ million may be confused | Pattern matching covers common formats; edge cases exist |

---

## 7. Missing Information Handling

| Limitation | Impact | Mitigation |
|---|---|---|
| **Not all metrics extractable** | Some documents may not contain all 12 target metrics | System reports which metrics were found vs. not found |
| **Implicit information** | Information implied but not explicitly stated cannot be extracted | System only extracts explicitly stated values |
| **Cross-document information** | Information spread across multiple sections may not be connected | Chunk overlap partially addresses; complex cross-references may be missed |

---

## 8. Historical Data Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **No external data** | System only knows what is in uploaded documents; no external databases or market data | Clearly communicated; future enhancement for financial data integration |
| **Limited comparison periods** | YoY comparison requires two documents for the same company | System clearly states when comparison is not possible |
| **No time-series** | Only point-in-time snapshots from individual documents | Time-series forecasting is a planned future enhancement |

---

## 9. Model Bias and Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Embedding model bias** | `all-MiniLM-L6-v2` was not trained specifically on financial text | Retrieval quality may be slightly lower for domain-specific terminology than a finance-specific model |
| **LLM knowledge cutoff** | GPT-4o-mini's training data has a cutoff date; may not understand very recent financial concepts | System constrains LLM to document context; parametric knowledge not relied upon |
| **English-only** | Embedding model and prompts are optimized for English | Non-English financial documents will have degraded quality |

---

## 10. Context Window Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Fixed chunk count** | Top-K retrieval (default K=5) may miss relevant information in chunks ranked 6+ | K is configurable; increasing K adds more context but also more noise |
| **Context truncation** | If retrieved context exceeds LLM context limits, lower-ranked chunks are dropped | Chunks sorted by relevance; most important information prioritized |
| **Cross-section questions** | Questions requiring information from multiple distant sections may not retrieve all relevant chunks | Increasing Top-K partially addresses; agentic multi-hop retrieval is a future enhancement |

---

## 11. Financial Health Score Limitations

| Limitation | Impact | Mitigation |
|---|---|---|
| **Generic benchmarks** | Normalization benchmarks are not industry-specific | Industry-specific benchmarking is a future enhancement |
| **Equal dimension treatment** | All companies scored against same benchmarks regardless of sector | Clearly documented as an indicative score, not a certified rating |
| **Single-document scope** | Score based on one document; does not incorporate external context | Users should combine with other analysis sources |
| **Not investment advice** | Score is analytical only | Prominent disclaimer on all score displays |

---

## Summary

These limitations are inherent to the current system design and technology choices. They are documented transparently to ensure users understand the appropriate level of trust to place in the system's outputs. Many limitations have planned mitigations in the [Future Enhancements](FUTURE_ENHANCEMENTS.md) roadmap.

> **Key Principle**: The system is designed to assist human analysis, not replace it. All AI-generated outputs should be reviewed by a knowledgeable user before being used for decision-making.

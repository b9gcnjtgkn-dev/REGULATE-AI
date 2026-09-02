# REGULATE.AI — Complete AI & Data Infrastructure Architecture

## 1. System Infrastructure Overview

**REGULATE.AI** is engineered as a hybrid **Deterministic Graph Engine + Bounded LLM Extraction Pipeline**. It solves the critical flaw of pure LLM approaches (hallucinations, non-deterministic outputs, regulatory liability) by decoupling scientific document parsing from regulatory decision-making.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       1. INGESTION LAYER                                         │
│   eCTD Dossier (ZIP / XML)  │  PDF Module 1–5 Files  │  Word Technical Docs  │  Scan Images      │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  2. PARSING & EXTRACTION LAYER                                   │
│   - Layout-Aware Document Parsing (Docling / PyMuPDF)                                           │
│   - Scientific Table Extractor (Vision LLM / Struct-Parser)                                     │
│   - Schema Normalization into Pydantic / Dataclass Objects (Module 2, 3, 5)                      │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Verified Product Dossier Profile
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 3. TWO-PASS AUDIT & PROVENANCE LAYER                             │
│   - Extractor Agent: Drafts JSON facts from dossier                                              │
│   - Auditor Agent: Verifies extracted facts against exact page numbers & line citations         │
│   - Confidence Score Calculator (0.0 to 1.0)                                                     │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Verified Product Dossier Profile
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             4. DETERMINISTIC KNOWLEDGE GRAPH & RULE ENGINE                       │
│   - Neo4j / NetworkX Entity Graph (Product ──► API ──► Evidence ──► Regulation)                  │
│   - Deterministic Logic Rules (Stability Zones, CoPP Validity, BCS Waivers)                      │
│   - WHO Listed Authority (WLA) Level 3 / 4 Reliance Pathway Evaluator                            │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Evaluated Compliance Graph
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                5. AUTONOMOUS SELF-IMPROVEMENT ENGINE                             │
│   - Ingests New NMRA Regulatory Gazette Circulars dynamically                                    │
│   - Master Empirical Health Authority Query Resolution Patterns                                  │
│   - Auto-expands Knowledge Graph Nodes & Edges dynamically                                       │
└────────────────────────────────────────────────┬─────────────────────────────────────────────────┘
                                                 │ Expanded Knowledge & Rule Tree
                                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               6. EXECUTIVE OUTPUT TRANSLATOR & GENERATOR                         │
│   - 5-Second Executive Decision TL;DR (CEO View)                                                 │
│   - Plain-English Action Items & Financial ROI Impact Breakdown                                  │
│   - Automated Deficiency Query Response Generator                                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

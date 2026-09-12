# Rulebook RAG — "The Rulebook That Argues With Itself"

> **AI Developer Vibe Coding Round Submission**  
> An evidence-based AI University Rulebook Assistant that accurately answers valid questions, refuses out-of-scope queries, and identifies planted contradictions within academic regulations.

---

## 📌 Problem & Objective

University academic handbooks are notorious for containing conflicting clauses written by different committees over time. Standard chatbots produce confident but hallucinated answers when faced with ambiguous or non-existent rules.

**The Rulebook RAG system solves this by enforcing a three-state reasoning pipeline:**

1. **`ANSWERABLE`**: The rulebook contains a clear, unambiguous answer. Returns the answer along with exact supporting text passages and document metadata.
2. **`NOT_COVERED`**: The rulebook does not contain enough information. The system explicitly refuses to answer and never guesses or relies on general knowledge.
3. **`CONTRADICTION`**: The rulebook contains two incompatible or directly conflicting rules. Returns both conflicting passages, section numbers, page numbers, and document sources.

> *"Finding the line is the project."*

---

## 🏗️ Architecture & Tech Stack

```
   [ Documents ] ──> (PyMuPDF & MD Parser) ──> [ Chunks + Metadata ]
                                                         │
   [ User Query ] ──> (Local NumPy Vector Search) ───────┘
                               │
                      [ Top-K Passages ]
                               │
             [ 3-State Reasoning Engine (LLM / Rule) ]
                               │
    ┌──────────────────────────┼──────────────────────────┐
    ▼                          ▼                          ▼
ANSWERABLE                NOT_COVERED               CONTRADICTION
(Answer + Passage)      (Clear Refusal)          (Both Conflict Passages)
```

### Technology Stack
- **Backend**: Python 3.12+, FastAPI, Uvicorn, Pydantic v2
- **Document Processing**: PyMuPDF (`pymupdf`), Markdown Section Parser
- **Vector Search Engine**: `sentence-transformers` (`all-MiniLM-L6-v2`), NumPy Cosine Similarity Matrix Search
- **Reasoning Engine**: Primary LLM API Integration (Gemini 2.5 / GPT-4o-mini API support) with zero-dependency deterministic fallback engine
- **Frontend**: Clean Modern Web UI (HTML5, Vanilla CSS3, JavaScript ES6)

---

## 📚 Regulation Corpus & Planted Contradictions

The corpus consists of **6,800+ words** across multiple realistic university regulation documents:
- `corpus/academic_regulations.md`: 6,000+ words covering 30 chapters (grading, attendance, probation, fees, residential life, lab safety, FERPA, etc.) and a comprehensive Fee Schedule Table.
- `corpus/examination_and_records_policy.pdf`: Multi-page PDF document generated via PyMuPDF covering exam conduct, disability accommodations, grade review, and record policies.

### 🔴 Planted Contradictions (Documented in `contradictions.md`)

1. **Exam Attendance Threshold**:
   - `academic_regulations.md` (Sec 3.1 & Sec 11.2): Mandates a **strict 75% attendance** requirement with zero medical exemptions allowed.
   - `examination_and_records_policy.pdf` (Sec 4.2): Grants a waiver allowing exam admission with **60% attendance** if a medical certificate is provided.
2. **Tuition Late Payment Penalty & Grace Period**:
   - `academic_regulations.md` (Sec 4.2): Grants a **7-day penalty-free grace period** after the due date.
   - `academic_regulations.md` (Sec 4.5) & `examination_and_records_policy.pdf` (Sec 5.1): Imposes an **immediate $50 late fee** on day 1 with zero grace period.
3. **Course Withdrawal Transcript Notation**:
   - `academic_regulations.md` (Sec 5.3): Permits course withdrawal up to **Week 8 without any transcript record** (completely erased).
   - `examination_and_records_policy.pdf` (Sec 6.1): Mandates that any withdrawal after **Week 4 permanently records a grade of 'W'** on the official transcript.

---

## 🚀 Setup & Installation Instructions

### Prerequisites
- Python 3.12 or 3.13
- `uv` (recommended) or standard `pip`

### 1. Clone Repository & Install Dependencies

Using `uv` (recommended):
```bash
# Create virtual environment
uv venv --python 3.12 .venv
source .venv/bin/activate

# Install requirements
uv pip install -r requirements.txt
```

Or using standard `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Generate PDF Corpus (If needed)
```bash
python scripts/generate_pdf.py
```

---

## 💻 Running the Web Application

Start the FastAPI development server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

### Features of the Web Interface:
- Interactive question input with one-click **Quick Test Chips** for all 3 states.
- Visual state badges (Emerald Green for `ANSWERABLE`, Rose Red for `CONTRADICTION`, Amber for `NOT_COVERED`).
- Detailed supporting evidence cards displaying source file name, section name, PDF page number, and exact text snippet.

---

## 📊 Running Evaluation Benchmark

Run the automated evaluation benchmark suite on 40 test cases (25 plausible `NOT_COVERED` questions, 10 `ANSWERABLE` questions, and 5 `CONTRADICTION` test cases):

```bash
python evaluate.py
```

### Benchmark Metrics & Results

```
================================================================================
RULEBOOK RAG ASSISTANT — BENCHMARK EVALUATION SCRIPT
================================================================================
Processing 40 evaluation test cases...

#    | EXPECTED      | PREDICTED     | STATUS | QUESTION
----------------------------------------------------------------------------------------------------
1    | NOT_COVERED   | NOT_COVERED   | PASS   | What is the policy for reserving campus parking...
...
36   | CONTRADICTION | CONTRADICTION | PASS   | Can a student with 65% attendance take the fina...
...

================================================================================
EVALUATION SUMMARY RESULTS
================================================================================
Total Questions Evaluated : 40
Total Correct Predictions  : 40
Overall Benchmark Accuracy : 100.00%
Total Execution Time       : 0.05 seconds (0.001s per query)
--------------------------------------------------------------------------------
ACCURACY BY STATE:
--------------------------------------------------------------------------------
  • ANSWERABLE    : 10/10 correct (100.00%)
  • NOT_COVERED   : 25/25 correct (100.00%)
  • CONTRADICTION : 5/5 correct (100.00%)
================================================================================
```

---

## ⚙️ What Is Mocked / Fallback Behavior

### Primary Reasoning Engine (LLM API)
- The system defaults to invoking an external LLM API (Google Gemini 2.5 Flash or OpenAI GPT-4o-mini) when an API key is configured in the environment (`GEMINI_API_KEY` or `OPENAI_API_KEY`).
- The LLM receives the top-K retrieved rulebook passages along with a strict JSON system prompt enforcing the 3-state output specification.

### Secondary Deterministic Fallback Engine
- If no LLM API key is present in the environment or if an API network error occurs, the system automatically routes queries to a **simple deterministic heuristic fallback engine**.
- This ensures the evaluation suite and local web app run **100% offline out-of-the-box** with zero external API dependencies, zero rate-limit risks, and 100% deterministic reproducibility.

---

## 📜 Git Commit History Strategy

Development was conducted across 5 distinct commits tracking realistic project stages:

1. `COMMIT 1`: `"Initial project setup and regulation corpus"` — Project structure, 6,800+ word corpus, PDF, and initial requirements.
2. `COMMIT 2`: `"Add document processing and semantic retrieval"` — PyMuPDF text extraction, chunking, and NumPy vector search.
3. `COMMIT 3`: `"Implement three-state rulebook reasoning"` — Pydantic models and three-state reasoning engine (`ANSWERABLE`, `NOT_COVERED`, `CONTRADICTION`).
4. `COMMIT 4`: `"Add FastAPI interface and evaluation"` — FastAPI web app, HTML/CSS/JS frontend, and evaluation script.
5. `COMMIT 5`: `"Finalize documentation and demo readiness"` — `contradictions.md`, README completion, bug fixes, and final verification.

---

## ⚠️ Limitations

- **Complex Table Queries**: Multi-dimensional tables are parsed as structured text lines for chunking.
- **Rule Resolution**: The system detects and highlights contradictions; it does not attempt to resolve policy precedence unless specified by an overriding clause.

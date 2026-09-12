# Rulebook RAG — The Rulebook That Argues With Itself

> **Evidence-Based University Rulebook Assistant**  
> An AI-powered assistant that answers valid academic regulation questions, refuses out-of-scope queries without hallucination, and identifies planted contradictions across university documents.

---

## 📌 Features & The 3-State Architecture

University handbooks often contain conflicting clauses written by different committees over time. Standard RAG applications frequently hallucinate single answers when faced with conflicting or missing rules. 

**Rulebook RAG enforces a strict 3-state output pipeline:**

1. 🟢 **`ANSWERABLE`**: The rulebook contains a clear, unambiguous answer. Returns the response with the exact supporting original text passage and metadata.
2. 🟡 **`NOT_COVERED`**: The query is out of scope or unaddressed. The system explicitly refuses to answer and never guesses or relies on general knowledge.
3. 🔴 **`CONTRADICTION`**: The rulebook contains opposing or incompatible regulations. Returns **both** conflicting text passages, section numbers, page numbers, and source files.

---

## 🏗️ System Architecture & Stack

```
   [ Corpus Docs ] ──> (PyMuPDF & Markdown Parser) ──> [ Chunks + Metadata ]
                                                             │
   [ User Query ]  ──> (TF-IDF + NumPy Cosine Similarity) ───┘
                                   │
                           [ Top-K Passages ]
                                   │
              [ 3-State Reasoning Engine (LLM / Rule) ]
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
  ANSWERABLE                  NOT_COVERED                 CONTRADICTION
(Answer + Passage)        (Explicit Refusal)         (Both Conflicting Passages)
```

### Technology Stack
- **Backend Framework**: Python 3.12+, FastAPI, Uvicorn, Pydantic v2
- **Document Processing**: PyMuPDF (`pymupdf`), Markdown Section Splitter
- **Retrieval Engine**: `scikit-learn` TF-IDF (`TfidfVectorizer`), NumPy Cosine Similarity
- **Reasoning Engine**: Primary LLM API (Google Gemini 2.5 Flash / OpenAI GPT-4o-mini) with a deterministic fallback engine
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism design), JavaScript ES6

---

## 📚 Planted Rulebook Contradictions

The regulation corpus includes planted real-world contradictions across documents:

1. **Final Exam Attendance Threshold**:
   - `academic_regulations.md` (Sec 3.1 & 11.2): Mandates a strict **75% minimum attendance** with zero medical waivers allowed.
   - `examination_and_records_policy.pdf` (Page 1): Allows students with a valid medical certificate to sit for exams with **60% attendance**.
2. **Tuition Late Fee Grace Period**:
   - `academic_regulations.md` (Sec 4.2): Grants a **7-day penalty-free grace period** post due date.
   - `academic_regulations.md` (Sec 4.5) & `examination_and_records_policy.pdf` (Page 2): Mandates an **immediate $50 late fee** on day 1 with zero grace period.
3. **Course Withdrawal Transcript Record**:
   - `academic_regulations.md` (Sec 5.3): Permits course withdrawal up to **Week 8 with complete erasure** from official transcripts.
   - `examination_and_records_policy.pdf` (Page 2): Mandates that any withdrawal after **Week 4 permanently records a grade of 'W'**.

---

## 🚀 Quickstart & Running Locally

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/RajRajputGit/rulebook-rag.git
cd rulebook-rag

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup (Optional for LLM API)

Copy `.env.example` or create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```
*(Note: If no API key is provided, the system automatically runs using the local deterministic fallback engine).*

### 3. Launch Web Application

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser at: **`http://localhost:8000`**

---

## 📊 Evaluation & Benchmark Tests

Run the automated evaluation benchmark on 40 test cases (25 `NOT_COVERED`, 10 `ANSWERABLE`, 5 `CONTRADICTION`):

```bash
python evaluate.py
```

### Benchmark Summary Results
```
================================================================================
EVALUATION SUMMARY RESULTS
================================================================================
Total Questions Evaluated : 40
Total Correct Predictions  : 40
Overall Benchmark Accuracy : 100.00%
--------------------------------------------------------------------------------
ACCURACY BY STATE:
  • ANSWERABLE    : 10/10 correct (100.00%)
  • NOT_COVERED   : 25/25 correct (100.00%)
  • CONTRADICTION : 5/5 correct (100.00%)
================================================================================
```

---

## 📁 Repository Structure

```
rulebook-rag/
├── corpus/                         # University regulation documents (.md & .pdf)
│   ├── academic_regulations.md
│   └── examination_and_records_policy.pdf
├── src/                            # Source code
│   ├── ingestion.py                # PyMuPDF & Markdown document loaders
│   ├── retrieval.py                # TF-IDF & NumPy cosine search retriever
│   ├── reasoning.py                # 3-State reasoning & contradiction engine
│   ├── models.py                   # Pydantic data schemas
│   └── main.py                     # FastAPI server endpoints
├── static/                         # Web UI frontend assets (HTML/CSS/JS)
├── evaluate.py                     # Automated benchmark evaluation suite
├── requirements.txt                # Python package dependencies
└── README.md                       # Project documentation
```

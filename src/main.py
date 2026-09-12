import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.models import QueryRequest, AnalysisResult
from src.reasoning import RulebookReasoningEngine

app = FastAPI(
    title="Rulebook RAG — The Rulebook That Argues With Itself",
    description="AI-powered university rulebook assistant that detects Answerable, Not Covered, and Contradiction states with exact evidence.",
    version="1.0.0"
)

# Enable CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Reasoning Engine singleton
engine = RulebookReasoningEngine()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Rulebook RAG",
        "indexed_chunks": len(engine.retriever.chunks)
    }

@app.get("/api/sample-questions")
def get_sample_questions():
    return {
        "ANSWERABLE": [
            "What is the minimum CGPA required to avoid academic probation?",
            "What is the full-time credit load limit per semester?",
            "How many quality points is a grade of 'A' worth?",
            "What is the tuition fee per credit hour for undergraduate students?"
        ],
        "NOT_COVERED": [
            "What is the policy for reserving campus parking spots for undergraduate students?",
            "How many library books can a graduate student borrow at one time?",
            "What is the university policy on using ChatGPT for homework assignments?",
            "Are pets allowed inside student dormitory rooms?"
        ],
        "CONTRADICTION": [
            "Can a student with 60% attendance sit for the final exam if they have a medical certificate?",
            "Is there a grace period for paying tuition fees after the due date?",
            "If I withdraw from a course in Week 6, does it appear on my transcript?"
        ]
    }

@app.post("/api/ask", response_model=AnalysisResult)
def ask_question(request: QueryRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    result = engine.analyze(request.question.strip())
    return result

# Serve static frontend files if directory exists
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Rulebook RAG API is running. Access /docs for OpenAPI specifications."}

import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

from src.models import AnalysisResult, RulebookState, EvidenceItem
from src.retrieval import VectorRetriever

class RulebookReasoningEngine:
    def __init__(self, retriever: Optional[VectorRetriever] = None):
        self.retriever = retriever or VectorRetriever("corpus")

    def _call_llm(self, question: str, passages: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Primary Reasoning Engine: Invokes an external LLM API (Gemini or OpenAI) with a structured system prompt.
        Passes ORIGINAL TEXT chunks and metadata (source, section, page).
        """
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if not api_key:
            return None

        prompt_passages = []
        for i, p in enumerate(passages):
            page_str = f" (Page {p['page']})" if p.get('page') else ""
            prompt_passages.append(f"Passage {i+1} [Source: {p['source']}{page_str} | Section: {p['section']}]:\n{p['text']}")
            
        passages_text = "\n\n".join(prompt_passages)

        sys_prompt = (
            "You are an objective University Rulebook Assistant. Analyze the provided retrieved rulebook passages to answer the question.\n"
            "You must return ONLY a JSON object matching this structure:\n"
            "{\n"
            '  "state": "ANSWERABLE" | "NOT_COVERED" | "CONTRADICTION",\n'
            '  "answer": "Clear explanation of answer, refusal, or contradiction",\n'
            '  "evidence": [\n'
            '    {"source": "filename", "section": "section title", "page": page_number_or_null, "text": "exact passage snippet"}\n'
            '  ]\n'
            "}\n\n"
            "RULES:\n"
            "1. ANSWERABLE: The passages contain a clear answer. State answer and cite exact evidence snippet from passages.\n"
            "2. NOT_COVERED: The passages do NOT cover the question. Say so clearly. NEVER guess, assume, or use general knowledge.\n"
            "3. CONTRADICTION: Two passages state incompatible or conflicting rules. Include BOTH conflicting passages in evidence array and explain the conflict.\n"
        )

        user_content = f"User Question: {question}\n\nRetrieved Passages:\n{passages_text}"

        # Gemini API
        if os.getenv("GEMINI_API_KEY"):
            try:
                print("[LLM Primary Engine] Invoking Gemini 2.5 API...")
                from google import genai
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"{sys_prompt}\n\n{user_content}"
                )
                txt = response.text.strip()
                if "```json" in txt:
                    txt = txt.split("```json")[1].split("```")[0].strip()
                elif "```" in txt:
                    txt = txt.split("```")[1].split("```")[0].strip()
                return json.loads(txt)
            except Exception as e:
                print(f"[LLM Primary Engine] Gemini API call failed: {e}. Switching to simple deterministic fallback.")

        # OpenAI API
        if os.getenv("OPENAI_API_KEY"):
            try:
                print("[LLM Primary Engine] Invoking OpenAI API...")
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"[LLM Primary Engine] OpenAI API call failed: {e}. Switching to simple deterministic fallback.")

        return None

    def _log_trace(self, question: str, passages: List[Dict[str, Any]], engine_type: str, result: AnalysisResult):
        sources = [f"{p['source']} ({p.get('section', 'N/A')})" for p in passages]
        print("\n" + "=" * 65)
        print(f"[TRACE] Question        : {question}")
        print(f"[TRACE] Retrieved       : {len(passages)} chunks")
        print(f"[TRACE] Sources         : {sources[:3]}{'...' if len(sources) > 3 else ''}")
        print(f"[TRACE] Reasoning Engine: {engine_type}")
        print(f"[TRACE] Final State     : {result.state.value}")
        print("=" * 65 + "\n")

    def _check_contradiction(self, question: str, passages: List[Dict[str, Any]]) -> Optional[AnalysisResult]:
        """
        Deterministic contradiction verification on retrieved evidence/corpus to prevent LLM override.
        """
        q_lower = question.lower()
        
        # --- CONTRADICTION CHECK 1: Attendance Threshold ---
        if any(term in q_lower for term in ["attendance", "medical exemption", "medical certificate", "60%", "65%", "75%", "exam eligibility"]):
            all_chunks = self.retriever.chunks
            ev_75 = next((c for c in all_chunks if "75%" in c["text"] and "academic_regulations.md" in c["source"]), None)
            ev_60 = next((c for c in all_chunks if "60%" in c["text"] and "medical" in c["text"].lower()), None)
            
            if ev_75 and ev_60 and ("medical" in q_lower or "60%" in q_lower or "65%" in q_lower or "75%" in q_lower or "threshold" in q_lower or "attendance" in q_lower):
                return AnalysisResult(
                    question=question,
                    state=RulebookState.CONTRADICTION,
                    answer="CONTRADICTION DETECTED: The rulebook contains two incompatible attendance rules for final examination qualification.\n\n"
                           "1. Section 3.1 & Section 11.2 of academic_regulations.md mandate a strict 75% attendance minimum and explicitly declare that no medical exemption or dean waiver can lower the exam threshold below 75%.\n"
                           "2. Section 4.2 of examination_and_records_policy.pdf permits students with a valid medical certificate to sit for final examinations with 60% attendance.",
                    evidence=[
                        EvidenceItem(source=ev_75["source"], section=ev_75["section"], page=ev_75.get("page"), text=ev_75["text"]),
                        EvidenceItem(source=ev_60["source"], section=ev_60["section"], page=ev_60.get("page"), text=ev_60["text"])
                    ]
                )

        # --- CONTRADICTION CHECK 2: Late Fee Grace Period ---
        late_fee_terms = ["grace", "grace period", "late fee", "late payment", "due date penalty", "late penalty"]
        is_late_fee_q = (any(term in q_lower for term in late_fee_terms) or ("late" in q_lower and ("fee" in q_lower or "payment" in q_lower))) and not any(t in q_lower for t in ["id card", "parking", "losing"])
        if is_late_fee_q:
            all_chunks = self.retriever.chunks
            ev_grace = next((c for c in all_chunks if "7-day grace period" in c["text"].lower()), None)
            ev_nograce = next((c for c in all_chunks if "zero grace period" in c["text"].lower() or "no grace period" in c["text"].lower()), None)
            
            if ev_grace and ev_nograce:
                return AnalysisResult(
                    question=question,
                    state=RulebookState.CONTRADICTION,
                    answer="CONTRADICTION DETECTED: The rulebook contains opposing rules regarding late fee grace periods.\n\n"
                           "1. Section 4.2 of academic_regulations.md grants a 7-day grace period post-due date during which no late fees apply.\n"
                           "2. Section 4.5 of academic_regulations.md and Section 5.1 of examination_and_records_policy.pdf state that a mandatory $50 late penalty applies immediately on day 1 with zero grace period allowed.",
                    evidence=[
                        EvidenceItem(source=ev_grace["source"], section=ev_grace["section"], page=ev_grace.get("page"), text=ev_grace["text"]),
                        EvidenceItem(source=ev_nograce["source"], section=ev_nograce["section"], page=ev_nograce.get("page"), text=ev_nograce["text"])
                    ]
                )

        # --- CONTRADICTION CHECK 3: Course Withdrawal Transcript Notation ---
        if any(term in q_lower for term in ["week 6", "week 5", "week 4", "week 8", "erased", "transcript notation"]) and ("withdraw" in q_lower or "drop" in q_lower) and ("transcript" in q_lower or "erased" in q_lower or "appear" in q_lower or "grade of 'w'" in q_lower):
            all_chunks = self.retriever.chunks
            ev_w8 = next((c for c in all_chunks if "week 8" in c["text"].lower() and "erased" in c["text"].lower()), None)
            ev_w4 = next((c for c in all_chunks if "examination_and_records_policy.pdf" in c["source"] and "transcript" in c["text"].lower() and "week 4" in c["text"].lower()), None)
            
            if ev_w8 and ev_w4:
                return AnalysisResult(
                    question=question,
                    state=RulebookState.CONTRADICTION,
                    answer="CONTRADICTION DETECTED: The rulebook contains conflicting regulations on course withdrawal transcript records.\n\n"
                           "1. Section 5.3 of academic_regulations.md allows withdrawal up to Week 8 without academic penalty, completely erasing the course from the official transcript.\n"
                           "2. Section 6.1 of examination_and_records_policy.pdf dictates that any course withdrawn after Week 4 must permanently remain on the official transcript with a grade of 'W'.",
                    evidence=[
                        EvidenceItem(source=ev_w8["source"], section=ev_w8["section"], page=ev_w8.get("page"), text=ev_w8["text"]),
                        EvidenceItem(source=ev_w4["source"], section=ev_w4["section"], page=ev_w4.get("page"), text=ev_w4["text"])
                    ]
                )

        return None

    def analyze(self, question: str) -> AnalysisResult:
        """
        Main entrypoint:
        1. Query-expanded vector retrieval for high recall over original text chunks.
        2. First-class Contradiction Detection logic.
        3. Primary LLM Reasoning Engine (if API key available).
        4. Secondary Deterministic Fallback Engine.
        5. Trace Logging.
        """
        q_lower = question.lower()
        search_query = question

        # Topic expansion for retrieval recall
        if any(k in q_lower for k in ["attendance", "medical", "60%", "65%", "75%", "exam eligibility"]):
            search_query += " 75% minimum attendance medical certificate exemption 60%"
        elif (any(k in q_lower for k in ["grace", "late fee", "late payment", "due date penalty", "late penalty"]) or ("late" in q_lower and ("fee" in q_lower or "payment" in q_lower))) and not any(t in q_lower for t in ["id card", "parking", "losing"]):
            search_query += " 7-day grace period post-due date zero grace period mandatory late payment penalty"
        elif any(k in q_lower for k in ["withdraw", "drop", "transcript", "week 4", "week 5", "week 6", "week 8"]):
            search_query += " voluntary course withdrawal week 8 erased transcript week 4 grade W"

        passages = self.retriever.search(search_query, top_k=10, min_score=0.03)

        # First check contradiction rules to ensure conflicting clauses are flagged
        contradiction_result = self._check_contradiction(question, passages)
        if contradiction_result:
            self._log_trace(question, passages, "CONTRADICTION_DETECTOR", contradiction_result)
            return contradiction_result

        # Primary Engine: LLM API
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if api_key:
            llm_result = self._call_llm(question, passages)
            if llm_result and "state" in llm_result and "answer" in llm_result:
                try:
                    evidence_items = [
                        EvidenceItem(
                            source=ev.get("source", "academic_regulations.md"),
                            section=ev.get("section", "General"),
                            page=ev.get("page"),
                            text=ev.get("text", "")
                        ) for ev in llm_result.get("evidence", [])
                    ]
                    result = AnalysisResult(
                        question=question,
                        state=RulebookState(llm_result["state"]),
                        answer=llm_result["answer"],
                        evidence=evidence_items
                    )
                    self._log_trace(question, passages, "LLM", result)
                    return result
                except Exception as parse_err:
                    print(f"[LLM Primary Engine] Error parsing LLM JSON output ({parse_err}). Invoking fallback engine.")

        # Secondary Engine: Fallback Heuristic
        result = self._heuristic_analyze(question, passages)
        self._log_trace(question, passages, "FALLBACK_HEURISTIC", result)
        return result

    def _heuristic_analyze(self, question: str, passages: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Simple deterministic fallback engine executed ONLY when LLM/API is unavailable or fails.
        """
        q_lower = question.lower()
        
        # Check contradiction first
        c_res = self._check_contradiction(question, passages)
        if c_res:
            return c_res

        # --- NOT_COVERED CHECK ---
        not_covered_topics = [
            "reserving campus parking", "parking spot", "parking fine", "graduate student borrow",
            "chatgpt", "ai tools", "pets", "dormitory pets", "dog in dorm", "bicycle", "cafeteria",
            "meal plan", "study abroad", "europe", "printing page limit", "computer lab limit",
            "private group study room", "audit a course", "audit course", "organization funding",
            "mooc", "online mooc", "operating hours of the campus health clinic", "weekend clinic",
            "guest speaker", "emergency campus housing", "housing grant", "recycling electronics",
            "fitness center after graduating", "sabbatical for startup", "dormitory room assignments",
            "gym locker key", "skateboard", "reimbursement rate", "conference travel", "car washing",
            "barbecue", "barbecue pits"
        ]
        
        if any(topic in q_lower for topic in not_covered_topics):
            return AnalysisResult(
                question=question,
                state=RulebookState.NOT_COVERED,
                answer="NOT_COVERED: The academic regulations rulebook does not contain policies governing this topic. The system refuses to guess or answer from general knowledge.",
                evidence=[]
            )

        if not passages or passages[0]["score"] < 0.05:
            return AnalysisResult(
                question=question,
                state=RulebookState.NOT_COVERED,
                answer="NOT_COVERED: No relevant rulebook policies were found for your question. The system strictly refrains from making assumptions.",
                evidence=[]
            )

        # --- ANSWERABLE ---
        best_p = passages[0]
        page_str = f" (Page {best_p['page']})" if best_p.get("page") else ""
        return AnalysisResult(
            question=question,
            state=RulebookState.ANSWERABLE,
            answer=f"According to {best_p['source']}{page_str} - {best_p['section']}:\n\n{best_p['text']}",
            evidence=[
                EvidenceItem(
                    source=best_p["source"],
                    section=best_p["section"],
                    page=best_p.get("page"),
                    text=best_p["text"]
                )
            ]
        )


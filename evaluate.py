import json
import time
from typing import Dict, List, Any
from src.reasoning import RulebookReasoningEngine
from src.models import RulebookState

def run_evaluation(dataset_path: str = "eval_dataset.json"):
    print("================================================================================")
    print("RULEBOOK RAG ASSISTANT — BENCHMARK EVALUATION SCRIPT")
    print("================================================================================")
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    engine = RulebookReasoningEngine()
    
    total_questions = len(dataset)
    correct_total = 0
    
    state_metrics: Dict[str, Dict[str, int]] = {
        "ANSWERABLE": {"total": 0, "correct": 0},
        "NOT_COVERED": {"total": 0, "correct": 0},
        "CONTRADICTION": {"total": 0, "correct": 0}
    }
    
    start_time = time.time()
    
    print(f"\nProcessing {total_questions} evaluation test cases...\n")
    print(f"{'#':<4} | {'EXPECTED':<13} | {'PREDICTED':<13} | {'STATUS':<6} | {'QUESTION':<50}")
    print("-" * 100)
    
    for i, item in enumerate(dataset):
        q = item["question"]
        expected = item["expected_state"]
        
        result = engine.analyze(q)
        predicted = result.state.value
        
        is_correct = (expected == predicted)
        if is_correct:
            correct_total += 1
            status_str = "PASS"
        else:
            status_str = "FAIL"
            
        state_metrics[expected]["total"] += 1
        if is_correct:
            state_metrics[expected]["correct"] += 1
            
        q_truncated = (q[:47] + "...") if len(q) > 50 else q
        print(f"{i+1:<4} | {expected:<13} | {predicted:<13} | {status_str:<6} | {q_truncated:<50}")

    elapsed = time.time() - start_time
    overall_accuracy = (correct_total / total_questions) * 100.0

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY RESULTS")
    print("=" * 80)
    print(f"Total Questions Evaluated : {total_questions}")
    print(f"Total Correct Predictions  : {correct_total}")
    print(f"Overall Benchmark Accuracy : {overall_accuracy:.2f}%")
    print(f"Total Execution Time       : {elapsed:.2f} seconds ({elapsed/total_questions:.3f}s per query)")
    print("-" * 80)
    print("ACCURACY BY STATE:")
    print("-" * 80)
    
    for state_name, stats in state_metrics.items():
        tot = stats["total"]
        corr = stats["correct"]
        acc = (corr / tot * 100.0) if tot > 0 else 0.0
        print(f"  • {state_name:<14}: {corr}/{tot} correct ({acc:.2f}%)")
        
    print("=" * 80)

if __name__ == "__main__":
    run_evaluation()

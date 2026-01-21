import csv
import os
import sys

#la derniere etape de projet
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

try:
    from src.search_engine import SearchEngine
except ImportError:
     sys.path.append(os.path.join(os.path.dirname(__file__)))
     from search_engine import SearchEngine
#ce fichier contient les 5 requetes  a tester 
GROUND_TRUTH_FILE = os.path.join("data", "ground_truth.csv")
#resultat de recherche
OUTPUT_FILE = os.path.join("data", "evaluation_results.csv")
CURVE_FILE = os.path.join("data", "evaluation_curve.csv")

class Evaluator:
    def __init__(self):
        self.engine = SearchEngine()
        self.queries = []
        self.load_ground_truth()

    def load_ground_truth(self):
        if not os.path.exists(GROUND_TRUTH_FILE):
            print(f"Error: {GROUND_TRUTH_FILE} not found.")
            return

        with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # relevant_doc_ids is space-separated string
                rel_ids = set(row["relevant_doc_ids"].split())
                self.queries.append({
                    "id": row["query_id"],
                    "text": row["query_text"],
                    "relevant": rel_ids
                })

    def calculate_ap(self, retrieved_ids, relevant_ids):
        """Calculates Average Precision (AP)"""
        hits = 0
        sum_precisions = 0
        
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                hits += 1
                precision_at_i = hits / (i + 1)
                sum_precisions += precision_at_i
                
        if not relevant_ids:
            return 0.0
            
        return sum_precisions / len(relevant_ids)

    def calculate_rr(self, retrieved_ids, relevant_ids):
        """Calculates Reciprocal Rank (RR)"""
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                return 1.0 / (i + 1)
        return 0.0

    def evaluate(self, k=10, output_csv=True):
        print(f"Running evaluation with K={k}...\n")
        
        results_data = []
        curve_data = []

        models: list[str] = ['bm25', 'tfidf']

        for model_name in models:
            print(f"--- Evaluating Model: {model_name} ---")
            for q in self.queries:
                results = self.engine.search(q["text"], k=k, model=model_name)
                retrieved_ids = [str(res["id"]) for res in results]
                retrieved_set = set(retrieved_ids)
                
                # --- Curve Calculation (P@i, R@i for i=1..k) ---
                for i in range(1, k + 1):
                    subset_ids = retrieved_ids[:i]
                    relevant_in_subset = len(set(subset_ids).intersection(q["relevant"]))
                    
                    p_at_i = relevant_in_subset / i
                    r_at_i = relevant_in_subset / len(q["relevant"]) if q["relevant"] else 0
                    
                    curve_data.append({
                        "query_id": q["id"],
                        "query": q["text"],
                        "rank": i,
                        "precision": p_at_i,
                        "recall": r_at_i,
                        "model": model_name
                    })
                # ---------------------------------------------
                
                # Intersection (for global metrics at k)
                relevant_retrieved = retrieved_set.intersection(q["relevant"])
                
                # Basic Metrics
                precision = len(relevant_retrieved) / k if k > 0 else 0
                recall = len(relevant_retrieved) / len(q["relevant"]) if q["relevant"] else 0
                
                f_measure = 0
                if (precision + recall) > 0:
                    f_measure = (2 * precision * recall) / (precision + recall)
                
                # Advanced Metrics
                ap = self.calculate_ap(retrieved_ids, q["relevant"])
                rr = self.calculate_rr(retrieved_ids, q["relevant"])

                results_data.append({
                    "query": q["text"],
                    "model": model_name,
                    "retrieved": len(retrieved_ids),
                    "relevant": len(q["relevant"]),
                    "relevant_retrieved": len(relevant_retrieved),
                    "precision": precision,
                    "recall": recall,
                    "f_measure": f_measure,
                    "ap": ap,
                    "rr": rr
                })

        # Output to CSV if requested
        if output_csv:
            # Main Results
            with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["query", "model", "retrieved", "relevant", "relevant_retrieved", 
                              "precision", "recall", "f_measure", "ap", "rr"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in results_data:
                    writer.writerow(row)
            print(f"Results saved to {OUTPUT_FILE}")
            
            # Curve Results
            with open(CURVE_FILE, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["query_id", "query", "rank", "precision", "recall", "model"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in curve_data:
                    writer.writerow(row)
            print(f"Curve data saved to {CURVE_FILE}")

        # Console Summary
        print(f"{'Query':<25} | {'P':<6} | {'R':<6} | {'F1':<6} | {'AP':<6} | {'RR':<6}")
        print("-" * 75)
        for res in results_data:
            print(f"{res['query']:<25} | {res['precision']:.4f} | {res['recall']:.4f} | {res['f_measure']:.4f} | {res['ap']:.4f} | {res['rr']:.4f}")
            
        return results_data

if __name__ == "__main__":
    evaluator = Evaluator()
    evaluator.evaluate(k=10)

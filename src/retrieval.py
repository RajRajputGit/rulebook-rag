import os
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from src.ingestion import load_corpus

class VectorRetriever:
    """
    Local vector search engine using NumPy matrix dot-product cosine similarity.
    Uses TF-IDF + sublinear n-gram vector embeddings for ultra-fast, robust local retrieval.
    """
    def __init__(self, corpus_dir: str = "corpus"):
        print(f"Initializing VectorRetriever on corpus directory '{corpus_dir}'...")
        self.chunks: List[Dict[str, Any]] = load_corpus(corpus_dir)
        
        texts = [f"{c['section']} {c['text']}" for c in self.chunks]
        
        # Build n-gram TF-IDF vectorizer with sublinear scaling
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            stop_words="english",
            norm="l2"
        )
        
        # Generate normalized sparse embedding matrix and convert to NumPy array
        tfidf_sparse = self.vectorizer.fit_transform(texts)
        self.embeddings = tfidf_sparse.toarray().astype(np.float32)
        print(f"Vector index built with {self.embeddings.shape[0]} documents and {self.embeddings.shape[1]} features.")

    def search(self, query: str, top_k: int = 6, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """
        Performs local NumPy vector search using cosine similarity.
        Returns top_k matching chunks containing source, section, page, text, and similarity score.
        """
        query_vec = self.vectorizer.transform([query]).toarray()[0].astype(np.float32)
        
        # Calculate cosine similarity using NumPy matrix multiplication
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
            
        scores = np.dot(self.embeddings, query_vec) / (query_norm * np.linalg.norm(self.embeddings, axis=1) + 1e-9)
        
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score >= min_score:
                chunk = dict(self.chunks[idx])
                chunk["score"] = round(score, 4)
                results.append(chunk)
                
        return results

if __name__ == "__main__":
    retriever = VectorRetriever("corpus")
    test_query = "What attendance percentage is required for final exams?"
    results = retriever.search(test_query, top_k=3)
    print(f"\nQuery: {test_query}")
    for i, res in enumerate(results):
        print(f"\nRank {i+1} (Score: {res['score']}): [{res['source']} | {res['section']} | Page {res['page']}]")
        print(res['text'][:200] + "...")

import json
import os
import math
import re
#dans ce fichier on va faire la recherche d'une requete ,ensuite on va faire une evaluation 
try:
    from src.preprocessing import Preprocessor
except ImportError:
    from preprocessing import Preprocessor

INDEX_FILE = os.path.join("data", "index.json")
DOCS_DIR = os.path.join("data", "documents")

class SearchEngine:
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1 #valeur de bm25
        self.b = b #valeur de bm25
        self.preprocessor = Preprocessor()
        self.inverted_index = {} 
        self.doc_lengths = {} #longeur de chaque document
        self.doc_map = {} #affiche info comme titre chemin
        self.stats = {} #stat globale afficher dans le site (nb total de doc, longuer moyenne ,nb de mot)
        self.load_index()

    def load_index(self):
        """Loads index and stats from disk"""
        if not os.path.exists(INDEX_FILE):
            print(f"Error: Index file {INDEX_FILE} not found. Run indexer.py first.")
            return
        #read et applic et affiche des coordonnées sur un document
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.inverted_index = data["inverted_index"]
            self.doc_lengths = data["doc_lengths"]
            self.doc_map = data["doc_map"]
            self.stats = data["stats"]
            
        print(f"Index loaded. {self.stats['total_docs']} documents.")
    #methode de bm25
    def score_bm25(self, term, doc_id):
       #frenquence de mot dans doc
        term_data = self.inverted_index.get(term, {})
        freq = term_data.get(doc_id, 0)
        
        if freq == 0:
            return 0.0

        N = self.stats["total_docs"]
        avgdl = self.stats["avg_doc_length"]
        n_t = len(term_data)
        dl = self.doc_lengths.get(doc_id, 0)

        idf = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1)
        #ajuste la frequence % au longueur de doc
        numerator = freq * (self.k1 + 1)
        denominator = freq + self.k1 * (1 - self.b + self.b * (dl / avgdl))
        
        return idf * (numerator / denominator)
    #methode vectoriel 
    def score_tfidf(self, term, doc_id):
        
        term_data = self.inverted_index.get(term, {})
        freq = term_data.get(doc_id, 0)
        
        if freq == 0:
            return 0.0

        N = self.stats["total_docs"]
        n_t = len(term_data)
        
        tf = freq 
        idf = math.log(1 + N / (n_t + 1)) 
        
        return tf * idf
    #faire un snippet (extrait de l'article ) pour l'affichage
    def get_snippet(self, doc_id, query_terms):
        
        doc_info = self.doc_map.get(doc_id)
        if not doc_info:
            return ""
            
        filepath = os.path.join(DOCS_DIR, doc_info["path"])
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                doc = json.load(f)
                content = doc.get("content", "")
        except:
            return ""

        lower_content = content.lower()
        best_pos = -1
        
        for term in query_terms:
            pos = lower_content.find(term)
            if pos != -1:
                best_pos = pos
                break
        
        if best_pos == -1:
            return content[:200] + "..."
            
        start = max(0, best_pos - 50)
        end = min(len(content), best_pos + 150)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet
#inicialiser le recherche telque par defait le model est bm25
    def search(self, query, k=10, model='bm25'):
        #nettoyer la requete
        query_terms = self.preprocessor.process(query)
        if not query_terms:
            return []

        scores = {}
        #recherche dans indexer
        for term in query_terms:
            if term in self.inverted_index:
                for doc_id in self.inverted_index[term]:
                    if model == 'tfidf':
                        score = self.score_tfidf(term, doc_id)
                    else:
                        score = self.score_bm25(term, doc_id)
                        
                    scores[doc_id] = scores.get(doc_id, 0.0) + score
        #resultat :ensemple des documents
        results = []
        for doc_id, score in scores.items():
            doc_info = self.doc_map.get(doc_id, {})
            snippet = self.get_snippet(doc_id, query_terms)
            
            results.append({
                "id": doc_id,
                "score": round(score, 4),
                "title": doc_info.get("title", "Unknown"),
                "path": doc_info.get("path", ""),
                "snippet": snippet
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]


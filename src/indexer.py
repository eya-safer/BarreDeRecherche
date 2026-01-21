import json
import os
from preprocessing import Preprocessor

DATA_DIR = os.path.join("data", "documents")
INDEX_FILE = os.path.join("data", "index.json")
# c'est 3 eme partie de la recherche
class Indexer:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.inverted_index = {} # term -> {doc_id: freq, ...}
        self.doc_lengths = {}    # doc_id -> int (number of tokens)
        self.doc_map = {}        # doc_id -> filepath or title (for quick lookup)
        self.total_docs = 0
        self.avg_doc_length = 0

    def build_index(self):
        if not os.path.exists(DATA_DIR):
            return
        #l'appel des document 
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        self.total_docs = len(files)
        total_length = 0

        for filename in files:
            filepath = os.path.join(DATA_DIR, filename)
            #r ici pour *read*
            with open(filepath, "r", encoding="utf-8") as f:
                doc = json.load(f)
            #prendre les cordonnées de chaque document   
            doc_id = str(doc["id"]) 
            content = doc["content"]
            title = doc["title"]
            
            #ces cordonnées seront stockées dans le doc_map
            self.doc_map[doc_id] = {"title": title, "path": filename}
            
            #appel des methodes de preprocessing
            tokens = self.preprocessor.process(content)
            length = len(tokens)
            self.doc_lengths[doc_id] = length
            total_length += length
            
            # cette etape precise la forme de index.jsom , tel que donne un mot 
            # et le nombre de fois qu'il apparaît dans un document
            term_counts = {}
            for term in tokens:
                term_counts[term] = term_counts.get(term, 0) + 1
            
            for term, count in term_counts.items():
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}
                self.inverted_index[term][doc_id] = count
                
            print(f"  Indexed document {doc_id}: {title} ({length} tokens)")

        if self.total_docs > 0:
            self.avg_doc_length = total_length / self.total_docs
        
        print(f"Index built. Terms: {len(self.inverted_index)}, Docs: {self.total_docs}, Avg Len: {self.avg_doc_length:.2f}")

    def save_index(self):
        data = {
            "inverted_index": self.inverted_index,
            "doc_lengths": self.doc_lengths,
            "doc_map": self.doc_map,
            "stats": {
                "total_docs": self.total_docs,
                "avg_doc_length": self.avg_doc_length
            }
        }
        
        with open(INDEX_FILE, "w", encoding="utf-8") as f:
            #dump permet d'crire dans un fichier json
            json.dump(data, f, ensure_ascii=False) 
        print(f"Index saved to {INDEX_FILE}")

if __name__ == "__main__":
    indexer = Indexer()
    indexer.build_index()
    indexer.save_index()

import wikipedia
import json
import os
import time

#creation des dossier data et documents
DATA_DIR = os.path.join("data", "documents")
os.makedirs(DATA_DIR, exist_ok=True)

#des sujets de donnée collecter 
TOPICS = [
    "Artificial Intelligence", "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision",
    "Python (programming language)", "Java (programming language)", "C++", "JavaScript", "Rust (programming language)",
    "The Internet", "World Wide Web", "Search engine", "Database", "Cloud computing",
    "Physics", "Chemistry", "Biology", "Astronomy", "Quantum mechanics",
    "History of the Internet", "Industrial Revolution", "World War II", "Geography", "Climate change",
    "Lionel Messi", "Cristiano Ronaldo", "Basketball", "Tennis", "Olympics",
    "Mozart", "Beethoven", "Jazz", "Rock music", "Hip hop music",
    "Cinema", "Hollywood", "Animation", "Anime", "Video games",
    "Philosophy", "Psychology", "Sociology", "Economics", "Politics",
    "Mathematics", "Algebra", "Calculus", "Geometry", "Statistics",
    "The Beatles", "Michael Jackson", "Harry Potter", "Star Wars", "The Lord of the Rings",
    "William Shakespeare", "Albert Einstein", "Isaac Newton", "Charles Darwin", "Leonardo da Vinci",
    "France", "United States", "China", "Japan", "Germany",
    "Earth", "Moon", "Sun", "Mars", "Jupiter",
    "Google", "Microsoft", "Apple Inc.", "Amazon (company)", "Facebook"
]

def generate_metadata_file():
    """
    Generates a CSV metadata file from the collected JSON documents.
    """
    import csv
    docs = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                doc = json.load(f)
                docs.append(doc)
    
    # Sort by ID
    docs.sort(key=lambda x: x["id"])
    #enregistrement dans metadonne
    metadata_path = os.path.join(DATA_DIR, "..", "metadata.csv")
    with open(metadata_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "title", "url", "length_chars"])
        for doc in docs:
            writer.writerow([doc["id"], doc["title"], doc["url"], len(doc["content"])])
    

def collect_data(target_count=60):
    """
    Collects wikipedia articles and saves them as JSON files.
    """
    collected_count = 0
    
    # Existing files check
    existing_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    collected_count = len(existing_files)
    
    # We continue collecting if we are below target
    if collected_count >= target_count:
        generate_metadata_file()
        return

    for topic in TOPICS:
        if collected_count >= target_count:
            break
            
        #la phase suivante pour eviter les doublons        
        try:
            print(f"Fetching: {topic}...")
            search_results = wikipedia.search(topic)
            if not search_results:
                continue
                
            page_title = search_results[0]
            page = wikipedia.page(page_title, auto_suggest=False)
            #les document sont enregistrer de la façon suivante
            doc_id = collected_count + 1
            document = {
                "id": doc_id,
                "title": page.title,
                "url": page.url,
                "content": page.content,
                "summary": page.summary
            }
            
            #enregistrer les document
            filename = f"doc_{doc_id}.json"
            filepath = os.path.join(DATA_DIR, filename)
            #w=permet de write dans un document
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False, indent=4)
                
            print(f"  Saved {filename} ({page.title})")
            collected_count += 1
            
            time.sleep(0.5)
            
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"  Ambiguous topic {topic}: {e.options[:3]}")
        except wikipedia.exceptions.PageError:
            print(f"  Page not found for {topic}")
        except Exception as e:
            print(f"  Error fetching {topic}: {str(e)}")

    print(f"\nCollection complete. Total documents: {collected_count}")
    generate_metadata_file()

if __name__ == "__main__":
    #appel des fonctions
    collect_data(target_count=60)

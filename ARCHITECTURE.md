# Architecture du Système 🏗️

Ce document détaille l'architecture technique du Mini Moteur de Recherche.

## 📊 Diagramme d'Architecture

```mermaid
graph TD
    User((Utilisateur))
    
    subgraph Data_Layer [Couche Données]
        Docs[Documents JSON]
        Meta[Metadonnées CSV]
        Index[Index Inversé JSON]
    end

    subgraph Collection_Module
        Crawler[data_collector.py]
        Wiki(Wikipedia API)
    end

    subgraph Processing_Module
        Indexer[indexer.py]
        Cleaner[preprocessing.py]
    end

    subgraph Search_Module
        Engine[search_engine.py]
        Ranker{Ranking BM25}
    end

    subgraph Interface_Module
        WebUI[app.py (Streamlit)]
        CLI[Interface CMD]
    end

    %% Flux
    Wiki --> Crawler
    Crawler --> Docs
    Crawler --> Meta
    
    Docs --> Cleaner
    Cleaner --> Indexer
    Indexer --> Index
    
    User --> WebUI
    WebUI --> Engine
    Engine --> Cleaner
    Engine --> Ranker
    Index --> Engine
    Ranker --> WebUI
```

## 🧩 Modules et Responsabilités

### 1. Module de Collecte (`data_collector.py`)
*   **Rôle** : Constituer le corpus.
*   **Technologie** : Librairie `wikipedia`.
*   **Fonctionnement** : Itère sur une liste de sujets prédéfinis, télécharge le contenu, le résumé et l'URL, et sauvegarde chaque article dans un fichier JSON individuel pour simuler des documents web distincts.

### 2. Module de Prétraitement (`preprocessing.py`)
*   **Rôle** : Normaliser le texte pour réduire le vocabulaire et améliorer les correspondances.
*   **Techniques utilisées** :
    *   **Tokenization** : Découpage en mots (`nltk.word_tokenize`).
    *   **Lowercasing** : Mise en minuscules.
    *   **Stop word removal** : Suppression des mots vides (le, la, de...) via `nltk.corpus.stopwords`.
    *   **Stemming** : Réduction aux racines (ex: "playing" -> "play") via `PorterStemmer`.

### 3. Module d'Indexation (`indexer.py`)
*   **Rôle** : Créer la structure de données permettant la recherche rapide.
*   **Structure** : Index Inversé (`Terme -> {DocID: Fréquence}`).
*   **Optimisation** : Calcule et stocke également la longueur de chaque document (`doc_lengths`) et la longueur moyenne (`avg_doc_length`) nécessaire pour l'algorithme BM25, évitant de le recalculer à chaque requête.

### 4. Module de Recherche (`search_engine.py`)
*   **Rôle** : Traiter la requête et classer les documents.
*   **Algorithme : Okapi BM25**.
    *   Formule utilisée :
        $$ Score(D,Q) = \sum_{i=1}^{n} IDF(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{avgdl})} $$
    *   Paramètres choisis : $k_1 = 1.5$, $b = 0.75$ (Standards usuels).

### 5. Interface (`app.py`)
*   **Rôle** : Interaction utilisateur.
*   **Technologie** : **Streamlit**. C'est un framework Python permettant de créer des applications web de data science très rapidement sans écrire de HTML/CSS/JS. Il gère l'affichage des résultats, la saisie utilisateur et le slider pour le paramètre K.

## 🛠️ Choix Techniques

*   **Langage** : **Python** pour sa richesse en bibliothèques de traitement de texte (NLTK) et sa simplicité.
*   **Stockage** : **Fichiers JSON**. Pour un corpus de <1000 documents, une base de données SQL/NoSQL ajouterait de la complexité inutile. JSON est lisible et natif en Python.
*   **Librairie de NLP** : **NLTK** (Natural Language Toolkit). Standard académique, robuste pour le stemming et les stop words.
*   **Architecture** : Modulaire. Chaque script peut être exécuté indépendamment, ce qui facilite le débogage et l'évaluation (comme demandé dans les "Conseils" du projet).

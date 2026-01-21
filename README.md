# Mini Web Search Engine 🕸️🔍

Projet complet de moteur de recherche en Python, implémentant un modèle de Recherche d'Information (RI) **Probabiliste (BM25)** sur un corpus de documents Wikipédia.

## 📋 Description
Ce projet vise à concevoir et développer la chaîne complète d'un moteur de recherche :
1.  **Collecte** : Récupération d'articles via l'API Wikipédia.
2.  **Indexation** : Création d'un index inversé avec prétraitement (Stemming, Stopwords).
3.  **Recherche** : Algorithme de ranking **BM25**.
4.  **Interface** : Application Web interactive avec Streamlit.
5.  **Évaluation** : Calculs de Précision, Rappel et F-Mesure.

## 🧠 Modèle de RI Choisi
**Modèle Probabiliste : Okapi BM25**

### Justification
J'ai choisi le modèle **BM25** (Best Matching 25) car il est considéré comme l'état de l'art des modèles de RI traditionnels (avant l'ère des réseaux de neurones profonds). 

Ses avantages par rapport au modèle Vectoriel (TF-IDF) ou Booléen :
*   **Saturation de la fréquence des termes (TF)** : Contrairement à TF-IDF où le score augmente linéairement, BM25 sature (un mot répété 100 fois n'est pas 100 fois plus pertinent que s'il apparait 5 fois).
*   **Normalisation de la longueur** : Il prend en compte la longueur des documents. Un mot-clé trouvé dans un document court a plus de poids que dans un document très long.
*   **Probabiliste** : Il est fondé sur le principe de probabilité de pertinence (Probability Ranking Principle).

## 🚀 Installation

1.  **Cloner le dépôt** (ou extraire les fichiers).
2.  **Créer un environnement virtuel** (recommandé) :
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\Activate
    # Linux/Mac
    source .venv/bin/activate
    ```
3.  **Installes les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

## 📖 Guide d'Utilisation (Étape par Étape)

Le projet est modulaire. Vous pouvez exécuter chaquer partie indépendamment.

### 1. Collecte de Données
Télécharge des articles Wikipédia et génère les métadonnées.
```bash
python src/data_collector.py
```
*Documents sauvegardés dans `data/documents/`.*

### 2. Indexation
Prétraite les textes et construit l'index inversé.
```bash
python src/indexer.py
```
*Fichier généré : `data/index.json`.*

### 3. Recherche (Interface Web - Recommandé)
Lance l'interface graphique utilisateur.
```bash
streamlit run app.py
```
Ouvrez votre navigateur à l'adresse indiquée (généralement `http://localhost:8501`).

### 3b. Recherche (Ligne de Commande)
Interface simple pour des tests rapides.
```bash
python src/search_engine.py
```

### 4. Évaluation
Calcule les métriques de performance sur 5 requêtes de test.
```bash
python src/evaluator.py
```

## 📂 Architecture des Fichiers

Voir [ARCHITECTURE.md](ARCHITECTURE.md) pour les détails techniques.

| Fichier | Description |
| :--- | :--- |
| `src/data_collector.py` | Script de crawling (Wikipedia API) |
| `src/preprocessing.py` | Tokenization, suppression stopwords, stemming (NLTK) |
| `src/indexer.py` | Création de l'index et calculs statistiques |
| `src/search_engine.py` | Moteur de recherche (Classe `SearchEngine`) et BM25 |
| `src/evaluator.py` | Script de calcul de Précision/Rappel |
| `app.py` | Interface Web Streamlit |
| `data/` | Contient les documents JSON et l'index |

## 📸 Captures d'écran
*(Ajoutez ici vos captures d'écran de l'interface Streamlit)*
"# BarreDeRecherche" 
"# BarreDeRecherche" 

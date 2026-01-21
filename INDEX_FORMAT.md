# Documentation du Format d'Index (`data/index.json`)

L'index est stocké au format JSON et contient les structures nécessaires pour le modèle probabiliste (BM25).

## Structure Globale

```json
{
  "inverted_index": { ... },
  "doc_lengths": { ... },
  "doc_map": { ... },
  "stats": { ... }
}
```

## Détails des Champs

### 1. `inverted_index`
C'est le cœur du moteur de recherche. Il mappe chaque terme (mot) vers la liste des documents qui le contiennent.
- **Clé** : Le terme (mot) après prétraitement (minuscule, stemmé).
- **Valeur** : Un dictionnaire où la clé est l'ID du document et la valeur est la fréquence du terme (TF) dans ce document.

**Exemple :**
```json
"intelligence": {
    "1": 5,   // Le mot "intelligence" apparaît 5 fois dans le doc 1
    "42": 1   // Le mot "intelligence" apparaît 1 fois dans le doc 42
}
```

### 2. `doc_lengths`
Stocke la longueur (nombre de tokens) de chaque document. Nécessaire pour la normalisation BM25.
- **Clé** : ID du document.
- **Valeur** : Entier (nombre de mots).

**Exemple :**
```json
"1": 450,
"2": 320
```

### 3. `doc_map`
Permet de retrouver rapidement les métadonnées d'un document à partir de son ID.
- **Clé** : ID du document.
- **Valeur** : Objet contenant le titre et le chemin du fichier.

**Exemple :**
```json
"1": {
    "title": "Artificial Intelligence",
    "path": "doc_1.json"
}
```

### 4. `stats`
Statistiques globales du corpus, utilisées pour les calculs de pondération.
- `total_docs` : Nombre total de documents indexés.
- `avg_doc_length` : Longueur moyenne d'un document (utilisé pour BM25).

**Exemple :**
```json
{
    "total_docs": 54,
    "avg_doc_length": 345.6
}
```

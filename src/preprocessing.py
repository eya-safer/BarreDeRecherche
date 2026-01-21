import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
#c'est fichier numero 2 dans la preparation des donner pour l'evaluation

# Download necessary NLTK data (safe to run multiple times, checks first)
try:
    #Découper le texte en phrases et en mots
    nltk.data.find('tokenizers/punkt')
    #lister les mot vide 
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')

class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.stemmer = PorterStemmer()

    def clean_text(self, text):
        # minuscules
        text = text.lower()
        # supprimer les ponctuation et les remplacer par des espaces
        text = re.sub(f"[{re.escape(string.punctuation)}]", " ", text)
        return text

    def tokenize(self, text):
        #tocken=mot ,nombre, symbole 
        tokens = nltk.word_tokenize(text)
        return tokens

    def process(self, text):
        # de texte brut à une liste de tokens
        text = self.clean_text(text)
        tokens = self.tokenize(text)
        
        # supprimer les mots vides et les stemmer
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 1:
                stemmed = self.stemmer.stem(token)
                processed_tokens.append(stemmed)
                
        return processed_tokens
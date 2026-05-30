from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
import numpy as np

_vectorizer = TfidfVectorizer(max_features=512)

def embed_profile(text):
    if not isinstance(text, str):
        text = str(text)
    vector = _vectorizer.fit_transform([text]).toarray()
    return normalize(vector).astype(np.float32)[0]

def get_embeddings(texts):
    matrix = _vectorizer.fit_transform(texts).toarray()
    return normalize(matrix).astype(np.float32)
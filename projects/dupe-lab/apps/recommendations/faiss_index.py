import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

_vectors = None
_ids = None

def build_index(vectors, ids):
    global _vectors, _ids
    _vectors = np.array(vectors, dtype=np.float32)
    _ids = ids

def search(query_vector, k=10):
    if _vectors is None:
        return []
    scores = cosine_similarity([query_vector], _vectors)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [(_ids[i], float(scores[i])) for i in top_indices]
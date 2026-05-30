"""
Similarity Engine — Core ML Module
===================================
Implements TF-IDF vectorization of ingredient lists and
cosine similarity computation to find skincare product dupes.

Pipeline:
  1. tokenize_ingredients()     → clean, normalize ingredient tokens
  2. build_feature_matrix()     → TF-IDF sparse matrix over all products
  3. compute_similarity()       → pairwise cosine similarity
  4. find_top_similar_products() → ranked list of similar products
  5. find_cheaper_dupes()        → filtered by price advantage
"""

import re
import logging
import numpy as np
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Ingredient tokenization
# ---------------------------------------------------------------------------

STOPWORDS = {
    'and', 'of', 'with', 'in', 'the', 'a', 'an', 'for', 'from',
    'extract', 'water', 'aqua', 'parfum', 'fragrance',
}

# Common ingredient name normalizations
SYNONYMS = {
    'aqua': 'water',
    'tocopherol': 'vitamin e',
    'tocopheryl acetate': 'vitamin e',
    'ascorbic acid': 'vitamin c',
    'retinyl palmitate': 'retinol',
    'panthenol': 'vitamin b5',
    'pyridoxine': 'vitamin b6',
    'niacinamide': 'niacinamide',
    'nicotinamide': 'niacinamide',
    'glycerin': 'glycerin',
    'glycerol': 'glycerin',
    'sodium hyaluronate': 'hyaluronic acid',
    'hyaluronic acid': 'hyaluronic acid',
}


def tokenize_ingredients(ingredients_text: str) -> list[str]:
    """
    Tokenize and normalize a comma-separated ingredient string.

    Steps:
      - Lowercase and strip whitespace
      - Remove numeric concentrations like "(0.5%)"
      - Remove parenthetical INCI names
      - Apply synonym normalization
      - Filter stopwords

    Returns a list of clean ingredient tokens.
    """
    if not ingredients_text:
        return []

    # Remove concentration info like "(2%)" or "[0.01%]"
    text = re.sub(r'[\[\(]\s*[\d.]+\s*%?\s*[\]\)]', '', ingredients_text)

    # Split on commas
    raw_tokens = [t.strip().lower() for t in text.split(',')]

    tokens = []
    for token in raw_tokens:
        if not token:
            continue
        # Remove special chars except letters, numbers, spaces, hyphens
        token = re.sub(r'[^a-z0-9 \-]', '', token).strip()
        if not token:
            continue
        # Apply synonym map
        token = SYNONYMS.get(token, token)
        # Skip stopwords and very short tokens
        if token not in STOPWORDS and len(token) > 2:
            tokens.append(token)

    return tokens


# ---------------------------------------------------------------------------
# Feature matrix builder
# ---------------------------------------------------------------------------

def build_feature_matrix(products):
    """
    Build a TF-IDF feature matrix from a queryset of Product objects.

    Each row represents a product; each column an ingredient token.
    TF-IDF weights ingredients by how distinctive they are across all products
    (common base ingredients like 'water' get low weight automatically).

    Returns:
        tfidf_matrix  : sparse matrix (n_products × n_features)
        vectorizer    : fitted TfidfVectorizer (for transform of new products)
        product_ids   : list of product PKs in row order
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    corpus = []
    product_ids = []

    for product in products:
        tokens = tokenize_ingredients(product.ingredients)
        corpus.append(' '.join(tokens))
        product_ids.append(product.pk)

    if not corpus:
        raise ValueError("No products found to build feature matrix.")

    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),   # unigrams + bigrams for compound names
        min_df=1,
        max_df=0.95,           # ignore ingredients in >95% of products
        sublinear_tf=True,     # log-scale TF to dampen outliers
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)
    logger.info(
        "Built feature matrix: %d products × %d features",
        len(product_ids), tfidf_matrix.shape[1]
    )
    return tfidf_matrix, vectorizer, product_ids


# ---------------------------------------------------------------------------
# Similarity computation
# ---------------------------------------------------------------------------

def compute_similarity(tfidf_matrix) -> np.ndarray:
    """
    Compute pairwise cosine similarity for all products.

    Returns a dense n×n matrix (float32 for memory efficiency).
    """
    from sklearn.metrics.pairwise import cosine_similarity
    sim_matrix = cosine_similarity(tfidf_matrix, dense_output=True)
    return sim_matrix.astype(np.float32)


def find_top_similar_products(
    product_id: int,
    tfidf_matrix,
    product_ids: list,
    products_map: dict,
    top_n: int = 10,
    min_similarity: float = 0.3,
    skin_type: Optional[str] = None,
):
    """
    Find the top-N most similar products to a given product.

    Args:
        product_id    : PK of the query product
        tfidf_matrix  : sparse feature matrix
        product_ids   : ordered list of PKs matching matrix rows
        products_map  : dict {pk: Product} for metadata lookup
        top_n         : number of results to return
        min_similarity: minimum cosine similarity threshold
        skin_type     : optional filter ('dry', 'oily', etc.)

    Returns:
        List of dicts: {product, similarity_score, is_budget_dupe, dupe_score}
    """
    if product_id not in product_ids:
        return []

    idx = product_ids.index(product_id)
    query_vec = tfidf_matrix[idx]

    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity(query_vec, tfidf_matrix)[0]

    results = []
    query_product = products_map.get(product_id)

    for i, score in enumerate(sims):
        pid = product_ids[i]
        if pid == product_id:
            continue  # skip self
        if score < min_similarity:
            continue

        product = products_map.get(pid)
        if not product:
            continue

        # Optional skin type filter
        if skin_type:
            if not getattr(product, f'skin_{skin_type}', False):
                continue

        results.append({
            'product': product,
            'similarity_score': float(score),
            'is_budget_dupe': _is_budget_dupe(query_product, product, score),
            'dupe_score': _compute_dupe_score(query_product, product, score),
        })

    results.sort(key=lambda x: x['dupe_score'], reverse=True)
    return results[:top_n]


def find_cheaper_dupes(
    product_id: int,
    tfidf_matrix,
    product_ids: list,
    products_map: dict,
    similarity_threshold: float = 0.75,
    top_n: int = 5,
):
    """
    Find products that are both highly similar AND cheaper.

    Returns the best budget dupes sorted by dupe_score descending.
    """
    query_product = products_map.get(product_id)
    if not query_product or not query_product.price:
        return []

    candidates = find_top_similar_products(
        product_id, tfidf_matrix, product_ids, products_map,
        top_n=50, min_similarity=similarity_threshold
    )

    dupes = [
        c for c in candidates
        if c['product'].price and c['product'].price < query_product.price
    ]

    dupes.sort(key=lambda x: x['dupe_score'], reverse=True)
    return dupes[:top_n]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_budget_dupe(query_product, candidate_product, similarity_score: float) -> bool:
    from django.conf import settings
    threshold = getattr(settings, 'BUDGET_DUPE_SIMILARITY_THRESHOLD', 0.75)
    return (
        similarity_score >= threshold
        and query_product is not None
        and candidate_product.price is not None
        and query_product.price is not None
        and candidate_product.price < query_product.price
    )


def _compute_dupe_score(query_product, candidate_product, similarity_score: float) -> float:
    """Combined score: 70% similarity + 30% price advantage."""
    if not query_product or not query_product.price or not candidate_product.price:
        return round(similarity_score * 100, 1)
    price_ratio = float(candidate_product.price) / float(query_product.price)
    price_advantage = max(0.0, 1.0 - price_ratio)
    return round((similarity_score * 0.7 + price_advantage * 0.3) * 100, 1)


# ---------------------------------------------------------------------------
# SimilarityEngine: high-level class used by views and management commands
# ---------------------------------------------------------------------------

class SimilarityEngine:
    """
    High-level wrapper around the ML pipeline.
    Handles caching of the TF-IDF matrix to avoid rebuilding on every request.
    """

    def __init__(self):
        self._matrix = None
        self._vectorizer = None
        self._product_ids = None
        self._products_map = None

    def _load(self, force_rebuild: bool = False):
        """Load or rebuild the in-memory feature matrix."""
        if self._matrix is not None and not force_rebuild:
            return

        from apps.products.models import Product
        products = list(Product.objects.all().order_by('id'))
        if not products:
            raise ValueError("No products in database. Run the data loader first.")

        self._matrix, self._vectorizer, self._product_ids = build_feature_matrix(products)
        self._products_map = {p.pk: p for p in products}
        logger.info("SimilarityEngine loaded %d products.", len(products))

    def get_similar(self, product_id: int, top_n: int = 10, skin_type: Optional[str] = None):
        self._load()
        return find_top_similar_products(
            product_id, self._matrix, self._product_ids,
            self._products_map, top_n=top_n, skin_type=skin_type,
        )

    def get_dupes(self, product_id: int, top_n: int = 5):
        self._load()
        return find_cheaper_dupes(
            product_id, self._matrix, self._product_ids,
            self._products_map, top_n=top_n,
        )

    def build_and_cache_all(self):
        """
        Compute all pairwise similarities and persist to SimilarityCache.
        Should be run as a management command or celery task — O(n²) operation.
        """
        from apps.products.models import Product, SimilarityCache
        self._load(force_rebuild=True)

        products = list(Product.objects.all().order_by('id'))
        sim_matrix = compute_similarity(self._matrix)

        created = 0
        for i, pid_a in enumerate(self._product_ids):
            batch = []
            for j, pid_b in enumerate(self._product_ids):
                if i >= j:
                    continue  # only upper triangle, avoid duplicates
                score = float(sim_matrix[i, j])
                if score < 0.3:
                    continue  # skip low-similarity pairs to save space
                batch.append(SimilarityCache(
                    product_a_id=pid_a,
                    product_b_id=pid_b,
                    similarity_score=score,
                ))
                # Mirror: also store (b, a)
                batch.append(SimilarityCache(
                    product_a_id=pid_b,
                    product_b_id=pid_a,
                    similarity_score=score,
                ))
            if batch:
                SimilarityCache.objects.bulk_create(
                    batch,
                    update_conflicts=True,
                    unique_fields=['product_a', 'product_b'],
                    update_fields=['similarity_score'],
                )
                created += len(batch)

        logger.info("Cached %d similarity pairs.", created)
        return created

    def get_tsne_coordinates(self, n_components: int = 2, perplexity: int = 30):
        """
        Reduce the TF-IDF matrix to 2D using t-SNE.
        Returns list of {product_id, x, y, name, brand, price, rank}.
        """
        from sklearn.manifold import TSNE
        self._load()

        # t-SNE works on dense arrays; use truncated SVD first for large datasets
        matrix_dense = self._matrix.toarray()
        n_samples = matrix_dense.shape[0]

        if n_samples < 4:
            return []

        # Adjust perplexity for small datasets
        perplexity = min(perplexity, max(2, n_samples // 3))

        # PCA pre-reduction if high-dimensional to speed up t-SNE
        if matrix_dense.shape[1] > 50:
            from sklearn.decomposition import TruncatedSVD
            svd = TruncatedSVD(n_components=min(50, n_samples - 1))
            matrix_dense = svd.fit_transform(matrix_dense)

        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            random_state=42,
            max_iter=500,
            learning_rate='auto',
            init='pca',
        )
        coords = tsne.fit_transform(matrix_dense)

        results = []
        for i, pid in enumerate(self._product_ids):
            product = self._products_map.get(pid)
            if not product:
                continue
            results.append({
                'id': pid,
                'x': float(coords[i, 0]),
                'y': float(coords[i, 1]),
                'name': product.name,
                'brand': product.brand,
                'price': float(product.price) if product.price else None,
                'rank': float(product.rank) if product.rank else None,
                'category': product.category,
            })

        return results

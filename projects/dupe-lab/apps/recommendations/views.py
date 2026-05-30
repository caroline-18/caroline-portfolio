import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.products.models import Product, SimilarityCache
from .similarity_engine import SimilarityEngine

logger = logging.getLogger(__name__)

# Module-level engine instance (lazy-loaded on first request)
_engine = None

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .embedding_service import embed_profile
from .faiss_index import search
from apps.products.models import Product

@login_required
def personalized_recommendations(request):
    profile = getattr(request.user, 'skin_profile', None)
    if not profile:
        return render(request, 'recommendations/no_profile.html')

    query_vec = embed_profile(profile)
    results   = search(query_vec, k=12)

    product_ids = [pid for pid, _ in results]
    score_map   = {pid: round(score * 100, 1) for pid, score in results}
    products    = Product.objects.filter(id__in=product_ids)
    products    = sorted(products, key=lambda p: -score_map[p.id])

    return render(request, 'recommendations/personalized.html', {
        'products': products,
        'score_map': score_map,
        'profile':  profile,
    })


def get_engine() -> SimilarityEngine:
    global _engine
    if _engine is None:
        _engine = SimilarityEngine()
    return _engine


def dupe_finder(request, slug):
    """
    Dupe Finder Results page.
    Displays similar products and budget dupes for a given product.
    """
    product = get_object_or_404(Product, slug=slug)
    skin_type = request.GET.get('skin_type', '')

    try:
        engine = get_engine()
        similar = engine.get_similar(product.pk, top_n=12, skin_type=skin_type or None)
        dupes = engine.get_dupes(product.pk, top_n=5)
    except Exception as e:
        logger.warning("Similarity engine error: %s", e)
        # Fall back to cached DB results
        similar_cache = (
            SimilarityCache.objects
            .filter(product_a=product)
            .select_related('product_b')
            .order_by('-similarity_score')[:12]
        )
        similar = [
            {
                'product': sc.product_b,
                'similarity_score': sc.similarity_score,
                'is_budget_dupe': sc.is_budget_dupe,
                'dupe_score': sc.dupe_score,
            }
            for sc in similar_cache
        ]
        dupes = [s for s in similar if s['is_budget_dupe']]

    return render(request, 'recommendations/dupe_finder.html', {
        'product': product,
        'similar': similar,
        'dupes': dupes,
        'skin_type': skin_type,
    })


@api_view(['GET'])
def api_get_similar_products(request):
    """
    REST API: return similar products for a given product ID.

    Query params:
      product_id  (required)
      top_n       (default 10)
      skin_type   (optional: dry, oily, normal, combination, sensitive)
    """
    product_id = request.GET.get('product_id')
    if not product_id:
        return Response({'error': 'product_id is required'}, status=400)

    try:
        product_id = int(product_id)
    except ValueError:
        return Response({'error': 'product_id must be an integer'}, status=400)

    product = get_object_or_404(Product, pk=product_id)
    top_n = int(request.GET.get('top_n', 10))
    skin_type = request.GET.get('skin_type', '') or None

    try:
        engine = get_engine()
        results = engine.get_similar(product_id, top_n=top_n, skin_type=skin_type)
    except Exception as e:
        logger.error("Similarity computation failed: %s", e)
        return Response({'error': 'Similarity computation failed', 'detail': str(e)}, status=500)

    return Response({
        'product': {'id': product.pk, 'name': product.name, 'brand': product.brand},
        'similar': [
            {
                'id': r['product'].pk,
                'name': r['product'].name,
                'brand': r['product'].brand,
                'price': float(r['product'].price) if r['product'].price else None,
                'rank': float(r['product'].rank) if r['product'].rank else None,
                'slug': r['product'].slug,
                'similarity_score': round(r['similarity_score'] * 100, 1),
                'dupe_score': r['dupe_score'],
                'is_budget_dupe': r['is_budget_dupe'],
            }
            for r in results
        ]
    })


@api_view(['GET'])
def api_get_cheaper_dupes(request):
    """
    REST API: return budget dupes (similar + cheaper) for a product.

    Query params:
      product_id  (required)
    """
    product_id = request.GET.get('product_id')
    if not product_id:
        return Response({'error': 'product_id is required'}, status=400)

    try:
        product_id = int(product_id)
    except ValueError:
        return Response({'error': 'product_id must be an integer'}, status=400)

    product = get_object_or_404(Product, pk=product_id)

    try:
        engine = get_engine()
        dupes = engine.get_dupes(product_id, top_n=5)
    except Exception as e:
        logger.error("Dupe computation failed: %s", e)
        return Response({'error': 'Dupe computation failed', 'detail': str(e)}, status=500)

    return Response({
        'product': {
            'id': product.pk,
            'name': product.name,
            'brand': product.brand,
            'price': float(product.price) if product.price else None,
        },
        'dupes': [
            {
                'id': r['product'].pk,
                'name': r['product'].name,
                'brand': r['product'].brand,
                'price': float(r['product'].price) if r['product'].price else None,
                'similarity_score': round(r['similarity_score'] * 100, 1),
                'dupe_score': r['dupe_score'],
                'savings': (
                    round(float(product.price) - float(r['product'].price), 2)
                    if product.price and r['product'].price else None
                ),
            }
            for r in dupes
        ]
    })

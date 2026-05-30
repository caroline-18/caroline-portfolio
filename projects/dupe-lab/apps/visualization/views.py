import json
import logging
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.recommendations.similarity_engine import SimilarityEngine

logger = logging.getLogger(__name__)
_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = SimilarityEngine()
    return _engine


def ingredient_map(request):
    """t-SNE ingredient similarity map page."""
    return render(request, 'visualization/ingredient_map.html')


@api_view(['GET'])
def api_ingredient_map_data(request):
    """
    REST API: return t-SNE 2D coordinates for all products.
    Used by Chart.js scatter plot on the map page.
    """
    try:
        engine = get_engine()
        data = engine.get_tsne_coordinates()
        return Response({'points': data, 'count': len(data)})
    except Exception as e:
        logger.error("t-SNE computation failed: %s", e)
        return Response({'error': str(e), 'points': []}, status=500)

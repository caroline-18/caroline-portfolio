import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Ingredient
from .safety import analyze_custom_ingredient_list, check_ingredient_safety


def ingredient_explorer(request):
    """Browse all ingredients with filtering."""
    category = request.GET.get('category', '')
    risk = request.GET.get('risk', '')
    q = request.GET.get('q', '').strip()

    ingredients = Ingredient.objects.all()

    if category:
        ingredients = ingredients.filter(category=category)
    if risk:
        ingredients = ingredients.filter(risk_level=risk)
    if q:
        ingredients = ingredients.filter(name__icontains=q)

    return render(request, 'ingredients/explorer.html', {
        'ingredients': ingredients[:100],
        'categories': Ingredient.CATEGORY_CHOICES,
        'risk_levels': Ingredient.RISK_CHOICES,
        'query': q,
        'selected_category': category,
        'selected_risk': risk,
    })


def ingredient_detail(request, name):
    """Detail page for a single ingredient."""
    ingredient = get_object_or_404(Ingredient, name__iexact=name)

    # Find products containing this ingredient
    from apps.products.models import Product
    products_with = Product.objects.filter(
        ingredients__icontains=ingredient.name
    ).order_by('-rank')[:10]

    return render(request, 'ingredients/detail.html', {
        'ingredient': ingredient,
        'products_with': products_with,
    })


def safety_checker(request):
    """Ingredient safety checker tool page."""
    result = None
    if request.method == 'POST':
        raw_text = request.POST.get('ingredients', '').strip()
        if raw_text:
            result = analyze_custom_ingredient_list(raw_text)

    return render(request, 'ingredients/safety_checker.html', {'result': result})


@api_view(['GET'])
def api_ingredient_info(request):
    """REST API: get ingredient info by name."""
    name = request.GET.get('name', '').strip()
    if not name:
        return Response({'error': 'name parameter required'}, status=400)

    try:
        ingredient = Ingredient.objects.get(name__iexact=name)
        return Response({
            'name': ingredient.name,
            'description': ingredient.description,
            'benefits': ingredient.benefits,
            'side_effects': ingredient.side_effects,
            'category': ingredient.category,
            'risk_level': ingredient.risk_level,
            'flags': ingredient.get_flags(),
        })
    except Ingredient.DoesNotExist:
        # Return basic info if not in DB
        return Response({
            'name': name,
            'description': 'No detailed information available for this ingredient.',
            'risk_level': 'safe',
            'flags': [],
        })


@api_view(['POST'])
def api_safety_check(request):
    """REST API: safety check on a list of ingredients."""
    ingredients_raw = request.data.get('ingredients', '')
    if isinstance(ingredients_raw, list):
        ingredients = ingredients_raw
    else:
        result = analyze_custom_ingredient_list(str(ingredients_raw))
        return Response(result)

    safety = check_ingredient_safety(ingredients)
    return Response({'ingredients': ingredients, 'safety': safety})

from .conflict_checker import check_ingredients_for_conflicts

def conflict_checker(request):
    results  = []
    products = []
    query    = ''

    if request.method == 'POST':
        query = request.POST.get('ingredients', '')
        results = check_ingredients_for_conflicts(query)

    return render(request, 'ingredients/conflict_checker.html', {
        'results': results,
        'query':   query,
    })

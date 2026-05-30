import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.ingredients.safety import check_ingredient_safety
from .models import Product, SimilarityCache
from .serializers import ProductSerializer, ProductDetailSerializer
from .price_fetcher import get_best_price, fetch_prices_for_product, save_prices_to_history


def home(request):
    featured = Product.objects.filter(rank__gte=4.0).order_by('-rank')[:8]
    categories = Product.objects.values_list('category', flat=True).distinct()
    total_products = Product.objects.count()
    return render(request, 'products/home.html', {
        'featured': featured,
        'categories': categories,
        'total_products': total_products,
    })


def resolve_price_url(request, product_id):
    from .price_fetcher import resolve_real_url
    from django.shortcuts import redirect
    url = request.GET.get('url', '')
    if not url:
        return JsonResponse({'error': 'No URL provided'}, status=400)
    final_url = resolve_real_url(url)
    return redirect(final_url)


def product_list(request):
    query        = request.GET.get('q', '').strip()
    category     = request.GET.get('category', '')
    skin_type    = request.GET.get('skin_type', '')
    min_price    = request.GET.get('min_price', '').strip()
    max_price    = request.GET.get('max_price', '').strip()
    made_in_india = request.GET.get('made_in_india', '')
    is_ayurvedic = request.GET.get('is_ayurvedic', '')
    sort         = request.GET.get('sort', '')

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(ingredients__icontains=query)
        )
    if category:
        products = products.filter(category=category)
    if skin_type:
        products = products.filter(**{f'skin_{skin_type}': True})
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            val = float(max_price)
            if val < 5000:
                products = products.filter(price__lte=val)
        except ValueError:
            pass
    if made_in_india:
        products = products.filter(made_in_india=True)
    if is_ayurvedic:
        products = products.filter(is_ayurvedic=True)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rank':
        products = products.order_by('-rank')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        serializer = ProductSerializer(products[:20], many=True)
        return JsonResponse({'products': serializer.data, 'count': products.count()})

    return render(request, 'products/product_list.html', {
        'products': products[:60],
        'query': query,
        'category': category,
        'skin_type': skin_type,
        'min_price': min_price,
        'max_price': max_price,
        'made_in_india': made_in_india,
        'is_ayurvedic': is_ayurvedic,
        'sort': sort,
        'categories': Product.CATEGORY_CHOICES,
        'total': products.count(),
    })


def product_detail(request, slug):
    """Full product detail page with dupe recommendations and reviews."""
    product = get_object_or_404(Product, slug=slug)

    # ── Handle review submission ──────────────────────────────
    review_submitted = False
    review_error     = None

    if request.method == 'POST':
        from apps.reviews.models import ProductReview
        body   = request.POST.get('body', '').strip()
        author = request.POST.get('author', '').strip() or 'Anonymous'
        rating = request.POST.get('rating', '').strip()

        if len(body) < 10:
            review_error = 'Review must be at least 10 characters.'
        else:
            try:
                rating_val = int(rating) if rating else None
                if rating_val and not (1 <= rating_val <= 5):
                    rating_val = None
            except ValueError:
                rating_val = None

            ProductReview.objects.create(
                product=product,
                author=author,
                body=body,
                rating=rating_val,
                source='manual',
            )
            review_submitted = True

    # ── Price & ingredients ───────────────────────────────────
    best_price    = get_best_price(product)
    price_history = product.price_history.order_by('fetched_at')[:30]
    ingredients   = product.get_ingredient_list()

    # ── Similar products ──────────────────────────────────────
    similar_cache = (
        SimilarityCache.objects
        .filter(product_a=product, similarity_score__gte=0.3)
        .select_related('product_b')
        .order_by('-similarity_score')[:10]
    )

    budget_dupes = []
    for sc in similar_cache:
        if (sc.product_b.price
                and product.price
                and sc.product_b.price < product.price
                and sc.similarity_score >= 0.5):
            budget_dupes.append({
                'product': sc.product_b,
                'score':   sc.similarity_score,
                'saving':  round(product.price - sc.product_b.price, 0),
            })

    safety_flags = check_ingredient_safety(ingredients)

    # ── Reviews ───────────────────────────────────────────────
    from apps.reviews.models import ProductReview, ProductReviewAggregate

    reviews = (
        ProductReview.objects
        .filter(product=product)
        .order_by('-created_at')[:20]
    )

    try:
        review_aggregate = product.review_aggregate
    except ProductReviewAggregate.DoesNotExist:
        review_aggregate = None

    return render(request, 'products/product_detail.html', {
        'product':          product,
        'best_price':       best_price,
        'price_history':    price_history,
        'ingredients':      ingredients,
        'similar_products': similar_cache,
        'budget_dupes':     budget_dupes,
        'safety_flags':     safety_flags,
        'reviews':          reviews,
        'review_aggregate': review_aggregate,
        'review_submitted': review_submitted,
        'review_error':     review_error,
    })


@require_GET
def search_autocomplete(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(brand__icontains=q)
    ).values('id', 'name', 'brand', 'price', 'slug')[:8]
    return JsonResponse({'results': list(products)})


@api_view(['GET'])
def api_search_product(request):
    q         = request.GET.get('q', '').strip()
    category  = request.GET.get('category', '')
    skin_type = request.GET.get('skin_type', '')
    products  = Product.objects.all()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(brand__icontains=q))
    if category:
        products = products.filter(category=category)
    if skin_type:
        products = products.filter(**{f'skin_{skin_type}': True})
    serializer = ProductSerializer(products[:20], many=True)
    return Response({'count': products.count(), 'results': serializer.data})


@api_view(['GET'])
def api_product_detail(request, pk):
    product    = get_object_or_404(Product, pk=pk)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)


from django.http import JsonResponse

def refresh_price(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    product = get_object_or_404(Product, id=product_id)
    results = fetch_prices_for_product(product)
    if results:
        save_prices_to_history(product, results)
        cheapest = min(results, key=lambda x: x['price'])
        return JsonResponse({
            'success':  True,
            'price':    cheapest['price'],
            'retailer': cheapest['retailer'],
            'url':      cheapest['url'],
            'count':    len(results),
        })
    return JsonResponse({'success': False, 'message': 'No prices found'})
import requests
from requests.exceptions import RequestException
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import re

SERPER_URL = "https://google.serper.dev/shopping"

RETAILERS = {
    'nykaa':         'Nykaa',
    'myntra':        'Myntra',
    'amazon':        'Amazon',
    'flipkart':      'Flipkart',
    'purplle':       'Purplle',
    'sephora':       'Sephora',
    'shoppersstop':  'Shoppers Stop',
    'shoppers stop': 'Shoppers Stop',
    'tira':          'Tira',
    'bigbasket':     'BigBasket',
    'blinkit':       'Blinkit',
    'meesho':        'Meesho',
}


def identify_retailer(source: str, url: str) -> str:
    """
    Identify retailer from Serper's source field first (most reliable),
    then fall back to URL matching.
    """
    source_lower = source.lower()
    for key, name in RETAILERS.items():
        if key in source_lower:
            return name

    url_lower = url.lower()
    for key, name in RETAILERS.items():
        if key in url_lower:
            return name

    # Return source name directly — better than 'other'
    return source if source else 'other'


def resolve_real_url(google_url: str) -> str:
    """Follow Google Shopping redirect to get the actual retailer URL."""
    if 'google.com' not in google_url:
        return google_url
    try:
        response = requests.get(
            google_url,
            allow_redirects=True,
            timeout=5,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/120.0.0.0 Safari/537.36'
            }
        )
        final_url = response.url
        if 'google.com' in final_url:
            return google_url
        return final_url
    except RequestException:
        return google_url


def is_relevant(title: str, product_keywords: set, brand: str, source: str = '') -> bool:
    if not product_keywords:
        return True
    title_lower  = title.lower()
    source_lower = source.lower()
    brand_lower  = brand.lower()

    # Check if brand appears in title or source
    brand_found = brand_lower in title_lower or brand_lower in source_lower

    # Count keyword matches
    matches   = sum(1 for kw in product_keywords if kw in title_lower)
    threshold = max(2, len(product_keywords) * 2 // 3)

    if brand_found and matches >= 1:
        return True
    if not brand_found and matches >= threshold:
        return True

    return False


def extract_price(price_str: str) -> float | None:
    """Extract numeric price from strings like '₹299', 'Rs. 499', '1,299.00'"""
    if not price_str:
        return None
    cleaned = re.sub(r'[^\d.]', '', price_str.replace(',', ''))
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_prices_for_product(product) -> list[dict]:
    """
    Search Google Shopping via Serper API for real-time prices.
    Returns list of {retailer, price, url, title, in_stock}
    """
    api_key = settings.SERPER_API_KEY
    if not api_key:
        return []

    query = f"{product.brand} {product.name}"

    try:
        response = requests.post(
            SERPER_URL,
            headers={
                'X-API-KEY':    api_key,
                'Content-Type': 'application/json',
            },
            json={
                'q':   query,
                'gl':  'in',
                'hl':  'en',
                'num': 10,
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Serper API error for {product.name}: {e}")
        return []

    results = []
    shopping_results = data.get('shopping', [])

    product_keywords = set(product.name.lower().split())
    stopwords = {'and', 'the', 'for', 'with', 'of', 'in', 'a', 'an', '&'}
    product_keywords -= stopwords

    for item in shopping_results:
        title     = item.get('title', '')
        link      = item.get('link', '')
        price_str = item.get('price', '')
        source    = item.get('source', '')

        if not is_relevant(title, product_keywords, product.brand, source):
            continue

        price = extract_price(price_str)
        if not price:
            continue

        retailer = identify_retailer(source, link)

        results.append({
            'retailer': retailer,
            'price':    price,
            'url':      link,   # keep Google URL — resolved lazily on click
            'title':    title,
            'in_stock': True,
        })

    return results


def save_prices_to_history(product, price_results: list[dict]):
    """Save fetched prices to PriceHistory model."""
    from .models import PriceHistory

    saved = []
    for result in price_results:
        if not result['price']:
            continue
        ph = PriceHistory.objects.create(
            product  = product,
            retailer = result['retailer'],
            price    = Decimal(str(result['price'])),
            url      = result['url'],
            in_stock = result['in_stock'],
        )
        saved.append(ph)
    return saved


def get_best_price(product) -> dict | None:
    """
    Get the cheapest current price for a product.
    Checks price history first, fetches fresh if older than 24 hours.
    """
    from .models import PriceHistory
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=24)
    recent = product.price_history.filter(fetched_at__gte=cutoff).order_by('price').first()

    if recent:
        return {
            'price':    float(recent.price),
            'retailer': recent.retailer,
            'url':      recent.url,
            'fresh':    True,
        }

    results = fetch_prices_for_product(product)
    if results:
        save_prices_to_history(product, results)
        cheapest = min(results, key=lambda x: x['price'])
        return {
            'price':    cheapest['price'],
            'retailer': cheapest['retailer'],
            'url':      cheapest['url'],
            'fresh':    False,
        }

    return None


def refresh_all_prices(limit: int = 100):
    """
    Refresh prices for products with stale or missing price data.
    Called by daily scheduled task.
    """
    from .models import Product
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=24)

    stale_products = Product.objects.exclude(
        price_history__fetched_at__gte=cutoff
    ).order_by('?')[:limit]

    updated = 0
    for product in stale_products:
        results = fetch_prices_for_product(product)
        if results:
            save_prices_to_history(product, results)
            updated += 1
            print(f"Updated prices for: {product.name}")

    return updated
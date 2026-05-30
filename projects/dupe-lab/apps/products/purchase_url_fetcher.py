import re
import requests
from urllib.parse import quote_plus

STORE_DOMAINS = [
    ("nykaa.com",       "Nykaa"),
    ("amazon.in",       "Amazon India"),
    ("flipkart.com",    "Flipkart"),
    ("purplle.com",     "Purplle"),
    ("myntra.com",      "Myntra"),
    ("tatacliq.com",    "Tata CLiQ"),
    ("healthkart.com",  "HealthKart"),
]


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


def _build_search_urls(brand: str, name: str) -> dict:
    """
    Build direct search URLs for each store.
    These are search pages — guaranteed to work without scraping.
    """
    query = quote_plus(f"{brand} {name}")
    slug = _slugify(f"{brand} {name}")

    return {
        "nykaa.com": {
            "store": "Nykaa",
            "url": f"https://www.nykaa.com/search/result/?q={query}&root=search"
        },
        "amazon.in": {
            "store": "Amazon India",
            "url": f"https://www.amazon.in/s?k={query}&i=beauty"
        },
        "flipkart.com": {
            "store": "Flipkart",
            "url": f"https://www.flipkart.com/search?q={query}&otracker=search"
        },
        "purplle.com": {
            "store": "Purplle",
            "url": f"https://www.purplle.com/search?q={query}"
        },
        "myntra.com": {
            "store": "Myntra",
            "url": f"https://www.myntra.com/{slug}"
        },
        "tatacliq.com": {
            "store": "Tata CLiQ",
            "url": f"https://www.tatacliq.com/search/?searchCategory=all&text={query}"
        },
        "healthkart.com": {
            "store": "HealthKart",
            "url": f"https://www.healthkart.com/search?q={query}"
        },
    }


def fetch_purchase_url(brand: str, product_name: str) -> dict:
    """
    Build direct search page URLs for each store.
    No scraping, no API — always works.
    When user clicks Buy Now they land on the search results
    for that exact product on each store.
    """
    store_urls = _build_search_urls(brand, product_name)

    all_found = [
        {"store": v["store"], "url": v["url"]}
        for v in store_urls.values()
    ]

    # Best = Nykaa first (most reliable for Indian skincare)
    best = all_found[0]

    return {
        "success": True,
        "url": best["url"],
        "store": best["store"],
        "all_found": all_found,
    }
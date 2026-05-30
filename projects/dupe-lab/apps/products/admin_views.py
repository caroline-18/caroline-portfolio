import json
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from .models import Product
from .purchase_url_fetcher import fetch_purchase_url


@staff_member_required
@require_POST
def fetch_purchase_url_view(request):
    """
    AJAX endpoint called by the admin Fetch URL button.
    POST body: { "product_id": 123 }
    """
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        product = Product.objects.get(pk=product_id)
    except (Product.DoesNotExist, KeyError, json.JSONDecodeError):
        return JsonResponse({"success": False, "error": "Product not found."}, status=400)

    result = fetch_purchase_url(product.brand, product.name)

    if result["success"]:
        # Auto-save the best URL
        product.purchase_url = result["url"]
        product.save(update_fields=["purchase_url"])

    return JsonResponse(result)
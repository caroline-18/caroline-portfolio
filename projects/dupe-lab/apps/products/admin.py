from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Product, SimilarityCache


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'brand', 'name', 'category', 'price', 'rank',
        'ingredient_count_display', 'skin_types_display',
        'purchase_link_display',
    ]
    list_filter = ['category', 'skin_dry', 'skin_oily', 'skin_normal',
                   'skin_combination', 'skin_sensitive']
    search_fields = ['brand', 'name', 'ingredients']

    # ✅ Add fetch_url_button to readonly_fields so it renders in the form
    readonly_fields = ['slug', 'created_at', 'updated_at', 'fetch_url_button']

    fieldsets = (
        ('Product Info', {
            'fields': ('brand', 'name', 'slug', 'category', 'price', 'rank', 'image_url')
        }),
        ('Purchase Link', {
            'fields': ('purchase_url', 'fetch_url_button'),
            'description': 'Add manually or click Fetch to auto-find across stores.'
        }),
        ('Ingredients', {
            'fields': ('ingredients',),
            'description': 'Enter ingredients as comma-separated values'
        }),
        ('Skin Type Compatibility', {
            'fields': ('skin_dry', 'skin_oily', 'skin_normal',
                       'skin_combination', 'skin_sensitive'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('made_in_india', 'is_ayurvedic', 'currency',
                       'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def fetch_url_button(self, obj):
        if not obj.pk:
            return "Save the product first, then fetch URL."
        return format_html(
            '''
            <button type="button" id="fetch-url-btn"
                onclick="fetchPurchaseUrl({})"
                style="background:#16a34a;color:white;border:none;padding:8px 16px;
                       border-radius:6px;cursor:pointer;font-size:13px;font-weight:600;">
                🔍 Fetch Purchase URL
            </button>
            <span id="fetch-status" style="margin-left:12px;font-size:13px;"></span>

            <div id="fetch-results" style="display:none;margin-top:10px;"></div>

            <script>
            function fetchPurchaseUrl(productId) {{
                const btn = document.getElementById('fetch-url-btn');
                const status = document.getElementById('fetch-status');
                const results = document.getElementById('fetch-results');

                btn.disabled = true;
                btn.textContent = '⏳ Searching...';
                status.textContent = '';
                results.style.display = 'none';

                fetch('/api/fetch-purchase-url/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
                    }},
                    body: JSON.stringify({{ product_id: productId }})
                }})
                .then(r => r.json())
                .then(data => {{
                    btn.disabled = false;
                    btn.textContent = '🔍 Fetch Purchase URL';

                    if (data.success) {{
                        // Fill the purchase_url field
                        const urlField = document.getElementById('id_purchase_url');
                        if (urlField) urlField.value = data.url;

                        status.style.color = '#16a34a';
                        status.textContent = '✓ Found on ' + data.store + ' — save to confirm.';

                        // Show all found stores
                        if (data.all_found && data.all_found.length > 1) {{
                            let html = '<strong style="font-size:12px;">Also found on:</strong><br>';
                            data.all_found.forEach(function(item) {{
                                html += '<a href="' + item.url + '" target="_blank" '
                                    + 'style="font-size:12px;margin-right:10px;color:#2563eb;'
                                    + 'background:#f0f7ff;padding:3px 8px;border-radius:4px;'
                                    + 'text-decoration:none;display:inline-block;margin-bottom:4px;">'
                                    + item.store + '</a> ';
                            }});
                            results.innerHTML = html;
                            results.style.display = 'block';
                        }}
                    }} else {{
                        status.style.color = '#dc2626';
                        status.textContent = '✗ ' + (data.error || 'Not found.');
                    }}
                }})
                .catch(function(err) {{
                    btn.disabled = false;
                    btn.textContent = '🔍 Fetch Purchase URL';
                    status.style.color = '#dc2626';
                    status.textContent = '✗ Network error.';
                }});
            }}
            </script>
            ''',
            obj.pk
        )
    fetch_url_button.short_description = "Auto-fetch"

    def ingredient_count_display(self, obj):
        count = obj.ingredient_count
        color = '#22c55e' if count > 10 else '#f59e0b' if count > 5 else '#ef4444'
        return format_html('<span style="color:{}">{} ingredients</span>', color, count)
    ingredient_count_display.short_description = 'Ingredients'

    def skin_types_display(self, obj):
        types = obj.get_skin_types()
        if not types:
            return format_html('<span style="color:#9ca3af">—</span>')
        return ', '.join(types)
    skin_types_display.short_description = 'Skin Types'

    def purchase_link_display(self, obj):
        if obj.purchase_url:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer" '
                'style="color:#22c55e;font-weight:600;">🛒 Buy Link</a>',
                obj.purchase_url
            )
        return format_html('<span style="color:#9ca3af">—</span>')
    purchase_link_display.short_description = 'Purchase Link'

    actions = ['rebuild_similarity_cache', 'fetch_purchase_urls_for_selected']

    def rebuild_similarity_cache(self, request, queryset):
        from apps.recommendations.similarity_engine import SimilarityEngine
        engine = SimilarityEngine()
        engine.build_and_cache_all()
        self.message_user(request, "Similarity cache rebuilt successfully.")
    rebuild_similarity_cache.short_description = "Rebuild similarity cache for selected products"

    def fetch_purchase_urls_for_selected(self, request, queryset):
        from .purchase_url_fetcher import fetch_purchase_url
        updated = 0
        skipped = 0
        failed = 0

        for product in queryset:
            # Skip products that already have a URL
            if product.purchase_url:
                skipped += 1
                continue
            try:
                result = fetch_purchase_url(product.brand, product.name)
                if result["success"]:
                    product.purchase_url = result["url"]
                    product.save(update_fields=["purchase_url"])
                    updated += 1
                else:
                    failed += 1
            except Exception:
                failed += 1

        self.message_user(
            request,
            f"✓ {updated} products updated, "
            f"{skipped} already had URLs (skipped), "
            f"{failed} failed."
        )
    fetch_purchase_urls_for_selected.short_description = "🛒 Fetch purchase URLs for selected products"



@admin.register(SimilarityCache)
class SimilarityCacheAdmin(admin.ModelAdmin):
    list_display = ['product_a', 'product_b', 'similarity_score', 'is_budget_dupe', 'computed_at']
    list_filter = ['computed_at']
    search_fields = ['product_a__name', 'product_b__name']
    readonly_fields = ['computed_at']
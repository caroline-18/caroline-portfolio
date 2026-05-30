from django.urls import path
from . import admin_views
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='list'),
    path('products/<slug:slug>/', views.product_detail, name='detail'),
    path('search/autocomplete/', views.search_autocomplete, name='autocomplete'),
    path('products/refresh-price/<int:product_id>/', views.refresh_price, name='refresh_price'),
    path('products/resolve-url/<int:product_id>/', views.resolve_price_url, name='resolve_url'),
    # REST API
    path('api/search-product/', views.api_search_product, name='api_search'),
    path('api/products/<int:pk>/', views.api_product_detail, name='api_detail'),
    path(
        "api/fetch-purchase-url/",
        admin_views.fetch_purchase_url_view,
        name="fetch_purchase_url"
    ),
]

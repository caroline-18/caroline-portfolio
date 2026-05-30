from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.ingredients.views import api_ingredient_info, api_safety_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.products.urls')),
    path('ingredients/', include('apps.ingredients.urls')),
    path('recommendations/', include('apps.recommendations.urls')),
    path('visualization/', include('apps.visualization.urls')),
    path('profiles/', include('apps.profiles.urls')),
    path('routines/', include('apps.routines.urls')),
    path('analytics/', include('apps.analytics.urls')),
    # Root-level API shortcuts (used by product detail JS modal)
    path('api/ingredient-info/', api_ingredient_info, name='api_ingredient_info'),
    path('api/safety-check/', api_safety_check, name='api_safety_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

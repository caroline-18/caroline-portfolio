from django.urls import path
from . import views

app_name = 'visualization'

urlpatterns = [
    path('map/', views.ingredient_map, name='map'),
    path('api/ingredient-map-data/', views.api_ingredient_map_data, name='api_map_data'),
]

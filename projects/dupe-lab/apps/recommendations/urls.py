from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('dupes/<slug:slug>/', views.dupe_finder, name='dupe_finder'),
    path('personalized/', views.personalized_recommendations, name='personalized'),
    # REST API
    path('api/get-similar-products/', views.api_get_similar_products, name='api_similar'),
    path('api/get-cheaper-dupes/', views.api_get_cheaper_dupes, name='api_dupes'),
]

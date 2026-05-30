from django.urls import path
from . import views

app_name = 'ingredients'

urlpatterns = [
    path('', views.ingredient_explorer, name='explorer'),
    path('safety-checker/', views.safety_checker, name='safety_checker'),
    path('conflict-checker/', views.conflict_checker, name='conflict_checker'),
    path('api/ingredient-info/', views.api_ingredient_info, name='api_info'),
    path('api/safety-check/', views.api_safety_check, name='api_safety'),
    path('<str:name>/', views.ingredient_detail, name='detail'),
]
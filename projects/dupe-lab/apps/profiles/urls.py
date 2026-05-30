from django.urls import path
from . import views

urlpatterns = [
    path('quiz/',   views.quiz_view,      name='quiz'),
    path('result/', views.profile_result, name='profile_result'),
    path('me/',     views.profile_detail, name='profile_detail'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('build/',                views.build_routine,  name='build_routine'),
    path('mine/',                 views.my_routines,    name='my_routines'),
    path('delete/<int:routine_id>/', views.delete_routine, name='delete_routine'),
]
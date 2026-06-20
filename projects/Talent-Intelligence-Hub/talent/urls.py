from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/", views.jobs, name="jobs"),
    path("jobs/<str:job_id>/", views.job_detail, name="job_detail"),
    path("skills/", views.skills, name="skills"),
    path("companies/", views.companies, name="companies"),
    path("cities/", views.cities, name="cities"),
    path("companies/<path:company_name>/",views.company_detail,name="company_detail"),
    path("cities/<str:city_name>/",views.city_detail,name="city_detail"),
    path("skills/<str:skill_name>/",views.skill_detail,name="skill_detail"),
]
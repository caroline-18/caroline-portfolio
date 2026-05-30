from django.contrib import admin
from .models import SkinProfile, SkinConcern

@admin.register(SkinProfile)
class SkinProfileAdmin(admin.ModelAdmin):
    list_display      = ['user', 'skin_type', 'climate', 'age_range', 'created_at']
    list_filter       = ['skin_type', 'climate']
    filter_horizontal = ['concerns']

@admin.register(SkinConcern)
class SkinConcernAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
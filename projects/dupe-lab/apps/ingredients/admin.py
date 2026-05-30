from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'risk_level', 'is_fragrance', 'is_paraben', 'is_sulfate']
    list_filter = ['category', 'risk_level', 'is_fragrance', 'is_alcohol', 'is_paraben', 'is_sulfate']
    search_fields = ['name', 'inci_name', 'description']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'inci_name', 'category', 'risk_level')
        }),
        ('Details', {
            'fields': ('description', 'benefits', 'side_effects')
        }),
        ('Safety Flags', {
            'fields': ('is_fragrance', 'is_alcohol', 'is_paraben', 'is_sulfate', 'is_silicone'),
            'classes': ('collapse',)
        }),
        ('Skin Suitability', {
            'fields': ('good_for_dry', 'good_for_oily', 'good_for_sensitive'),
            'classes': ('collapse',)
        }),
    )


from .models import IngredientConflict

@admin.register(IngredientConflict)
class IngredientConflictAdmin(admin.ModelAdmin):
    list_display = ['ingredient_a', 'ingredient_b', 'severity']

from django.contrib import admin
from .models import ProductReview, ProductReviewAggregate


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display  = ('product', 'author', 'rating', 'sentiment_label',
                     'sentiment_score', 'analysed', 'created_at')
    list_filter   = ('sentiment_label', 'analysed', 'source')
    search_fields = ('product__name', 'author', 'body')
    readonly_fields = ('sentiment_label', 'sentiment_score', 'analysed',
                       'aspect_hydration', 'aspect_texture', 'aspect_scent',
                       'aspect_irritation', 'aspect_efficacy')

    actions = ['reanalyse_selected']

    def reanalyse_selected(self, request, queryset):
        queryset.update(analysed=False)
        # Re-save each to trigger the signal
        for review in queryset:
            review.save()
        self.message_user(request, f"Queued {queryset.count()} reviews for re-analysis.")
    reanalyse_selected.short_description = "Re-analyse sentiment for selected reviews"


@admin.register(ProductReviewAggregate)
class ProductReviewAggregateAdmin(admin.ModelAdmin):
    list_display = ('product', 'total_reviews', 'avg_rating',
                    'positive_pct', 'negative_pct', 'last_updated')
    readonly_fields = [f.name for f in ProductReviewAggregate._meta.fields]
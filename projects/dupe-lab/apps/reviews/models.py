from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.products.models import Product


class ProductReview(models.Model):
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author      = models.CharField(max_length=120, blank=True, default='Anonymous')
    body        = models.TextField()
    rating      = models.PositiveSmallIntegerField(
                      validators=[MinValueValidator(1), MaxValueValidator(5)],
                      null=True, blank=True)
    source      = models.CharField(max_length=60, blank=True,
                      help_text="e.g. nykaa, purplle, manual")
    created_at  = models.DateTimeField(auto_now_add=True)

    # ── Sentiment ──────────────────────────────────────────────
    sentiment_label = models.CharField(
                          max_length=20, blank=True,
                          choices=[('positive','Positive'),
                                   ('neutral', 'Neutral'),
                                   ('negative','Negative')])
    sentiment_score = models.FloatField(null=True, blank=True,
                          help_text="Confidence 0–1 for the predicted label")
    analysed        = models.BooleanField(default=False)

    # ── Aspect scores (0.0–1.0, null = not mentioned) ──────────
    aspect_hydration  = models.FloatField(null=True, blank=True)
    aspect_texture    = models.FloatField(null=True, blank=True)
    aspect_scent      = models.FloatField(null=True, blank=True)
    aspect_irritation = models.FloatField(null=True, blank=True)
    aspect_efficacy   = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} — {self.sentiment_label or 'unanalysed'}"


class ProductReviewAggregate(models.Model):
    """Cached aggregate sentiment stats per product. Rebuilt on demand."""
    product             = models.OneToOneField(Product, on_delete=models.CASCADE,
                              related_name='review_aggregate')
    total_reviews       = models.PositiveIntegerField(default=0)
    avg_rating          = models.FloatField(null=True, blank=True)
    positive_pct        = models.FloatField(null=True, blank=True)
    neutral_pct         = models.FloatField(null=True, blank=True)
    negative_pct        = models.FloatField(null=True, blank=True)
    avg_hydration       = models.FloatField(null=True, blank=True)
    avg_texture         = models.FloatField(null=True, blank=True)
    avg_scent           = models.FloatField(null=True, blank=True)
    avg_irritation      = models.FloatField(null=True, blank=True)
    avg_efficacy        = models.FloatField(null=True, blank=True)
    last_updated        = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Aggregate — {self.product.name}"
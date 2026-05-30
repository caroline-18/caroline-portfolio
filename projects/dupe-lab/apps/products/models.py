from django.db import models
from django.utils.text import slugify


class Product(models.Model):
    """
    Represents a skincare product with full ingredient and metadata profile.
    This is the core model — all similarity and dupe logic references this.
    """
    CATEGORY_CHOICES = [
        ('moisturizer', 'Moisturizer'),
        ('serum', 'Serum'),
        ('cleanser', 'Cleanser'),
        ('toner', 'Toner'),
        ('sunscreen', 'Sunscreen'),
        ('mask', 'Mask'),
        ('eye_cream', 'Eye Cream'),
        ('exfoliator', 'Exfoliator'),
        ('oil', 'Face Oil'),
        ('treatment', 'Treatment'),
        ('other', 'Other'),
    ]

    brand = models.CharField(max_length=200)
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=600, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rank = models.FloatField(null=True, blank=True, help_text="Product rating (0-5)")
    ingredients = models.TextField(help_text="Comma-separated ingredient list")
    image_url = models.URLField(blank=True)

    # ✅ NEW: Direct purchase link (Amazon, Sephora, Nykaa, etc.)
    purchase_url = models.URLField(
        blank=True,
        null=True,
        help_text="Direct link to purchase this product (e.g. Amazon, Nykaa, Sephora)"
    )

    # Skin type compatibility flags
    skin_dry = models.BooleanField(default=False)
    skin_oily = models.BooleanField(default=False)
    skin_normal = models.BooleanField(default=False)
    skin_combination = models.BooleanField(default=False)
    skin_sensitive = models.BooleanField(default=False)

    made_in_india = models.BooleanField(default=False)
    is_ayurvedic = models.BooleanField(default=False)
    currency = models.CharField(max_length=5, default='INR')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    embedding = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['brand', 'name']
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['category']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f"{self.brand} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.brand}-{self.name}")
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_ingredient_list(self):
        """Parse comma-separated ingredients into a clean list."""
        return [i.strip() for i in self.ingredients.split(',') if i.strip()]

    def get_skin_types(self):
        """Return list of compatible skin type names."""
        types = []
        if self.skin_dry: types.append('Dry')
        if self.skin_oily: types.append('Oily')
        if self.skin_normal: types.append('Normal')
        if self.skin_combination: types.append('Combination')
        if self.skin_sensitive: types.append('Sensitive')
        return types

    @property
    def ingredient_count(self):
        return len(self.get_ingredient_list())


class SimilarityCache(models.Model):
    """
    Caches pairwise cosine similarity scores between products.
    Avoids recomputing expensive ML operations on every request.
    """
    product_a = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='similarity_as_a'
    )
    product_b = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='similarity_as_b'
    )
    similarity_score = models.FloatField()
    computed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product_a', 'product_b')
        indexes = [
            models.Index(fields=['product_a', 'similarity_score']),
        ]

    def __str__(self):
        return f"{self.product_a} <-> {self.product_b}: {self.similarity_score:.3f}"

    @property
    def is_budget_dupe(self):
        """True if product_b is cheaper and highly similar to product_a."""
        from django.conf import settings
        threshold = getattr(settings, 'BUDGET_DUPE_SIMILARITY_THRESHOLD', 0.75)
        return (
            self.similarity_score >= threshold
            and self.product_b.price is not None
            and self.product_a.price is not None
            and self.product_b.price < self.product_a.price
        )

    @property
    def dupe_score(self):
        """
        Combined score weighing similarity + price advantage.
        Higher is better. Returns 0-100.
        """
        if not self.product_a.price or not self.product_b.price:
            return self.similarity_score * 100

        price_ratio = float(self.product_b.price) / float(self.product_a.price)
        price_advantage = max(0, 1 - price_ratio)
        score = (self.similarity_score * 0.7 + price_advantage * 0.3) * 100
        return round(score, 1)


class PriceHistory(models.Model):
    product    = models.ForeignKey(Product, related_name='price_history', on_delete=models.CASCADE)
    retailer   = models.CharField(max_length=100, default='nykaa')
    price      = models.DecimalField(max_digits=10, decimal_places=2)
    url        = models.URLField(blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
    in_stock   = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fetched_at']

    def __str__(self):
        return f"{self.product.name} — ₹{self.price} at {self.retailer}"
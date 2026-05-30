from django.db import models


class Ingredient(models.Model):
    """
    Master ingredient dictionary with descriptions, benefits, and safety info.
    Populated from the INCI (International Nomenclature of Cosmetic Ingredients) database.
    """
    RISK_CHOICES = [
        ('safe', 'Safe'),
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('avoid', 'Avoid'),
    ]

    CATEGORY_CHOICES = [
        ('humectant', 'Humectant'),
        ('emollient', 'Emollient'),
        ('occlusant', 'Occlusant'),
        ('antioxidant', 'Antioxidant'),
        ('exfoliant', 'Exfoliant'),
        ('surfactant', 'Surfactant'),
        ('preservative', 'Preservative'),
        ('fragrance', 'Fragrance'),
        ('sunscreen', 'UV Filter'),
        ('brightener', 'Brightener'),
        ('peptide', 'Peptide'),
        ('retinoid', 'Retinoid'),
        ('vitamin', 'Vitamin'),
        ('botanical', 'Botanical Extract'),
        ('oil', 'Oil'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=300, unique=True)
    inci_name = models.CharField(max_length=300, blank=True, help_text="INCI scientific name")
    description = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    risk_level = models.CharField(max_length=10, choices=RISK_CHOICES, default='safe')

    # Skin type suitability
    good_for_dry = models.BooleanField(default=False)
    good_for_oily = models.BooleanField(default=False)
    good_for_sensitive = models.BooleanField(default=False)

    # Flags
    is_fragrance = models.BooleanField(default=False)
    is_alcohol = models.BooleanField(default=False)
    is_paraben = models.BooleanField(default=False)
    is_sulfate = models.BooleanField(default=False)
    is_silicone = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name

    @property
    def risk_color(self):
        colors = {
            'safe': '#22c55e',
            'low': '#84cc16',
            'moderate': '#f59e0b',
            'high': '#ef4444',
            'avoid': '#7f1d1d',
        }
        return colors.get(self.risk_level, '#9ca3af')

    def get_flags(self):
        flags = []
        if self.is_fragrance: flags.append('Fragrance')
        if self.is_alcohol: flags.append('Alcohol')
        if self.is_paraben: flags.append('Paraben')
        if self.is_sulfate: flags.append('Sulfate')
        if self.is_silicone: flags.append('Silicone')
        return flags

class IngredientConflict(models.Model):
    SEVERITY_CHOICES = [
        ('avoid',   'Avoid together'),
        ('caution', 'Use with caution'),
        ('time',    'Use at different times'),
    ]
    ingredient_a = models.CharField(max_length=200, help_text="First ingredient name or keyword")
    ingredient_b = models.CharField(max_length=200, help_text="Second ingredient name or keyword")
    severity     = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='caution')
    reason       = models.TextField()
    safe_alternative = models.TextField(blank=True, help_text="What to do instead")

    class Meta:
        unique_together = ['ingredient_a', 'ingredient_b']

    def __str__(self):
        return f"{self.ingredient_a} + {self.ingredient_b} ({self.severity})"
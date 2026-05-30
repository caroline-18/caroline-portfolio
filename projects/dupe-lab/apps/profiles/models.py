from django.db import models
from django.contrib.auth.models import User

SKIN_TYPES = [('oily','Oily'),('dry','Dry'),('combination','Combination'),
               ('normal','Normal'),('sensitive','Sensitive')]

class SkinConcern(models.Model):
    name = models.CharField(max_length=100)   # acne, aging, hyperpigmentation…
    slug = models.SlugField(unique=True)

    def __str__(self): return self.name

class SkinProfile(models.Model):
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='skin_profile')
    skin_type   = models.CharField(max_length=20, choices=SKIN_TYPES)
    concerns    = models.ManyToManyField(SkinConcern, blank=True)
    climate     = models.CharField(max_length=50, default='temperate')  # arid/tropical/temperate/cold
    age_range   = models.CharField(max_length=20, default='25-34')
    fitzpatrick = models.IntegerField(default=2)   # I–VI skin tone scale
    embedding   = models.JSONField(null=True, blank=True)  # 128-dim vector, computed async
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self): return f"{self.user.username} skin profile"
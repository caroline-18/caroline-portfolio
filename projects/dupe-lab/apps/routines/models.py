from django.db import models
from django.contrib.auth.models import User

class Routine(models.Model):
    ROUTINE_TYPES = [('am','Morning'),('pm','Evening'),('weekly','Weekly')]
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    name         = models.CharField(max_length=100)
    routine_type = models.CharField(max_length=10, choices=ROUTINE_TYPES, default='am')
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.name}"

class RoutineStep(models.Model):
    routine  = models.ForeignKey(Routine, related_name='steps', on_delete=models.CASCADE)
    product  = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    step_num = models.PositiveIntegerField()
    notes    = models.TextField(blank=True)

    class Meta:
        ordering = ['step_num']
        unique_together = ['routine', 'step_num']

    def __str__(self):
        return f"Step {self.step_num}: {self.product.name}"
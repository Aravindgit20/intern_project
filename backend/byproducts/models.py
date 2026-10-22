from django.db import models

from processing.models import RawMaterial


class ByProduct(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    raw_material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE
    )

    byproduct_type = models.CharField(
        max_length=100
    )

    quantity = models.FloatField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    potential_applications = models.JSONField(
        default=list,
        blank=True
    )

    assigned_to = models.ForeignKey(
        'app.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.byproduct_type} "
            f"from {self.raw_material}"
        )
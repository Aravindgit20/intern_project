
from django.db import models
from app.models import User


class RawMaterial(models.Model):

    MATERIAL_CHOICES = (
        ('bauxite', 'Bauxite'),
        ('scrap_aluminum', 'Scrap Aluminum'),
    )

    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product_id = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True
    )

    material_type = models.CharField(
        max_length=100,
        choices=MATERIAL_CHOICES
    )

    quantity = models.FloatField(
        help_text="Enter quantity in kilograms (kg)"
    )

    lower_yield = models.FloatField(
        blank=True,
        null=True
    )

    predicted_yield = models.FloatField(
        blank=True,
        null=True
    )

    upper_yield = models.FloatField(
        blank=True,
        null=True
    )

    # Actual Processing Result
    actual_yield = models.FloatField(
        blank=True,
        null=True
    )

    waste_quantity = models.FloatField(
        blank=True,
        null=True
    )

    # Reinforcement Learning Status
    rl_processed = models.BooleanField(
        default=False
    )

    # Reinforcement Learning State and Action
    rl_state = models.CharField(
        max_length=200,
        null=True,
        blank=True
    )

    rl_action = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    # Processing Information
    process_stage = models.CharField(
        max_length=100,
        default='Processing'
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    # Generate Product ID Automatically
    def save(self, *args, **kwargs):

        if not self.product_id:

            last_material = (
                RawMaterial.objects
                .filter(product_id__isnull=False)
                .order_by('-product_id')
                .first()
            )

            if last_material:
                self.product_id = last_material.product_id + 1
            else:
                self.product_id = 1

        super().save(*args, **kwargs)

    # String Representation
    def __str__(self):

        return (
            f"{self.product_id} - "
            f"{self.material_type} - "
            f"{self.quantity}kg "
            f"by {self.agent.username}"
        )


# Reinforcement Learning Feedback
class RLFeedback(models.Model):

    material = models.ForeignKey(
        RawMaterial,
        on_delete=models.CASCADE,
        related_name='rl_feedback'
    )

    predicted_yield = models.FloatField()

    actual_yield = models.FloatField()

    waste_quantity = models.FloatField()

    rl_state = models.CharField(
        max_length=200
    )

    rl_action = models.CharField(
        max_length=100
    )

    reward = models.FloatField()

    q_value = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"RL Feedback - "
            f"Product {self.material.product_id} - "
            f"Reward {self.reward}"
        )

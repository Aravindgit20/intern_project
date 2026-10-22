from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('scrap_team', 'Scrap Team'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username


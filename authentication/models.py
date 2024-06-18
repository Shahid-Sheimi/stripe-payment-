from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    USER_ROLE_CHOICES = [
        ("customer", "Customer"),
        ("member", "Member"),
        ("admin", "Admin")
    ]
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES, default='customer')
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permissions', blank=True)

    class Meta:
        ordering = ['id']


from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    # Remove Django's default date_joined field
    date_joined = None

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Email Address'
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

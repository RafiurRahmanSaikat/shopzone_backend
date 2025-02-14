from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("store_owner", "Store Owner"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    profile_picture = models.TextField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]

    def get_cache_key(self):
        return f"user_data_{self.id}"

    def clear_cache(self):
        cache.delete(self.get_cache_key())


@receiver(post_save, sender=User)
def clear_user_cache(sender, instance, **kwargs):
    instance.clear_cache()

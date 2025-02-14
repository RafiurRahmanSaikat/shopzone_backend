from django.contrib.auth import get_user_model

User = get_user_model()
from django.db import models


class StoreCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_stores"
    )

    store_categories = models.ManyToManyField(StoreCategory)

    def __str__(self):
        return self.name

from django.contrib.auth import get_user_model

User = get_user_model()
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from store.models import Store


class Brand(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    rating = models.FloatField(default=0)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        avg_rating = Review.objects.filter(product=self.product).aggregate(
            Avg("rating")
        )["rating__avg"]
        self.product.rating = avg_rating
        self.product.save()

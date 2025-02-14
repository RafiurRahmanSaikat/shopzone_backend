from django.contrib import admin

from .models import Cart, CartItem, Order, OrderProduct

# Register your models here.


admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderProduct)

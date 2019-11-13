from django.contrib import admin
from core.models import Item, OrderItem, Order, Variation, BillingAddress

# Register your models here.

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Variation)
admin.site.register(BillingAddress)
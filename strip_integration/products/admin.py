from django.contrib import admin
from .models import Product , PaymentIntent
# Register your models here.

admin.site.register(Product)
admin.site.register(PaymentIntent)
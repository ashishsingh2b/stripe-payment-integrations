from rest_framework import serializers
from .models import Product, PaymentIntent

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price']

class PaymentIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIntent
        fields = ['id', 'payment_intent_id', 'amount', 'status', 'created_at']

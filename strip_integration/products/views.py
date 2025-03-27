import stripe
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, PaymentIntent
from .serializers import ProductSerializer, PaymentIntentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        try:
            product = self.get_object()
            
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(product.price * 100),  # Convert to cents
                currency='usd',
                metadata={'product_id': product.id}
            )

            # Save payment intent to database
            payment_intent = PaymentIntent.objects.create(
                payment_intent_id=intent.id,
                product=product,
                amount=product.price,
                status=intent.status
            )

            return Response({
                'clientSecret': intent.client_secret,
                'payment_intent_id': intent.id
            })
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        try:
            payment_intent_id = request.data.get('payment_intent_id')
            payment_intent = PaymentIntent.objects.get(payment_intent_id=payment_intent_id)
            
            # Verify payment status with Stripe
            stripe_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Update payment status
            payment_intent.status = stripe_intent.status
            payment_intent.save()

            return Response({
                'status': stripe_intent.status
            })
        except PaymentIntent.DoesNotExist:
            return Response({
                'error': 'Payment intent not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': 'An unexpected error occurred'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

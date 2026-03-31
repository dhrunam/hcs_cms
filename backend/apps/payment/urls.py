from django.urls import path

from apps.payment.views import (
    PaymentGatewayConfigView,
    PaymentInitiateView,
    PaymentLatestTransactionView,
    PaymentResponseCallbackView,
)

app_name = "payment"

urlpatterns = [
    path("config/", PaymentGatewayConfigView.as_view(), name="payment-config"),
    path("initiate/", PaymentInitiateView.as_view(), name="payment-initiate"),
    path("latest/", PaymentLatestTransactionView.as_view(), name="payment-latest"),
    path("response", PaymentResponseCallbackView.as_view(), name="payment-response"),
]


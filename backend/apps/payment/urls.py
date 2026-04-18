from django.urls import path

from apps.payment.views import (
    PaymentGatewayConfigView,
    PaymentInitiateView,
    PaymentOfflineSubmissionView,
    PaymentLatestTransactionView,
    PaymentAllTransactionsView,
    PaymentResponseCallbackView,
)

app_name = "payment"

urlpatterns = [
    path("config/", PaymentGatewayConfigView.as_view(), name="payment-config"),
    path("initiate/", PaymentInitiateView.as_view(), name="payment-initiate"),
    path("offline/", PaymentOfflineSubmissionView.as_view(), name="payment-offline"),
    path("latest/", PaymentLatestTransactionView.as_view(), name="payment-latest"),
    path("all/", PaymentAllTransactionsView.as_view(), name="payment-all"),
    path("response", PaymentResponseCallbackView.as_view(), name="payment-response"),
]


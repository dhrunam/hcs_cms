from django.urls import path

from apps.payment.views import (
    PaymentGatewayConfigView,
    PaymentInitiateView,
    PaymentOfflineSubmissionView,
    PaymentLatestTransactionView,
    PaymentResponseCallbackView,
    PaymentTransactionsListView,
)

app_name = "payment"

urlpatterns = [
    path("config/", PaymentGatewayConfigView.as_view(), name="payment-config"),
    path("initiate/", PaymentInitiateView.as_view(), name="payment-initiate"),
    path("offline/", PaymentOfflineSubmissionView.as_view(), name="payment-offline"),
    path("latest/", PaymentLatestTransactionView.as_view(), name="payment-latest"),
    path(
        "transactions/",
        PaymentTransactionsListView.as_view(),
        name="payment-transactions-list",
    ),
    path("response", PaymentResponseCallbackView.as_view(), name="payment-response"),
]


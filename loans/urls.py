from django.urls import path

from .views import LoanListCreate, PaymentListCreate

urlpatterns = [
    path("loans/", LoanListCreate.as_view(), name="loan_list_create"),
    path("payments/", PaymentListCreate.as_view(), name="payment_list_create"),
]

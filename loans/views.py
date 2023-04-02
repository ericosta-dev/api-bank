from rest_framework import generics

from .models import Loan, Payment
from .serializers import LoanSerializer, PaymentSerializer


class LoanListCreate(generics.ListCreateAPIView):
    """
    A view for creating and listing loans via the API.
    """

    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def get_queryset(self):
        return self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class PaymentListCreate(generics.ListCreateAPIView):
    """
    A view for creating and listing payments via the API.
    """

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return self.queryset.filter(loan__customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save()

from rest_framework import serializers

from .models import Loan, Payment


class LoanSerializer(serializers.ModelSerializer):
    """
    A serializer for the Loan model that adds a field for the remaining balance of the loan.
    """

    remaining_balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    pro_rata_interest = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"

    def to_representation(self, instance):
        """
        Override the default representation to include the remaining balance of the loan.
        """
        representation = super().to_representation(instance)
        representation["remaining_balance"] = instance.remaining_balance()
        representation["pro_rata_interest"] = instance.calculate_pro_rata_interest()
        return representation


class PaymentSerializer(serializers.ModelSerializer):
    """
    A serializer for the Payment model.
    """

    class Meta:
        model = Payment
        fields = "__all__"

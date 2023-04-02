import uuid
from datetime import date, datetime

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Loan(models.Model):
    """A class that represents a loan.

    Attributes:
        id (UUIDField): A unique identifier for the loan.
        nominal_value (DecimalField): The value of the loan.
        interest_rate (DecimalField): The interest rate charged on the loan.
        ip_address (GenericIPAddressField): The IP address of the borrower.
        request_date (DateField): The date when the loan was requested.
        bank (TextField): The name of the bank that issued the loan.
        customer (ForeignKey): The user who borrowed the loan.

    Methods:
        remaining_balance: Calculates the balance remaining after payments are made.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nominal_value = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]
    )
    ip_address = models.GenericIPAddressField()
    request_date = models.DateField()
    bank = models.TextField()
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    iof_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0)]
    )

    def remaining_balance(self, end_date=None):
        """Calculates the balance remaining after payments are made, including compound interest.

        Args:
            end_date (date): The date up to which the remaining balance should be calculated.
                            If not provided, the current date is used.

        Returns:
            Float: The outstanding balance on the loan.
        """
        self.nominal_value = float(self.nominal_value)
        self.interest_rate = float(self.interest_rate)

        if end_date is None:
            end_date = date.today()

        days_since_request = (end_date - self.request_date).days
        daily_interest_rate = (1 + (self.interest_rate / 100)) ** (1 / 30) - 1
        balance_with_interest = self.nominal_value * (1 + daily_interest_rate) ** days_since_request

        total_payments = sum(payment.payment_amount for payment in self.payments.all())

        return balance_with_interest - float(total_payments)

    def calculate_pro_rata_interest(self, end_date=None):
        self.interest_rate = float(self.interest_rate)
        self.nominal_value = float(self.nominal_value)
        self.iof_rate = float(self.iof_rate)

        if end_date is None:
            end_date = date.today()

        days_since_request = (end_date - self.request_date).days
        daily_interest_rate = (1 + (self.interest_rate / 100)) ** (1 / 30) - 1
        interest_pro_rata = self.nominal_value * (
            (1 + daily_interest_rate) ** days_since_request - 1
        )

        iof_amount = self.nominal_value * (self.iof_rate / 100)

        total_interest = interest_pro_rata + iof_amount

        return total_interest


class Payment(models.Model):
    """
    A model representing a payment made on a loan.

    Attributes:
        loan (Loan): The loan associated with this payment.
        pay_day (Date): The date the payment was made.
        payment_amount (Decimal): The amount of the payment made.
    """

    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    pay_day = models.DateField()
    payment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

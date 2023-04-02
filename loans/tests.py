from datetime import date, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Loan, Payment


class LoanAPITestCase(APITestCase):
    """
    A test case for the Loan API views.

    Attributes:
        client (APIClient): The test client used to make HTTP requests.
        user (User): A test user used to make API requests with an access token.
        token (str): An access token used to authenticate requests.
    """

    def setUp(self):
        """
        Set up the test case by creating a test user and obtaining an access token.
        """
        self.client = APIClient()

        self.user = User.objects.create_user(username="testuser", password="testpassword")

        response = self.client.post(
            reverse("token_obtain_pair"), {"username": "testuser", "password": "testpassword"}
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_create_loan(self):
        """
        Test creating a new loan via the API.
        """
        url = reverse("loan_list_create")
        data = {
            "nominal_value": "5000.00",
            "interest_rate": "1.5",
            "ip_address": "192.168.1.1",
            "request_date": "2023-04-01",
            "bank": "Banco do Brasil",
            "customer": self.user.pk,
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)
        self.assertEqual(Loan.objects.get().nominal_value, 5000.00)

    def test_create_payment(self):
        """
        Test creating a new payment for a loan via the API.
        """
        loan = Loan.objects.create(
            nominal_value=5000.00,
            interest_rate=1.5,
            ip_address="192.168.1.1",
            request_date="2023-04-01",
            customer=self.user,
            iof_rate=0.38,
        )

        url = reverse("payment_list_create")
        data = {"loan": str(loan.pk), "pay_day": "2023-04-30", "payment_amount": "200.00"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(loan.payments.count(), 1)
        self.assertEqual(loan.payments.get().payment_amount, 200.00)

    def test_loan_visibility(self):
        """
        Test that a user can only see their own loans via the API.
        """
        user2 = User.objects.create_user(username="testuser2", password="testpassword2")

        loan_user1 = Loan.objects.create(
            nominal_value=5000.00,
            interest_rate=1.5,
            ip_address="192.168.1.1",
            request_date="2023-04-01",
            bank="Caixa Econômica",
            customer=self.user,
            iof_rate=0.38,
        )

        loan_user2 = Loan.objects.create(
            nominal_value=4000.00,
            interest_rate=2.0,
            ip_address="192.168.1.2",
            request_date="2023-04-02",
            bank="Banco do Brasil",
            customer=user2,
            iof_rate=0.38,
        )

        response = self.client.get(reverse("loan_list_create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(loan_user1.id))

        response = self.client.post(
            reverse("token_obtain_pair"), {"username": "testuser2", "password": "testpassword2"}
        )
        token_user2 = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_user2}")

        response = self.client.get(reverse("loan_list_create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(loan_user2.id))

    def test_calculate_pro_rata_interest(self):
        """
        Calculate pro-rata interest for a loan and check if the calculated interest matches the expected value.
        """
        loan = Loan.objects.create(
            nominal_value=5000.00,
            interest_rate=1.5,
            ip_address="192.168.1.1",
            request_date=date(2023, 4, 1),
            bank="Banco do Brasil",
            customer=self.user,
            iof_rate=0.38,
        )

        end_date = loan.request_date + timedelta(days=30)
        interest_30_days = loan.calculate_pro_rata_interest(end_date=end_date)
        expected_interest_30_days = loan.nominal_value * (
            loan.interest_rate / 100
        ) + loan.nominal_value * (loan.iof_rate / 100)
        self.assertAlmostEqual(interest_30_days, expected_interest_30_days, delta=0.01)

        end_date = loan.request_date + timedelta(days=60)
        interest_60_days = loan.calculate_pro_rata_interest(end_date=end_date)

        daily_interest_rate = (1 + (loan.interest_rate / 100)) ** (1 / 30) - 1
        interest_pro_rata_60_days = loan.nominal_value * ((1 + daily_interest_rate) ** 60 - 1)
        iof_amount = loan.nominal_value * (loan.iof_rate / 100)
        expected_interest_60_days = interest_pro_rata_60_days + iof_amount

        self.assertAlmostEqual(interest_60_days, expected_interest_60_days, delta=0.01)

    def test_create_loan_with_invalid_interest_rate(self):
        """
        Test if creating a loan with an invalid interest rate returns a HTTP 400 Bad Request response.
        """
        loan_data = {
            "nominal_value": 5000.00,
            "interest_rate": -1.5,
            "ip_address": "192.168.1.1",
            "request_date": "2023-04-01",
            "bank": "Banco do Brasil",
            "customer": self.user.id,
        }

        response = self.client.post(reverse("loan_list_create"), data=loan_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_loan_with_invalid_nominal_value(self):
        """
        Test if creating a loan with an invalid nominal value returns a HTTP 400 Bad Request response.
        """
        loan_data = {
            "nominal_value": -5000.00,
            "interest_rate": 1.5,
            "ip_address": "192.168.1.1",
            "request_date": "2023-04-01",
            "bank": "Banco do Brasil",
            "customer": self.user.id,
        }

        response = self.client.post(reverse("loan_list_create"), data=loan_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_with_invalid_amount(self):
        """
        Test if creating a loan payment with an invalid amount returns a HTTP 400 Bad Request response.
        """
        loan = Loan.objects.create(
            nominal_value=5000.00,
            interest_rate=1.5,
            ip_address="192.168.1.1",
            request_date="2023-04-01",
            bank="Banco do Brasil",
            customer=self.user,
        )

        payment_data = {"loan": loan.id, "pay_day": "2023-05-01", "payment_amount": -100.00}

        response = self.client.post(
            reverse("payment_list_create"), data=payment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_payments_multiple_users(self):
        """
        Test if listing payments returns only the payments of the authenticated user.

        """
        user2 = User.objects.create_user(username="user2", password="testpassword")

        loan_user1 = Loan.objects.create(
            nominal_value=5000.00,
            interest_rate=1.5,
            ip_address="192.168.1.1",
            request_date="2023-04-01",
            bank="Banco do Brasil",
            customer=self.user,
        )

        loan_user2 = Loan.objects.create(
            nominal_value=3000.00,
            interest_rate=2.0,
            ip_address="192.168.1.1",
            request_date="2023-04-01",
            bank="Banco do Brasil",
            customer=user2,
        )

        payment_user1 = Payment.objects.create(
            loan=loan_user1, pay_day="2023-05-01", payment_amount=100.00
        )

        payment_user2 = Payment.objects.create(
            loan=loan_user2, pay_day="2023-05-01", payment_amount=200.00
        )

        self.client.force_authenticate(user=self.user)
        response_user1 = self.client.get(reverse("payment_list_create"), format="json")
        self.assertEqual(response_user1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_user1.data), 1)
        self.assertEqual(str(response_user1.data[0]["id"]), str(payment_user1.id))

        self.client.force_authenticate(user=user2)
        response_user2 = self.client.get(reverse("payment_list_create"), format="json")
        self.assertEqual(response_user2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_user2.data), 1)
        self.assertEqual(str(response_user2.data[0]["id"]), str(payment_user2.id))

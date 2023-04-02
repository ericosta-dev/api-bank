# Generated by Django 4.1.7 on 2023-03-31 01:58

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Loan",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("nominal_value", models.DecimalField(decimal_places=2, max_digits=10)),
                ("interest_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("ip_address", models.GenericIPAddressField()),
                ("request_date", models.DateField()),
                ("bank", models.TextField()),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("pay_day", models.DateField()),
                ("payment_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "loan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="loans.loan",
                    ),
                ),
            ],
        ),
    ]
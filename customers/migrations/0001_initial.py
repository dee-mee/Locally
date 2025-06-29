# Generated by Django 5.0.3 on 2025-06-21 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=50)),
                ("last_name", models.CharField(blank=True, max_length=50)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                ("phone", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "customer_type",
                    models.CharField(
                        choices=[
                            ("individual", "Individual"),
                            ("business", "Business"),
                            ("wholesale", "Wholesale"),
                            ("retail", "Retail"),
                        ],
                        default="individual",
                        max_length=20,
                    ),
                ),
                (
                    "company_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "tax_number",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="Tax ID/VAT"
                    ),
                ),
                ("address", models.TextField(blank=True, null=True)),
                ("city", models.CharField(blank=True, max_length=100, null=True)),
                ("state", models.CharField(blank=True, max_length=100, null=True)),
                ("postal_code", models.CharField(blank=True, max_length=20, null=True)),
                ("country", models.CharField(blank=True, max_length=100, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
                "ordering": ["first_name", "last_name"],
            },
        ),
    ]

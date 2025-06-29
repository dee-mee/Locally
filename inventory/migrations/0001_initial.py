# Generated by Django 5.0.3 on 2025-06-21 22:30

import django.core.validators
import django.db.models.deletion
import inventory.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
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
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Product",
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
                ("name", models.CharField(max_length=200)),
                (
                    "sku",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        null=True,
                        unique=True,
                        verbose_name="SKU",
                    ),
                ),
                ("barcode", models.CharField(blank=True, max_length=50, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "cost_price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Cost price per unit",
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "selling_price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Selling price per unit",
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "tax_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=0.0,
                        help_text="Tax rate in percentage (e.g., 16 for 16%)",
                        max_digits=5,
                    ),
                ),
                (
                    "stock_quantity",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        choices=[
                            ("piece", "Piece"),
                            ("kg", "Kilogram"),
                            ("g", "Gram"),
                            ("l", "Liter"),
                            ("ml", "Milliliter"),
                            ("m", "Meter"),
                            ("cm", "Centimeter"),
                            ("box", "Box"),
                            ("pack", "Pack"),
                            ("dozen", "Dozen"),
                        ],
                        default="piece",
                        max_length=10,
                    ),
                ),
                (
                    "reorder_level",
                    models.DecimalField(
                        decimal_places=2,
                        default=10,
                        help_text="Minimum stock level before reordering",
                        max_digits=10,
                        verbose_name="Reorder Level",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("inactive", "Inactive"),
                            ("discontinued", "Discontinued"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=inventory.models.product_image_path,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=["jpg", "jpeg", "png", "gif"]
                            )
                        ],
                    ),
                ),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="products",
                        to="inventory.category",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_products",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "last_updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_products",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="StockMovement",
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
                (
                    "movement_type",
                    models.CharField(
                        choices=[
                            ("purchase", "Purchase"),
                            ("sale", "Sale"),
                            ("return", "Return"),
                            ("adjustment", "Adjustment"),
                            ("damaged", "Damaged"),
                            ("expired", "Expired"),
                        ],
                        max_length=20,
                    ),
                ),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=10)),
                ("reference", models.CharField(blank=True, max_length=100, null=True)),
                ("notes", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stock_movements",
                        to="inventory.product",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["name"], name="inventory_p_name_f6a6a1_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["sku"], name="inventory_p_sku_f85905_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["barcode"], name="inventory_p_barcode_3a77e5_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(fields=["status"], name="inventory_p_status_2ba142_idx"),
        ),
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["category"], name="inventory_p_categor_607069_idx"
            ),
        ),
    ]

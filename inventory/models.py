from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import os

class Supplier(models.Model):
    """Supplier model for product vendors"""
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class ProductTag(models.Model):
    """Tag model for product categorization"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#6c757d')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class Category(models.Model):
    """Product category model"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('inventory:category_detail', kwargs={'slug': self.slug})


def product_image_path(instance, filename):
    """Generate file path for product images"""
    ext = filename.split('.')[-1]
    filename = f"{timezone.now().timestamp()}.{ext}"
    return os.path.join('products', filename)


class Product(models.Model):
    """Product model for inventory items"""
    # Product status choices
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DISCONTINUED = 'discontinued'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (DISCONTINUED, 'Discontinued'),
    ]

    # Unit of measure choices
    UNIT_CHOICES = [
        ('piece', 'Piece'),
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('l', 'Liter'),
        ('ml', 'Milliliter'),
        ('m', 'Meter'),
        ('cm', 'Centimeter'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('dozen', 'Dozen'),
    ]

    # Basic Information
    name = models.CharField(max_length=200)
    sku = models.CharField('SKU', max_length=50, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products'
    )
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text='Cost price per unit'
    )
    taxable = models.BooleanField(
        default=True,
        help_text='Whether this product is taxable'
    )
    selling_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text='Selling price per unit'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0,
        help_text='Tax rate in percentage (e.g., 16 for 16%)'
    )
    
    # Inventory
    track_inventory = models.BooleanField(
        default=True,
        help_text='Track stock levels for this product'
    )
    stock_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(
        max_length=10, 
        choices=UNIT_CHOICES, 
        default='piece'
    )
    reorder_level = models.DecimalField(
        'Reorder Level',
        max_digits=10, 
        decimal_places=2, 
        default=10,
        help_text='Minimum stock level before reordering'
    )
    
    # Product Status
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default=ACTIVE
    )
    alert_low_stock = models.BooleanField(
        default=True,
        help_text='Send alerts when stock is low'
    )
    allow_backorder = models.BooleanField(
        default=False,
        help_text='Allow ordering more than available stock'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this product is active and visible to customers'
    )
    
    # Product Organization
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Product brand or manufacturer'
    )
    supplier = models.ForeignKey(
        'inventory.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Primary supplier for this product'
    )
    tags = models.ManyToManyField(
        'inventory.ProductTag',
        blank=True,
        help_text='Tags for categorizing products'
    )
    
    # Shipping Information
    WEIGHT_UNIT_CHOICES = [
        ('g', 'Grams (g)'),
        ('kg', 'Kilograms (kg)'),
        ('lb', 'Pounds (lb)'),
        ('oz', 'Ounces (oz)'),
    ]
    
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Product weight'
    )
    weight_unit = models.CharField(
        max_length=2,
        choices=WEIGHT_UNIT_CHOICES,
        default='kg',
        help_text='Unit of measurement for weight'
    )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Length in centimeters'
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Width in centimeters'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in centimeters'
    )
    
    # Additional Information
    image = models.ImageField(
        upload_to=product_image_path, 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
        ]
    )
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='created_products'
    )
    last_updated_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='updated_products',
        blank=True
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_unit_display()})"
    
    def save(self, *args, **kwargs):
        # Generate SKU if not provided
        if not self.sku:
            prefix = 'PRD'
            if self.category:
                prefix = f"{self.category.name[:3].upper()}"
            self.sku = f"{prefix}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Ensure selling price is not less than cost price
        if self.selling_price < self.cost_price:
            self.selling_price = self.cost_price
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('inventory:product_detail', kwargs={'pk': self.pk})
    
    def is_low_stock(self):
        """Check if product is below reorder level"""
        return self.stock_quantity <= self.reorder_level
    
    def get_stock_status(self):
        """Get stock status as text"""
        if self.stock_quantity <= 0:
            return 'out_of_stock'
        elif self.is_low_stock():
            return 'low_stock'
        return 'in_stock'
    
    def get_stock_status_display(self):
        """Get human-readable stock status"""
        status = self.get_stock_status()
        status_map = {
            'out_of_stock': 'Out of Stock',
            'low_stock': 'Low Stock',
            'in_stock': 'In Stock',
        }
        return status_map.get(status, 'Unknown')
    
    def get_stock_status_class(self):
        """Get CSS class for stock status"""
        status = self.get_stock_status()
        status_classes = {
            'out_of_stock': 'danger',
            'low_stock': 'warning',
            'in_stock': 'success',
        }
        return status_classes.get(status, 'secondary')
    
    def get_profit_margin(self):
        """Calculate profit margin as a percentage"""
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
    
    def clean(self):
        """Custom validation"""
        if self.stock_quantity < 0:
            raise ValidationError({
                'stock_quantity': 'Stock quantity cannot be negative.'
            })
        
        if self.selling_price < self.cost_price:
            raise ValidationError({
                'selling_price': 'Selling price cannot be less than cost price.'
            })


class StockMovement(models.Model):
    """Tracks inventory stock movements"""
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
    ]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock_movements'
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Update product stock based on movement type
        if self.pk is None:  # Only on creation
            if self.movement_type in ['purchase', 'return']:
                self.product.stock_quantity += self.quantity
            elif self.movement_type in ['sale', 'damaged', 'expired']:
                self.product.stock_quantity -= self.quantity
            
            # Ensure stock doesn't go below zero
            if self.product.stock_quantity < 0:
                raise ValidationError({
                    'quantity': f'Insufficient stock. Only {self.product.stock_quantity + self.quantity} available.'
                })
            
            self.product.save()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Reverse the stock movement when deleted
        if self.movement_type in ['purchase', 'return']:
            self.product.stock_quantity -= self.quantity
        elif self.movement_type in ['sale', 'damaged', 'expired']:
            self.product.stock_quantity += self.quantity
        
        self.product.save()
        super().delete(*args, **kwargs)

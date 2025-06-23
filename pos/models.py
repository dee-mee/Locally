from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
import uuid

# Use string reference to avoid circular import
# Product model will be imported in the methods where needed

class Order(models.Model):
    """
    Represents an order in the POS system.
    """
    ORDER_STATUS_OPEN = 'open'
    ORDER_STATUS_COMPLETED = 'completed'
    ORDER_STATUS_CANCELLED = 'cancelled'
    
    ORDER_STATUS_CHOICES = [
        (ORDER_STATUS_OPEN, _('Open')),
        (ORDER_STATUS_COMPLETED, _('Completed')),
        (ORDER_STATUS_CANCELLED, _('Cancelled')),
    ]
    
    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_PARTIALLY_PAID = 'partially_paid'
    PAYMENT_STATUS_REFUNDED = 'refunded'
    PAYMENT_STATUS_FAILED = 'failed'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, _('Pending')),
        (PAYMENT_STATUS_PAID, _('Paid')),
        (PAYMENT_STATUS_PARTIALLY_PAID, _('Partially Paid')),
        (PAYMENT_STATUS_REFUNDED, _('Refunded')),
        (PAYMENT_STATUS_FAILED, _('Failed')),
    ]
    
    order_number = models.CharField(_('Order Number'), max_length=50, unique=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pos_orders',
        verbose_name=_('User')
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('Customer')
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default=ORDER_STATUS_OPEN
    )
    payment_status = models.CharField(
        _('Payment Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING
    )
    subtotal = models.DecimalField(
        _('Subtotal'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        _('Tax Amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        _('Discount Amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    total = models.DecimalField(
        _('Total'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    tax_rate = models.DecimalField(
        _('Tax Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f'Order #{self.order_number} - {self.get_status_display()} - ${self.total}'
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number
            self.order_number = f'ORD-{timezone.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:8].upper()}'
        
        # Update timestamps
        if self.status == self.ORDER_STATUS_COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def update_totals(self):
        """Update order totals based on items"""
        # Calculate subtotal from order items
        result = self.items.aggregate(
            subtotal=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price'),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            ),
            tax_amount=Sum(
                ExpressionWrapper(
                    F('quantity') * F('price') * F('tax_rate') / 100,
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                )
            )
        )
        
        self.subtotal = result['subtotal'] or 0
        self.tax_amount = result['tax_amount'] or 0
        self.total = self.subtotal + self.tax_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'tax_amount', 'total', 'updated_at'])
    
    def get_absolute_url(self):
        return reverse('pos:order_detail', kwargs={'pk': self.pk})


class OrderItem(models.Model):
    """
    Represents an item within an order.
    """
    order = models.ForeignKey(
        'pos.Order',
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Order')
    )
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Product')
    )
    quantity = models.DecimalField(
        _('Quantity'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    price = models.DecimalField(
        _('Price'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    tax_rate = models.DecimalField(
        _('Tax Rate (%)'),
        max_digits=5,
        decimal_places=2,
        default=0
    )
    taxable = models.BooleanField(_('Taxable'), default=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        ordering = ('created_at',)
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} - ${self.price}'
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    
    @property
    def tax_amount(self):
        return self.subtotal * (self.tax_rate / 100) if self.taxable else 0
    
    @property
    def total(self):
        return self.subtotal + self.tax_amount
    
    def save(self, *args, **kwargs):
        # Set the price from the product if not set
        if not self.price and self.product:
            self.price = self.product.price
        
        # Set tax rate if not set
        if not self.tax_rate and hasattr(settings, 'POS_DEFAULT_TAX_RATE'):
            self.tax_rate = settings.POS_DEFAULT_TAX_RATE
        
        super().save(*args, **kwargs)
        
        # Update order totals
        if self.order:
            self.order.update_totals()
    
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        if order:
            order.update_totals()


class Payment(models.Model):
    """
    Represents a payment for an order.
    """
    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_CREDIT_CARD = 'credit_card'
    PAYMENT_METHOD_DEBIT_CARD = 'debit_card'
    PAYMENT_METHOD_MOBILE_MONEY = 'mobile_money'
    PAYMENT_METHOD_BANK_TRANSFER = 'bank_transfer'
    PAYMENT_METHOD_CHECK = 'check'
    PAYMENT_METHOD_OTHER = 'other'
    
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, _('Cash')),
        (PAYMENT_METHOD_CREDIT_CARD, _('Credit Card')),
        (PAYMENT_METHOD_DEBIT_CARD, _('Debit Card')),
        (PAYMENT_METHOD_MOBILE_MONEY, _('Mobile Money')),
        (PAYMENT_METHOD_BANK_TRANSFER, _('Bank Transfer')),
        (PAYMENT_METHOD_CHECK, _('Check')),
        (PAYMENT_METHOD_OTHER, _('Other')),
    ]
    
    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_COMPLETED = 'completed'
    PAYMENT_STATUS_FAILED = 'failed'
    PAYMENT_STATUS_REFUNDED = 'refunded'
    PAYMENT_STATUS_PARTIALLY_REFUNDED = 'partially_refunded'
    
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, _('Pending')),
        (PAYMENT_STATUS_COMPLETED, _('Completed')),
        (PAYMENT_STATUS_FAILED, _('Failed')),
        (PAYMENT_STATUS_REFUNDED, _('Refunded')),
        (PAYMENT_STATUS_PARTIALLY_REFUNDED, _('Partially Refunded')),
    ]
    
    order = models.ForeignKey(
        'pos.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Order')
    )
    transaction_id = models.CharField(
        _('Transaction ID'),
        max_length=100,
        blank=True,
        null=True
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    amount_tendered = models.DecimalField(
        _('Amount Tendered'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    change_given = models.DecimalField(
        _('Change Given'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    payment_method = models.CharField(
        _('Payment Method'),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=PAYMENT_METHOD_CASH
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_STATUS_PENDING
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_payments',
        verbose_name=_('Processed By')
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ('-created_at',)
    
    def __str__(self):
        return f'Payment #{self.id} - ${self.amount} - {self.get_status_display()}'
    
    def save(self, *args, **kwargs):
        # Generate transaction ID if not provided
        if not self.transaction_id:
            self.transaction_id = f'PYMT-{timezone.now().strftime("%Y%m%d")}-{str(uuid.uuid4())[:8].upper()}'
        
        # Update order payment status if payment is completed
        if self.status == self.PAYMENT_STATUS_COMPLETED and self.order:
            total_paid = self.order.payments.filter(
                status=self.PAYMENT_STATUS_COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            if total_paid >= self.order.total:
                self.order.payment_status = Order.PAYMENT_STATUS_PAID
            else:
                self.order.payment_status = Order.PAYMENT_STATUS_PARTIALLY_PAID
            
            self.order.save()
        
        super().save(*args, **kwargs)


class Sale(models.Model):
    """
    Represents a sales transaction in the Point of Sale system.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    sale_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    sale_date = models.DateTimeField(default=timezone.now)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS, 
        default='cash'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'

    def __str__(self):
        return f'Sale #{self.sale_number} - {self.total}'

    def save(self, *args, **kwargs):
        if not self.sale_number:
            # Generate a unique sale number (you might want to customize this)
            last_sale = Sale.objects.order_by('-id').first()
            last_id = last_sale.id if last_sale else 0
            self.sale_number = f'SALE-{last_id + 1:06d}'
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    """
    Represents an item within a sale transaction.
    """
    sale = models.ForeignKey('pos.Sale', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Product', on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Sale Item'
        verbose_name_plural = 'Sale Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.name} @ {self.unit_price}'

    def save(self, *args, **kwargs):
        # Calculate the total before tax and discount
        subtotal = self.quantity * self.unit_price
        
        # Calculate tax amount
        tax_amount = subtotal * (self.tax_rate / 100)
        
        # Calculate total after tax and discount
        self.total = (subtotal + tax_amount) - self.discount_amount
        
        super().save(*args, **kwargs)
        
        # Update the sale total
        self.sale.save()

    def delete(self, *args, **kwargs):
        sale = self.sale
        super().delete(*args, **kwargs)
        # Update the sale total after deletion
        sale.save()

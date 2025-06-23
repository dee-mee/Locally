from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Customer(models.Model):
    """Customer model for storing customer information"""
    CUSTOMER_TYPES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    customer_type = models.CharField(
        max_length=20, 
        choices=CUSTOMER_TYPES, 
        default='individual'
    )
    company_name = models.CharField(max_length=100, blank=True, null=True)
    tax_number = models.CharField('Tax ID/VAT', max_length=50, blank=True, null=True)
    
    # Address Information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} ({self.get_full_name()})"
        return self.get_full_name()
    
    def get_full_name(self):
        """Return the full name of the customer"""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_absolute_url(self):
        return reverse('customers:customer_detail', kwargs={'pk': self.pk})
    
    def get_short_name(self):
        """Return a short name for the customer"""
        if self.company_name:
            return self.company_name[:20] + ('...' if len(self.company_name) > 20 else '')
        return self.first_name
    
    @property
    def total_purchases(self):
        """Return the total amount spent by the customer"""
        from pos.models import Sale
        total = Sale.objects.filter(customer=self).aggregate(
            total=models.Sum('total')
        )['total'] or 0
        return total
    
    @property
    def total_orders(self):
        """Return the total number of orders placed by the customer"""
        from pos.models import Sale
        return Sale.objects.filter(customer=self).count()

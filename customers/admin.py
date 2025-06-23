from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Customer

class CustomerResource(resources.ModelResource):
    """Resource for importing/exporting customer data"""
    class Meta:
        model = Customer
        fields = (
            'first_name', 'last_name', 'email', 'phone', 'customer_type',
            'company_name', 'tax_number', 'address', 'city', 'state',
            'postal_code', 'country', 'notes', 'is_active', 'created_at', 'updated_at'
        )
        export_order = fields

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    """Admin configuration for Customer model"""
    resource_class = CustomerResource
    list_display = (
        'name', 'company_name', 'email', 'phone', 'customer_type',
        'total_orders_display', 'total_purchases_display', 'is_active', 'customer_actions'
    )
    list_filter = ('customer_type', 'is_active', 'created_at')
    search_fields = (
        'first_name', 'last_name', 'company_name', 'email', 'phone',
        'tax_number', 'address', 'city', 'state', 'postal_code', 'country'
    )
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'first_name', 'last_name', 'email', 'phone', 'customer_type',
                'company_name', 'tax_number', 'is_active'
            )
        }),
        (_('Address Information'), {
            'fields': (
                'address', 'city', 'state', 'postal_code', 'country'
            )
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name(self, obj):
        """Return full name of the customer"""
        return f"{obj.first_name} {obj.last_name}"
    name.short_description = _('Name')
    name.admin_order_field = 'first_name'
    
    def total_orders_display(self, obj):
        """Display total number of orders"""
        return obj.total_orders
    total_orders_display.short_description = _('Orders')
    total_orders_display.admin_order_field = 'total_orders'
    
    def total_purchases_display(self, obj):
        """Display total purchases amount"""
        return f"${obj.total_purchases:,.2f}" if obj.total_purchases > 0 else "-"
    total_purchases_display.short_description = _('Total Spent')
    total_purchases_display.admin_order_field = 'total_purchases'
    
    def customer_actions(self, obj):
        """Add action buttons"""
        view_url = reverse('admin:customers_customer_view', args=[obj.id])
        edit_url = reverse('admin:customers_customer_change', args=[obj.id])
        return format_html(
            '<a href="{}" class="button">View</a> <a href="{}" class="button">Edit</a>',
            view_url, edit_url
        )
    customer_actions.short_description = _('Actions')
    customer_actions.allow_tags = True
    
    def get_urls(self):
        """Add custom URLs for customer actions"""
        from django.urls import path
        
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:customer_id>/view/',
                self.admin_site.admin_view(self.customer_view),
                name='customers_customer_view',
            ),
        ]
        return custom_urls + urls
    
    def customer_view(self, request, customer_id, extra_context=None):
        """Custom view for customer details"""
        from django.shortcuts import get_object_or_404
        from django.template.response import TemplateResponse
        
        customer = get_object_or_404(Customer, pk=customer_id)
        context = {
            **self.admin_site.each_context(request),
            'title': _('Customer Details'),
            'opts': self.model._meta,
            'customer': customer,
            'has_change_permission': self.has_change_permission(request, customer),
            'has_delete_permission': self.has_delete_permission(request, customer),
            'has_view_permission': self.has_view_permission(request, customer),
            **(extra_context or {}),
        }
        return TemplateResponse(
            request,
            'admin/customers/customer/view.html',
            context,
        )
    
    def save_model(self, request, obj, form, change):
        """Set created_by/updated_by fields"""
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


from .models import Order, OrderItem, Payment, Sale, SaleItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'quantity', 'price', 'tax_rate', 'taxable', 'subtotal', 'tax_amount', 'total')
    readonly_fields = ('subtotal', 'tax_amount', 'total')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('transaction_id', 'amount', 'payment_method', 'status', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'customer__name', 'notes')
    readonly_fields = ('order_number', 'subtotal', 'tax_amount', 'discount_amount', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline, PaymentInline]
    fieldsets = (
        (None, {
            'fields': ('order_number', 'user', 'customer', 'status', 'payment_status')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sale_number', 'user', 'customer', 'status', 'total', 'sale_date')
    list_filter = ('status', 'payment_method', 'sale_date')
    search_fields = ('sale_number', 'customer__name', 'user__username', 'notes')
    readonly_fields = ('sale_number', 'subtotal', 'tax_amount', 'discount_amount', 'total', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('sale_number', 'customer', 'user', 'status', 'payment_method')
        }),
        (_('Pricing'), {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total')
        }),
        (_('Dates'), {
            'fields': ('sale_date', 'created_at', 'updated_at')
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'unit_price', 'total')
    list_filter = ('sale__status',)
    search_fields = ('sale__sale_number', 'product__name')
    readonly_fields = ('total',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('transaction_id', 'order__order_number', 'notes')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('order', 'transaction_id', 'amount', 'payment_method', 'status')
        }),
        (_('Payment Details'), {
            'fields': ('amount_tendered', 'change_given')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
        (_('Notes'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

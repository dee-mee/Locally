from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from .models import Category, Product, StockMovement

User = get_user_model()


class StockMovementInline(admin.TabularInline):
    """Inline for stock movements in Product admin"""
    model = StockMovement
    extra = 0
    readonly_fields = ('movement_type', 'quantity', 'reference', 'created_by', 'created_at')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""
    list_display = ('name', 'product_count', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _product_count=models.Count('products')
        )
    
    def product_count(self, obj):
        return obj._product_count
    product_count.admin_order_field = '_product_count'
    product_count.short_description = 'Products'


class StockQuantityFilter(admin.SimpleListFilter):
    """Filter products by stock status"""
    title = 'stock status'
    parameter_name = 'stock_status'
    
    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock_quantity__gt=models.F('reorder_level'))
        if self.value() == 'low_stock':
            return queryset.filter(
                stock_quantity__lte=models.F('reorder_level'),
                stock_quantity__gt=0
            )
        if self.value() == 'out_of_stock':
            return queryset.filter(stock_quantity__lte=0)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model"""
    list_display = (
        'name', 'category', 'stock_quantity_with_status', 'unit', 
        'selling_price', 'cost_price', 'profit_margin', 'status', 'updated_at'
    )
    list_filter = (
        'status', 'category', StockQuantityFilter, 'unit', 'created_at', 'updated_at'
    )
    search_fields = ('name', 'sku', 'barcode', 'description')
    list_editable = ('status', 'selling_price', 'cost_price')
    list_select_related = ('category', 'created_by', 'last_updated_by')
    readonly_fields = (
        'created_at', 'updated_at', 'created_by', 'last_updated_by',
        'stock_quantity', 'profit_margin', 'stock_status'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'description', 'category', 'status')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price', 'tax_rate', 'profit_margin')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'unit', 'reorder_level', 'stock_status')
        }),
        ('Additional Information', {
            'fields': ('image', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'last_updated_by'),
            'classes': ('collapse',)
        }),
    )
    inlines = [StockMovementInline]
    
    def stock_quantity_with_status(self, obj):
        status_class = obj.get_stock_status_class()
        return format_html(
            '<span class="badge bg-{}">{} {}</span>',
            status_class, obj.stock_quantity, obj.get_unit_display()
        )
    stock_quantity_with_status.short_description = 'Stock'
    stock_quantity_with_status.admin_order_field = 'stock_quantity'
    
    def stock_status(self, obj):
        status = obj.get_stock_status_display()
        status_class = obj.get_stock_status_class()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            status_class, status
        )
    stock_status.short_description = 'Stock Status'
    
    def profit_margin(self, obj):
        margin = obj.get_profit_margin()
        color = 'success' if margin > 0 else 'danger' if margin < 0 else 'secondary'
        return format_html(
            '<span class="text-{}">{:.1f}%</span>',
            color, margin
        )
    profit_margin.short_description = 'Margin'
    profit_margin.admin_order_field = 'profit_margin_calc'
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            profit_margin_calc=(
                (models.F('selling_price') - models.F('cost_price')) / 
                models.F('cost_price') * 100
            ) if models.F('cost_price') != 0 else 0
        )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin interface for StockMovement model"""
    list_display = ('created_at', 'product_link', 'movement_type', 'quantity', 'reference', 'created_by')
    list_filter = ('movement_type', 'created_at', 'product')
    search_fields = ('product__name', 'reference', 'notes')
    readonly_fields = ('created_at', 'created_by')
    date_hierarchy = 'created_at'
    
    def product_link(self, obj):
        url = reverse('admin:inventory_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'
    product_link.admin_order_field = 'product__name'
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of stock movements as they affect inventory
        return False
    
    def get_actions(self, request):
        # Disable bulk delete
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


# Add custom admin site header
admin.site.site_header = 'Mini Inventory System Admin'
admin.site.site_title = 'Mini Inventory System'
admin.site.index_title = 'Welcome to Mini Inventory System Admin'

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import csv

from inventory.models import Product, Category, StockMovement
from pos.models import Sale, SaleItem

@login_required
def report_list(request):
    """Display a list of available reports"""
    return render(request, 'reports/report_list.html')

@login_required
def sales_report(request):
    """Generate sales report with filtering options"""
    # Default date range: last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get filter parameters
    date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
    date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
    
    # Convert string dates to date objects
    try:
        date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
        date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        date_from = start_date
        date_to = end_date
    
    # Get sales in date range
    sales = Sale.objects.filter(
        sale_date__date__gte=date_from,
        sale_date__date__lte=date_to
    ).order_by('-sale_date')
    
    # Calculate totals
    total_sales = sales.count()
    total_amount = sum(sale.total for sale in sales)
    
    context = {
        'sales': sales,
        'date_from': date_from,
        'date_to': date_to,
        'total_sales': total_sales,
        'total_amount': total_amount,
    }
    
    # Handle CSV export
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="sales_report_{date_from}_to_{date_to}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Sale #', 'Customer', 'Items', 'Subtotal', 'Tax', 'Total'])
        
        for sale in sales:
            writer.writerow([
                sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                sale.sale_number,
                str(sale.customer) if sale.customer else 'Walk-in',
                sum(item.quantity for item in sale.items.all()),
                sale.subtotal,
                sale.tax_amount,
                sale.total
            ])
        
        return response
    
    return render(request, 'reports/sales_report.html', context)

@login_required
def inventory_report(request):
    """Generate inventory status report"""
    # Get filter parameters
    category_id = request.GET.get('category')
    low_stock = 'low_stock' in request.GET
    out_of_stock = 'out_of_stock' in request.GET
    
    # Get products with related data
    products = Product.objects.select_related('category').all()
    
    # Apply filters
    if category_id:
        products = products.filter(category_id=category_id)
    
    if low_stock:
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=F('reorder_level'))
    
    if out_of_stock:
        products = products.filter(stock_quantity__lte=0)
    
    # Calculate inventory value
    inventory_value = sum(p.cost_price * p.stock_quantity for p in products)
    
    # Get categories for filter dropdown
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'inventory_value': inventory_value,
    }
    
    # Handle CSV export
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['SKU', 'Name', 'Category', 'Stock', 'Cost', 'Price', 'Status'])
        
        for product in products:
            status = 'In Stock'
            if product.stock_quantity <= 0:
                status = 'Out of Stock'
            elif product.stock_quantity <= product.reorder_level:
                status = 'Low Stock'
                
            writer.writerow([
                product.sku or '',
                product.name,
                str(product.category) if product.category else '',
                product.stock_quantity,
                product.cost_price,
                product.selling_price,
                status
            ])
        
        return response
    
    return render(request, 'reports/inventory_report.html', context)

@login_required
def purchases_report(request):
    """Generate purchases report"""
    # Similar structure to sales_report
    # Implementation depends on your purchase model
    return render(request, 'reports/coming_soon.html', {'report_name': 'Purchases Report'})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from inventory.models import Product, Category
from pos.models import Sale, SaleItem

@login_required
def dashboard(request):
    # Get current date and time
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Calculate statistics
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('reorder_level')).count()
    
    # Calculate today's sales
    today_sales = Sale.objects.filter(created_at__date=today).aggregate(
        total_sales=Sum('total') or 0,
        total_items=Count('items', distinct=True) or 0
    )
    
    # Calculate weekly sales
    weekly_sales = Sale.objects.filter(created_at__date__gte=last_week).aggregate(
        total_sales=Sum('total') or 0,
        total_orders=Count('id', distinct=True) or 0
    )
    
    # Get top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('saleitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    # Get recent sales
    recent_sales = Sale.objects.select_related('customer').order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'top_products': top_products,
        'recent_sales': recent_sales,
    }
    
    return render(request, 'frontend/dashboard.html', context)

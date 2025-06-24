from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.views.generic import RedirectView, FormView, View
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from inventory.models import Product, Category
from pos.models import Sale, SaleItem

class CustomLoginView(View):
    """Custom login view that handles authentication with better error handling"""
    template_name = 'frontend/registration/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('frontend:dashboard')
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            next_url = request.POST.get('next') or 'frontend:dashboard'
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, self.template_name, self.get_context_data())
    
    def get_context_data(self, **kwargs):
        context = {
            'next': self.request.GET.get('next', ''),
            'form': AuthenticationForm(),
        }
        context.update(kwargs)
        return context

@require_http_methods(["GET", "POST"])
def custom_logout(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.method == 'POST':
        auth_logout(request)
        messages.info(request, "You have been successfully logged out.")
        return redirect('frontend:login')
    
    # For GET requests, just show a confirmation page
    return render(request, 'frontend/logout_confirmation.html')

class LogoutView(RedirectView):
    """Handle logout with GET requests for backward compatibility"""
    url = reverse_lazy('frontend:login')
    
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            auth_logout(self.request)
            messages.info(self.request, "You have been successfully logged out.")
        return super().get_redirect_url(*args, **kwargs)

import json
from customers.models import Customer

@login_required
def dashboard(request):
    # Get current date and time
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Calculate statistics
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock_quantity__lte=F('reorder_level')).count()

    # Calculate total revenue (all time)
    total_revenue = Sale.objects.aggregate(total=Sum('total'))['total'] or 0

    # Calculate today's sales
    today_sales = Sale.objects.filter(created_at__date=today).aggregate(
        total_sales=Sum('total') or 0,
        total_items=Count('items', distinct=True) or 0
    )

    # Calculate yesterday's revenue
    yesterday = today - timedelta(days=1)
    yesterday_revenue = Sale.objects.filter(created_at__date=yesterday).aggregate(
        total=Sum('total')
    )['total'] or 0

    # Calculate weekly sales (last 7 days)
    weekly_sales = Sale.objects.filter(created_at__date__gte=last_week).aggregate(
        total_sales=Sum('total') or 0,
        total_orders=Count('id', distinct=True) or 0
    )

    # Get top selling products
    top_products = Product.objects.annotate(
        total_sold=Sum('saleitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]

    # Get recent sales for revenue history (last 7)
    revenue_history = Sale.objects.select_related('customer').order_by('-created_at')[:7]

    # Top 5 customers by total purchases
    top_customers = Customer.objects.annotate(
        total_spent=Sum('orders__total')
    ).order_by('-total_spent')[:5]

    # Prepare data for charts (last 7 days)
    sales_chart_labels = []
    sales_chart_data = []
    conversion_chart_data = []
    doughnut_chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        sales = Sale.objects.filter(created_at__date=day).aggregate(total=Sum('total'))['total'] or 0
        sales_chart_labels.append(day.strftime('%a'))
        sales_chart_data.append(float(sales))
        # Placeholder for conversion rate
        conversion_chart_data.append(round(0.4 + 0.02 * i, 2))
    # Doughnut: today's sales vs. rest of week
    week_total = sum(sales_chart_data)
    today_total = sales_chart_data[-1] if sales_chart_data else 0
    doughnut_chart_data = [today_total, max(week_total - today_total, 0)]

    # Quick fix: visits = unique users who placed orders today, conversion = 100%
    todays_visits = Sale.objects.filter(created_at__date=today).values('user').distinct().count()
    conversion_rate = 100.0

    context = {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_revenue': total_revenue,
        'today_sales': today_sales,
        'weekly_sales': weekly_sales,
        'top_products': top_products,
        'recent_sales': revenue_history,
        'top_customers': top_customers,
        'revenue_history': revenue_history,
        'sales_chart_labels': json.dumps(sales_chart_labels),
        'sales_chart_data': json.dumps(sales_chart_data),
        'conversion_chart_data': json.dumps(conversion_chart_data),
        'doughnut_chart_data': json.dumps(doughnut_chart_data),
        'conversion_rate': conversion_rate,
        'todays_visits': todays_visits,
        'yesterday_revenue': yesterday_revenue,
    }

    return render(request, 'frontend/dashboard.html', context)

@login_required
def dashboard_stats(request):
    """
    API endpoint to get dashboard statistics for AJAX updates
    """
    from django.db.models import Sum, Count, F
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    # Calculate statistics
    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock_quantity__lte=F('reorder_level')).count()
    
    # Calculate total revenue (all time)
    total_revenue = float(Sale.objects.aggregate(total=Sum('total'))['total'] or 0)
    
    # Calculate weekly sales
    weekly_sales = float(Sale.objects.filter(
        created_at__date__gte=last_week
    ).aggregate(total=Sum('total'))['total'] or 0)
    
    # Get total orders and pending orders
    total_orders = Sale.objects.count()
    pending_orders = Sale.objects.filter(status='pending').count()
    
    # Get total customers and new customers this month
    from customers.models import Customer
    total_customers = Customer.objects.count()
    
    first_day_of_month = today.replace(day=1)
    new_customers_this_month = Customer.objects.filter(
        date_joined__date__gte=first_day_of_month
    ).count()
    
    return JsonResponse({
        'total_revenue': total_revenue,
        'weekly_sales': weekly_sales,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_customers': total_customers,
        'new_customers_this_month': new_customers_this_month,
    })

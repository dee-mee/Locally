from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .models import Customer
from .forms import CustomerForm

@login_required
def customer_list(request):
    """Display a list of customers with search and filter options"""
    query = request.GET.get('q', '')
    customer_type = request.GET.get('type', '')
    
    customers = Customer.objects.all()
    
    # Apply search
    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )
    
    # Apply filters
    if customer_type:
        customers = customers.filter(customer_type=customer_type)
    
    # Ordering
    customers = customers.order_by('first_name', 'last_name')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(customers, 25)  # Show 25 customers per page
    
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
    
    context = {
        'customers': customers,
        'query': query,
        'customer_type': customer_type,
        'customer_types': dict(Customer.CUSTOMER_TYPES),
    }
    
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_detail(request, pk):
    """Display details of a specific customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Get recent transactions (you'll need to implement this based on your models)
    recent_transactions = []  # Replace with actual query
    
    context = {
        'customer': customer,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, _('Customer created successfully.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': _('Add New Customer'),
    }
    
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_edit(request, pk):
    """Edit an existing customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_by = request.user
            customer.save()
            messages.success(request, _('Customer updated successfully.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'customer': customer,
        'title': _('Edit Customer'),
    }
    
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    """Delete a customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, _('Customer deleted successfully.'))
        return redirect('customers:customer_list')
    
    context = {
        'customer': customer,
        'title': _('Delete Customer'),
    }
    
    return render(request, 'customers/customer_confirm_delete.html', context)

def customer_import(request):
    """Import customers from CSV/Excel"""
    if request.method == 'POST':
        # Handle file upload and import
        # This is a placeholder - implement actual import logic
        messages.success(request, _('Customers imported successfully.'))
        return redirect('customers:customer_list')
    
    return render(request, 'customers/customer_import.html')

def customer_export(request):
    """Export customers to CSV/Excel"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers_export.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'First Name', 'Last Name', 'Email', 'Phone', 'Company', 
        'Customer Type', 'Address', 'City', 'State', 'Postal Code', 'Country', 'Tax ID'
    ])
    
    # Write data
    customers = Customer.objects.all()
    for customer in customers:
        writer.writerow([
            customer.first_name,
            customer.last_name or '',
            customer.email or '',
            customer.phone or '',
            customer.company_name or '',
            customer.get_customer_type_display(),
            customer.address or '',
            customer.city or '',
            customer.state or '',
            customer.postal_code or '',
            customer.country or '',
            customer.tax_number or '',
        ])
    
    return response

# API Views
@login_required
def api_customer_search(request):
    """API endpoint for searching customers"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    customers = Customer.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(company_name__icontains=query) |
        Q(email__iexact=query) |
        Q(phone__icontains=query)
    ).filter(is_active=True)[:10]
    
    results = [{
        'id': c.id,
        'text': f"{c.first_name} {c.last_name}" + (f" ({c.company_name})" if c.company_name else ''),
        'name': f"{c.first_name} {c.last_name}",
        'company': c.company_name or '',
        'email': c.email or '',
        'phone': c.phone or '',
    } for c in customers]
    
    return JsonResponse({'results': results})

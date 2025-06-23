from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Count, F
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from inventory.models import Product, Category
from .models import Sale, SaleItem, Order, OrderItem, Payment
from .pos_settings import *

# Import the pos_settings module to access POS settings
try:
    from . import pos_settings as pos_conf
except ImportError:
    pos_conf = None

class DashboardView(LoginRequiredMixin, TemplateView):
    """POS Dashboard View"""
    template_name = 'pos/pos_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories for the product filter
        categories = Category.objects.all()
        
        # Get products with stock > 0 or based on settings
        if getattr(settings, 'POS_ALLOW_OUT_OF_STOCK', False):
            products = Product.objects.all()
        else:
            products = Product.objects.filter(stock_quantity__gt=0)
            
        # Apply search filter if provided
        search_query = self.request.GET.get('q', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(sku__iexact=search_query) |
                Q(barcode__iexact=search_query)
            )
        
        # Apply category filter if provided
        category_id = self.request.GET.get('category')
        if category_id:
            products = products.filter(categories__id=category_id)
        
        # Pagination
        paginator = Paginator(products, getattr(settings, 'POS_ITEMS_PER_PAGE', 24))
        page = self.request.GET.get('page')
        
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        
        # Get current open order for the user
        current_order = Order.objects.filter(
            user=self.request.user,
            status=Order.ORDER_STATUS_OPEN
        ).first()
        
        # If no open order, create one
        if not current_order and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            current_order = Order.objects.create(
                user=self.request.user,
                status=Order.ORDER_STATUS_OPEN
            )
        
        context.update({
            'products': products,
            'categories': categories,
            'current_order': current_order,
            'tax_rate': getattr(settings, 'POS_DEFAULT_TAX_RATE', 0.0),
            'currency': getattr(settings, 'POS_CURRENCY', '$'),
            'enable_barcode_scanner': getattr(settings, 'POS_ENABLE_BARCODE_SCANNER', True),
        })
        
        return context


def sale_list(request):
    """List all sales"""
    sales = Sale.objects.all().order_by('-sale_date')
    return render(request, 'pos/sale_list.html', {'sales': sales})

def sale_create(request):
    """Create a new sale"""
    if request.method == 'POST':
        # Handle sale creation
        pass
    return render(request, 'pos/sale_form.html')

def sale_detail(request, pk):
    """View details of a specific sale"""
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'pos/sale_detail.html', {'sale': sale})

def sale_print(request, pk):
    """Generate a printable receipt for a sale"""
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'pos/sale_receipt.html', {'sale': sale})

def sale_refund(request, pk):
    """Process a refund for a sale"""
    if request.method == 'POST':
        # Handle refund logic
        pass
    return redirect('pos:sale_detail', pk=pk)

@login_required
def api_product_search(request):
    """API endpoint for searching products"""
    query = request.GET.get('q', '')
    barcode = request.GET.get('barcode')
    
    if not query and not barcode:
        return JsonResponse({'error': 'No search query provided'}, status=400)
    
    products = Product.objects.all()
    
    if barcode:
        products = products.filter(barcode=barcode)
    else:
        products = products.filter(
            Q(name__icontains=query) |
            Q(sku__iexact=query) |
            Q(barcode__iexact=query)
        )
    
    # Apply stock filter if needed
    if not getattr(settings, 'POS_ALLOW_OUT_OF_STOCK', False):
        products = products.filter(stock_quantity__gt=0)
    
    products = products[:10]  # Limit to 10 results
    
    results = [{
        'id': p.id,
        'name': p.name,
        'sku': p.sku,
        'barcode': p.barcode,
        'price': str(p.price),
        'stock': p.stock_quantity,
        'image': p.image.url if p.image else '',
        'category': p.category.name if p.category else '',
        'taxable': p.is_taxable,
        'description': p.description or ''
    } for p in products]
    
    return JsonResponse({'products': results})


@login_required
def add_to_cart(request):
    """Add a product to the cart"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            product = Product.objects.get(id=product_id)
            
            # Check if product is in stock if not allowing out of stock
            if not getattr(settings, 'POS_ALLOW_OUT_OF_STOCK', False) and product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Not enough stock. Only {product.stock_quantity} available.'
                }, status=400)
                
            # Get or create order
            order, created = Order.objects.get_or_create(
                user=request.user,
                status=Order.ORDER_STATUS_OPEN,
                defaults={
                    'subtotal': 0,
                    'tax_amount': 0,
                    'total': 0,
                    'tax_rate': getattr(settings, 'POS_DEFAULT_TAX_RATE', 0.0)
                }
            )
            
            # Add or update order item
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price': product.price,
                    'taxable': product.is_taxable
                }
            )
            
            if not created:
                order_item.quantity += quantity
                order_item.save()
            
            # Update order totals
            order.update_totals()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart',
                'order_total': order.total,
                'item_count': order.items.count()
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__user=request.user,
                order__status=Order.ORDER_STATUS_OPEN
            )
            
            # Check stock if not allowing out of stock
            if not getattr(settings, 'POS_ALLOW_OUT_OF_STOCK', False) and item.product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'message': f'Not enough stock. Only {item.product.stock_quantity} available.'
                }, status=400)
            
            item.quantity = quantity
            item.save()
            
            # Update order totals
            item.order.update_totals()
            
            return JsonResponse({
                'success': True,
                'message': 'Cart updated',
                'item_total': item.total,
                'order_total': item.order.total,
                'subtotal': item.order.subtotal,
                'tax_amount': item.order.tax_amount
            })
            
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def remove_cart_item(request, item_id):
    """Remove item from cart"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__user=request.user,
                order__status=Order.ORDER_STATUS_OPEN
            )
            
            order = item.order
            item.delete()
            
            # Update order totals
            order.update_totals()
            
            return JsonResponse({
                'success': True,
                'message': 'Item removed from cart',
                'order_total': order.total,
                'item_count': order.items.count()
            })
            
        except OrderItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def checkout(request):
    """Process checkout"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            order = Order.objects.get(
                user=request.user,
                status=Order.ORDER_STATUS_OPEN
            )
            
            # Validate order
            if order.items.count() == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Cannot checkout with an empty cart'
                }, status=400)
            
            # Get payment details
            payment_method = request.POST.get('payment_method', 'cash')
            amount_tendered = float(request.POST.get('amount_tendered', 0))
            
            # Validate payment
            if payment_method == 'cash' and amount_tendered < order.total:
                return JsonResponse({
                    'success': False,
                    'message': 'Insufficient payment',
                    'amount_required': order.total - amount_tendered
                }, status=400)
            
            # Process payment
            with transaction.atomic():
                # Create payment
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total,
                    payment_method=payment_method,
                    amount_tendered=amount_tendered,
                    change_given=max(0, amount_tendered - order.total) if payment_method == 'cash' else 0,
                    processed_by=request.user
                )
                
                # Update order status
                order.status = Order.ORDER_STATUS_COMPLETED
                order.payment_status = Order.PAYMENT_STATUS_PAID
                order.completed_at = timezone.now()
                order.save()
                
                # Update inventory if enabled
                if getattr(settings, 'POS_UPDATE_INVENTORY', True):
                    for item in order.items.all():
                        if item.product.track_inventory:
                            item.product.stock_quantity -= item.quantity
                            item.product.save()
            
            # Generate receipt
            receipt_url = reverse('pos:receipt', kwargs={'pk': order.id})
            
            return JsonResponse({
                'success': True,
                'message': 'Order completed successfully',
                'order_id': order.id,
                'receipt_url': receipt_url,
                'print_url': reverse('pos:print_receipt', kwargs={'pk': order.id})
            })
            
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No active order found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

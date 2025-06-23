from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.apps import apps

@login_required
def view_receipt(request, pk):
    """View a receipt for a completed order"""
    Order = apps.get_model('pos', 'Order')
    Payment = apps.get_model('pos', 'Payment')
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    # Only allow viewing receipts for completed orders
    if order.status != Order.ORDER_STATUS_COMPLETED:
        messages.error(request, _('Cannot view receipt for an uncompleted order'))
        return redirect('pos:dashboard')
    
    # Get the payment information
    payment = order.payments.filter(status=Payment.PAYMENT_STATUS_COMPLETED).first()
    
    context = {
        'order': order,
        'payment': payment,
        'title': _('Receipt'),
        'store_name': getattr(settings, 'STORE_NAME', 'My Store'),
        'store_address': getattr(settings, 'STORE_ADDRESS', ''),
        'store_phone': getattr(settings, 'STORE_PHONE', ''),
        'store_email': getattr(settings, 'STORE_EMAIL', ''),
        'store_website': getattr(settings, 'STORE_WEBSITE', ''),
        'tax_identification_number': getattr(settings, 'TAX_IDENTIFICATION_NUMBER', ''),
        'currency': getattr(settings, 'CURRENCY', '$'),
        'show_tax_identification': getattr(settings, 'SHOW_TAX_IDENTIFICATION', False),
        'show_payment_method': getattr(settings, 'SHOW_PAYMENT_METHOD', True),
        'show_change_due': getattr(settings, 'SHOW_CHANGE_DUE', True),
        'show_cashier_name': getattr(settings, 'SHOW_CASHIER_NAME', True),
        'show_thank_you_message': getattr(settings, 'SHOW_THANK_YOU_MESSAGE', True),
        'thank_you_message': getattr(settings, 'THANK_YOU_MESSAGE', _('Thank you for your business!')),
        'show_return_policy': getattr(settings, 'SHOW_RETURN_POLICY', True),
        'return_policy': getattr(settings, 'RETURN_POLICY', _('Items can be returned within 14 days with receipt.')),
    }
    
    return render(request, 'pos/includes/receipt.html', context)

@login_required
def print_receipt(request, pk):
    """Print a receipt for a completed order"""
    Order = apps.get_model('pos', 'Order')
    Payment = apps.get_model('pos', 'Payment')
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    # Only allow printing receipts for completed orders
    if order.status != Order.ORDER_STATUS_COMPLETED:
        messages.error(request, _('Cannot print receipt for an uncompleted order'))
        return redirect('pos:dashboard')
    
    # Get the payment information
    payment = order.payments.filter(status=Payment.PAYMENT_STATUS_COMPLETED).first()
    
    context = {
        'order': order,
        'payment': payment,
        'title': _('Receipt'),
        'store_name': getattr(settings, 'STORE_NAME', 'My Store'),
        'store_address': getattr(settings, 'STORE_ADDRESS', ''),
        'store_phone': getattr(settings, 'STORE_PHONE', ''),
        'store_email': getattr(settings, 'STORE_EMAIL', ''),
        'store_website': getattr(settings, 'STORE_WEBSITE', ''),
        'tax_identification_number': getattr(settings, 'TAX_IDENTIFICATION_NUMBER', ''),
        'currency': getattr(settings, 'CURRENCY', '$'),
        'show_tax_identification': getattr(settings, 'SHOW_TAX_IDENTIFICATION', False),
        'show_payment_method': getattr(settings, 'SHOW_PAYMENT_METHOD', True),
        'show_change_due': getattr(settings, 'SHOW_CHANGE_DUE', True),
        'show_cashier_name': getattr(settings, 'SHOW_CASHIER_NAME', True),
        'show_thank_you_message': getattr(settings, 'SHOW_THANK_YOU_MESSAGE', True),
        'thank_you_message': getattr(settings, 'THANK_YOU_MESSAGE', _('Thank you for your business!')),
        'show_return_policy': getattr(settings, 'SHOW_RETURN_POLICY', True),
        'return_policy': getattr(settings, 'RETURN_POLICY', _('Items can be returned within 14 days with receipt.')),
        'print_only': True,  # Flag to indicate this is for printing
    }
    
    # Render the receipt as plain text for printing
    receipt_text = render_to_string('pos/includes/receipt.txt', context)
    
    # Create a response with the receipt text
    response = HttpResponse(receipt_text, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="receipt-{order.order_number}.txt"'
    
    return response

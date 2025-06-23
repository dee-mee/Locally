from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .receipt_views import view_receipt, print_receipt

app_name = 'pos'

urlpatterns = [
    # POS Dashboard
    path('', login_required(views.DashboardView.as_view()), name='dashboard'),
    
    # Cart Operations
    path('api/cart/add/', login_required(views.add_to_cart), name='add_to_cart'),
    path('api/cart/update/<int:item_id>/', login_required(views.update_cart_item), name='update_cart_item'),
    path('api/cart/remove/<int:item_id>/', login_required(views.remove_cart_item), name='remove_cart_item'),
    path('api/checkout/', login_required(views.checkout), name='checkout'),
    
    # Product Search
    path('api/products/', login_required(views.api_product_search), name='api_product_search'),
    
    # Sales History
    path('sales/', login_required(views.sale_list), name='sale_list'),
    path('sale/create/', login_required(views.sale_create), name='sale_create'),
    path('sale/<int:pk>/', login_required(views.sale_detail), name='sale_detail'),
    path('sale/<int:pk>/print/', login_required(views.sale_print), name='sale_print'),
    path('sale/<int:pk>/refund/', login_required(views.sale_refund), name='sale_refund'),
    
    # Receipts
    path('receipt/<int:pk>/', login_required(view_receipt), name='receipt'),
    path('receipt/<int:pk>/print/', login_required(print_receipt), name='print_receipt'),
]

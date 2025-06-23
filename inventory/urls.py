from django.urls import path
from django.contrib.auth.decorators import permission_required

from . import views

app_name = 'inventory'

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', 
         permission_required('inventory.add_category')(views.CategoryCreateView.as_view()),
         name='category_add'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<slug:slug>/edit/', 
         permission_required('inventory.change_category')(views.CategoryUpdateView.as_view()),
         name='category_edit'),
    path('categories/<slug:slug>/delete/', 
         permission_required('inventory.delete_category')(views.CategoryDeleteView.as_view()),
         name='category_delete'),
    
    # Product URLs
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', 
         permission_required('inventory.add_product')(views.ProductCreateView.as_view()),
         name='product_add'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', 
         permission_required('inventory.change_product')(views.ProductUpdateView.as_view()),
         name='product_edit'),
    path('products/<int:pk>/delete/', 
         permission_required('inventory.delete_product')(views.ProductDeleteView.as_view()),
         name='product_delete'),
    path('products/<int:product_id>/adjust-stock/', 
         permission_required('inventory.change_product')(views.adjust_stock),
         name='adjust_stock'),
    path('products/import/', 
         permission_required('inventory.add_product')(views.import_products),
         name='import_products'),
    
    # AJAX Endpoints
    path('ajax/product-search/', views.ajax_product_search, name='ajax_product_search'),
    path('ajax/product/<int:product_id>/', views.ajax_get_product, name='ajax_get_product'),
    
    # Reports
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/stock-movements/', views.stock_movements_report, name='stock_movements_report'),
    
    # Bulk Actions
    path('products/bulk-action/', 
         permission_required('inventory.change_product')(views.ProductBulkActionView.as_view()),
         name='product_bulk_action'),
]

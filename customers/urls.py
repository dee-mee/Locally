from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='customer_list'),
    path('add/', views.customer_create, name='customer_create'),
    path('quick-add/', views.customer_create, name='customer_quick_add'),  # For quick add from POS
    path('<int:pk>/', views.customer_detail, name='customer_detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('import/', views.customer_import, name='customer_import'),
    path('export/', views.customer_export, name='customer_export'),
    path('api/search/', views.api_customer_search, name='customer_search'),
]

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Reports URLs will be added here
    path('', views.report_list, name='report_list'),
    path('sales/', views.sales_report, name='sales_report'),
    path('inventory/', views.inventory_report, name='inventory_report'),
    path('purchases/', views.purchases_report, name='purchases_report'),
]

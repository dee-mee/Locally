"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # Frontend app (includes auth URLs)
    path('', include('frontend.urls', namespace='frontend')),
    
    # POS app
    path('pos/', include('pos.urls', namespace='pos')),
    
    # Inventory app
    path('inventory/', include('inventory.urls', namespace='inventory')),
    
    # Reports app
    path('reports/', include('reports.urls', namespace='reports')),
    
    # Authentication URLs (handled by frontend app)
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='frontend/registration/password_reset.html',
             email_template_name='frontend/registration/password_reset_email.html',
             subject_template_name='frontend/registration/password_reset_subject.txt',
             success_url='done/'
         ),
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='frontend/registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='frontend/registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='frontend/registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

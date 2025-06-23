from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'frontend'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),  # This is the main dashboard
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='frontend/registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('logout/confirm/', views.LogoutView.as_view(), name='logout_confirm'),
    
    # Add other frontend URLs here
]

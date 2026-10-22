from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.homepage, name='home'),
    path('register/', views.register_view, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('agent/', views.agent_dashboard, name='agent_dashboard'),
    path('scrap/', TemplateView.as_view(template_name='index.html'), name='scrap_dashboard'),
    path('admins/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('manage-operations/', views.manage_operations, name='manage_operations'),
    path('delete-material/<int:material_id>/', views.delete_material, name='delete_material'),
    path('delete-byproduct/<int:byproduct_id>/', views.delete_byproduct, name='delete_byproduct'),
    path('api/current-user/', views.api_current_user, name='api_current_user'),
]
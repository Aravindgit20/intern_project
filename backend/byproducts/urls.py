from django.urls import path
from . import views

urlpatterns = [
    path('api/scrap-byproducts/', views.api_scrap_byproducts, name='api_scrap_byproducts'),
    path('api/update-byproduct/', views.api_update_byproduct, name='api_update_byproduct'),
]

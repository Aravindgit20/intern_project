from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_material, name='submit_material'),
    path('submission/', views.my_submissions, name='my_submissions'),
    path('api/my-submissions/', views.api_my_submissions, name='api_my_submissions'),
    path('api/submit-material/', views.api_submit_material, name='api_submit_material'),
]

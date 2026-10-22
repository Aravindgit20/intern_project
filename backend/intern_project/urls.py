from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    # =========================================================
    # APP URLS
    # =========================================================

    path(
        '',
        include('app.urls')
    ),

    path(
        '',
        include('processing.urls')
    ),

    path(
        '',
        include('byproducts.urls')
    ),

    # =========================================================
    # REACT AGENT DASHBOARD
    # =========================================================

    path(
        'react-agent/',
        TemplateView.as_view(
            template_name='index.html'
        )
    ),

    # =========================================================
    # REACT SCRAP TEAM DASHBOARD
    # =========================================================

    path(
        'react-scrap/',
        TemplateView.as_view(
            template_name='index.html'
        )
    ),
]
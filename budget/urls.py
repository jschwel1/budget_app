"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include, path, re_path
from . import views

app_name='budget'

urlpatterns = [
    path(r'', views.home_page, name='home'),
    re_path(r'^config/$', views.config_page, name='config'),
    re_path(r'^overview/(?P<page>[\d]*)?/?$', views.overview_page, name='overview'),
    re_path(r'^login/$', views.login_page, name='login'),
    re_path(r'^logout/$', views.logout_page, name='logout'),
    re_path(r'^get_overview_data/(?P<page>[\d]*)?/$', views.get_overview_data, name='get_overview_data'),
    re_path(r'^get_individual_overview_data/(?P<bank>[0-9a-zA-Z]+)$', views.get_individual_overview_data, name='get_individual_overview_data'),
    re_path(r'^export_transactions_to_csv/$', views.export_tx_as_csv, name='export_transactions_to_csv'),
    re_path(r'^monthly_overview/$',views.monthly_overview, name='monthly_overview'),
    re_path(r'^budget_status/$',views.monthly_overview, name='budget_status'),
    re_path(r'^recalc_values/$',views.recalculate_all, name='recalculate_all'),
    path(r'base', views.load_base, name='base'),
]

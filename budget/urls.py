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
    re_path(r'^overview/$', views.overview_page, name='overview'),
    re_path(r'^login/$', views.login_page, name='login'),
    re_path(r'^logout/$', views.logout_page, name='logout'),
    path(r'base', views.load_base, name='base'),
]

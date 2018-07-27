from django.shortcuts import render

# Create your views here.

def home_page(request):
    context = {}
    return render(request, 'budget/index.html', context)

def load_base(request):
    return render(request, 'budget/base.html')

def config_page(request):
    context = {}
    return render(request, 'budget/config.html', context)

def overview_page(request):
    context = {}
    return render(request, 'budget/overview.html', context)


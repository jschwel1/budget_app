from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from .models import Bank, Category, Transaction, Budget, BudgetCategory
from .forms import TransactionForm

# Create your views here.


def home_page(request):
    context = {}
    return render(request, 'budget/index.html', context)

def login_page(request):
    context = {}
    if request.method == 'POST':
        username=request.POST.get('username','')
        password=request.POST.get('password','')
        error_msg=''
          
        # Register 
        if request.POST.get('register','') != '':
            try:
                User.create(username=username,password=password)
                login(request,user)
                return redirect('budget:home')
            except:
                error_msg='username already taken'
        # login
        else:
            user=authenticate(username=username, password=password)
            if user == None:
                error_msg='invalid username or password'
            else:
                login(request,user)
                return redirect('budget:home')
        context = {
            'username': username,
            'error_msg':error_msg,
        } 
    return render(request, 'budget/login.html', context)

@login_required
def logout_page(request):
    context = {}
    logout(request)
    return render(request, 'budget/logout.html', context)

@login_required
def load_base(request):
    return render(request, 'budget/base.html')

@login_required
def config_page(request):
    context = {}
    return render(request, 'budget/config.html', context)

@login_required
def overview_page(request):
    context = {}
    user = get_user(request)
    all_transactions = Transaction.objects.filter(user__exact=user).order_by('date')
    tx_form = TransactionForm()
    context = {
        'all_transactions': all_transactions,
        'tx_form': tx_form,
    }
    return render(request, 'budget/overview.html', context)


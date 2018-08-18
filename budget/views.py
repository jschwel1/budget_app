from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from .models import Bank, Category, Transaction, Budget, BudgetCategory
from .forms import TransactionForm
import traceback

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
    pk = ''
    if request.method == 'POST':
        tx_form = TransactionForm(user, request.POST)#, user=get_user(request))
        if tx_form.is_valid:
            # New Entry
            if request.POST.get('submit_new','') != '':
                try:
                    print('just started')
                    transaction = tx_form.save(commit=False)
                    print('saved')
                    category = Category.objects.filter(user__exact=get_user(request)).get(category__exact=transaction.category)
                    transaction.category = category
                    transaction.user=user
                    print(transaction)
                    transaction.save()
                except BaseException as e:
                    print(str(type(e)),': ', e)
            elif request.POST.get('update','') != '':
                pk = request.POST.get('pk','')
                try:
                    transaction = tx_form.save(commit=False)
                    original = Transaction.objects.get(pk=pk)
                    # confirm the user is correct
                    if (original.user == get_user(request)):
                        transaction.user = user
                        transaction.pk = pk
                        transaction.save()
                except BaseException as e:
                    print(str(type(e)),': ', e)
                    traceback.print_exc()
            # delete entry
            else:
                pk = request.POST.get('pk')
                try:
                    # Get list as displayed
                    tx_list = list(Transaction.objects.filter(user__exact=user).order_by('-date'))
                    tx_user = Transaction.objects.get(pk=pk).user
                    if (tx_user == user):
                        # Get the index of the element in the list
                        idx = tx_list.index(Transaction.objects.get(pk=pk))
                        Transaction.objects.get(pk=pk).delete()
                        del tx_list[idx]

                        if (idx >= len(tx_list)):
                            tx_form = TransactionForm(user=user, instance=tx_list[-1])
                            pk = tx_list[-1].id
                        else:
                            tx_form = TransactionForm(user=user, instance=tx_list[idx])
                            pk = tx_list[idx].id
                    
                except BaseException as e:
                    print(str(type(e)),': ', e)
                    traceback.print_exc()
                    pk = ''
                    tx_form = TransactionForm(user=user)
    else:
        tx_form = TransactionForm(user=user)
    all_transactions = Transaction.objects.filter(user__exact=user).order_by('-date')
    # Update transaction amounts to strings with parens for negatives
    locations = []
    for tx in all_transactions:
        if tx.amount < 0:
            tx.amount = '('+str(-1*tx.amount)+')'
        else:
            tx.amount = str(tx.amount)

        locations.append(tx.location)
    
    all_banks = Bank.objects.all()
    for bank in all_banks:
        locations.append(str(bank.name))
    locations = sorted(list(set(locations)))
    all_categories = Category.objects.filter(user__exact=user)
    context = {
        'all_transactions': all_transactions,
        'tx_form': tx_form,
        'all_banks': all_banks,
        'locations': locations,
        'all_categories': all_categories,
        'pk': pk,
    }
    return render(request, 'budget/overview.html', context)


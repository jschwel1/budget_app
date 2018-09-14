from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from .models import Bank, Category, Transaction, Budget, BudgetCategory
from .forms import TransactionForm, UploadFileForm
import traceback, json, re

# Create your views here.


def home_page(request):
    context = {}
    return render(request, 'budget/index.html', context)

def login_page(request):
    context = {}
    if request.method == 'POST':
        username=request.POST.get('username','')
        context['username'] = username
        password=request.POST.get('password','')
        error_msg=''
          
        # Register
        if request.POST.get('register','') != '':
            try:
                context['register'] = True
                firstname = request.POST.get('firstname','')
                context['firstname'] = firstname
                lastname = request.POST.get('lastname','')
                context['lastname'] = lastname
                email = request.POST.get('email','')
                context['email'] = email
                user = User.objects.create_user(username,
                                                email,
                                                password)
                user.last_name = lastname
                user.first_name = firstname
                user.save()
                login(request,user)
                # Create Income and Transfer categories
                Category.objects.create(category='Transfer',user=user)
                Category.objects.create(category='Income',user=user)
                return redirect('budget:home')
            except:
                error_msg='username already taken'
                context['error_msg'] = error_msg
        # login
        else:
            user=authenticate(username=username, password=password)
            if user == None:
                error_msg='invalid username or password'
                context['login'] = True
            else:
                login(request,user)
                return redirect('budget:home')
        context['username'] = username
        context['error_msg'] = error_msg
    else:
        context['login'] = True
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
    user = get_user(request)
    # Get all configurable data
    if request.method == 'POST':
        # Categories
        # Add new categories (if blank or disabled, ignore)
        new_categories = {nc:request.POST.get(nc, '')
                            for nc in request.POST
                            if nc.startswith('new__')}
                            
        existing_categories = {ec:request.POST.get(ec, '')
                            for ec in request.POST
                            if ec.startswith('existing__')}
        
        for nc in new_categories:
            nc_name = request.POST.get(nc,'');
            # If the new category is enabled and not empty
            if nc_name != '' and request.POST.get('new__'+nc_name+'__enabled', '') != '':
                if (len(Category.objects.filter(user=user).filter(category__iexact=nc_name))==0):
                    new_cat = Category(category=nc_name, user=user)
                    new_cat.save()
            
        # Update existing ones (if they changed)
        for ec in existing_categories:
            if (ec.endswith('enabled')): continue
            cat_id = re.split('existing__(\d+)__category', ec)[1]
            name = request.POST.get(ec, '')
            isEnabled = request.POST.get('existing__'+cat_id+'__enabled', '')
            # If entire category is deleted, disabled, and there are no transactions for it, it can be removed
            if (name == '' and isEnabled == ''):
                if(len(Transaction.objects.filter(category__id=int(cat_id))) == 0):
                    Category.objects.get(id=cat_id).delete()
            else:
                # If the name changed, update it
                if (name != Category.objects.get(id=int(cat_id)).category):
                    if (name != '' and len(Category.objects.filter(user=user).filter(category__exact=name)) == 0):
                        cat = Category.objects.get(id=int(cat_id))
                        cat.category = name;
                        cat.save()
                if (isEnabled != ''):
                    cat = Category.objects.get(id=int(cat_id))
                    cat.enabled = True
                    cat.save()
                else:
                    cat = Category.objects.get(id=int(cat_id))
                    cat.enabled = False
                    cat.save()
                
        # Banks
        
        # Budgets
    
    all_categories = Category.objects.filter(user=user)
    context = {
        'all_categories': all_categories,
    }
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
                    transaction = tx_form.save(commit=False)
                    category = Category.objects.filter(user__exact=get_user(request)).get(category__exact=transaction.category)
                    transaction.category = category
                    transaction.user=user
                    transaction.save()
                except BaseException as e:
                    print(str(type(e)),': ', e)
                    traceback.print_exc()
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
            elif request.POST.get('delete','') != '':
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
            elif request.POST.get('upload_bulk', '') != '':
               pass
    else:
        tx_form = TransactionForm(user=user)
    
    
    all_transactions = Transaction.objects.filter(user__exact=user).order_by('-date')
    # Update transaction amounts to strings with parens for negatives
    locations = []
    for tx in all_transactions:
        locations.append(tx.location)
    
    all_banks = Bank.objects.filter(user=user)
    for bank in all_banks:
        locations.append(str(bank.name))
    locations = sorted(list(set(locations)))
    all_categories = Category.objects.filter(user__exact=user)
    
    context = {
        'tx_form': tx_form,
        'all_banks': all_banks,
        'locations': locations,
        'all_categories': all_categories,
        'file_form': UploadFileForm(),
    }
    return render(request, 'budget/overview.html', context)


@login_required
def get_overview_data(request, bank=None):
    user = get_user(request)
    
    if (bank == None):
        all_transactions = Transaction.objects.filter(user__exact=user).order_by('date') # reversed, but will be flipped after calculations
        all_banks = Bank.objects.filter(user=user)
    else:
        
        all_transactions = Transaction.objects.filter(user__exact=user)\
                                .filter(Q(location__exact=bank)|Q(card_used__name__exact=bank))\
                                .order_by('date') # reversed, but will be flipped after calculations
        all_banks = Bank.objects.filter(user=user).filter(name__exact=bank)
        
    all_categories = Category.objects.filter(user__exact=user)
    
    # Get net and bank values
    net_and_bank = {'net': 0.0}
    bank_lookup = {}
    for bank in all_banks:
        net_and_bank[bank.name] = bank.starting_amount
    
    tx_list = []
    for tx in all_transactions:
        cur_tx = vars(tx)
        # Add all the banks
        cur_tx['net'] = net_and_bank['net']
        for bank in all_banks:
            cur_tx[bank.name] = net_and_bank[bank.name]
        cur_tx['card_used'] = str(tx.card_used)
        cur_tx['category'] = str(tx.category)
        cur_tx['date'] = str(tx.date.strftime('%B %d, %Y'))
        # category == transfer -> check from and to, don't update net (to should be a bank)
        if cur_tx['category'].lower() == 'transfer':
            loc = tx.location # to
            card_used = tx.card_used.name # from
            
            try:
                cur_tx[loc] += tx.amount
                net_and_bank[loc] = cur_tx[loc]
                cur_tx[card_used] -= tx.amount
                net_and_bank[card_used] = cur_tx[card_used]
            except BaseException as e:
                print('loc:', loc)
                print('cur_tx:', cur_tx)
                print(type(e), e)
                traceback.print_exc()
        # category == income -> check bank to
        elif cur_tx['category'].lower() == 'income':
            to = tx.card_used.name
            try:
                cur_tx[to] += tx.amount
                net_and_bank[to] = cur_tx[to]
                cur_tx['net'] += float(tx.amount)
                cur_tx['net'] = round(cur_tx['net'],2)
                net_and_bank['net'] = cur_tx['net']
            except BaseException as e:
                print(type(e), e)
                traceback.print_exc()
                
        # category == anything else -> check bank from
        else:
            card_used = tx.card_used.name
            try:
                cur_tx[card_used] -= tx.amount
                net_and_bank[card_used] = cur_tx[card_used]
                cur_tx['net'] -= float(tx.amount)
                cur_tx['net'] = round(cur_tx['net'],2)
                net_and_bank['net'] = cur_tx['net']
            except BaseException as e:
                print(type(e), e)
                traceback.print_exc()
        
        for bank in all_banks:
            if (cur_tx[bank.name] < 0):
                cur_tx[bank.name] = '$(' + str(-1*cur_tx[bank.name]) + ')'
            else:
                cur_tx[bank.name] = '$' + str(cur_tx[bank.name])
        if (cur_tx['net'] < 0):
            cur_tx['net'] = '$(' + str(-1*cur_tx['net']) + ')'
        else:
            cur_tx['net'] = '$' + str(cur_tx['net'])
        
        if tx.amount < 0:
            cur_tx['amount'] = '$('+str(-1*cur_tx['amount'])+')'
        else:
            cur_tx['amount'] = '$'+str(cur_tx['amount'])
        
        tx_list.append(cur_tx)
        del cur_tx['_state']
        
    tx_list.reverse()
    return JsonResponse({'transactions':tx_list})
    

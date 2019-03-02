from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, get_user
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.template import Context, loader
from .models import Bank, Category, Transaction, Budget, BudgetCategory, TransactionBankAmount
from .forms import TransactionForm, UploadFileForm
from .extra_functions import *
import traceback, json, re, csv, datetime
from sys import platform
from .extra_functions import *
import datetime
import time
import math

# Create your views here.

'''
========================== HOME PAGE ==========================
'''
def home_page(request):
    context = {}
    return render(request, 'budget/index.html', context)


'''
========================== LOGIN PAGE ==========================  
'''
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
                # Create Net bank
                Bank.objects.create(starting_amount=0.00, name='Net', user=user, display=False)
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


'''
========================== LOGOUT PAGE ==========================  
'''
@login_required
def logout_page(request):
    context = {}
    logout(request)
    return render(request, 'budget/logout.html', context)


'''
========================== Base Page PAGE ==========================  
'''
@login_required
def load_base(request):
    return render(request, 'budget/base.html')


'''
========================== CONFIG PAGE ==========================  
'''
@login_required
def config_page(request):
    context = {}
    user = get_user(request)
    # Get all configurable data
    # Categories
    if request.method == 'POST' and request.POST.get('submit_categories','') != '':
        # Add new categories (if blank or disabled, ignore)
        new_categories = {  nc:request.POST.get(nc, '')
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
    if request.method == 'POST' and request.POST.get('submit_banks','') != '':
        new_banks = {  nb:request.POST.get(nb, '')
                            for nb in request.POST
                            if (nb.startswith('new__') and nb.endswith('__name'))}
                            
        existing_banks = {eb:request.POST.get(eb, '')
                            for eb in request.POST
                            if eb.startswith('existing__') and eb.endswith('__bank')}
        # Add new banks
        print('New Banks:', new_banks)
        for nb in new_banks:
            nb_name = request.POST.get(nb,'')
            nb_starting_amount = request.POST.get('new__'+nb_name+'__starting_amount', '')
            if (nb_starting_amount == ''):
                nb_starting_amount = 0.00;
            else:
                nb_starting_amount = float(re.sub(r'\$?','',nb_starting_amount))
            nb_display = request.POST.get('new__'+nb_name+'__display', '') != '' # True = disp == 'on' != ''
            nb_name = re.sub(' ', '', nb_name) # Remove any spaces, since they cause issues with getting overview data
            print('name: ', nb_name)
            print('sa: ', nb_starting_amount)
            print('display: ', nb_display)
            if(nb_name != '' and len(Bank.objects.filter(user=user).filter(name__iexact=nb_name))==0):
                new_bank = Bank(name=nb_name, starting_amount=nb_starting_amount, display=nb_display, user=user)
                new_bank.save()
                print('New bank,',new_bank,'Saved!')
        
        # Updating existing banks
        for eb in existing_banks:
            eb_id = re.split('existing__(\d+)__bank', eb)[1]
            eb_name = request.POST.get('existing__'+eb_id+'__bank','')
            eb_starting_amount = request.POST.get('existing__'+eb_id+'__starting_amount','')
            if (eb_starting_amount == ''):
                eb_starting_amount = 0.00;
            else:
                eb_starting_amount = float(re.sub(r'\$','',eb_starting_amount))
            eb_display = request.POST.get('existing__'+eb_id+'__display','') != ''
            if(eb_name == '' and not eb_display):
                bank = Bank.objects.get(id=eb_id)
                if (    len(Transaction.objects.filter(card_used__exact=bank)) == 0\
                    and len(Transaction.objects.filter(location__iexact=bank.name)) == 0):
                    bank.delete()
            else:
                bank = Bank.objects.get(id=eb_id)
                if (eb_name != '' and eb_name != bank.name and len(Bank.objects.filter(user=user).filter(name__exact=eb_name)) == 0):
                    for tx in Transaction.objects.filter(user=user):
                        if (tx.location == bank.name):
                            tx.location = eb_name
                            tx.save()
                    bank.name = eb_name
                if (eb_starting_amount != bank.starting_amount):
                    bank.starting_amount = eb_starting_amount
                bank.display = eb_display
                bank.save()
                
                
        
    # Budgets
    
    all_categories = Category.objects.filter(user=user)
    all_banks = Bank.objects.filter(user=user)
    context = {
        'all_categories': all_categories,
        'all_banks': all_banks,
    }
    return render(request, 'budget/config.html', context)


'''
========================== OVERVIEW PAGE ==========================  
'''
@login_required
def overview_page(request, page):
    print('page: ', page)
    context = {}
    user = get_user(request)
    pk = ''
    bulk_upload_error = None
    tx_per_page = 100
    tx_form = TransactionForm(user=user)
    num_pages = 1
    if request.method == 'POST':
        if request.POST.get('upload_bulk', '') != '':
            bulk_upload_error = []
            tx_file = request.FILES['bulk_tx_file']
            if (tx_file.size >= 1000000):  # keep files to < 1MB (just over 400 lines)
                bulk_upload_error.append('File size is too big, keep it below 1MB')
            elif (not str(tx_file).endswith('.csv')):
                bulk_upload_error.append('File must be a .csv (comma separated values)')
            else:
                # with open(tx_file) as f:
                mindate = datetime.date(year=datetime.MAXYEAR, month=12, day=31)
                file_contents = ''.join(tx_file.read().decode('utf-8'))
                rows = re.split(r'\r?\n', file_contents)
                if (rows[0].startswith('date')):
                    rows = rows[1:]
                print(rows)
                for row in rows:
                    if (row == ''): continue
                    data = re.split(' ?, ?', row)
                    try:
                        tx_date_l = data[0].split('/')
                        tx_date = datetime.date(int(tx_date_l[2]), int(tx_date_l[0]), int(tx_date_l[1]))
                        tx_cat = Category.objects.filter(user=user).get(category__exact=data[4])
                        tx_card_used = Bank.objects.filter(user=user).get(name__exact=data[5])
                        _, created = Transaction.objects.get_or_create(
                            date=tx_date,
                            category=tx_cat,
                            card_used=tx_card_used,
                            user=user,
                            notes=data[3],
                            location=data[2],
                            amount=float(data[1])
                        )
                        if tx_date < mindate:
                            mindate = tx_date
                        print(created)
                    except BaseException as e:
                        print('Error from: ', row)
                        print(type(e), e)
                        bulk_upload_error.append(row)
                print('recalculating all bank-transaction amounts since', mindate)
                calc_all_since(mindate, user)
        else:
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
                        calc_all_since(transaction.date, user)
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
                            calc_all_since(transaction.date, user)
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
                            tx_date = Transaction.objects.get(pk=pk).date
                            Transaction.objects.get(pk=pk).delete()
                            calc_all_since(tx_date, user)
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
    if (page == "" or page is None):
        page = 1
    else:
        page = int(page)
        if (page < 0):
            page = 1
    max_page = math.ceil(len(all_transactions)/tx_per_page)
    page = min(page, max_page)
    start_idx = max((page-1)*tx_per_page, 0)
    print('Starting index at', start_idx)
    
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
        'bulk_upload_error': (bulk_upload_error if bulk_upload_error is not None else ''),
        'bulk_upload': (bulk_upload_error is not None),
        'total_txs': len(all_transactions)-start_idx,
        'page': page,
    }
    return render(request, 'budget/overview.html', context)


'''
========================== GET OVERVIEW DATA ==========================  
'''
@login_required
def get_overview_data(request, page=1):
    user = get_user(request)
    tx_per_page = 100
    print('page: ', page)
    
    all_transactions = Transaction.objects.filter(user__exact=user).order_by('-date') # reversed, but will be flipped after calculations
    if (page == "" or page is None):
        page = 1
    else:
        page = int(page)
        if (page < 0):
            page = 1
    max_page = math.ceil(len(all_transactions)/tx_per_page)
    page = min(page, max_page)
    start_idx = max((page-1)*tx_per_page, 0)
    end_idx = min(start_idx+(tx_per_page), len(all_transactions))
    print('Getting txs from %d to %d'%(start_idx, end_idx))
    all_transactions = all_transactions[start_idx:end_idx]
    all_banks = Bank.objects.filter(user=user).filter(display=True)
    
    all_categories = Category.objects.filter(user__exact=user)
    if (platform == 'win32'):
        time_format='%B %#d, %Y'
    else:
        time_format='%B %-d, %Y'

    times = []
    tx_list = []
    for tx in all_transactions:
        start = time.time()
        tx_tbas = tx.transactionbankamount_set.get_queryset()
        cur_tx = vars(tx)
        # Add all the banks
        for bank in all_banks:
            cur_tx[bank.name] = tx_tbas.get(bank__name=bank.name).amount + bank.starting_amount
        cur_tx['card_used'] = str(tx.card_used)
        cur_tx['category'] = str(tx.category)
        cur_tx['date'] = str(tx.date.strftime(time_format))
        for bank in all_banks:
            if (cur_tx[bank.name] < 0):
                cur_tx[bank.name] = '$(' + str(-1*cur_tx[bank.name]) + ')'
            else:
                cur_tx[bank.name] = '$' + str(cur_tx[bank.name])
        
        if tx.amount < 0:
            cur_tx['amount'] = '$('+str(-1*cur_tx['amount'])+')'
        else:
            cur_tx['amount'] = '$'+str(cur_tx['amount'])
        
        tx_list.append(cur_tx)
        del cur_tx['_state']
        times.append(time.time()-start)
        
    print('each transaction took an average of %f seconds with a max of %f and a min of %f'%(sum(times)/len(times),max(times),min(times)))
    print('total time ~%f'%sum(times))
    return JsonResponse({'transactions':tx_list})
    


'''
========================== GET INDIVIDUAL OVERVIEW DATA ==========================  
'''
@login_required
def get_individual_overview_data(request, bank):
    user = get_user(request)
    print('Finding data for ', bank)
    all_transactions = Transaction.objects.filter(user__exact=user)\
                            .filter(Q(location__exact=bank)|Q(card_used__name__exact=bank))\
                            .order_by('-date') # reversed, but will be flipped after calculations
    bank = Bank.objects.filter(user=user).get(name__exact=bank)
    all_categories = Category.objects.filter(user__exact=user)
    if (platform == 'win32'):
        time_format='%B %#d, %Y'
    else:
        time_format='%B %-d, %Y'

    tx_list = []
    for tx in all_transactions:
        tx_tbas = tx.transactionbankamount_set.get_queryset()
        cur_tx = vars(tx)
        # Add all the banks
        cur_tx[bank.name] = tx_tbas.get(bank__name=bank.name).amount + bank.starting_amount
        cur_tx['card_used'] = str(tx.card_used)
        cur_tx['category'] = str(tx.category)
        cur_tx['date'] = str(tx.date.strftime(time_format))
        if (cur_tx[bank.name] < 0):
            cur_tx[bank.name] = '$(' + str(-1*cur_tx[bank.name]) + ')'
        else:
            cur_tx[bank.name] = '$' + str(cur_tx[bank.name])
        
        if tx.amount < 0:
            cur_tx['amount'] = '$('+str(-1*cur_tx['amount'])+')'
        else:
            cur_tx['amount'] = '$'+str(cur_tx['amount'])
        
        tx_list.append(cur_tx)
        del cur_tx['_state']
    
    return JsonResponse({'transactions':tx_list})

@login_required
def export_tx_as_csv(request):
    user = get_user(request)
    transactions = Transaction.objects.filter(user=user).order_by('-date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exported_transactions_for_%s.csv'%user.username
    writer = csv.writer(response)
    writer.writerow(['date', 'amount', 'location', 'notes', 'category', 'card used', 'id'])
    for tx in transactions:
        writer.writerow([str(tx.date.month)+'/'+str(tx.date.day)+'/'+str(tx.date.year), tx.amount, tx.location, tx.notes, tx.category.category, tx.card_used.name, tx.id])
        
    return response
    
@login_required
def recalculate_all(request):
    user = get_user(request)
    date = datetime.date(year=datetime.MINYEAR,month=1,day=1)
    calc_all_since(date, user)

    return redirect('/budget/overview/')
    

def monthly_overview(request):
    pass

def budget_status(request):
    pass

from django.contrib import admin
from budget.models import Bank, Transaction

# Register your models here.

class BankAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bank, BankAdmin);

class TransactionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Transaction, TransactionAdmin);


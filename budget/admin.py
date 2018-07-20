from django.contrib import admin
from budget.models import Bank, Category, Transaction

# Register your models here.

class BankAdmin(admin.ModelAdmin):
    pass
admin.site.register(Bank, BankAdmin);

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category']
admin.site.register(Category, CategoryAdmin);

class TransactionAdmin(admin.ModelAdmin):
    pass
admin.site.register(Transaction, TransactionAdmin);


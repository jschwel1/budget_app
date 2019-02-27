from django.contrib import admin
from budget.models import Bank, Category, Transaction, Budget, BudgetCategory, TransactionBankAmount

# Register your models here.

class BankAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'starting_amount', 'display']
admin.site.register(Bank, BankAdmin);

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'user', 'enabled']
admin.site.register(Category, CategoryAdmin);

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','date', 'amount', 'category', 'location', 'notes', 'card_used']
admin.site.register(Transaction, TransactionAdmin)

class BudgetAdmin(admin.ModelAdmin):
    list_display=['id', 'user', 'start', 'end']
admin.site.register(Budget, BudgetAdmin)

class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display=['id', 'budget', 'category', 'amount']
admin.site.register(BudgetCategory, BudgetCategoryAdmin)

class TransactionBankAmountAdmin(admin.ModelAdmin):
    list_display=['id', 'transaction', 'bank', 'amount']
admin.site.register(TransactionBankAmount, TransactionBankAmountAdmin)

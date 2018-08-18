from django.contrib import admin
from budget.models import Bank, Category, Transaction, Budget, BudgetCategory

# Register your models here.

class BankAdmin(admin.ModelAdmin):
    list_display = ['name', 'starting_amount']
admin.site.register(Bank, BankAdmin);

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'user']
admin.site.register(Category, CategoryAdmin);

class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user','date', 'amount', 'category', 'location', 'notes', 'card_used']
admin.site.register(Transaction, TransactionAdmin)

class BudgetAdmin(admin.ModelAdmin):
    list_display=['user', 'start', 'end']
admin.site.register(Budget, BudgetAdmin)

class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display=['budget', 'category', 'amount']
admin.site.register(BudgetCategory, BudgetCategoryAdmin)

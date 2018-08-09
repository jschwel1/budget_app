from django import forms
from .models import Bank, Category, Transaction, Budget, BudgetCategory

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ('starting_amount', 'name')

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category',)

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ('date', 'amount', 'category', 'location', 'notes', 'card_used')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget=forms.SelectDateWidget(empty_label='Nothing')

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('start', 'end')

class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ('budget', 'category', 'amount')


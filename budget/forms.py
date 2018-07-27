from django import forms


class BankForm(forms.ModelForm):
    class meta:
        model = Bank
        fields = ('starting_amount', 'name')

class CategoryForm(forms.ModelForm):
    class meta:
        model = Category
        fields = ('category')

class TransactionForm(forms.ModelForm):
    class meta:
        model = Transaction
        fields = ('date', 'amount', 'category', 'location', 'notes', 'card_used')

class BudgetForm(forms.ModelForm);
    class meta:
        model = Budget
        fields = ('start', 'end')

class BudgetCategoryForm(forms.ModelForm):
    class meta:
        model = BudgetCategoryForm
        fields = ('budget', 'category', 'amount')


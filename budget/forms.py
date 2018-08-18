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
    def __init__(self, user=None, *args, **kwargs):
        print('Initializing form')
        super().__init__(*args, **kwargs)
        print('Completed Super Init')

        categories = []
        if user != None:
            print('user', user)
            for category in Category.objects.filter(user__exact=user):
                categories.append((str(category.id), str(category)))
        else:
            print('no user')
            for category in Category.objects.all():
                categories.append((str(category.id), str(category)))

        print('categories: ', categories)
        self.fields['category'].widget.choices=categories
        print('added categories widget')
        self.fields['date'].widget=forms.SelectDateWidget(empty_label=None)
        self.fields['location'].label='Location/To (for transfers)'
        self.fields['location'].widget.attrs={'autocomplete':'off', 'list':'Locations'}
        print('Done')

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('start', 'end')

class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ('budget', 'category', 'amount')


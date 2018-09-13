from django import forms
from .models import Bank, Category, Transaction, Budget, BudgetCategory
import datetime

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
        super().__init__(*args, **kwargs)

        categories = []
        if user != None:
            for category in Category.objects.filter(user__exact=user):
                categories.append((str(category.id), str(category)))
        else:
            for category in Category.objects.all():
                categories.append((str(category.id), str(category)))

        self.fields['category'].widget.choices=categories
        self.fields['category'].widget.attrs={'id':'form_category'}
        self.fields['date'].widget=forms.SelectDateWidget(empty_label=None,
                                        years=range(1950,datetime.date.today().year+2))
        self.fields['date'].widget.attrs={'id':'form_date'}
        self.fields['location'].label='Location/To (for transfers)'
        self.fields['location'].widget.attrs={'autocomplete':'off', 'list':'Locations', 'id': 'form_location'}
        self.fields['amount'].widget.attrs={'id':'form_amount', 'step':'0.01'}
        self.fields['notes'].widget.attrs={'id':'form_notes'}
        self.fields['card_used'].widget.attrs={'id':'form_card_used'}
        

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('start', 'end')

class BudgetCategoryForm(forms.ModelForm):
    class Meta:
        model = BudgetCategory
        fields = ('budget', 'category', 'amount')

class UploadFileForm(forms.Form):
    file = forms.FileField()

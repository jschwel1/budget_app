from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime, django

# Create your models here.

class Bank(models.Model):
    class Meta:
        verbose_name_plural = "Banks"
    starting_amount = models.DecimalField(max_digits=15, decimal_places=2)
    name = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    display = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"
    category = models.CharField(max_length=65)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    def __str__(self):
        return self.category;

class Transaction(models.Model):
    class Meta:
        verbose_name_plural = "Transactions"

    date = models.DateField(default=django.utils.timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    # Location can be a place or the name of a bank in the case of balance payments
    location = models.CharField(max_length=64)
    notes = models.CharField(max_length=64, default='')
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    card_used = models.ForeignKey(Bank, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_pk(self):
        try:
            return self.id
        except:
            return 'N/A'

    def __str__(self):
        return str(self.user)+': '+\
               str(self.date.day)+'/'+str(self.date.month)+'/'+str(self.date.year)+' '+\
               str(self.amount)+' '+\
               str(self.category)+' '+\
               str(self.location)+' '+\
               str(self.notes)+' '+\
               str(self.card_used) +\
               ' ('+str(self.get_pk())+')'

    def get_value(self, v):
        return self.__dict__[v]
    def set_value(self, a, v):
        self.__dict__[a] = v
    
class Fund(models.Model):
    class Meta:
        verbose_name_plural = "Funds"

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start = models.DateField(default=timezone.now)
    end = models.DateField(default=timezone.now)
    cap = models.DecimalField(default=0,max_digits=15,decimal_places=2)
    accrual = models.DecimalField(default=0,max_digits=15,decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority = models.IntegerField(default=10) # lower number = higher priority

    def __str__(self):
        return self.name + ': ' + self.start + '->' + self.end + ', ' + self.accrual + '(%s)'%self.accrual;

class Budget(models.Model):
    class Meta:
        verbose_name_plural = "Budgets"

    start = models.DateField(default=timezone.now)
    end = models.DateField(default=timezone.now)
    cap = models.DecimalField(max_digits=15,decimal_places=2, default=0.00)
    cumulate = models.BooleanField(default=True) # Grow
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.start + '->' + self.end;

class BudgetCategory(models.Model):
    class Meta:
        verbose_name_plural = "Budget Categories"
        
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return self.budget + ' | ' + self.category + ' -> ' + self.amount

class TransactionBankAmount(models.Model):
    class Meta:
        verbose_name_plural = "Transaction Bank Amounts"
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.transaction) + ' [' + self.bank.name + '] ' + str(self.amount)


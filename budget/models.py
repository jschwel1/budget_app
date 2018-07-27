from django.db import models
from django.utils import timezone
import datetime, django

# Create your models here.

class Bank(models.Model):
    starting_amount = models.IntegerField();
    name = models.CharField(max_length=64);

    def __str__(self):
        return name;

class Category(models.Model):
    category = models.CharField(max_length=64);
    
    def __str__(self):
        return category;

class Transaction(models.Model):
    date = models.DateField(default=django.utils.timezone.now);
    amount = models.IntegerField();
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING);
    # Location can be a place or the name of a bank in the case of balance payments
    location = models.CharField(max_length=64);
    notes = models.CharField(max_length=64);
    card_used = models.ForeignKey(Bank, on_delete=models.CASCADE)

    def __str__(self):
        return date.day+'/'+date.month+'/'+date.year+' '+amount+' '+category+' '+location+' '+notes+' '+card_used
    
class Budget(models.Model):
    start=models.DateField(default=timezone.now)
    end=models.DateField(default=timezone.now)

    def __str__(self):
        return start + '->' + end;

class BudgetCategory():
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE);
    category = models.ForeignKey(Category, on_delete=models.CASCADE);
    amount = models.IntegerField();

    def __str__(self):
        return budget + ' | ' + category + ' -> ' + amount


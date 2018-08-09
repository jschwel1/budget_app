from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime, django

# Create your models here.

class Bank(models.Model):
    class Meta:
        verbose_name_plural = "Banks"
    starting_amount = models.IntegerField()
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"
    category = models.CharField(max_length=65)
    
    def __str__(self):
        return self.category;

class Transaction(models.Model):
    class Meta:
        verbose_name_plural = "Transactions"

    date = models.DateField(default=django.utils.timezone.now)
    amount = models.IntegerField()
    # Location can be a place or the name of a bank in the case of balance payments
    location = models.CharField(max_length=64)
    notes = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    card_used = models.ForeignKey(Bank, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)+': '+\
               str(self.date.day)+'/'+str(self.date.month)+'/'+str(self.date.year)+' '+\
               str(self.amount)+' '+\
               str(self.category)+' '+\
               str(self.location)+' '+\
               str(self.notes)+' '+\
               str(self.card_used)
    
class Budget(models.Model):
    class Meta:
        verbose_name_plural = "Budgets"

    start=models.DateField(default=timezone.now)
    end=models.DateField(default=timezone.now)

    def __str__(self):
        return self.start + '->' + self.end;

class BudgetCategory(models.Model):
    class Meta:
        verbose_name_plural = "Budget Categories"
        
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE);
    category = models.ForeignKey(Category, on_delete=models.CASCADE);
    amount = models.IntegerField()

    def __str__(self):
        return self.budget + ' | ' + self.category + ' -> ' + self.amount


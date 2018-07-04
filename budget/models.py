from django.db import models
import datetime

# Create your models here.

class Bank(models.Model):
	starting_amount = models.IntegerField();
	name = models.CharField(max_length=64);

	def __str__(self):
		return name;

class Transaction(models.Model):
	date = models.DateField(default=datetime.date.today());
	amount = models.IntegerField();
	category = models.CharField(max_length=64);
	# Location can be a place or the name of a bank in the case of balance payments
	location = models.CharField(max_length=64);
	notes = models.CharField(max_length=64);
	card_used = models.ForeignKey(Bank, on_delete=models.CASCADE)

	def __str__(self):
		return date.day+'/'+date.month+'/'+date.year+' '+amount+' '+category+' '+location+' '+notes+' '+card_used
	
	
	


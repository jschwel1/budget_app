from budget.models import Bank, Category, Transaction, Budget, BudgetCategory, TransactionBankAmount


def calc_all_since(date, user):
    ''' calc_all_since(date, user)
        Calculate all transaction bank amount entries for each transaction past this date.
        This function will remove all transactionbankamount entries starting on the date listed,
        then starting on the date, organize all transactions by date and recalculate all 
        Transactionbankamounts.
    '''
    # Remove all transaction-bank amounts for this user past the modified date
    TransactionBankAmount.objects.filter(transaction__user=user).filter(transaction__date__gte=date).delete()
    # Get the most recent transactionbankamount object
    most_recent = TransactionBankAmount.objects.filter(transaction__user=user).order_by('transaction__date').last()
    all_transactions = Transaction.objects.filter(user__exact=user).order_by('date')


    # Get the starting amounts for each bank
    all_banks = Bank.objects.filter(user=user)#.values_list(flat=True)

    prev_tba_set = None
    if most_recent is not None:
        txs = Transaction.objects.filter(user=user).filter(date__gt=most_recent.transaction.date).order_by('date')
        tbas = most_recent.transaction.transactionbankamount_set.get_queryset()
        prev_tba_set = tbas
    else:
        txs = Transaction.objects.filter(user=user).all()

    for tx in txs:
        # For transfers:
        if str(tx.category).lower() == 'transfer':
            loc_to = tx.location
            loc_from = tx.card_used.name

            for bank in all_banks:
                tba = TransactionBankAmount.objects.create(transaction=tx, bank=bank)
                if bank.name == loc_to:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount + tx.amount
                    else:
                        tba.amount = tx.amount
                elif bank.name == loc_from:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount - tx.amount
                    else:
                        tba.amount = -tx.amount
                # If net or some other bank not involved, just keep it the same
                else:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount
                    else:
                        tba.amount = 0.00
                tba.save()
        # If an Income
        elif str(tx.category).lower() == 'income':
            for bank in all_banks:
                tba = TransactionBankAmount.objects.create(transaction=tx, bank=bank)
                if bank.name == 'Net' or bank.name == tx.card_used.name:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount + tx.amount
                    else:
                        tba.amount = tx.amount
                else:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount
                    else:
                        tba.amount = 0.00
                tba.save()
                    
        # If some kind of transaction              
        else:
            for bank in all_banks:
                tba = TransactionBankAmount.objects.create(transaction=tx, bank=bank)
                if bank.name == 'Net' or bank.name == tx.card_used.name:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount - tx.amount
                    else:
                        tba.amount = -tx.amount
                else:
                    if prev_tba_set is not None:
                        tba.amount = prev_tba_set.get(bank__name=bank.name).amount
                    else:
                        tba.amount = 0.00
                tba.save()

        # Updated prev_tba_set
        prev_tba_set = tx.transactionbankamount_set.get_queryset()
                    

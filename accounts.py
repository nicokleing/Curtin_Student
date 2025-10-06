'''
  Practical Test 4

  accounts.py - class for bank account portfolio
  
  Student Name   :
  Student Number :
  Date/prac time :
'''

class Portfolio ():
    '''
    Portfolio - holds a collection of BankAccount objects, taking transaction
                requests and matching to the specific account, then calling the
                BankAccount methods to actually do the transaction.
    '''
    def __init__(self):
        self.accounts = []

    def addAccount(self, name, number, balance):
        '''
        addAccount - creates a BankAccount and adds into the list of accounts

        name - name of account (string)
        number - account number (string)
        balance - initial balance (float/int)

        '''
        self.accounts.append(BankAccount(name, number, balance))

    def deposit(self, name, amount):
        '''
        deposit - deposits amount into account with matching name
        
        name - name of account (string)
        amount - amount to be deposited (float/int)
        '''
        temp = None
        for acct in self.accounts:
            if acct.name == name:
                temp = acct
        if temp:
            print(f"---> Depositing ${amount} into account {name}")
            temp.deposit(amount)
            print("         Complete")

    def withdraw(self, name, amount):
        '''
        withdraw - withdraws amount into account with matching name
        
        name - name of account (string)
        amount - amount to be withdrawn (float/int)
        '''
        temp = None
        for acct in self.accounts:
            if acct.name == name:
                temp = acct
        if temp:
            print(f"---> Withdrawing ${amount} from account {name}")
            temp.withdraw(amount)
            print("         Complete")


    def balances(self):
        '''
        balances - list and calculate total balances of accounts
        '''
        print('\nBalances of All Accounts:')
        print('--------------------------------------------')
        total = 0
        print(f"{'Name':15} {'Number':15} {'Balance':7}")
        print('--------------------------------------------')
        for a in self.accounts:
            print(f"{a.name:15} {a.num:15} {a.bal:7}")
            total = total + a.bal
        print('--------------------------------------------')
        print(f"{'TOTAL':15} {total:23}")
        print('--------------------------------------------')
        print()

    def getNumAccounts(self):
        '''
        getNumAccounts - returns the number of accounts in the portfolio
        
        enter your code below
        '''
        ...

    def getTotalBalance(self):
        '''
        getNumAccounts - returns the number of accounts in the poartfolio
        
        enter your code below - the balances code may help
        '''
        ...

    
class BankAccount ():

    def __init__(self, name, number, balance):
        self.name = name
        self.num = number
        self.bal = balance

    def withdraw(self, amount):
            self.bal = self.bal - amount

    def deposit(self, amount):
        self.bal = self.bal + amount

class InsufficientFundsError(Exception):
    '''
    Insufficient Funds error - to be raised where a transaction exceeds available balance
    '''
    pass

class AccountNotFoundError(Exception):
    '''
    Account Not Found error - to be raised where account name doesn't match accounts in portfolio
    '''
    pass

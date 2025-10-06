'''
  Practical Test 4

  accounts.py - class for bank account portfolio
  
  Student Name   :
  Student Number :
  Date/prac time :
'''

class Portfolio():
    '''
    Portfolio - keeps a list of BankAccount objects and manages deposits,
                withdrawals and balances for each account.
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
        withdraw - withdraws amount from account with matching name
        '''
        temp = None
        for acct in self.accounts:
            if acct.name == name:
                temp = acct
        if temp:
            print(f"---> Withdrawing ${amount} from account {name}")
            try:
                temp.withdraw(amount)
                print("         Complete")
            except InsufficientFundsError as e:
                print("         Failed -", e)

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
        '''
        return len(self.accounts)

    def getTotalBalance(self):
        '''
        getTotalBalance - returns the total balance of all accounts in the portfolio
        '''
        total = 0
        for a in self.accounts:
            total += a.bal
        return total


class BankAccount():
    '''
    BankAccount - class for a single bank account
    '''
    def __init__(self, name, number, balance):
        '''
        __init__ - creates the account and sets the starting balance

        name - name of account (string)
        number - account number (string)
        balance - initial balance (float/int)
        '''
        self.name = name
        self.num = number
        self.bal = balance

    def withdraw(self, amount):
        '''
        withdraw - subtracts amount from balance if enough funds,
                   otherwise raises InsufficientFundsError

        amount - amount to withdraw (float/int)
        '''
        if amount > self.bal:
            raise InsufficientFundsError(
                f"Insufficient funds in account '{self.name}'. "
                f"Available: ${self.bal}, Requested: ${amount}"
            )
        self.bal -= amount

    def deposit(self, amount):
        '''
        deposit - adds amount to balance

        amount - amount to deposit (float/int)
        '''
        self.bal += amount



class InsufficientFundsError(Exception):
    '''
    InsufficientFundsError - raised when a withdrawal exceeds available balance
    '''
    pass


class AccountNotFoundError(Exception):
    '''
    AccountNotFoundError - raised when an account name doesn't match any in the portfolio
    '''
    pass

'''
  Practical Test 4

  testAccounts.py - program to test functions of accounts.py
  
  Student Name   :
  Student Number :
  Date/prac time :
'''
from accounts import BankAccount, Portfolio

print("\n------ Bank Accounts Portfolio ---------\n")
myAccounts = Portfolio()

# [STEP 1] Create two accounts and show initial balances
print("[STEP 1] Creating accounts: Castle (888888-1, $2000) and Shrubbery (888888-2, $200)")
myAccounts.addAccount("Castle", "888888-1", 2000)
myAccounts.addAccount("Shrubbery", "888888-2", 200)

print("[STEP 1] Initial balances")
myAccounts.balances()

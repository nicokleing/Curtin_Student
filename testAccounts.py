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

# [STEP 2] Deposit and withdraw operations
print("\n[STEP 2] Deposit $200 into Castle and withdraw $20 from Shrubbery")
myAccounts.deposit("Castle", 200)
myAccounts.withdraw("Shrubbery", 20)

print("[STEP 2] Attempt to withdraw $2000 from Shrubbery (should fail later once exceptions are added)")
myAccounts.withdraw("Shrubbery", 2000)

print("[STEP 2] Balances after all operations")
myAccounts.balances()



# [STEP 3] Test getNumAccounts() and getTotalBalance()
print("\n[STEP 3] Testing getNumAccounts() and getTotalBalance()")
print("Number of accounts:", myAccounts.getNumAccounts())
print("Total balance:", myAccounts.getTotalBalance())


# [STEP 4] Add 'Grail', withdraw $2000 from it, and re-test summaries
print("\n[STEP 4] Adding account: Grail (888888-3, $200)")
myAccounts.addAccount("Grail", "888888-3", 200)

print("[STEP 4] Withdraw $2000 from Grail (exceptions not added yet)")
myAccounts.withdraw("Grail", 2000)

print("[STEP 4] Balances after Grail operations")
myAccounts.balances()

print("[STEP 4] Re-check summaries (now 3 accounts)")
print("Number of accounts:", myAccounts.getNumAccounts())
print("Total balance:", myAccounts.getTotalBalance())
from accounts_helper import load_accounts, save_accounts, authenticate, get_balance, withdraw, deposit, transfer

accounts = load_accounts()

# Pick Ravi (1001) for testing
acc_no = "1001"
pin = "1234"

if authenticate(accounts, acc_no, pin):
    print("Login OK ✅")

    print("Initial balance:", get_balance(accounts, acc_no))

    withdraw(accounts, acc_no, 500)
    print("After withdraw 500:", get_balance(accounts, acc_no))

    deposit(accounts, acc_no, 200)
    print("After deposit 200:", get_balance(accounts, acc_no))

    transfer(accounts, acc_no, "1002", 300)
    print("After transfer 300 to 1002:", get_balance(accounts, acc_no))
    print("Priya (1002) balance:", get_balance(accounts, "1002"))

    # Save changes
    save_accounts(accounts)

    print("Transactions of Ravi:", accounts[acc_no]["transactions"])
else:
    print("Login Failed ❌")

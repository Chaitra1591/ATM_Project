import json
from typing import Dict, Any

ACCOUNTS_FILE = "accounts.json"

# Get account by name

# Fetch account by acc_no
def get_account(acc_no):
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
    for acc in accounts:
        if acc['acc_no'] == acc_no:
            return acc
    return None


def load_accounts() -> Dict[str, Dict[str, Any]]:
    with open(ACCOUNTS_FILE, "r") as f:
        data = json.load(f)
    return {a["acc_no"]: a for a in data}

# Save updated account
def save_account(updated_account):
    with open('accounts.json', 'r') as f:
        accounts = json.load(f)
    for i, acc in enumerate(accounts):
        if acc['acc_no'] == updated_account['acc_no']:
            accounts[i] = updated_account
            break
    with open('accounts.json', 'w') as f:
        json.dump(accounts, f, indent=4)

def authenticate(accounts: Dict[str, Dict[str, Any]], acc_no: str, pin: str) -> bool:
    acc = accounts.get(acc_no)
    return bool(acc and str(acc["pin"]) == str(pin))
def get_balance(accounts, acc_no: str) -> float:
    acc = accounts.get(acc_no)
    return acc["balance"] if acc else None

def withdraw(accounts, acc_no: str, amount: float) -> bool:
    acc = accounts.get(acc_no)
    if not acc or amount <= 0:
        return False
    if acc["balance"] >= amount:
        acc["balance"] -= amount
        acc["transactions"].append(f"Withdraw: -{amount}")
        return True
    return False

def deposit(accounts, acc_no: str, amount: float) -> bool:
    acc = accounts.get(acc_no)
    if not acc or amount <= 0:
        return False
    acc["balance"] += amount
    acc["transactions"].append(f"Deposit: +{amount}")
    return True

def transfer(accounts, from_acc: str, to_acc: str, amount: float) -> bool:
    if from_acc == to_acc:
        return False
    if withdraw(accounts, from_acc, amount):
        deposit(accounts, to_acc, amount)
        acc = accounts[from_acc]
        acc["transactions"].append(f"Transfer to {to_acc}: -{amount}")
        accounts[to_acc]["transactions"].append(f"Transfer from {from_acc}: +{amount}")
        return True
    return False


if __name__ == "__main__":
    accounts = load_accounts()
    print(f"Loaded {len(accounts)} accounts")

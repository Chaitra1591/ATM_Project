import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from accounts_helper import get_account, save_account


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret'

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acc_no = request.form['acc_no']
        pin = request.form['pin']
        acc = get_account(acc_no)
        if not acc:  # add your PIN check here
            flash('Invalid account or PIN', 'danger')
            return redirect(url_for('login'))
        session['account_id'] = acc_no
        session['user_name'] = acc['name']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    account = get_account(session['account_id'])
    return render_template('dashboard.html', account=account)


@app.route('/deposit', methods=['POST'])
def deposit():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    
    amount = float(request.form['amount'])
    acc_no = session['account_id']
    account = get_account(acc_no)
    
    account['balance'] += amount
    save_account(account)
    
    flash(f"₹{amount} deposited successfully!")
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    
    amount = float(request.form['amount'])
    acc_no = session['account_id']
    account = get_account(acc_no)
    
    if amount > account['balance']:
        flash("Insufficient balance!")
    else:
        account['balance'] -= amount
        save_account(account)
        flash(f"₹{amount} withdrawn successfully!")
    
    return redirect(url_for('dashboard'))



@app.route('/transfer', methods=['POST'])
def transfer():
    if 'account_id' not in session:
        return redirect(url_for('login'))

    to_acc_no = request.form['to_account']
    amount = float(request.form['amount'])
    
    sender_acc_no = session['account_id']
    sender = get_account(sender_acc_no)
    receiver = get_account(to_acc_no)

    if receiver is None:
        flash("Target account not found!")
    elif amount > sender['balance']:
        flash("Insufficient balance!")
    else:
        sender['balance'] -= amount
        receiver['balance'] += amount
        save_account(sender)
        save_account(receiver)
        flash(f"₹{amount} transferred to account {to_acc_no} successfully!")
    
    return redirect(url_for('dashboard'))

@app.route("/logout")
def logout():
    session.pop("account_id", None)
    session.pop("user_name", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






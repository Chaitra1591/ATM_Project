from flask import Flask, render_template, request, redirect, url_for, session, flash
from accounts_helper import get_account, save_account
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acc_no = request.form['acc_no']
        pin = request.form['pin']

        account = get_account(acc_no)

        if account and account['pin'] == pin:
            session['user'] = acc_no
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid account number or PIN")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    account = get_account(session['user'])
    return render_template('dashboard.html', account=account)
@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    account = get_account(session['user'])
    account['balance'] += amount
    save_account(account)  # function to save updated account
    flash(f"₹{amount} deposited successfully!")
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    account = get_account(session['user'])
    if amount > account['balance']:
        flash("Insufficient balance!")
    else:
        account['balance'] -= amount
        save_account(account)
        flash(f"₹{amount} withdrawn successfully!")
    return redirect(url_for('dashboard'))


@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))

    to_acc = request.form['to_account']
    amount = float(request.form['amount'])

    sender = get_account(session['user'])
    receiver = get_account(to_acc)

    if receiver is None:
        flash("Target account not found!")  # ⚠ shows if acc_no wrong
    elif amount > sender['balance']:
        flash("Insufficient balance!")
    else:
        sender['balance'] -= amount
        receiver['balance'] += amount
        save_account(sender)
        save_account(receiver)
        flash(f"₹{amount} transferred to {to_acc} successfully!")

    return redirect(url_for('dashboard'))


@app.route("/logout")
def logout():
    session.pop("acc_no", None)
    return redirect(url_for("login"))




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway sets PORT automatically
    app.run(host="0.0.0.0", port=port)




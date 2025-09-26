from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

# ---------------- App Setup ----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///atm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    pin_hash = db.Column(db.String(200))
    accounts = db.relationship('Account', backref='user', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Integer, default=0)  # stored in paise
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    type = db.Column(db.String(20))  # 'deposit' or 'withdraw'
    amount = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    balance_after = db.Column(db.Integer)

# ---------------- Helpers ----------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'account_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def paise_to_str(p):
    return f"{p/100:.2f}"

def money_to_paise(amount_str):
    try:
        return int(float(amount_str) * 100)
    except:
        return 0

# ---------------- Routes ----------------
@app.route('/')
def index():
    if 'account_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        acc_no = request.form['account_number']
        pin = request.form['pin']
        acc = Account.query.filter_by(account_number=acc_no).first()
        if not acc or not check_password_hash(acc.user.pin_hash, pin):
            flash('Invalid account or PIN', 'danger')
            return redirect(url_for('login'))
        session['account_id'] = acc.id
        session['user_name'] = acc.user.name
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    acc = Account.query.get(session['account_id'])
    return render_template(
        'dashboard.html',
        account=acc,
        balance=paise_to_str(acc.balance)
    )

# ---------------- Deposit ----------------
@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    acc = Account.query.get(session['account_id'])
    if request.method == 'POST':
        amount = money_to_paise(request.form['amount'])
        if amount <= 0:
            flash('Enter a valid amount', 'danger')
            return redirect(url_for('deposit'))
        acc.balance += amount
        transaction = Transaction(
            account_id=acc.id,
            type='deposit',
            amount=amount,
            balance_after=acc.balance
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Deposited ₹{amount/100:.2f} successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('deposit.html', balance=paise_to_str(acc.balance))

# ---------------- Withdraw ----------------
@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    acc = Account.query.get(session['account_id'])
    if request.method == 'POST':
        amount = money_to_paise(request.form['amount'])
        if amount <= 0:
            flash('Enter a valid amount', 'danger')
            return redirect(url_for('withdraw'))
        if amount > acc.balance:
            flash('Insufficient balance!', 'danger')
            return redirect(url_for('withdraw'))
        acc.balance -= amount
        transaction = Transaction(
            account_id=acc.id,
            type='withdraw',
            amount=amount,
            balance_after=acc.balance
        )
        db.session.add(transaction)
        db.session.commit()
        flash(f'Withdrew ₹{amount/100:.2f} successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('withdraw.html', balance=paise_to_str(acc.balance))

# ---------------- Mini Statement ----------------

from datetime import datetime
import pytz

@app.route('/mini_statement')
@login_required
def mini_statement():
    acc = Account.query.get(session['account_id'])
    transactions = (Transaction.query
                    .filter_by(account_id=acc.id)
                    .order_by(Transaction.timestamp.desc())
                    .limit(5).all())

    # IST timezone
    ist = pytz.timezone('Asia/Kolkata')

    formatted_transactions = []
    for t in transactions:
        local_time = t.timestamp.replace(tzinfo=pytz.utc).astimezone(ist)
        formatted_transactions.append({
            'type': t.type,
            'amount': t.amount / 100,
            'balance_after': t.balance_after / 100,
            'timestamp': local_time.strftime("%d-%b-%Y %I:%M %p")  # Correct local time
        })

    return render_template(
        'mini_statement.html',
        transactions=formatted_transactions,
        balance=paise_to_str(acc.balance)
    )


# ---------------- Logout ----------------
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

#create account

from werkzeug.security import generate_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        account_number = request.form['account_number']
        pin = request.form['pin']
        confirm_pin = request.form['confirm_pin']

        # Validation
        if pin != confirm_pin:
            flash('PINs do not match!', 'danger')
            return redirect(url_for('register'))

        if Account.query.filter_by(account_number=account_number).first():
            flash('Account number already exists!', 'danger')
            return redirect(url_for('register'))

        # Create user and account
        new_user = User(name=name, pin_hash=generate_password_hash(pin))
        db.session.add(new_user)
        db.session.commit()

        new_account = Account(account_number=account_number, balance=0, user_id=new_user.id)
        db.session.add(new_account)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ---------------- Dev: Seed Test Account ----------------
@app.route('/seed')
def seed():
    db.create_all()
    if User.query.first():
        return 'Already seeded'
    u = User(name='Test User', pin_hash=generate_password_hash('1234'))
    db.session.add(u)
    db.session.commit()
    a = Account(account_number='ACC1001', balance=50000, user_id=u.id)  # ₹500.00
    db.session.add(a)
    db.session.commit()
    return 'Seeded'

# ---------------- Run App ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)

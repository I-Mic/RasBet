"""
Routes and views for the flask application.
"""

import regex
import hashlib

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, session, url_for, abort, request, redirect
from RasBet import app, db
from .models import User, Transaction



'''
WEB
'''

@app.route('/')
@app.route('/home/')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact/')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about/')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )


@app.get('/login/')
@app.get('/register/')
@app.get('/account_access/')
def account_access():
    """Renders the login page."""
    return render_template(
        'account_access.html',
        title='Login',
        year=datetime.now().year,
        message='Your login page'
    )


@app.get('/user/')
def edit_account():
    
    user = db.get_or_404(User, session['id'])
    
    if not user:
        abort(404, "User not found")
        
    return render_template(
        'account_page.html',
        balance = user.balance
    )


@app.get('/user/transactions')
def user_transactions():
    
    user = db.get_or_404(User, session['id'])
    
    if not user:
        abort(404, "User not found")
    
    transactions = db.session.execute(db.select(Transaction).filter_by(user_id = session['id'])).scalars()
    
    return render_template(
        'account_transactions.html',
        transactions = transactions,
        balance = user.balance
    )
    


'''
API
'''

EMAIL_REGEX = regex.compile('^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$')

def check_valid_email(email):
    return bool(EMAIL_REGEX.match(email))

def check_valid_birthdate(birthdate):
    legal_birthdate = date.today() - relativedelta(years=18)

    return birthdate <= legal_birthdate
    
def get_hashed_passwd(passwd):
    return hashlib.sha256(passwd.encode()).hexdigest()

@app.post('/user/register')
def register():
    email = request.form["email"]

    if not check_valid_email(email):
        abort(404, 'Email not valid')

    birthdate = datetime.strptime(request.form['birthdate'], "%Y-%m-%d").date()

    if not check_valid_birthdate(birthdate):
        abort(404, 'Birthdate doesn\'t meet legal conditions')
    
    
    user = User(
        email = email,
        name = request.form['name'],
        passwd = get_hashed_passwd(request.form['passwd']),
        birthdate = birthdate
    )
    session['id'] = user.id
    session['name'] = user.name
    session['email'] = user.email

    db.session.add(user)
    db.session.commit()

            
    return redirect(url_for('home'))
    

@app.post('/user/login')
def login():
    email = request.form["email"]

    if not check_valid_email(email):
        abort(404, 'Email not valid')

    user = db.first_or_404(db.select(User).filter_by(email=email)) # It is already unique

    if user.passwd != get_hashed_passwd(request.form['passwd']):
        abort(404, "Wrong credentials")

    session['id'] = user.id
    session['name'] = user.name
    session['email'] = user.email
            
    return redirect(url_for('home'))

@app.post('/user/')
def edit():
    
    user = db.first_or_404(User, session.id)
    
    if not user:
        abort(404, "User not found")
    
    new_name = request.form['name']
    new_email = request.form['email']
    if new_name:
        user.name = new_name
        session['name'] = new_name
    
    if new_email:
        user.email = new_email
        session['email'] = new_email
        
    if request.form['password']:
        user.password = get_hashed_passwd(request.form['password'])
    
    
    db.session.commit()


@app.post('/logout/')
def log_out():
    session.pop('id')
    session.pop('name')
    session.pop('email')
    return redirect(url_for('home')) 
    

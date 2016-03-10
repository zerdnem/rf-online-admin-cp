import pyodbc
from wtforms import Form, PasswordField, validators, StringField
from functools import wraps
from flask import session, flash, redirect, url_for


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    email = StringField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password',[validators.DataRequired(),
                        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


class GMRegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20)])
    password = PasswordField('New Password',[validators.DataRequired(),
                        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


def connection_rfuser():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=RF_User;UID=sa;PWD=wanker12')
    cur = conn.cursor()
    return cur, conn


def connection_rfworld():
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=RF_World;UID=sa;PWD=wanker12')
    cur = conn.cursor()
    return cur, conn


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.", 'error')
            return redirect(url_for('cp.main_page'))

    return wrap

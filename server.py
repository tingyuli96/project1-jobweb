#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash

# tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Idontknow'
Bootstrap(app)

# XXX: The Database URI should be in the format of:
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "tl2861"
DB_PASSWORD = "vo564c85"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
class RegisterFormCandidate(FlaskForm):
    uid = IntegerField('uid',validators=[InputRequired(), NumberRange(min=1,max=1000)])
    username = StringField('username',validators=[InputRequired()])
    password = PasswordField('password',validators=[InputRequired(), Length(min=8,max=80)])
    university = StringField('university')
    skills = StringField('skills')
    major = StringField('major')
    city = StringField('city')
    state = StringField('state')
    country = StringField('country')

class RegisterFormCompany(FlaskForm):
    uid = IntegerField('uid',validators=[InputRequired(), NumberRange(min=5001,max=6000)])
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8,max=80)])
    company = StringField('company', validators=[InputRequired()])

@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request
    The variable g is globally accessible
    """
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        import traceback; traceback.print_exc()
        g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print "hhhh"
    if request.method == 'POST':
        # Get Form Fields
        username = request.form.get('username')
        password = request.form.get('password')
        print username
        print password

        # Create cursor
        # cur = mysql.connection.cursor()

        # # Get user by username
        # result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        cursor = g.conn.execute("SELECT name FROM candidate;")
        l = []
        for row in cursor:
            l.append(row['name'])
            print("name:", row['name'])
        print l


        # if result > 0:
        #     # Get stored hash
        #     data = cur.fetchone()
        #     password = data['password']
        if username in l:
            cursor = g.conn.execute("SELECT password FROM candidate where name = %s;", l[0])
            m = []
            for row in cursor:
                m.append(row['password'])
                print("password:", row['password'])
            # Compare Passwords
            # if sha256_crypt.verify(password_candidate, password):
            #     # Passed
            #     session['logged_in'] = True
            #     session['username'] = username

            #     flash('You are now logged in', 'success')
            if m[0] == password:
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')
    # ----------------------------
    # form = LoginForm()

    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user:
    #         if check_password_hash(user.password, form.password.data):
    #             login_user(user, remember=form.remember.data)
    #             return redirect(url_for('dashboard'))

    #     return '<h1>Invalid username or password</h1>'
    #     #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    # return render_template('login.html', form=form)
"""
@app.route('/signup')
def signup():
    return render_template('signup.html')
"""

@app.route('/signup_candidate')
def signup_candidate():
    form = RegisterFormCandidate()

    if form.validate_on_submit():
        newcandidate = 'INSERT INTO Candidate VALUES (:uid,:name,:password,:university)';
        g.conn.execute(Candidate(newcandidate), uid = form.uid.data, name = form.username.data, password = form.password.data, university = form.university.data);
        return redirect('/')
    return render_template('/signup_candidate.html', form=form)
@app.route('/signup_company')
def signup_company():
    form = RegisterFormCompany()

    return render_template('/signup_company.html', form=form)
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
"""
if __name__ == '__main__':
    app.run(debug=True)
"""
if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()

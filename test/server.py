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

# tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
# app = Flask(__name__, template_folder=tmpl_dir)
app = Flask(__name__)
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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
# @app.route('/')
# def index():
#   """
#   request is a special object that Flask provides to access web request information:
#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
#   See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
#   """

#   # DEBUG: this is debugging code to see what request looks like
#   print request.args


#   #
#   # example of a database query
#   #
#   cursor = g.conn.execute("SELECT name FROM test")
#   names = []
#   for result in cursor:
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

#   #
#   # Flask uses Jinja templates, which is an extension to HTML where you can
#   # pass data to a template and dynamically generate HTML based on the data
#   # (you can think of it as simple PHP)
#   # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
#   #
#   # You can see an example template in templates/index.html
#   #
#   # context are the variables that are passed to the template.
#   # for example, "data" key in the context variable defined below will be
#   # accessible as a variable in index.html:
#   #
#   #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#   #     <div>{{data}}</div>
#   #
#   #     # creates a <div> tag for each element in data
#   #     # will print:
#   #     #
#   #     #   <div>grace hopper</div>
#   #     #   <div>alan turing</div>
#   #     #   <div>ada lovelace</div>
#   #     #
#   #     {% for n in data %}
#   #     <div>{{n}}</div>
#   #     {% endfor %}
#   #
#   context = dict(data = names)


#   #
#   # render_template looks in the templates/ folder for files.
#   # for example, the below file reads template/index.html
#   #
#   return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
# @app.route('/another')
# def another():
#   return render_template("anotherfile.html")


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   print name
#   cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#   g.conn.execute(text(cmd), name1 = name, name2 = name);
#   return redirect('/')


# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()

#below is from open source template
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

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
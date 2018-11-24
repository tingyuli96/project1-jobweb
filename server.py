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
from flask import Flask, request, render_template, g, redirect, Response, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm, Form
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, IntegerField
from wtforms.validators import InputRequired,  DataRequired, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
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


def login_required_can(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            #flash('hey yo login first')
            return redirect(url_for('login_can'))
    return wrap

def login_required_com(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            #flash('hey yo login first')
            return redirect(url_for('login_com'))
    return wrap


class RegisterFormCandidate(FlaskForm):
    """candidate register"""
    uid = IntegerField('uid',validators=[InputRequired()])
    username = StringField('username',validators=[InputRequired()])
    password = PasswordField('password',validators=[InputRequired()])
    university = StringField('university')

class RegisterFormCompany(FlaskForm):
    """company user register"""
    uid = IntegerField('uid',validators=[InputRequired()])
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    cid = IntegerField('cid', validators=[InputRequired()])

class AddFormCompany(FlaskForm):
    """add company to database"""
    cid = IntegerField('cid',validators=[InputRequired()])
    name = StringField('name',validators=[InputRequired()])
    size = SelectField('size',choices=[('1','1-10'),('2','10-50'),('3','50-100'),('4','100-250'),('5','250-1000'),('6','1000-5000'),('7','5000-10000'),('8','10000-25000'),('9','25000+')])
    description = TextAreaField('description')

# class CandidateProfile():
#     def __init__(self):
#         uid = None
#         name = None
#         password = None
#         university = None
#         skills = {} #key:skill name, value: proficency
#         majors = {} #key: name, value: level
#         applyjobs = [] #(cid,title)

#     def setuid(self,uid):
#         self.uid = uid

#     def setname(self,name):
#         self.name = name

#     def setpassword(self,password):
#         self.password = password

#     def setuniversity(self,university):
#         self.university = university

#     def addskills(self,skill,proficency):
#         self.skills[skill] = proficency

#     def addmajors(self,major,level):
#         self.majors[major] = level

#     def addapplyjobs(self,cid,title):
#         applyjobs.append((cid,title))

#     def name(self):
#         print self.name
#         return self.name



def check_exist_uid(uid):
    """
    if uid exist in database, return True
    """
    uidlist = []
    cursor1 = g.conn.execute("select uid from candidate")
    cursor2 = g.conn.execute("select uid from companyusers_affi")
    for result in cursor1:
        uidlist.append(result['uid'])
    for result in cursor2:
        uidlist.append(result['uid'])
    cursor1.close()
    cursor2.close()
    if uid in uidlist:
        return True
    else:
        return False

def check_exist_cid(cid):
    """
    if cid exist in database, return True
    """
    cidlist = []
    cursor = g.conn.execute("select cid from companyusers_affi")
    for result in cursor:
        cidlist.append(result['cid'])
    cursor.close()
    if cid in cidlist:
        return True
    else:
        return False

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


@app.route('/dashboard_can/<uid>')
@login_required_can
def dashboard_can(uid):
    getcandidate = "SELECT * FROM candidate WHERE uid=:uid;"
    cursor = g.conn.execute(text(getcandidate),uid=uid)
    for result in cursor:
        name = result['name']
        university = result['university']
    cursor.close()

    getSkill = "SELECT sname, proficiency FROM can_has_skills WHERE uid=:uid;"
    cursor1 = g.conn.execute(text(getSkill),uid=uid)
    skill_pro = ''
    for result in cursor1:
        skill_pro = skill_pro + result['sname']+": "
        skill_pro = skill_pro + str(result['proficiency']) + ";\n"
    cursor1.close()

    getMajor = "SELECT * FROM can_has_major WHERE uid=:uid;"
    cursor2 = g.conn.execute(text(getMajor),uid=uid)
    maj = ''
    for result in cursor2:
        maj = maj + result['mname']+": "
        maj = maj + result['level'] + "; "
    cursor2.close()

    
    can_job = "select can_apply_pos.title, company.cname from can_apply_pos inner join company on can_apply_pos.cid = company.cid where can_apply_pos.uid = :uid;"
    cursor3 = g.conn.execute(text(can_job),uid=uid)
    job = ''
    for result in cursor3:
        job = job + result['cname']+": "
        job = job + result['title'] + ";\n "
    cursor3.close()

    comm = "select * from can_expect_loc where uid = :uid;"
    cursor4 = g.conn.execute(text(comm),uid=uid)
    loc = ''
    for result in cursor4:
        loc = loc + result['city']+", "
        loc = loc + result['state'] + ", "
        loc = loc + result['country'] + ", "
    cursor4.close()

    context = dict(uid=uid, name=name,university=university,maj=maj, skill_pro=skill_pro,  loc=loc, job=job)
    return render_template('dashboard_can.html',**context)

@app.route('/dashboard_com/<uid>')
@login_required_com
def dashboard_com(uid):
    getcompanyuser = "SELECT * FROM companyusers_affi WHERE uid=:uid;"
    cursor1 = g.conn.execute(text(getcompanyuser),uid=uid)
    for result in cursor1:
        name = result['name']
        cid = result['cid']
    cursor1.close()
    cursor2 = g.conn.execute("SELECT * from company WHERE cid = {};".format(cid))
    sizedic=dict([('1','1-10'),('2','10-50'),('3','50-100'),('4','100-250'),('5','250-1000'),('6','1000-5000'),('7','5000-10000'),('8','10000-25000'),('9','25000+')])
    for result in cursor2:
        cname = result['cname']
        size = sizedic[str(result['size'])]
        description = result['description']
    cursor2.close()
    cursor3 = g.conn.execute("SELECT title, posttime FROM position_liein_post WHERE cid = {} and uid = {};".format(cid,uid))
    jobs = []
    for result in cursor3:
        jobs.append(result)
    cursor3.close()
    context = dict(uid=uid, name=name,cid=cid,cname=cname,size=size,description=description,jobs=jobs)
    return render_template('dashboard_com.html',**context)




#credit to https://github.com/realpython/discover-flas
@app.route('/login_can', methods=['GET', 'POST'])
def login_can():
    if request.method == 'POST':
        # Get Form Fields
        uid = request.form.get('uid')
        password = request.form.get('password')
        print uid
        print password

        cursor = g.conn.execute("SELECT uid FROM candidate;")
        l = []
        for row in cursor:
            l.append(row['uid'])
            print("uid:", row['uid'])

        if int(uid) in l:
            t = text("SELECT password FROM candidate where uid = :newuid ;")
            cursor = g.conn.execute(t, newuid=uid)
            m = []
            for row in cursor:
                m.append(row['password'])
                print("password:", row['password'])

            if m[0] == password:
                session['logged_in'] = True
                return redirect(url_for('dashboard_can',uid=uid))
            else:
                error = 'Invalid login_can. Please try again.'
                return render_template('login_can.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Uid not found'
            return render_template('login_can.html', error=error)

    return render_template('login_can.html')



@app.route('/login_com', methods=['GET', 'POST'])
def login_com():
    if request.method == 'POST':
        # Get Form Fields
        uid = request.form.get('uid')
        password = request.form.get('password')
        print uid
        print password

        cursor = g.conn.execute("SELECT uid FROM companyusers_affi;")
        l = []
        for row in cursor:
            l.append(row['uid'])
            print("uid:", row['uid'])

        if int(uid) in l:
            t = text("SELECT password FROM companyusers_affi where uid = :newuid ;")
            cursor = g.conn.execute(t, newuid=uid)
            m = []
            for row in cursor:
                m.append(row['password'])
                print("password:", row['password'])

            if m[0] == password:
                session['logged_in'] = True
                return redirect(url_for('dashboard_com',uid=uid))
            else:
                error = 'Invalid login_com. Please try again.'
                return render_template('login_com.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Uid not found'
            return render_template('login_com.html', error=error)

    return render_template('login_com.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/signup_candidate', methods=['GET', 'POST'])
def signup_candidate():
    form = RegisterFormCandidate()
    print 'uid:{}'.format(form.uid.data)
    if form.validate_on_submit():
        print 'add new user'
        newcandidate = 'INSERT INTO Candidate VALUES (:uid,:name,:password,:university)';
        newuid = form.uid.data
        newname = form.username.data
        newpassword = form.password.data
        newuniversity = form.university.data
        flag = check_exist_uid(newuid)
        if not flag:
            g.conn.execute(text(newcandidate), uid = newuid, name = newname,\
                           password = newpassword, university = newuniversity);
            return redirect(url_for('login_can'))
        else:
            return render_template('/signup_candidate.html', form=form, notvaliduser = True)
    return render_template('/signup_candidate.html', form=form, notvaliduser = False)

@app.route('/signup_company', methods=['GET','POST'])
def signup_company():
    form = RegisterFormCompany()
    print 'uid:{}'.format(form.uid.data)
    print 'user:{}'.format(form.username.data)
    print 'password:{}'.format(form.password.data)
    print 'cid:{}'.format(form.cid.data)
    # if request.method == 'POST':
    if form.validate_on_submit():
        print 'add new company user'
        newuid = form.uid.data
        newusername = form.username.data
        newpassword = form.password.data
        newcid = form.cid.data
        newcompanyuser = "INSERT INTO companyusers_affi VALUES (:uid,:username,:password,:cid)";
        flag1 = check_exist_uid(newuid)
        flag2 = check_exist_cid(newcid)
        if not flag1 and flag2:
            print 'valid, add'
            g.conn.execute(text(newcompanyuser), \
                uid = newuid, \
                username = newusername,\
                password = newpassword, \
                cid = newcid);
            return redirect(url_for('login_com')) 
        elif flag1:
            print "not valid uid"
            return render_template('/signup_company.html', form=form, notvaliduser = True, notvalidcid = False)
        elif not flag2:
            print "not valid cid"
            return render_template('/signup_company.html', form=form, notvaliduser = False, notvalidcid = True)
        else:
            print "not valid unknow"
            return render_template('/signup_company.html', form=form, notvaliduser = False, notvalidcid=False)
    return render_template('/signup_company.html', form=form, notvaliduser = False, notvalidcid=False)

# def signup_company():
# #    form = RegisterFormCompany()
#     if request.method == 'POST':
#         print 'add new company user'
#         newuid = request.form.get['uid']
#         newusername = request.form.get['username']
#         newpassword = request.form.get['password']
#         newcid = request.form.get['cid']
#         newcompanyuser = "INSERT INTO companyusers_affi VALUES (:uid,:username,:password,:company)"
#         flag = check_valid_uid(newuid)
#         if flag:
#             g.conn.execute(text(newcompanyuser), uid = newuid, name = newname,\
#                            password = newpassword, cid = newcid);
#             cur = g.conn.execute("select * from companyusers_affi;")
#             for i in cur:
#                 print i
#             return redirect("/")
#         else:
#             return render_template('/signup_company.html', notvaliduser = True)
#     return render_template('/signup_company.html', notvaliduser = False)

@app.route('/add_company', methods=['GET','POST'])
def add_company():
    """add company to database"""
    form = AddFormCompany()
    if form.validate_on_submit():
        print 'add_company'
        newcid = form.cid.data
        newname = form.name.data
        newsize = form.size.data
        newdesciption = form.description.data
        flag = check_exist_cid(newcid)
        if not flag:
            newcompany = "INSERT INTO company VALUES (:cid,:cname,:size,:description);"
            g.conn.execute(text(newcompany),cid=newcid,cname=newname,size=newsize,description=newdesciption)
            return redirect("/")
        else:
            return render_template('/add_company.html',form=form, notvalidcid=True)
    return render_template('/add_company.html',form=form, notvalidcid=False)


class updateClass_can(FlaskForm):
    """add company to database"""
    uid = IntegerField('uid')
    name = StringField('name')
    password = PasswordField('password')
    university = StringField('university')
    major = StringField('major')
    skill1 = StringField('skill1')
    skill2 = StringField('skill2')
    skill3 = StringField('skill3')
    preLoc = StringField('prefered location')


@app.route('/updateInfo_can', methods=['GET', 'POST'])
@login_required_com
def updateInfo_can():
    form = updateClass_can()
    #print 'uid:{}'.format(form.uid.data)
    if form.validate_on_submit():
        print 'add new user'
        newcandidate = 'INSERT INTO Candidate VALUES (:uid,:name,:password,:university)';
        newname = form.username.data
        newpassword = form.password.data
        newuniversity = form.university.data
        flag = check_exist_uid(newuid)
        if not flag:
            g.conn.execute(text(newcandidate), uid = newuid, name = newname,\
                           password = newpassword, university = newuniversity);
            return redirect(url_for('login_can'))
        else:
            return render_template('/updateinfo_can.html', form=form, notvaliduser = True)
    return render_template('/updateinfo_can.html', form=form, notvaliduser = False)

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
    @click.argument('PORT', default=5000, type=int)
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

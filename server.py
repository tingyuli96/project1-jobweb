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
from datetime import date
from sets import Set
import re
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
        if 'uid' in session:
            return f(*args, **kwargs)
        else:
            #flash('hey yo login first')
            return redirect(url_for('login_can'))
    return wrap

def login_required_com(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'uid' in session:
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

class UpdateFormCompanyUser(FlaskForm):
    """company user register"""
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    cid = IntegerField('cid', validators=[InputRequired()])

class AddFormCompany(FlaskForm):
    """add company to database"""
    cid = IntegerField('cid',validators=[InputRequired()])
    name = StringField('name',validators=[InputRequired()])
    size = SelectField('size',choices=[('1','1-10'),('2','10-50'),('3','50-100'),('4','100-250'),('5','250-1000'),('6','1000-5000'),('7','5000-10000'),('8','10000-25000'),('9','25000+')])
    description = TextAreaField('description')

class UpdateFormCompany(FlaskForm):
    """add company to database"""
    name = StringField('name',validators=[InputRequired()])
    size = SelectField('size',choices=[('1','1-10'),('2','10-50'),('3','50-100'),('4','100-250'),('5','250-1000'),('6','1000-5000'),('7','5000-10000'),('8','10000-25000'),('9','25000+')])
    description = TextAreaField('description')

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
    cursor = g.conn.execute("select cid from company;")
    for result in cursor:
        cidlist.append(result['cid'])
    cursor.close()
    print cidlist
    print cid
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
    if 'uid' in session:
        uid = session['uid']
        return render_template('index.html',uid=uid)
    else:
        return render_template('index.html',uid=None)


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
    # job = ''
    # for result in cursor3:
    #     job = job + result['cname']+": "
    #     job = job + result['title'] + ";\n "
    jobs = []
    for result in cursor3:
        jobs.append(result)
    cursor3.close()

    comm = "select * from can_expect_loc where uid = :uid;"
    cursor4 = g.conn.execute(text(comm),uid=uid)
    loc = ''
    for result in cursor4:
        loc = loc + result['city']+", "
        loc = loc + result['state'] + ", "
        loc = loc + result['country'] + ", "
    cursor4.close()

    context = dict(uid=uid, name=name,university=university,maj=maj, skill_pro=skill_pro,  loc=loc, jobs=jobs)
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
    command = "SELECT * from company WHERE cid = :cid;"
    cursor2 = g.conn.execute(text(command),cid=cid)
    sizedic=dict([('1','1-10'),('2','10-50'),('3','50-100'),('4','100-250'),('5','250-1000'),('6','1000-5000'),('7','5000-10000'),('8','10000-25000'),('9','25000+')])
    for result in cursor2:
        cname = result['cname']
        size = sizedic[str(result['size'])]
        description = result['description']
    cursor2.close()
    command = "SELECT title, posttime FROM position_liein_post WHERE cid = :cid and uid = :uid;"
    cursor3 = g.conn.execute(text(command),cid=cid,uid=uid)
    jobs = []
    for result in cursor3:
        jobs.append(result)
    cursor3.close()
    context = dict(uid=uid, name=name,cid=cid,cname=cname,size=size,description=description,jobs=jobs)
    return render_template('dashboard_com.html',**context)

@app.route('/findcandidate', methods = ['GET','POST'])
@login_required_com
def findcandidate():
    usruid = session['uid']
    uid = Set()
    cursor = g.conn.execute("SELECT uid FROM candidate;")
    for result in cursor:
        uid.add(result['uid'])
    #     university.append(result['university'])
    # majors = []
    # cursor = g.conn.execute("SELECT mname FROM majors;")
    # for result in cursor:
    #     majors.append(result['mname'])
    if request.method == 'POST':
        uid_s = Set() #skills
        uid_m = Set() #major
        # uid_u = Set() #university
        findsname = request.form.get('skill')
        findmname = request.form.get('major')
        if findsname != "":
            print '------start match--------'
            findsname = '%'+findsname+'%'
            print 'findsname:{}'.format(findsname)
            command = "SELECT uid from can_has_skills WHERE sname ilike :sname;"
            cursor = g.conn.execute(text(command),sname = findsname)
            for result in cursor:
                uid_s.add(result['uid'])
        else:
            uid_s = uid.copy()
        if findmname != "":
            print '------start match--------'
            findmname = '%'+findmname+'%'
            print 'findmname:{}'.format(findmname)
            command = "SELECT uid from can_has_major WHERE mname ilike :mname;"
            cursor = g.conn.execute(text(command),mname=findmname)
            for result in cursor:
                uid_m.add(result['uid'])
        else:
            uid_m = uid.copy()
        uid = uid_m & uid_s
        print 'uid:{}'.format(uid)
        # return redirect(url_for('findcandidate',uid=uid))
    print 'uid:{}'.format(uid)
    command = "SELECT uid, name, university from candidate where uid = :uid"
    profile = []
    for id in uid:
        cursor = g.conn.execute(text(command),uid=id)
        for result in cursor:
            profile.append(result)
    print "profile={}".format(profile)
    context = dict(usruid = usruid, profile=profile)
    return render_template('/findcandidate.html',**context)

@app.route('/profile_can/<uid>')
@login_required_com
def profile_can(uid):
    usruid = session['uid']
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
    comm = "select * from can_expect_loc where uid = :uid;"
    cursor4 = g.conn.execute(text(comm),uid=uid)
    loc = ''
    for result in cursor4:
        loc = loc + result['city']+", "
        loc = loc + result['state'] + ", "
        loc = loc + result['country'] + ", "
    cursor4.close()
    context = dict(usruid=usruid, uid=uid, name=name,university=university,maj=maj, skill_pro=skill_pro,  loc=loc)
    return render_template('profile_can.html',**context)

@app.route('/updateInfo_com', methods=['GET','POST'])
@login_required_com
def updateInfo_com():
    uid = session['uid']
    getcompanyuser = "SELECT * FROM companyusers_affi WHERE uid=:uid;"
    cursor1 = g.conn.execute(text(getcompanyuser),uid=uid)
    for result in cursor1:
        cid = result['cid']
    form = UpdateFormCompanyUser()
    if form.validate_on_submit():
        newusername = form.username.data
        newpassword = form.password.data
        newcid = form.cid.data
        newcompanyuser = "UPDATE companyusers_affi SET name = :username,password=:password,cid=:cid WHERE uid=:uid;"
        flag = check_exist_cid(newcid)
        if flag:
            print 'valid, add'
            g.conn.execute(text(newcompanyuser), \
                uid = uid,\
                username = newusername,\
                password = newpassword, \
                cid = newcid);
            return redirect(url_for('dashboard_com',uid=uid)) 
        else:
            print "not valid cid"
            return render_template('/updateInfo_com', uid=uid, cid=cid, form=form, notvalidcid = True)
    return render_template ('/updateInfo_com.html', uid=uid, cid=cid, form=form, notvalidcid=False)

@app.route('/editcompany/<cid>', methods=['GET','POST'])
@login_required_com
def editcompany(cid):
    uid = session['uid']
    form = UpdateFormCompany()
    if form.validate_on_submit():
        print 'add_company'
        newname = form.name.data
        newsize = form.size.data
        newdesciption = form.description.data
        newcompany = "UPDATE company SET cname=:cname,size=:size,description=:description WHERE cid=:cid;"
        g.conn.execute(text(newcompany),cid=cid,cname=newname,size=newsize,description=newdesciption)
        return redirect(url_for('dashboard_com',uid=uid))
    return render_template('/editcompany.html',uid=uid, cid=cid, form=form)

@app.route('/deleteuser_com')
@login_required_com
def deleteuser_com():
    uid = session['uid']
    session.pop('uid', None)
    command = "SELECT cid, title FROM position_liein_post WHERE uid=:uid;"
    cursor = g.conn.execute(text(command),uid=uid)
    joblist = []
    for result in cursor:
        joblist.append(result)
    for job in joblist:
        command = "DELETE FROM pos_require_skills WHERE cid=:cid and title=:title;"
        cursor = g.conn.execute(text(command),cid=job['cid'],title=job['title'])
        command = "DELETE FROM pos_expect_major WHERE cid=:cid and title=:title;"
        cursor = g.conn.execute(text(command),cid=job['cid'],title=job['title'])
    command = "DELETE FROM position_liein_post WHERE uid=:uid;"
    cursor = g.conn.execute(text(command),uid=uid)
    command = "DELETE FROM companyusers_affi WHERE uid=:uid;"
    cursor = g.conn.execute(text(command),uid=uid)
    return redirect('/')

@app.route('/deletejob/<cid>/<title>')
@login_required_com
def deletejob(cid,title):
    uid = session['uid']
    command = "DELETE FROM pos_require_skills WHERE cid=:cid and title=:title;"
    cursor = g.conn.execute(text(command),cid=cid,title=title)
    command = "DELETE FROM pos_expect_major WHERE cid=:cid and title=:title;"
    cursor = g.conn.execute(text(command),cid=cid,title=title)
    command = "DELETE FROM position_liein_post WHERE cid=:cid and title=:title;"
    cursor = g.conn.execute(text(command),cid=cid,title=title)
    return redirect(url_for('dashboard_com',uid=uid))

@app.route('/postjob/<cid>/<uid>', methods=['GET','POST'])
@login_required_com
def postjob(cid,uid):
    cursor = g.conn.execute("SELECT * FROM location")
    hascity = Set()
    hasstate = Set()
    hascountry = Set()
    haslocation = []
    for result in cursor:
        hascity.add(result['city'])
        hasstate.add(result['state'])
        hascountry.add(result['country'])
        haslocation.append(result)
    cursor.close()
    context = dict(cid=cid,uid=uid,hascity=hascity,hasstate=hasstate,hascountry=hascountry, locationerror=False, titleerror=False, dateerror=False)
    if request.method == 'POST':
        title = request.form.get('title')
        appddl = request.form.get('appddl')
        worktype = request.form.get('worktype')
        description = request.form.get('description')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        posttime = str(date.today())
        # check if appdl is the right formate
        dateformateflag = re.match(r"\d{4}-\d{2}-\d{2}",appddl) #return True if match
        monthflag = False 
        dateflag = False
        if dateformateflag:
            month = int(re.search(r"(?<=\d{4}-)\d{2}",appddl).group(0)) 
            if month > 0 and month < 13:
                monthflag = True
            day = int(re.search(r"\d{2}$",appddl).group(0))
            if day > 0 and day < 31:
                dateflag = True
        validdate = dateformateflag and monthflag and dateflag
        # get exist title of this cid
        command = "SELECT title from position_liein_post WHERE cid=:cid;"
        cursor = g.conn.execute(text(command),cid=cid)
        hastitle = []
        for result in cursor:
            hastitle.append(result['title'])
        print 'posttime:{}'.format(posttime)
        if (city,state,country) in haslocation and title not in hastitle and validdate:
            command = "INSERT INTO position_liein_post VALUES(:cid,:uid,:country,:state,:city,:title,:description,:worktype,:appddl,:posttime);"
            cursor = g.conn.execute(text(command),cid=cid,uid=uid,country=country,state=state,city=city,title=title,description=description,worktype=worktype,appddl=appddl,posttime=posttime)
            cursor.close()
            return redirect(url_for('editjob',cid=cid,title=title))
        if title in hastitle:
            print '--------title exist-------------'
            context['titleerror'] = True
        if (city,state,country) not in haslocation:
            context['locationerror'] = True
        if not validdate:
            context['dateerror'] = True
        return render_template('postjob.html',**context)
    return render_template('/postjob.html',**context)


@app.route('/addlocation_com/<cid>/<uid>', methods = ['GET','POST'])
def addlocation_com(cid,uid):
    if request.method == 'POST':
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        cursor = g.conn.execute("SELECT * FROM location")
        hascity = Set()
        hasstate = Set()
        hascountry = Set()
        for result in cursor:
            hascity.add(result['city'])
            hasstate.add(result['state'])
            hascountry.add(result['country'])
        cursor.close()
        if city not in hascity or state not in hasstate or country not in hascountry:
            command = "INSERT INTO location VALUES (:city,:state,:country);"
            cursor = g.conn.execute(text(command),city=city,state=state,country=country);
            cursor.close()
            return redirect(url_for('postjob',cid=cid,uid=uid))
        else:
            return render_template('addlocation.html', uid = uid, error=True)

    return render_template('addlocation.html', uid = uid, error=False)

# @app.route('/editprofile_com/<cid>/<uid>', methods = ['GET','POST'])
# def editprofile_com(cid,uid):


@app.route('/editjob/<cid>/<title>')
@login_required_com
def editjob(cid,title):
    """
    show the overview of the job and edit on the end of list
    other uid can edie too
    """
    uid = session['uid']
    command = "SELECT * FROM company WHERE cid = :cid;"
    cursor = g.conn.execute(text(command),cid=cid)
    for result in cursor:
        company = result
    command = "SELECT * FROM position_liein_post where cid = :cid and title = :title;"
    cursor = g.conn.execute(text(command),cid=cid,title=title)
    for result in cursor:
        position = result
    cursor.close()
    command = "SELECT * FROM pos_require_skills where cid = :cid and title = :title;"
    cursor = g.conn.execute(text(command), cid=cid,title=title)
    skills = []
    for result in cursor:
        skills.append(result)
    cursor.close()
    command = "SELECT * FROM pos_expect_major where cid = :cid and title = :title"
    cursor = g.conn.execute(text(command),cid=cid,title=title)
    majors = []
    for result in cursor:
        majors.append(result)
    context = dict(uid=uid, company = company, position = position, skills = skills, majors = majors)
    return render_template('editjob.html', **context)

@app.route('/editjob_overview/<cid>/<title>', methods = ['GET','POST'])
@login_required_com
def editjob_overview(cid,title):
    uid = session['uid']
    cursor = g.conn.execute("SELECT * FROM location")
    hascity = Set()
    hasstate = Set()
    hascountry = Set()
    haslocation = []
    for result in cursor:
        hascity.add(result['city'])
        hasstate.add(result['state'])
        hascountry.add(result['country'])
        haslocation.append(result)
    cursor.close()
    context = dict(cid=cid,uid=uid,title=title, hascity=hascity,hasstate=hasstate,hascountry=hascountry, locationerror=False, dateerror=False)
    if request.method == 'POST':
        appddl = request.form.get('appddl')
        worktype = request.form.get('worktype')
        description = request.form.get('description')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        posttime = str(date.today())
        # check if appdl is the right formate
        dateformateflag = re.match(r"\d{4}-\d{2}-\d{2}",appddl) #return True if match
        monthflag = False 
        dateflag = False
        if dateformateflag:
            month = int(re.search(r"(?<=\d{4}-)\d{2}",appddl).group(0)) 
            if month > 0 and month < 13:
                monthflag = True
            day = int(re.search(r"\d{2}$",appddl).group(0))
            if day > 0 and day < 31:
                dateflag = True
        validdate = dateformateflag and monthflag and dateflag
        # get exist title of this cid
        if (city,state,country) in haslocation and validdate:
            command = "UPDATE position_liein_post SET country=:country,state=:state,\
                        city=:city,description=:description,worktype=:worktype,\
                        appddl=:appddl,posttime=:posttime\
                        WHERE cid=:cid and title = :title;"
            cursor = g.conn.execute(text(command),cid=cid,country=country,state=state,city=city,title=title,description=description,worktype=worktype,appddl=appddl,posttime=posttime)
            cursor.close()
            return redirect(url_for('editjob',cid=cid,title=title))
        if (city,state,country) not in haslocation:
            context['locationerror'] = True
        if not validdate:
            context['dateerror'] = True
        return render_template('/editjob_overview.html',**context)
    return render_template('/editjob_overview.html',**context)

@app.route('/addjob_skill/<cid>/<title>', methods = ['GET','POST'])
@login_required_com
def addjob_skill(cid,title):
    """
    add skill to pos_require_skills
    """
    context = dict(cid=cid,title=title,nameerror=False)
    if request.method == 'POST':
        skills = {}
        sname = request.form.get('sname')
        proficiency = request.form.get('proficiency')
        cursor = g.conn.execute("SELECT * FROM skills")
        hasskills = [] # skill in table skill
        for result in cursor:
            hasskills.append(result['sname'])
        if sname not in hasskills:
            command = "INSERT INTO skills VALUES (:sname);"
            cursor = g.conn.execute(text(command),sname=sname)
        command = "SELECT sname FROM pos_require_skills WHERE cid = :cid and title = :title;"
        cursor = g.conn.execute(text(command),cid=cid,title=title)
        hassname = [] # skill in pos_require_skill
        for result in cursor:
            hassname.append(result['sname'])
        if sname not in hassname:
            print 'proficiency={}'.format(proficiency)
            command = "INSERT INTO pos_require_skills VALUES (:title,:cid,:sname,:proficiency);"
            cursor = g.conn.execute(text(command),title=title,cid=cid,sname=sname,proficiency=proficiency)
            cursor.close()
            return redirect(url_for('editjob',cid=cid,title=title))
        else:
            context['nameerror']=True
            cursor.close()
            return render_template('addjob_skill.html',**context)
    return render_template('addjob_skill.html',**context)

@app.route('/editjob_skill/<cid>/<title>/<sname>', methods = ['GET','POST'])
@login_required_com
def editjob_skill(cid,title,sname):
    context = dict(cid=cid,title=title,sname=sname)
    if request.method == 'POST':
        proficiency =  request.form.get("proficiency")
        command = "UPDATE pos_require_skills SET proficiency = :proficiency WHERE cid=:cid and title=:title and sname=:sname;"
        cursor = g.conn.execute(text(command),proficiency=proficiency,cid=cid,title=title,sname=sname)
        cursor.close()
        return redirect(url_for('editjob',cid=cid,title=title))
    return render_template('/editjob_skill.html',**context)

@app.route('/deletejob_skill/<cid>/<title>/<sname>')
@login_required_com
def deletejob_skill(cid,title,sname):
    command = "DELETE FROM pos_require_skills WHERE cid=:cid and title=:title and sname=:sname;"
    cursor=g.conn.execute(text(command),cid=cid,title=title,sname=sname)
    cursor.close()
    return redirect(url_for('editjob',cid=cid,title=title))

@app.route('/addjob_major/<cid>/<title>', methods = ['GET','POST'])
@login_required_com
def addjob_major(cid,title):
    """
    add skill to pos_require_skills
    """
    context = dict(cid=cid,title=title,nameerror=False)
    if request.method == 'POST':
        majors = {}
        mname = request.form.get('mname')
        level = request.form.get('level')
        cursor = g.conn.execute("SELECT * FROM major")
        hasmajors = [] # skill in table skill
        for result in cursor:
            hasmajors.append(result['mname'])
        if mname not in hasmajors:
            command = "INSERT INTO major VALUES (:mname);"
            cursor = g.conn.execute(text(command),mname=mname)
        command = "SELECT mname FROM pos_expect_major WHERE cid = :cid and title = :title;"
        cursor = g.conn.execute(text(command),cid=cid,title=title)
        hasmname = [] # skill in pos_expect_skill
        for result in cursor:
            hasmname.append(result['mname'])
        if mname not in hasmname:
            print 'level={}'.format(level)
            command = "INSERT INTO pos_expect_major(title,cid,mname,level) VALUES (:title,:cid,:mname,:level);"
            cursor = g.conn.execute(text(command),title=title,cid=cid,mname=mname,level=level)
            cursor.close()
            return redirect(url_for('editjob',cid=cid,title=title))
        else:
            context['nameerror']=True
            cursor.close()
            return render_template('addjob_major.html',**context)
    return render_template('addjob_major.html',**context)

@app.route('/editjob_major/<cid>/<title>/<mname>', methods = ['GET','POST'])
@login_required_com
def editjob_major(cid,title,mname):
    context = dict(cid=cid,title=title,mname=mname)
    if request.method == 'POST':
        level =  request.form.get("level")
        command = "UPDATE pos_expect_major SET level = :level WHERE cid=:cid and title=:title and mname=:mname;"
        cursor = g.conn.execute(text(command),level=level,cid=cid,title=title,mname=mname)
        cursor.close()
        return redirect(url_for('editjob',cid=cid,title=title))
    return render_template('/editjob_major.html',**context)

@app.route('/deletejob_major/<cid>/<title>/<mname>')
@login_required_com
def deletejob_major(cid,title,mname):
    command = "DELETE FROM pos_expect_major WHERE cid=:cid and title=:title and mname=:mname;"
    cursor=g.conn.execute(text(command),cid=cid,title=title,mname=mname)
    cursor.close()
    return redirect(url_for('editjob',cid=cid,title=title))



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
                session['uid'] = request.form['uid']
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
                session['uid'] = request.form['uid']
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
    session.pop('uid', None)
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
        print "newcid={}".format(newcid)
        flag = check_exist_cid(newcid)
        if not flag:
            print 'flag={}'.format(flag)
            newcompany = "INSERT INTO company VALUES (:cid,:cname,:size,:description);"
            g.conn.execute(text(newcompany),cid=newcid,cname=newname,size=newsize,description=newdesciption)
            return redirect("/")
        else:
            return render_template('/add_company.html',form=form, notvalidcid=True)
    return render_template('/add_company.html',form=form, notvalidcid=False)


class updateClass_can(FlaskForm):
    """add company to database"""
    password = PasswordField('password')
    university = StringField('university')
    major = StringField('major(eg: Computer Science,PHD)')
    skill1 = StringField('skill1(skill name,proficiency level(number 1-5, 5 means expert)), eg: Java,3')
    skill2 = StringField('skill2, eg: Java,5')
    skill3 = StringField('skill3, eg: Java,5')
    preLoc = StringField('prefered location(city,state,country, eg: New York,NY,US)')



# @app.route('/editjob/<cid>/<title>')
# @login_required_com
# def editjob(cid,title):


@app.route('/updateInfo_can', methods=['GET', 'POST'])
@login_required_can
def updateInfo_can():
    form = updateClass_can()
    #print 'uid:{}'.format(form.uid.data)
    uid = session['uid']
    if form.validate_on_submit():
        newPassword = form.password.data
        newUniversity = form.university.data
        newMajor = form.major.data
        newPreLoc = form.preLoc.data
        newSkill1 = form.skill1.data
        newSkill2 = form.skill2.data
        newSkill3 = form.skill3.data
        if newPassword != '':
            comm = "update candidate set password =:newPassword where uid =:uid; "
            g.conn.execute(text(comm), uid=uid, newPassword=newPassword)



        # if not flag:
        #     g.conn.execute(text(newcandidate), uid = newuid, name = newname,\
        #                    password = newpassword, university = newuniversity);
        #     return redirect(url_for('login_can'))
        # else:
        #     return render_template('/updateinfo_can.html', form=form, notvaliduser = True)
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


## Install
### Requirement
python2.7 
virtualenv
### Set up
1. install virtualenv 
```
pip install virtualenv
```
2. create folder and activate a virtual environment
```
virtualenv -p python2.7 <projectname>
cd <projectname>
source bin/activate
```
3. get code
```
git clone https://github.com/colirain/project1-jobweb.git
```
4. install dependencies
```
pip -r requirements.txt
```

## Old instruct
Install pip if needed

        sudo apt-get install python-pip

Install libraries

        pip install click flask sqlalchemy


Edit `server.py` to set your database URI

        DATABASEURI = "<your database uri>"


Run it in the shell


        python server.py

Get help:

        python server.py --help

      

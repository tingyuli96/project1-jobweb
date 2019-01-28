# Get Hired
This is a design of a job hunting website.
The database we are planning to build is a job hunting platform. The clients are the companies who post open jobs and candidates who are looking for new jobs. The companies can search for the target candidates and send them invitations, and also they can receive applications from candidates.

## main feature
- Candidates can create his/her own profile, which includes unique id, name, and also connects to skills set, major,  ideal locations.  
- Company also have their own profiles with cid, name, size, description, and company users are affiliated to exactly one company.
- Both candidates and companies can search by set the filters from the entity set, and rank the results by preference like relevant or date post. 

## E-R diagram
![E-R diagram](https://github.com/colirain/project1-jobweb/ERdiagram/Project1-v3.png)

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
mkdir <projectname>
cd <projectname>
mkdir env 
virtualenv -p python2.7 env 
source /env/bin/activate
```
3. get code
```
git clone https://github.com/colirain/project1-jobweb.git
```
4. install dependencies
```
pip install --requirements requirements.txt
```
5. exit environment
```
deactivate
```
     

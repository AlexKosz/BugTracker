import requests
import json
from flask import Flask, g, render_template, request, redirect, session, url_for, flash  
from mysqlconnection import connectToMySQL



def validate_user(user):
    is_valid = False
    mysql = connectToMySQL('bugTracker')
    responses = mysql.query_db('SELECT * FROM users')
    for x in range (len(responses)):
        users.append(responses[x])
    for x in range (len(users)):
        if (users[x]['username'] == session['username']):
            print("found user")
            if(users[x]['password'] == session['password']):
                session['user_id'] = users[x]['id']
                is_valid = True
                return is_valid
            else:
                  flash("Invalid Password")
                  return is_valid
    flash("Invalid Username and/or Password")
    return is_valid
    

def validate_registration(user):
    is_valid = True
    print(user)
    if user['name'] == "" or user['password'] == "" or user['username'] == "" or user['githubProf'] == "":
        flash("All fields must be present")
        is_valid = False

    if len(user['name'])<2:
        flash("First name must be at least 2 characters long")
        is_valid = False

    if len(user['password']) < 8:
        flash("password must be at least 8 characters long")
        is_valid = False

    if user['githubProf'].startswith('http') :
        flash("Do not include https on your github link")
        is_valid = False
    return is_valid

def validate_project(project):
    is_valid = True
    if project['name'] == "" or project['scope'] == "" or project['lang'] == "" or project['githubLink'] == "":
        flash("All fields must be present")
        is_valid = False

    if len(project['name'])<2:
        flash("Name must be at least 2 characters long")
        is_valid = False

    if len(project['scope']) < 8:
        flash("Description must be at least 5 characters long")
        is_valid = False

    if len(project['lang']) < 8:
        flash("Description must be at least 2 characters long")
        is_valid = False




    if project['githubLink'].startswith('http') :
        flash("Do not include https on your github link")
        is_valid = False
    return is_valid







users = []
app = Flask(__name__)    
app.secret_key = 'secKey'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM users WHERE id = %(id)s'
        data = {
            "id": session['user_id']
            }
        user = mysql.query_db(query, data)
        user = user[0]
        session['user']=user
        g.user = user
        
        
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        is_valid = validate_user(request.form)
        if not is_valid:
            return redirect(url_for('login'))
        return redirect(url_for('profile'))        
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.pop('user_id', None)
        is_valid = validate_registration(request.form)
        print (is_valid)
        if is_valid:
            mysql = connectToMySQL('bugTracker')
            query='INSERT INTO users (username, password, githubProf, name) VALUES (%(username)s, %(password)s, %(githubProf)s, %(name)s);'
            data = {
                "username": request.form['username'],
                "password": request.form['password'],
                "githubProf": request.form['githubProf'],
                "name": request.form['name']
                }
            mysql.query_db(query, data)
            return redirect(url_for('login'))
        return redirect(url_for('register'))    
    return render_template('register.html')


@app.route('/newProj', methods=['GET', 'POST'])
def newProj():
    if session.get('user_id') is None:
        return redirect('/')
    if request.method == 'POST':


        is_valid=validate_project(request.form)
        if is_valid:
            name = request.form['name']
            scope = request.form['scope']
            githubLink = request.form['githubLink']
            lang = request.form['lang']
            finished = 0
            user_id = session['user_id']
            mysql = connectToMySQL('bugTracker')
            query='INSERT INTO projects (name, scope, lang, githubLink, finished, user_id) VALUES (%(name)s, %(scope)s, %(lang)s, %(githubLink)s, %(finished)s, %(user_id)s);'
            data = {
                "name": name,
                "scope": scope,
                "lang": lang,
                "githubLink": githubLink,
                "finished": finished,
                "user_id": user_id,
                }
                
            mysql.query_db(query, data)
            return redirect(url_for('profile'))
        return redirect(url_for('newProj'))
    return render_template('newProj.html')


@app.route('/newBug', methods=['GET', 'POST'])
def newBug():
    if session.get('user_id') is None:
        return redirect('/')
    if request.method == 'POST':
        code = request.form['code']
        description = request.form['description']
        project_id = session['project_id']
        user_id = session['user_id']

        mysql = connectToMySQL('bugTracker')
        query='INSERT INTO bugs (Code, Description, Solved, cause, project_id, user_id) VALUES (%(code)s, %(description)s, %(solved)s, %(cause)s, %(project_id)s, %(user_id)s);'
        data = {
            "code": code,
            "description": description,
            "solved": 0,
            "cause": "unkown",
            "project_id": project_id,
            "user_id": user_id,
            }
            
        mysql.query_db(query, data)
        return redirect(url_for('project', project_id=session['project_id']))

    return render_template('newBug.html')






@app.route('/profile')
def profile():
        if session.get('user_id') is None:
            return redirect('/')
        projects = []
        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM projects WHERE user_ID=%(user_ID)s;'
        data = {
            "user_ID": session['user']['id']
            }   
        
        projects = mysql.query_db(query, data)

        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM bugs WHERE user_id=%(user_ID)s;'
        data = {
            "user_ID": session['user']['id']
            }   
        bugs = mysql.query_db(query, data)



        return render_template('profile.html', projects=projects, bugs=bugs)


@app.route('/project/<project_id>')
def project(project_id):
        if session.get('user_id') is None:
            return redirect('/')
        session.pop('project', None)
        session['project_id'] = project_id
        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM projects WHERE id=%(project_id)s;'
        data = {
            "project_id": project_id
            }   
            
        project = mysql.query_db(query, data)[0]

        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM bugs WHERE project_id=%(project_id)s;'
        data = {
            "project_id": project_id
            }   
        bugs = mysql.query_db(query, data)
        print(project, bugs)
        return render_template('project.html', project=project, bugs=bugs)



@app.route('/deleteProject/<project_id>')
def deleteProject(project_id):    
  

    mysql = connectToMySQL('bugTracker')
    query='DELETE FROM projects WHERE id=%(project_id)s;'
    data = {
        "project_id": project_id
        }     
    mysql.query_db(query, data)      

    mysql = connectToMySQL('bugTracker')
    query='DELETE FROM bugs WHERE project_id=%(project_id)s;'
    data = {
       "project_id": project_id
       }   
    mysql.query_db(query, data)

    print("done with db")
    return redirect(url_for('profile'))


@app.route('/deleteBug/<bug_id>')
def deleteBug(bug_id):    
    mysql = connectToMySQL('bugTracker')
    query='DELETE FROM bugs WHERE id=%(bug_id)s;'
    data = {
        "bug_id": bug_id
        }     
    mysql.query_db(query, data)      
    return redirect(url_for('project', project_id=session['project_id']))



@app.route('/resolveBug/<bug_id>', methods=['GET', 'POST'])
def resolveBug(bug_id):
        if session.get('user_id') is None:
            return redirect('/')
        bug = []
        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM bugs WHERE id=%(bug_id)s;'
        data = {
            "bug_id": bug_id
            }     
        bug = mysql.query_db(query, data)  
        bug = bug[0]
        if request.method == 'POST':
            cause = request.form['cause']
            solution = request.form['solution']
            user_id = session['user_id']
            mysql = connectToMySQL('bugTracker')
            query='UPDATE bugs SET cause = %(cause)s, solution = %(solution)s, solved = %(solved)s WHERE id = %(bug_id)s;'
            data = {
                "cause": cause,
                "solution": solution,
                "solved": 1,
                "bug_id": bug_id
                }
            mysql.query_db(query, data)
            return redirect(url_for('project', project_id=session['project_id']))
        return render_template('resovleBug.html', bug=bug)











if __name__=="__main__":    
    app.run(debug=True)    


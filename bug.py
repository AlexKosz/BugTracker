import requests
import json
from flask import Flask, g, render_template, request, redirect, session, url_for  
from mysqlconnection import connectToMySQL



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
        username = request.form['username']
        password = request.form['password']
        mysql = connectToMySQL('bugTracker')
        responses = mysql.query_db('SELECT * FROM users')
        for x in range (len(responses)):
            users.append(responses[x])

        for x in range (len(users)):
            if (users[x]['username'] == username):
                print("found user")
                if(users[x]['password'] == password):
                    session['user_id'] = users[x]['id']
                    return redirect(url_for('profile'))
                else:
                    print("invalid password")
        return redirect(url_for('login')) 
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session.pop('user_id', None)
        username = request.form['username']
        password = request.form['password']
        githubProf = request.form['githubProf']
        name = request.form['name']
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

    return render_template('register.html')


@app.route('/newProj', methods=['GET', 'POST'])
def newProj():
    if request.method == 'POST':
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

    return render_template('newProj.html')


@app.route('/newBug', methods=['GET', 'POST'])
def newBug():
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
        projects = []
        mysql = connectToMySQL('bugTracker')
        query='SELECT * FROM projects WHERE user_ID=%(user_ID)s;'
        data = {
            "user_ID": session['user']['id']
            }   
        
        projects = mysql.query_db(query, data)
        return render_template('profile.html', projects=projects)


@app.route('/project/<project_id>')
def project(project_id):
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
    print("delete")   

    mysql = connectToMySQL('bugTracker')
    query='DELETE FROM projects WHERE id=%(project_id)s;'
    data = {
        "project_id": project_id
        }     
    mysql.query_db(query, data)      
    print("done with db")

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
    print("delete")   

    mysql = connectToMySQL('bugTracker')
    query='DELETE FROM bugs WHERE id=%(bug_id)s;'
    data = {
        "bug_id": bug_id
        }     
    mysql.query_db(query, data)      
    return redirect(url_for('project', project_id=session['project_id']))














if __name__=="__main__":    
    app.run(debug=True)    


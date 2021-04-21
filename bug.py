import requests
import json
from flask import Flask, g, render_template, request, redirect, session, url_for  # Import Flask to allow us to create our app
from mysqlconnection import connectToMySQL



users = []




app = Flask(__name__)    # Create a new instance of the Flask class called "app"
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
        print (user)
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
        print(users)

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

@app.route('/profile')
def profile():


    return render_template('profile.html')








if __name__=="__main__":    
    app.run(debug=True)    


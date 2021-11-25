import re
from flask import Flask, Response, request, session, redirect, url_for, render_template, flash
import json
import pymongo
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = "jerin"

########Connection##########
try:
    mongo = pymongo.MongoClient(
        host='localhost',
        port=27017,
        serverSelectionTimeoutMS=1000
        )
    db = mongo.blog
    mongo.server_info()
except:
    print ("Error - Couldn't connect to Mongo'")
########Connection##########

@app.route("/homepage")
def homepage():
    blog = db.blogs.find({})
    return render_template('index.html', blog=blog)

@app.route("/registerpage")
def registerpage():
    return render_template('register.html')

@app.route("/loginpage")
def loginpage():
    return render_template('login.html')

@app.route("/newblog")
def newblog():
    return render_template('newpost.html')

@app.route("/viewblog")
def viewblog():
    if not session.get('logged'):
        return redirect(url_for('loginpage'))
    else:
        myvar = request.args.get('myvar', '')
        blog = db.blogs.find({'_id' : ObjectId(myvar)})
        return render_template('viewblog.html', blog=blog)
        

@app.route("/search", methods=['GET', 'POST'])
def search():
    search = db.blogs.find({"$or":[ {"author": {"$regex": request.form['search']}}, {"title": {"$regex": request.form['search']}}, {"category":request.form['search']}]})
    return render_template('search.html', search = search)
    

@app.route("/logout")
def logout():
    session.pop('username',None)
    session.pop('email',None)
    session.pop('id',None)
    session.pop('logged',None)
    blog = db.blogs.find({})
    return render_template('index.html', blog=blog)

########Registration#########
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = db.students
        existing_user = users.find_one({'email' : request.form['email']})

        if existing_user is None:
            users.insert_one({'username': request.form['username'], 'email' : request.form['email'], 'password' : request.form['password']})
            data = list(users.find({'email' : request.form['email']}))
            for user in data:
                user["_id"] = str(user["_id"])
            session['id'] = user["_id"]    
            session['email'] = request.form['email']
            session['username'] = request.form['username']
            session['logged'] = 'TRUE'
            return redirect(url_for("homepage"))
        else:
            flash('Email Already Exists')
            return render_template('register.html')
    return redirect(url_for("registerpage"))
########Registration#########

########Login#########
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_stud = db.students.find_one({'email' : request.form['email'], 'password' : request.form['password']})
        if login_stud:
            data = list(db.students.find({'email' : request.form['email']}))
            for user in data:
                user["_id"] = str(user["_id"])
                session['username'] = user["username"]
            session['id'] = user["_id"]
            session['email'] = request.form['email']
            session['logged'] = 'TRUE'
            return redirect(url_for("homepage"))
        else:
            flash('Invalid Email/Password')
            return redirect(url_for("loginpage"))
########Login#########

########New Blog Post#########
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog = db.blogs
        blog.insert_one({'student_id': session['id'], 'author': session['username'], 'title' : request.form['title'], 'category' : request.form['category'], 'smalldesc' : request.form['smalldesc'], 'reflink' : request.form['reflink'],'content' : request.form['content'], 'likes': 0})
        return redirect(url_for("homepage"))
            
    return redirect(url_for("newblog"))
########New Blog Post#########

if __name__ == '__main__':
    app.run(debug=True)
    
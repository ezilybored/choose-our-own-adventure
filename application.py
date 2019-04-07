import os
import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configures Socket I/O
app.config['SECRET_KEY'] = 'art24tushet625rpl43522dc'
socketio = SocketIO(app, manage_session=False) # manage_session=False hands the session handling to flask

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://tygtumblgerbrs:05f0c922f34bd53dbe8b38c0c231e264ed3a2c1e8d48bcf01e3a85d78ad1febc@ec2-54-247-70-127.eu-west-1.compute.amazonaws.com:5432/d8vfveb2569p2u'
db = SQLAlchemy(app)

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Object class setup
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.String, nullable=False)
    twitter = db.Column(db.String, nullable=False)
    # Links to the Choices class. 
    choices = db.relationship('Choice', backref='user')
    isadmin = db.Column(db.Boolean, nullable=False)

class Post(db.Model):
    __tablename__ = "posts"
    post_id = db.Column(db.Integer, primary_key=True)
    posttext = db.Column(db.String, nullable=False)
    # Links to the Choices class.
    choice = db.relationship('Choice', backref='post')
    date = db.Column(db.DateTime, nullable=False)
    optionA = db.Column(db.String, nullable=False)
    optionB = db.Column(db.String, nullable=False)
    optionC = db.Column(db.String, nullable=False)
    optionD = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    winchoice = db.Column(db.String, nullable=False)

class Choice(db.Model):
    __tablename = "choices"
    choice_id = db.Column(db.Integer, primary_key=True)
    choice = db.Column(db.String, nullable=False)
    # Links to the users table user_id column.
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    selected = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    # Links to the posts table post_id column.
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"))

""" User registration, Login and Logout process """

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html")

        get_password = request.form.get("password")
        get_newuser = request.form.get("username")
        get_dob = request.form.get("dob")
        get_email = request.form.get("email")
        get_twitter = request.form.get("twitter")

        insert = User(user_name=get_newuser, password=get_password, email=get_email, date_of_birth=get_dob, twitter=get_twitter, isadmin=False)
        db.session.add(insert)
        db.session.commit()

        if not insert:
            return render_template("error.html", error = "Failed user entry")
        
        session["user_id"] = insert

        return redirect("/")
    
    else:
        return render_template("register.html")


@app.route("/regcheck", methods=["GET", "POST"])
def regcheck():
    """Allows the site to check whether a particular username has been taken yet"""

    username = request.form.get("username")
    user = User.query.filter_by(user_name=username).first()

    if not user:
        t = jsonify({"success": True})
        return t
    else:
        f = jsonify({"success": False})
        return f


"""This section of code relates to the users pages"""


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """The main home page of the website"""

    #topost = db.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    #print("index page")

    return render_template("index.html", text=topost)
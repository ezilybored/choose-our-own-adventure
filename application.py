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
import datetime

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

        # This generates the hash of the inputted password
        get_password=generate_password_hash(request.form.get("password")),
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

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    session.clear()

    if request.method == "POST":
        username=request.form.get("username")
        password=request.form.get("password")
        user = User.query.filter_by(user_name=username).first()
        print(user)

        # Ensure username exists and password is correct using check_password_hash from werkzeug.security
        if not check_password_hash(user.password, password):
            return render_template("error.html", error = "username or password are incorrect")

        session["user_id"] = user.user_id

        session["admin"]= User.query.filter_by(user_name=username, isadmin=True).first()

        if not session["admin"]:
            return redirect("/")

        else:
            return redirect("/admin")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    session.clear()

    return redirect("/")



"""This section of code relates to the users pages"""

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@login_required
def index():
    """The main home page of the website"""

    topost = Post.query.order_by(Post.post_id.desc()).first()

    return render_template("index.html", text=topost)



"""This section of code relates to the admin pages"""

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    """The admin home screen that shows a running tally of the totals for each post selection for the week"""

    topost = Post.query.order_by(Post.post_id.desc()).first()
    postid = topost.post_id
    optionA = len(Choice.query.filter_by(post_id=postid, choice="A").all())
    optionB = len(Choice.query.filter_by(post_id=postid, choice="B").all())
    optionC = len(Choice.query.filter_by(post_id=postid, choice="C").all())
    optionD = len(Choice.query.filter_by(post_id=postid, choice="D").all())

    total = (optionA + optionB + optionC + optionD)
    if total == 0:
        percentA = 0;
        percentB = 0;
        percentC = 0;
        percentD = 0;
    else:
        percentA = round(((optionA/total) * 100), 2)
        percentB = round(((optionB/total) * 100), 2)
        percentC = round(((optionC/total) * 100), 2)
        percentD = round(((optionD/total) * 100), 2)

    votes = {"A": percentA, "B": percentB, "C": percentC, "D": percentD}
    jvotes = [percentA, percentB, percentC, percentD]

    return render_template("admin.html", votes=votes, text=topost, jvotes=jvotes)

@app.route("/newpost", methods=["GET", "POST"])
@login_required
def newpost():
    """Where the admin can create new posts"""
    anyposts = Post.query.all()
    date = datetime.date.today()
    newpost = request.form.get("newpost")
    optionA = request.form.get("optionA")
    optionB = request.form.get("optionB")
    optionC = request.form.get("optionC")
    optionD = request.form.get("optionD")

    if not anyposts:
        if request.method == "POST":

                insert = User(posttext=newpost, date=date, user_name=get_newuser, optionA=optionA, optionB=optionB, optionC=optionC, optionD=optionD, enabled=True, winchoice="Not yet selected")
                db.session.add(insert)
                db.session.commit()

                # For some reason this set the date separaetely to the rest. was there a reason for this?
                #db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            #post=newpost)

                return render_template("newpost.html")
        else:
            return render_template("newpost.html")

    else:
        # Select most recent post and get the date of the post
        topost = Post.query.order_by(Post.post_id.desc()).first()
        lastdate = topost.date.date()
        # Calculates the number of days since the last post
        daydifference = abs((lastdate - date).days)
        print(daydifference)

        if request.method == "POST":
            if daydifference >= 7:

                insert = Post(posttext=newpost, date=date, optionA=optionA, optionB=optionB, optionC=optionC, optionD=optionD, enabled=True, winchoice="Not yet selected")
                db.session.add(insert)
                db.session.commit()

                #db.execute("UPDATE posts SET date_of_post = current_date WHERE post = :post",
                            #post=newpost)

                return render_template("newpost.html")

            else:
                return render_template("error.html", error = ("You have already posted this week, try again in " + str(daydifference) + " days"))

        return render_template("newpost.html")
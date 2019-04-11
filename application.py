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
import json

# Configure application
app = Flask(__name__)

# Configures Socket I/O
# Move the secret key to an environment variable on heroku
app.config['SECRET_KEY'] = 'art24tushet625rpl43522dc'
socketio = SocketIO(app, manage_session=False) # manage_session=False hands the session handling to flask

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://loprfyygondmhd:ce3ed7d99a5014adc7fd020075bee4f20c490d85686f238ff6fc78ce2f4ca8f5@ec2-46-137-188-105.eu-west-1.compute.amazonaws.com:5432/d8t3git44gis72'
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
        
        user = User.query.filter_by(user_name=get_newuser).first()
        session["user_id"] = user.user_id

        session["admin"]= User.query.filter_by(user_name=get_newuser, isadmin=True).first()

        if not session["admin"]:
            return redirect("/")
        else:
            return redirect("/admin")
    
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

@app.route("/archive", methods=["GET", "POST"])
@login_required
def archive():
    """A history of all previous posts, essentially the story from week 1"""
    page = request.args.get('page', 1, type=int)
    paginate = 1
    postlist = Post.query.paginate(page, paginate, False)
    next_url = url_for('archive', page=postlist.next_num) \
        if postlist.has_next else None
    prev_url = url_for('archive', page=postlist.prev_num) \
        if postlist.has_prev else None

    return render_template("archive.html", posts=postlist.items, next_url=next_url, prev_url=prev_url)

@socketio.on("submit vote")
def vote(data):
    selection = data["selection"]
    postid = data["postid"]
    date = datetime.date.today()

    insert = Choice(choice=selection, user_id=session["user_id"], selected=True, date=date, post_id=postid)
    db.session.add(insert)
    db.session.commit()

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

    emit("vote totals", votes, broadcast=True)
    emit("vote json", jvotes, broadcast=True)

@app.route("/votecheck", methods=["POST"])
@login_required
def votecheck():
    """Allows the site to check if the user has posted yet this week"""
    recentPost = Post.query.order_by(Post.post_id.desc()).first()
    postid = recentPost.post_id
    currentUser = session["user_id"]
    selected = Choice.query.filter_by(post_id=postid, user_id=currentUser, selected=True).first()
    enabled = Post.query.filter_by(post_id=postid, enabled=True).first()

    if not selected and enabled:
        t = jsonify({"success": True, "postid": postid})
        return t
    if not enabled:
        d = jsonify({"success": "Not"})
        return d
    else:
        f = jsonify({"success": False})
        return f

@app.route("/choices")
@login_required
def choices():
    """Shows the choices made by the user"""
    # Need to join post and choices tables then paginate the results
    currentUser = session["user_id"]
    print("user: ", currentUser)
    page = request.args.get('page', 1, type=int)
    print("page: ", page)
    paginate = 1
    print("paginate: ", paginate)
    choicesmade = db.session.query(Choice, Post).outerjoin(Choice, Post.post_id == Choice.post_id).filter_by(user_id=currentUser).paginate(page, paginate, False)
    print("choices: ", choicesmade)
    print(choicesmade.items)
    next_url = url_for('choices', page=choicesmade.next_num) \
        if choicesmade.has_next else None
    prev_url = url_for('choices', page=choicesmade.prev_num) \
        if choicesmade.has_prev else None

    return render_template("choices.html", choices=choicesmade.items, next_url=next_url, prev_url=prev_url)



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

                return render_template("newpost.html")
        else:
            return render_template("newpost.html")

    else:
        topost = Post.query.order_by(Post.post_id.desc()).first()
        lastdate = topost.date.date()
        daydifference = abs((lastdate - date).days)

        if request.method == "POST":
            if daydifference >= 7:

                insert = Post(posttext=newpost, date=date, optionA=optionA, optionB=optionB, optionC=optionC, optionD=optionD, enabled=True, winchoice="Not yet selected")
                db.session.add(insert)
                db.session.commit()

                return render_template("newpost.html")

            else:
                return render_template("error.html", error = ("You have already posted this week, try again in " + str(daydifference) + " days"))

        return render_template("newpost.html")

@app.route("/editpost", methods=["GET", "POST"])
@login_required
def editpost():
    """Allows the admin to edit any posts that may have errors"""

    return render_template("editpost.html")

@app.route("/getoptions", methods=["GET", "POST"])
@login_required
def getoptions():
    """Retrieves the dates that posts were made"""

    dates = Post.query.with_entities(Post.date).all()

    if not dates:
        f = jsonify({"success": False})
        print(f)
        return f
    else:
        t = jsonify({"success": True, "dates": dates})
        print(t)
        return t


@app.route("/retrieveposts", methods=["POST"])
@login_required
def retrieveposts():
    """Retrieves a previous post so that the admin can make any edits required"""
    date = request.form.get("date")
    post = Post.query.filter_by(date=date).first()

    if not post:
        f = jsonify({"success": False})
        return f
    else:
        topost = post.posttext
        postid = post.post_id
        t = jsonify({"success": True, "post": topost, "postid": postid})
        return t

@app.route("/updateposts", methods=["POST"])
@login_required
def updateposts():
    """Updates the saved posts with any changes made by the admin"""

    if request.method == "POST":
        updatepost = request.form.get("postedit")
        postid = request.form.get("postid")

        toupdate = Post.query.filter_by(post_id=postid).first()
        toupdate.posttext = updatepost
        db.session.add(toupdate)
        db.session.commit()

    return render_template("editpost.html")

@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    """Loads the users page with page 1 table"""
    page = request.args.get('page', 1, type=int)
    paginate = 5
    userlist = User.query.paginate(page, paginate, False)
    next_url = url_for('users', page=userlist.next_num) \
        if userlist.has_next else None
    prev_url = url_for('users', page=userlist.prev_num) \
        if userlist.has_prev else None

    return render_template("users.html", users=userlist.items, next_url=next_url, prev_url=prev_url)


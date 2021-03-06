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

"""
Example syntax for creating a new user
jeff = User(user_name='jeff', password='123456', email='jeff@jeff.com', date_of_birth="15/02/89", twitter="@jeff", isadmin=True)
lily = User(user_name='lily', password='123456', email='lily@lily.com', date_of_birth="15/02/89", twitter="@lily", isadmin=False)
anakin = User(user_name='anakin', password='123456', email='anakin@anakin.com', date_of_birth="15/02/89", twitter="@anakin", isadmin=False)
db.session.add(jeff)
db.session.commit()

Example syntax for creating a new post
date needs to be in the form of a python datetime object. Need to import datetime
week1 = Post(posttext="This is a test post", date=datetime.date(2019, 4, 6), optionA="optionA", optionB="optionB", optionC="optionC", optionD="optionD", enabled=True, winchoice="")
week2 = Post(posttext="This is another test post", date=datetime.date(2019, 4, 13), optionA="optionA", optionB="optionB", optionC="optionC", optionD="optionD", enabled=True, winchoice="")
db.session.add(week1)
db.session.commit()
datetime.date.today() sets todays date

Example syntax for creating a new choice
user is passed a reference to a User object via the backref user. The foreign key gets the user_id
post is passed a reference to a Post object via the backref post. The foreign key gets the post_id
choice1 = Choice(choice="A", user=lily , selected=True, date=datetime.date(2019, 4, 6), post=week1)
choice2 = Choice(choice="B", user=jeff , selected=True, date=datetime.date(2019, 4, 6), post=week1)
choice3 = Choice(choice="B", user=jeff , selected=True, date=datetime.date(2019, 4, 6), post=week1)
choice4 = Choice(choice="A", user=lily , selected=True, date=datetime.date(2019, 4, 13), post=week2)
db.session.add(choice1)
db.session.commit()

Example for selecting a user from the users table
jeff = User.query.filter_by(user_name='jeff').first()
lily = User.query.filter_by(user_name='lily').first()

Example for selecting a post from the posts table
week1 = Post.query.filter_by(post_id='1').first()

Example for finding the choices made by a user
Uses the selected user and the choices relationship
jeff.choices
More data can be gleaned from this object as it is made using a relationship.
Finding the choice data from that choice object
jeff.choices[0].choice
Finding the date data from that choice object
jeff.choices[0].date

Example for finding the post_id or user_id of a choice using the foreign keys. 
Only these specific data can be found using foreign keys
choice2 = Choice.query.filter_by(choice_id='2').first()
choice2.post_id
choice2.user_id

Joining tables to get more data
join = db.session.query(User, Choice).outerjoin(Choice, User.user_id == Choice.user_id).all()
Find data
join[0].User.user_name give the name of the first user returned
join[1].User.user_name give the name of the second user returned
join[1].Choice.choice gives the choice of the second user returned

Joins the tables to return all choices made by user lily. Arranges by choice_id
join = db.session.query(User, Choice).outerjoin(Choice, User.user_id == Choice.user_id).filter_by(user_id=lily.user_id).order_by(Choice.choice_id).all()
The same but in descending order
join = db.session.query(User, Choice).outerjoin(Choice, User.user_id == Choice.user_id).filter_by(user_id=lily.user_id).order_by(Choice.choice_id.desc()).all()

"""

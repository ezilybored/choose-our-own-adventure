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
class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.String, nullable=False)
    twitter = db.Column(db.String, nullable=False)
    # Links to the choices table. One to many relationship as user has many choices.
    choices = db.relationship('Choices', backref='user')
    isadmin = db.Column(db.Boolean, nullable=False)

class Posts(db.Model):
    __tablename__ = "posts"
    post_id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.String, nullable=False)
    optionA = db.Column(db.String, nullable=False)
    optionB = db.Column(db.String, nullable=False)
    optionC = db.Column(db.String, nullable=False)
    optionD = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    winchoice = db.Column(db.String, nullable=False)

class Choices(db.Model):
    __tablename = "choices"
    choice_id = db.Column(db.Integer, primary_key=True)
    # Links to the users table user_id column. One to one relationship as each choice has only one user making it
    choice = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    selected = db.Column(db.Boolean, nullable=False)
    # Links to the posts table post_id column. One to one relationship as each choice has only one post it relates to
    post_id = db.Column(db.Integer, db.ForeignKey("posts.post_id"), nullable=False)

"""
Example syntax for creating a new user
jeff = Users(user_name='jeff', password='123456', email='jeff@jeff.com', date_of_birth="15/02/89", twitter="@jeff")
db.session.add(jeff)
db.session.commit()

"""
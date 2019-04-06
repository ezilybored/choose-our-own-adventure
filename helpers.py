import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps

# This ensures that the user is actually logged in. Is a decoration to app routes
# Sends the user back to the login page if the user_id stored in sessions is None
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
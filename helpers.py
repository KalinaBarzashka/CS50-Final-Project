from flask import render_template, request, redirect, url_for, session
from functools import wraps

def handle_error(message, code=400):
  """Render message in an error page to the user."""
  return render_template("error.html", code=code, message=message), code

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function
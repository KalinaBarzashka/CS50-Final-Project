from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

from helpers import handle_error

# Configure application
app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///national-monuments.db"
db = SQLAlchemy(app)

class Agency(db.Model):
  id = db.Column(db.Integer, primary_key=True) # autoincrement=True
  name = db.Column(db.String(200), nullable=False)
  department = db.Column(db.String(200), nullable=False)

  def __repr__(self):
    return '<Task %r>' % self.id

class Area(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  isdeleted = db.Column(db.Boolean, default=0)
  deletedon = db.Column(db.Date, nullable=True)
  createdon = db.Column(db.Date, default=datetime.date(datetime.now()))
  createdby = db.Column(db.String(100), nullable=False)
  monumnets = relationship("Monument")

class Monument(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(200), nullable=False)
  latitude = db.Column(db.Numeric(2,6), nullable=False)
  longitude = db.Column(db.Numeric(2,6), nullable=False)
  agencyid = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=False)
  areaid = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
  dateestablished = db.Column(db.Date, nullable=True)
  acres = db.Column(db.Integer, nullable=True)
  description = db.Column(db.String(1000), nullable=False)
  imageurl = db.Column(db.String(512), nullable=False)
  isapproved = db.Column(db.Boolean, default=0)
  createdon = db.Column(db.Date, default=datetime.date(datetime.now()))
  createdby = db.Column(db.String(100), nullable=False)
  isdeleted = db.Column(db.Boolean, default=0)
  deletedon = db.Column(db.Date, nullable=True)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(200), nullable=False, unique=True)
  hash = db.Column(db.String(1000), nullable=False)
  isadmin = db.Column(db.Boolean, default=0)
  firstname = db.Column(db.String(100), nullable=False)
  lastname = db.Column(db.String(100), nullable=False)

class Visit(db.Model):
  userid = db.Column(db.Integer)
  monumentid = db.Column(db.Integer)
  visitedon = db.Column(db.Date, default=datetime.date(datetime.now()))
  grade = db.Column(db.Integer, nullable=False)
  comment = db.Column(db.String(500), nullable=False)
  __table_args__ = (
        PrimaryKeyConstraint(userid, monumentid),
        {},
  )

with app.app_context(): 
    db.create_all()

# Ensure templates are auto-reloaded - Whether to check for modifications of the template source and reload it automatically.
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"]) # decorator
def index():
  if request.method == "POST":
    task_content = request.form["content"]
  else:
    # first_agency = Agency(name="test", department="department1")
    # db.session.add(first_agency)
    # db.session.commit()
    agencies = Agency.query.all()
    return render_template("index.html", agencies=agencies)

@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""

  if request.method == "POST":

    # Return handle_error if username is blank
    username = request.form.get("username")
    if not username:
      return handle_error("must provide username", 400)

    # Return handle_error if password is blank
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if not password or not confirmation:
      return handle_error("missing password", 400)

    # Return handle_error if passwords does not match
    if password != confirmation:
      return handle_error("passwords don't match", 400)

    # Query to see if username is taken
    dbuser = User.query.filter(User.username == username).first()
    if dbuser:
      return handle_error("username already taken", 400)

    # Create User entity and populate database
    hash = generate_password_hash(password, "sha256")
    user = User(username=username, hash=hash, firstname="firstname", lastname="lastname")
    db.session.add(user)
    db.session.commit()

    # Redirect user to login page
    # flash("Registered!")
    return redirect("/login")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""

  # Forget any user_id
  session.clear()

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    # Ensure username was submitted
    if not request.form.get("username"):
      return handle_error("must provide username", 403)

    # Ensure password was submitted
    elif not request.form.get("password"):
      return handle_error("must provide password", 403)

    # Query database for username
    username = request.form.get("username")
    user = User.query.filter(User.username == username).first()

    # Ensure username exists and password is correct
    if not user or not check_password_hash(user.hash, request.form.get("password")):
      return handle_error("invalid username and/or password", 403)

    # Remember which user has logged in
    session["user_id"] = user.id

    # Redirect user to home page
    return redirect("/")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("login.html")

@app.route("/logout")
def logout():
  """Log user out"""

  # Forget any user_id
  session.clear()

  # Redirect user to login form
  return redirect("/")

if __name__ == "__main__":
  app.run(debug=True)
from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

from helpers import handle_error, login_required

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

class State(db.Model):
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
  latitude = db.Column(db.Numeric(3,6), nullable=False)
  longitude = db.Column(db.Numeric(3,6), nullable=False)
  agencyid = db.Column(db.Integer, db.ForeignKey('agency.id'), nullable=False)
  stateid = db.Column(db.Integer, db.ForeignKey('state.id'), nullable=False)
  dateestablished = db.Column(db.Date, nullable=True)
  acres = db.Column(db.Integer, nullable=True)
  description = db.Column(db.String(6000), nullable=False)
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

@app.route("/", methods=["GET"]) # decorator
def index():
  # first_agency = Agency(name="test", department="department1")
  # db.session.add(first_agency)
  # db.session.commit()
  agencies = Agency.query.count()
  monuments = Monument.query.count()
  users = User.query.count()
  return render_template("index.html", agencies=agencies, monuments=monuments, users=users)

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

    # Get next url (the one prev to login)
    next = request.form.get("next")

    if not next:
      # Redirect user to home page
      return redirect("/")
    
    return redirect(next)  

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

@app.route("/agencies")
@login_required
def agency():
  """List all agencies"""
  agencies = Agency.query.order_by(Agency.name).all()
  return render_template("agency/agencies.html", agencies=agencies)

@app.route("/agency/create", methods=["GET", "POST"])
@login_required
def createAgency():
  """Create new agency"""
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    # Return handle_error if name is blank
    name = request.form.get("agencyName")
    if not name:
      return handle_error("must provide name of the agency", 400)

    existing = Agency.query.filter(Agency.name == name).first()

    if existing:
      return handle_error("agency with the specific name already exists", 400)

    # Return handle_error if department is blank
    department = request.form.get("agencyDepartment")
    if not department:
      return handle_error("must provide department of the agency", 400)

    agency = Agency(name=name, department=department)
    db.session.add(agency)
    db.session.commit()

    return redirect("/agencies")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("agency/create.html")
  
@app.route("/agency/edit/<id>", methods=["GET", "POST"])
@login_required
def editAgency(id):
  """Edit agency"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    
    # Return handle_error if name is blank
    name = request.form.get("agencyName")
    if not name:
      return handle_error("must provide name of the agency", 400)

    existing = Agency.query.filter(Agency.name == name).first()

    if existing:
      return handle_error("agency with the specific name already exists", 400)

    # Return handle_error if department is blank
    department = request.form.get("agencyDepartment")
    if not department:
      return handle_error("must provide department of the agency", 400)

    # Update record in database
    agency = Agency.query.filter(Agency.id==id).first()
    agency.name = name
    agency.department = department
    db.session.commit()
    
    return redirect("/agencies")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    agency = Agency.query.filter(Agency.id==id).first()
    return render_template("agency/edit.html", agency=agency)

@app.route("/agency/delete/<id>", methods=["GET", "POST"])
@login_required
def deleteAgency(id):
  """Delete agency"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    agency = Agency.query.filter(Agency.id == id).first()

    if not agency:
      return handle_error("the specific agency does not exist", 400)

    # Delete record from database
    db.session.delete(agency)
    db.session.commit()
    
    return redirect("/agencies")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    agency = Agency.query.filter(Agency.id==id).first()
    return render_template("agency/delete.html", agency=agency)

@app.route("/states")
@login_required
def state():
  """List all states"""
  states = State.query.filter(State.isdeleted == 0).order_by(State.name).all()
  return render_template("state/states.html", states=states)

@app.route("/state/create", methods=["GET", "POST"])
@login_required
def createState():
  """Create new state"""
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    # Return handle_error if name is blank
    name = request.form.get("stateName")
    if not name:
      return handle_error("must provide name of the state", 400)

    existing = State.query.filter(State.name == name).first()

    if existing:
      return handle_error("state with the specific name already exists", 400)

    state = State(name=name, createdby=session["user_id"])
    db.session.add(state)
    db.session.commit()

    return redirect("/states")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("state/create.html")

@app.route("/state/edit/<id>", methods=["GET", "POST"])
@login_required
def editState(id):
  """Edit state"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    
    # Return handle_error if name is blank
    name = request.form.get("stateName")
    if not name:
      return handle_error("must provide name of the state", 400)

    existing = State.query.filter(State.name == name).first()

    if existing:
      return handle_error("state with the specific name already exists", 400)

    # Update record in database
    state = State.query.filter(State.id==id).first()
    state.name = name
    db.session.commit()
    
    return redirect("/states")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    state = State.query.filter(State.id==id).first()
    return render_template("state/edit.html", state=state)

@app.route("/state/delete/<id>", methods=["GET", "POST"])
@login_required
def deleteState(id):
  """Delete state"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    state = State.query.filter(State.id == id).first()

    if not state:
      return handle_error("the specific state does not exist", 400)

    # Delete record from database
    db.session.delete(state)
    db.session.commit()
    
    return redirect("/states")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    state = State.query.filter(State.id==id).first()
    return render_template("state/delete.html", state=state)

@app.route("/monuments")
@login_required
def monument():
  """List all monuments"""
  monuments = Monument.query.filter(Monument.isdeleted == 0 and Monument.isapproved == 1).order_by(Monument.name).all()
  return render_template("monument/monuments.html", monuments=monuments)

@app.route("/monument/create", methods=["GET", "POST"])
@login_required
def createMonument():
  """Create new monument"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    # Return handle_error if name is blank
    name = request.form.get("monumentName")
    if not name:
      return handle_error("must provide name of the monument", 400)

    # Return handle_error if name is used
    existing = Monument.query.filter(Monument.name == name).first()

    if existing:
      return handle_error("monument with the specific name already exists", 400)

    # Return handle_error if description is blank
    desc = request.form.get("monumentDescription")
    if not desc:
      return handle_error("must provide description of the monument", 400)
    
    # Return handle_error if latitude is blank
    latitude = request.form.get("monumentLatitude")
    if not latitude:
      return handle_error("must provide latitude of the monument", 400)

    # Return handle_error if longitude is blank
    longitude = request.form.get("monumentLongitude")
    if not longitude:
      return handle_error("must provide longitude of the monument", 400)

    # Return handle_error if image url is blank
    imageurl = request.form.get("monumentImageUrl")
    if not imageurl:
      return handle_error("must provide image url of the monument", 400)

    agencyid = request.form.get("monumentAgency")
    stateid = request.form.get("monumentState")
    dateestablished = datetime.strptime(request.form.get("monumentEstablished"), '%Y-%m-%d') #2022-12-03
    acres = request.form.get("monumentAcres")

    # Create monument
    monument = Monument(name=name, description=desc, latitude=latitude, longitude=longitude, agencyid=agencyid, stateid=stateid, dateestablished=dateestablished, acres=acres, imageurl=imageurl, createdby=session["user_id"])
    db.session.add(monument)
    db.session.commit()

    return redirect("/monuments")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    states = State.query.filter(State.isdeleted == 0).all()
    agencies = Agency.query.all()
    return render_template("monument/create.html", states=states, agencies=agencies)

@app.route("/monument/edit", methods=["GET", "POST"])
@login_required
def editMonument():
  """Edit monument"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    pass

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("monument/edit.html")

@app.route("/monument/delete", methods=["GET", "POST"])
@login_required
def delete_monument():
  """delete monument"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    pass

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("monument/delete.html")


if __name__ == "__main__":
  app.run(debug=True)
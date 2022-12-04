from flask import Flask, render_template, url_for, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

from models import Agency, State, Monument, User, Visit, db
from helpers import handle_error, login_required, admin_required

# Configure application
app = Flask(__name__)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///national-monuments.db"
# db = SQLAlchemy(app)
db.init_app(app)

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
@admin_required
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
@admin_required
def editAgency(id):
  """Edit agency"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    
    # Return handle_error if name is blank
    name = request.form.get("agencyName")
    if not name:
      return handle_error("must provide name of the agency", 400)

    existing = Agency.query.filter(Agency.name == name).first()

    if existing and str(existing.id) != id:
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
@admin_required
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
@admin_required
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
@admin_required
def editState(id):
  """Edit state"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    
    # Return handle_error if name is blank
    name = request.form.get("stateName")
    if not name:
      return handle_error("must provide name of the state", 400)

    existing = State.query.filter(State.name == name).first()

    if existing and str(existing.id) != id:
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
@admin_required
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
  monuments = Monument.query.filter(Monument.isdeleted == 0, Monument.isapproved == 1).order_by(Monument.name).all()
  return render_template("monument/monuments.html", monuments=monuments)

@app.route("/monument/create", methods=["GET", "POST"])
@login_required
@admin_required
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
    states = State.query.filter(State.isdeleted == 0).order_by(State.name).all()
    agencies = Agency.query.order_by(Agency.name).all()
    return render_template("monument/create.html", states=states, agencies=agencies)

@app.route("/monument/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def editMonument(id):
  """Edit monument"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":

    # Return handle_error if name is blank
    name = request.form.get("monumentName")
    if not name:
      return handle_error("must provide name of the monument", 400)

    # Return handle_error if name is used
    existing = Monument.query.filter(Monument.name == name).first()

    if existing and str(existing.id) != id:
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

    # Update record in database
    monument = Monument.query.filter(Monument.id==id).first()
    monument.name = name
    monument.description = desc
    monument.latitude = latitude
    monument.longitude = longitude
    monument.agencyid = agencyid
    monument.stateid = stateid
    monument.dateestablished = dateestablished
    monument.acres = acres
    monument.imageurl = imageurl
    db.session.commit()
    
    return redirect("/monuments")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    states = State.query.filter(State.isdeleted == 0).order_by(State.name).all()
    agencies = Agency.query.order_by(Agency.name).all()
    monument = Monument.query.filter(Monument.id==id).first()
    return render_template("monument/edit.html", monument=monument, states=states, agencies=agencies)

@app.route("/monument/delete/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_monument(id):
  """delete monument"""

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
    
    monument = Monument.query.filter(Monument.id == id).first()

    if not monument:
      return handle_error("the specific monument does not exist", 400)

    # Delete record from database
    db.session.delete(monument)
    db.session.commit()
    
    return redirect("/monuments")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    monument = Monument.query.filter(Monument.id==id).first()
    return render_template("monument/delete.html", monument=monument)

@app.route("/monument/details/<id>")
@login_required
def details_monument(id):
  monument = Monument.query.filter(Monument.id==id).first()
  agency = Agency.query.filter(Agency.id==monument.agencyid).first()
  state = State.query.filter(State.id==monument.stateid).first()

  return render_template("monument/details.html", monument=monument, agency=agency, state=state)

@app.context_processor
def utility_processor():
    def is_admin():
      userid = session["user_id"]
      dbuser = User.query.filter(User.id == userid).first()
      return dbuser.isadmin
    return dict(is_admin=is_admin)
    
if __name__ == "__main__":
  app.run(debug=True)
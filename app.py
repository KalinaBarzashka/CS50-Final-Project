from flask import Flask, flash, render_template, url_for, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, date

from models import Agency, State, Monument, User, Visit, db
from helpers import handle_error, login_required, admin_required
from wtforms import Form
from validators import RegistrationForm, LoginForm, AgencyForm, StateForm, MonumentForm

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

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"]) # decorator
def index():
  agencies = Agency.query.count()
  monuments = Monument.query.count()
  users = User.query.count()

  return render_template("index.html", agencies=agencies, monuments=monuments, users=users)

@app.route("/register", methods=["GET", "POST"])
def register():
  """Register user"""
  form = RegistrationForm(request.form)

  if request.method == "POST" and form.validate():

    username = form.username.data
    password = form.password.data
    confirmation = form.confirmation.data

    # Query to see if username is taken
    dbuser = User.query.filter(User.username == username).first()
    if dbuser:
      return handle_error("username already taken", 400)

    # Create User entity and populate database
    hash = generate_password_hash(password, "sha256")
    user = User(username=username, hash=hash, firstname="", lastname="")
    db.session.add(user)
    db.session.commit()

    # Redirect user to login page
    # flash("Registered!")
    flash("Successfully registered!")
    return redirect("/login")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""
  form = LoginForm(request.form)

  # Forget any user_id
  session.clear()

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():

    username = form.username.data
    password = form.password.data

    # Query database for username
    user = User.query.filter(User.username == username).first()

    # Ensure username exists and password is correct
    if not user or not check_password_hash(user.hash, password):
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
    return render_template("login.html", form=form)

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
  form = AgencyForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():

    # get data
    name = form.name.data
    department = form.department.data
    # check if name already exists
    existing = Agency.query.filter(Agency.name == name).first()

    if existing:
      return handle_error("agency with the specific name already exists", 400)

    agency = Agency(name=name, department=department)
    db.session.add(agency)
    db.session.commit()

    flash("Create agency successfully!")
    return redirect("/agencies")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("agency/create.html", form=form)
  
@app.route("/agency/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def editAgency(id):
  """Edit agency"""
  form = AgencyForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():
    
    # get data
    name = form.name.data
    department = form.department.data

    # check if name already exists
    existing = Agency.query.filter(Agency.name == name).first()

    if existing and str(existing.id) != id:
      return handle_error("agency with the specific name already exists", 400)

    # Update record in database
    agency = Agency.query.filter(Agency.id==id).first()
    agency.name = name
    agency.department = department
    db.session.commit()
    
    flash("Edit agency successfully!")
    return redirect("/agencies")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    agency = Agency.query.filter(Agency.id==id).first()
    return render_template("agency/edit.html", agency=agency, form=form)

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
    
    flash("Agency deleted successfully!")
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
  form = StateForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():

    # get data
    name = form.name.data

    # check if name already exists
    existing = State.query.filter(State.name == name).first()

    if existing:
      return handle_error("state with the specific name already exists", 400)

    state = State(name=name, createdby=session["user_id"])
    db.session.add(state)
    db.session.commit()

    flash("Create state successfully!")
    return redirect("/states")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    return render_template("state/create.html", form=form)

@app.route("/state/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def editState(id):
  """Edit state"""
  form = StateForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():
    
    # get data
    name = form.name.data

    # check if name already exists
    existing = State.query.filter(State.name == name).first()

    if existing and str(existing.id) != id:
      return handle_error("state with the specific name already exists", 400)

    # Update record in database
    state = State.query.filter(State.id==id).first()
    state.name = name
    db.session.commit()
    
    flash("Edit state successfully!")
    return redirect("/states")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    state = State.query.filter(State.id==id).first()
    return render_template("state/edit.html", state=state, form=form)

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
    
    flash("State deleted successfully!")
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
  form = MonumentForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():
    
    # get data
    name = form.name.data
    description = form.description.data
    latitude = form.latitude.data
    longitude = form.longitude.data
    imageurl = form.imageurl.data
    dateestablished = form.dateestablished.data
    acres = form.acres.data
    
    # check if name already exists
    existing = Monument.query.filter(Monument.name == name).first()

    if existing:
      return handle_error("monument with the specific name already exists", 400)

    agencyid = request.form.get("monumentAgency")
    stateid = request.form.get("monumentState")
    # dateestablishedformatted = datetime.strptime(dateestablished, '%Y-%m-%d') #2022-12-03

    # Create monument
    monument = Monument(name=name, description=description, latitude=latitude, longitude=longitude, agencyid=agencyid, stateid=stateid, dateestablished=dateestablished, acres=acres, imageurl=imageurl, createdby=session["user_id"])
    db.session.add(monument)
    db.session.commit()

    flash("Create monument successfully!")
    return redirect("/monument/approve")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    states = State.query.filter(State.isdeleted == 0).order_by(State.name).all()
    agencies = Agency.query.order_by(Agency.name).all()
    return render_template("monument/create.html", states=states, agencies=agencies, form=form)

@app.route("/monument/edit/<id>", methods=["GET", "POST"])
@login_required
@admin_required
def editMonument(id):
  """Edit monument"""
  form = MonumentForm(request.form)

  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST" and form.validate():

    # get data
    name = form.name.data
    description = form.description.data
    latitude = form.latitude.data
    longitude = form.longitude.data
    imageurl = form.imageurl.data
    dateestablished = form.dateestablished.data
    acres = form.acres.data
    
    # check if name already exists
    existing = Monument.query.filter(Monument.name == name).first()

    if existing and str(existing.id) != id:
      return handle_error("monument with the specific name already exists", 400)

    agencyid = request.form.get("monumentAgency")
    stateid = request.form.get("monumentState")
    # dateestablished = datetime.strptime(request.form.get("monumentEstablished"), '%Y-%m-%d') #2022-12-03

    # Update record in database
    monument = Monument.query.filter(Monument.id==id).first()
    monument.name = name
    monument.description = description
    monument.latitude = latitude
    monument.longitude = longitude
    monument.agencyid = agencyid
    monument.stateid = stateid
    monument.dateestablished = dateestablished
    monument.acres = acres
    monument.imageurl = imageurl
    db.session.commit()
    
    flash("Edit monument successfully!")
    return redirect("/monuments")

  # User reached route via GET (as by clicking a link or via redirect)
  else:
    states = State.query.filter(State.isdeleted == 0).order_by(State.name).all()
    agencies = Agency.query.order_by(Agency.name).all()
    monument = Monument.query.filter(Monument.id==id).first()
    return render_template("monument/edit.html", monument=monument, states=states, agencies=agencies, form=form)

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
    
    flash("Monument deleted successfully!")
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

  visit = Visit.query.filter(Visit.userid == session["user_id"], Visit.monumentid == monument.id).first()
  isvisited = False
  if visit:
    isvisited = True

  return render_template("monument/details.html", monument=monument, agency=agency, state=state, isvisited=isvisited, visit=visit)

@app.route("/monument/approve")
@login_required
def not_approved_monuments():
  monuments = Monument.query.filter(Monument.isdeleted == 0, Monument.isapproved == 0).order_by(Monument.name).all()
  return render_template("/monument/approve.html", monuments=monuments)

@app.route("/monument/approve/<id>")
@login_required
def approve_monument(id):
  monument = Monument.query.filter(Monument.id==id).first()
  monument.isapproved = 1
  db.session.commit()

  return redirect("/monuments")

@app.route("/monument/decline/<id>")
@login_required
def decline_monument(id):
  monument = Monument.query.filter(Monument.id==id).first()
  monument.isdeleted = 1
  monument.deletedon = datetime.date(datetime.now())
  db.session.commit()

  return redirect("/monument/approve")

@app.route("/monument/visit/<id>", methods=["POST"])
@login_required
def visit_monument(id):
  monument = Monument.query.filter(Monument.id==id).first()
  userid = session.get("user_id")
  grade = request.form.get("grade")
  comment = request.form.get("comment")

  visit = Visit(userid=userid, monumentid=monument.id, grade=grade, comment=comment)
  db.session.add(visit)
  db.session.commit()

  flash("Monument visited successfully!")
  return redirect("/monument/visited")

@app.route("/monument/visited")
@login_required
def visited_monuments():  
  visitedMonuments = Visit.query.filter(Visit.userid == session["user_id"]).all()
  monumentIds = []

  if visitedMonuments:
    for visitObj in visitedMonuments:
      monumentIds.append(visitObj.monumentid)
    
  monuments = Monument.query.filter(Monument.id.in_(monumentIds), Monument.isdeleted == 0).all()

  return render_template("/monument/visited.html", monuments=monuments)

@app.context_processor
def utility_processor():
    def is_admin():
      userid = session["user_id"]
      dbuser = User.query.filter(User.id == userid).first()
      return dbuser.isadmin
    return dict(is_admin=is_admin)
  
if __name__ == "__main__":
  app.run(debug=True)
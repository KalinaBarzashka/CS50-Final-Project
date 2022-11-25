from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date

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

@app.route("/", methods=["GET", "POST"]) # decorator
def index():
  if request.method == "POST":
    task_content = request.form["content"]
  else:
    first_agency = Agency(name="test", department="department1")
    db.session.add(first_agency)
    db.session.commit()
    agencies = Agency.query.all()
    return render_template("index.html", agencies=agencies)

if __name__ == "__main__":
  app.run(debug=True)
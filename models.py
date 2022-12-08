from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()

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
  monuments = relationship("Monument")

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

  def is_admin(self):
    return self.isadmin

class Visit(db.Model):
  userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  monumentid = db.Column(db.Integer, db.ForeignKey('monument.id'), nullable=False)
  visitedon = db.Column(db.Date, default=datetime.date(datetime.now()))
  grade = db.Column(db.Integer, nullable=False)
  comment = db.Column(db.String(500), nullable=False)
  __table_args__ = (
        PrimaryKeyConstraint(userid, monumentid),
        {},
  )
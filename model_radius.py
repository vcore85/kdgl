# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from sqlalchemy import Column
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost:3306/radius?charset=utf8mb4'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Radcheck(db.Model):
	__tablename__ = 'radcheck'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), nullable=False)
	attribute = db.Column(db.String(64), nullable=False)
	op = db.Column(db.String(2), default='==',nullable=False)
	value = db.Column(db.String(253), nullable=False)
	def __repr__(self):
		return '<Radcheck %r>' % self.username

class Radgroupreply(db.Model):
	__tablename__ = 'radgroupreply'
	id = db.Column(db.Integer, primary_key=True)
	groupname = db.Column(db.String(64), nullable=False)
	attribute = db.Column(db.String(64), nullable=False)
	op = db.Column(db.String(2), default='=',nullable=False)
	value = db.Column(db.String(253), nullable=False)
	def __repr__(self):
		return '<Radgroupreply %r>' % self.groupname

class Radusergroup(db.Model):
	__tablename__ = 'radusergroup'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), nullable=False)
	groupname = db.Column(db.String(64), nullable=False)
	priority = db.Column(db.Integer, default='1', nullable=False)
	def __repr__(self):
		return '<Radusergroup %r>' % self.username

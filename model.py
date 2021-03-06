# coding=utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from sqlalchemy import Column
from datetime import datetime

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost:3306/radius?charset=utf8mb4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

class Customer(db.Model):
	__tablename__ = 'customer'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	address = db.Column(db.String(200), nullable=True)
	tel = db.Column(db.String(30), nullable=True)
	status = db.Column(db.String(30), nullable=True)
	def __repr__(self):
		return '<Customer %r>' % self.name

class Subscriber(db.Model):
	__tablename__ = 'subscriber'
	id = db.Column(db.Integer, primary_key=True)
	customerid = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
	onusn = db.Column(db.String(20), nullable=True)
	pppoename = db.Column(db.String(20), nullable=False)
	pppoepassword  = db.Column(db.String(20), nullable=True)
	productid  = db.Column(db.Integer, nullable=True)
	pppoeendtime  = db.Column(db.DateTime, nullable=True)
	status  = db.Column(db.String(30), nullable=True)
	def __repr__(self):
		return '<Subscriber %r>' % self.pppoename

class Bill(db.Model):
	__tablename__ = 'bill'
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
	customerid = db.Column(db.Integer, db.ForeignKey('customer.id'),nullable=False)
	subscriberid = db.Column(db.Integer, db.ForeignKey('subscriber.id'), nullable=False)
	billtime = db.Column(db.DateTime, default=datetime.now())
	money = db.Column(db.Integer, nullable=True)
	productid = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)
	productbuynum = db.Column(db.Integer, nullable=True)
	def __repr__(self):
		return '<Bill %r>' % self.money

class Product(db.Model):
	__tablename__ = 'product'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), nullable=False)
	value = db.Column(db.Integer, nullable=True)
	usetime  = db.Column(db.String(10), nullable=True)
	upbandwidth  = db.Column(db.Integer, nullable=True)
	downbandwidth  = db.Column(db.Integer, nullable=True)
	def __repr__(self):
		return '<Product %r>' % self.name

class Task(db.Model):
	__tablename__ = 'task'
	id = db.Column(db.Integer, primary_key=True)
	#name add、del
	name = db.Column(db.String(30), nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
	customerid = db.Column(db.Integer, db.ForeignKey('customer.id'),nullable=False)
	subscriberid = db.Column(db.Integer, db.ForeignKey('subscriber.id'), nullable=False)
	billid = db.Column(db.Integer, db.ForeignKey('bill.id'),nullable=False)
	productid = db.Column(db.Integer, db.ForeignKey('product.id'),nullable=False)
	createtime = db.Column(db.DateTime, default=datetime.now())
	crontime = db.Column(db.DateTime, default=datetime.now())
	finishtime = db.Column(db.DateTime, nullable=True)
	#status 0未执行、1执行成功、2执行失败
	status = db.Column(db.Integer, default=0)
	def __repr__(self):
		return '<Task %r>' % self.name

class Log(db.Model):
	__tablename__ = 'log'
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
	info  = db.Column(db.String(500), nullable=True)
	time  = db.Column(db.DateTime, nullable=True)

	def __repr__(self):
		return '<Log %r>' % self.name

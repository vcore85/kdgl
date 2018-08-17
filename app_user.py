from flask import Flask, render_template, request, flash, redirect, render_template_string
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from flask_babel import Babel
from model import User,Customer,Bill,Task,Product,Log
from flask_wtf import FlaskForm

app = Flask(__name__)
app.secret_key = 'vcore@qq.com'
babel = Babel(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_ENABLE_USERNAME'] = True
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = False
app.config['USER_ENABLE_REGISTER'] = True
app.config['USER_ENABLE_FORGOT_PASSWORD'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'

db = SQLAlchemy(app)




user_manager = UserManager(app, db, User)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def view_customer():
    return render_template('customer.html')

class Form_customer_new(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    tel = StringField('tel', validators=[DataRequired()])

@app.route('/customer_new', methods=['GET', 'POST'])
@login_required
def customer_new():
    form = Form_customer_new()
    if request.method == 'POST':
        name = request.form['name']
        print(request.form['name'])
        print(request.form['address'])
        print(request.form['tel'])
        db.session.add(Customer(name=request.form['name'], address=request.form['address'], tel=request.form['tel']))
        db.session.commit()
        customer_n = Customer.query.filter_by(name=name).first_or_404()
        print(customer_n)
        return render_template('customer_new_result.html', cus=customer_n)
    return render_template('customer_new.html', form=form)

@app.route('/customer_search', methods=['GET', 'POST'])
@login_required
def customer_search():
    return render_template('customer_search.html')

@app.route('/product', methods=['GET', 'POST'])
@login_required
def product():
    return render_template('product.html')

@app.route('/bill', methods=['GET', 'POST'])
@login_required
def bill():
    return render_template('bill.html')

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    return render_template('log.html')

if __name__ == '__main__':
    app.run()

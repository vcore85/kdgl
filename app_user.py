from flask import Flask, render_template, request,flash,redirect, render_template_string
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from flask_babel import Babel

app = Flask(__name__)
app.secret_key = 'vcore@qq.com'
bootstrap = Bootstrap(app)
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


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

user_manager = UserManager(app, db, User)

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/customer', methods=['GET', 'POST'])
@login_required
def customer():
    return render_template('customer.html')

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

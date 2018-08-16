from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(user_id):
        return User.get(user_id)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    return render_template('customer.html')

@app.route('/product', methods=['GET', 'POST'])
def product():
    return render_template('product.html')

@app.route('/bill', methods=['GET', 'POST'])
def bill():
    return render_template('bill.html')

@app.route('/log', methods=['GET', 'POST'])
def log():
    return render_template('log.html')

if __name__ == '__main__':
    app.run()

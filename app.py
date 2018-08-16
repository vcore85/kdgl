from flask import Flask, render_template, request,flash,redirect, render_template_string
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin

app = Flask(__name__)
app.secret_key = 'vcore@qq.com'
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"请登录！"
login_manager.session_protection = 'strong'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_ENABLE_USERNAME'] = True
app.config['USER_REQUIRE_RETYPE_PASSWORD'] = False

db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(id):
    print("load_user user_id :", id)
    return db.session.query(User).filter_by(id=id).first()

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128))

    def __repr__(self):
        return '<User %r>' % self.username

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(5, 20)])
    remember = BooleanField('Remember me')
    submit = SubmitField()

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print("User is :", db.session.query(User).filter_by(username=form.username.data,password=form.password.data))
        if login_user(db.session.query(User).filter_by(username=form.username.data,password=form.password.data)):
            flash('登录成功.')
            print("login user info :", form.username.data, "  ,  ", form.password.data)
            next = request.args.get('next')
            return redirect(next or app.url_for('index'))
        else:
            flash('登录失败.')
            print("login failed")
            return render_template('login.html', form=form)

    print("login.html")
    return render_template('login.html', form=form)

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

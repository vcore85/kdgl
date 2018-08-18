# coding=utf-8
from flask import Flask, render_template, request, flash, redirect, render_template_string, url_for
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, current_user
from flask_babel import Babel
from model import User, Customer, Bill, Task, Product, Log, Subscriber
from flask_wtf import FlaskForm
from datetime import datetime, date

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

@app.route('/customer/<customer_id>', methods=['GET', 'POST'])
@login_required
def view_customer(customer_id):
    customer_v = Customer.query.filter_by(id=customer_id).first_or_404()
    return render_template('customer_view.html', cus=customer_v)

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

class CustoemrSearchForm(FlaskForm):
    choices = [('name', u'客户名称'),
               ('tel', u'联系电话'),
               ('address', u'客户地址')]
    select = SelectField('查询客户:', choices=choices)
    search = StringField('', validators=[DataRequired()])

@app.route('/customer_search', methods=['GET', 'POST'])
@login_required
def customer_search():
    search = CustoemrSearchForm(request.form)
    if request.method == 'POST':
        if search.data['select'] == 'name':
            results = Customer.query.filter(Customer.name.contains(search.data['search'])).all()
        elif search.data['select'] == 'address':
            results = Customer.query.filter(Customer.address.contains(search.data['search'])).all()
        elif search.data['select'] == 'tel':
            results = Customer.query.filter(Customer.tel.contains(search.data['search'])).all()
        return render_template('customer_search_result.html', form=search, result=results)
    return render_template('customer_search.html', form=search)

@app.route('/product', methods=['GET', 'POST'])
@login_required
def product():
    return render_template('product.html')

@app.route('/product/<product_id>', methods=['GET', 'POST'])
@login_required
def view_product(product_id):
    form = ProductNewForm(request.form)
    product_v = Product.query.filter_by(id=product_id).first()
    if request.method == 'POST':
 #       product_v.name = request.form['name']
        product_v.usetime = request.form['usetime']
        product_v.value = request.form['value']
        print(request.form['value'])
        product_v.upbandwidth = request.form['upbandwidth']
        product_v.downbandwidth = request.form['downbandwidth']
        db.session.merge(product_v)
        db.session.commit()
        flash(request.form['name']+u'  产品信息修改完成','success')
    return render_template('product_view.html', form=form, product=product_v)

class ProductNewForm(FlaskForm):
    choices = [('month', u'月'),
               ('year', u'年'),
               ('day', u'日')]
    usetime = SelectField('产品周期:', choices=choices)
    name = StringField('', validators=[DataRequired()])
    value = StringField('', validators=[DataRequired()])
    upbandwidth = StringField('', validators=[DataRequired()])
    downbandwidth = StringField('', validators=[DataRequired()])

@app.route('/product_new', methods=['GET', 'POST'])
@login_required
def product_new():
    form = ProductNewForm(request.form)
    if request.method == 'POST':
        name = form.data['name']
        product_n_test = Product.query.filter_by(name=form.data['name']).first()
        print(product_n_test)
       # print(product_n_test)
        if product_n_test is None:
            db.session.add(Product(name=form.data['name'], usetime=form.data['usetime'], value=form.data['value'], upbandwidth=form.data['upbandwidth'], downbandwidth=form.data['downbandwidth']))
            db.session.commit()
            product_n = Product.query.filter_by(name=form.data['name']).first()
            print(product_n)
            flash(u'产品： '+form.data['name']+u'      完成创建，请继续添加产品', 'success')
        else:
            flash(u'产品： '+form.data['name']+u'      已存在,请修改产品名称后重新提交', 'error')
 #       return render_template('product_new_result.html', cus=customer_n)
    return render_template('product_new.html', form=form)

@app.route('/product_search', methods=['GET', 'POST'])
@login_required
def product_search():
    results = Product.query.all()
    return render_template('product_search_result.html', result=results)

@app.route('/customerbuy/<customer_id>', methods=['GET', 'POST'])
@login_required
def customerbuy(customer_id):
    product = Product.query.all()
    customer_v = Customer.query.filter_by(id=customer_id).first_or_404()
    print(url_for('product_search'))
    if request.method == 'POST':
        print(request.form['product_selected'])
        print(request.form['productbuynum-'+request.form['product_selected']]+u'年')
        print (request.form['pppoename'])
        print (request.form['onusn'])
        print(request.form['total'])
        print (customer_id)
        print(current_user.id)
        pppoeendtime = date.today().replace(year=date.today().year + int(request.form['productbuynum-'+request.form['product_selected']]), day=date.today().day + 1)
        print(pppoeendtime)
        return redirect(url_for('customerbuyconfirm', customer_id=customer_id)+'?productid='+request.form['product_selected']+'&productbuynum='+request.form['productbuynum-'+request.form['product_selected']]+'&pppoename='+request.form['pppoename']+'&pppoepassword='+request.form['pppoepassword']+'&onusn='+request.form['onusn'])
    return render_template('customer_buy.html', product=product, cus=customer_v)

@app.route('/customerbuyconfirm/<customer_id>', methods=['GET', 'POST'])
@login_required
def customerbuyconfirm(customer_id):
    product_c = Product.query.filter_by(id=request.args.get('productid')).first_or_404()
    customer_c = Customer.query.filter_by(id=customer_id).first_or_404()
    money = product_c.value*int(request.args.get('productbuynum'))
    print(money)
    if request.method == 'POST':
        print('POST')
        if request.args.get('pppoename') is not None and request.args.get('pppoepassword') is not None and request.args.get('productbuynum') is not None:
            print(request.args.get('onusn'))
            pppoeendtime = date.today().replace(year=date.today().year + int(request.args.get('productbuynum')), day=date.today().day + 1)
            print(pppoeendtime)
            db.session.add(Subscriber(customerid=customer_id, onusn=request.args.get('onusn'), pppoename=request.args.get('pppoename'), pppoepassword=request.args.get('pppoepassword'), productid=product_c.id, pppoeendtime=pppoeendtime, status=1))
            db.session.add(Bill(userid=current_user.id, customerid=customer_id, billtime=datetime.now(), money=money, productid=product_c.id, productbuynum=int(request.args.get('productbuynum'))))
    return render_template('customer_buy_confirm.html', product=product_c, customer=customer_c, productbuynum=request.args.get('productbuynum'), pppoename=request.args.get('pppoename'), pppoepassword=request.args.get('pppoepassword'), onusn=request.args.get('onusn'), total=money)

@app.route('/bill', methods=['GET', 'POST'])
@login_required
def bill():
    return render_template('bill.html')

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    return render_template('log.html')



@app.context_processor
def utility_processor():
    def usetime_convert(usetime):
        if usetime == 'year':
            usetime_c = u'年'
        elif usetime == 'month':
            usetime_c = u'月'
        elif usetime == 'day':
            usetime_c = u'日'
        return usetime_c
    return dict(usetime_convert=usetime_convert)


if __name__ == '__main__':
    app.run()

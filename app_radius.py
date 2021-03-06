# coding=utf-8
from flask import Flask, render_template, request, flash, redirect, render_template_string, url_for
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin, current_user
from flask_babel import Babel
from model import User, Customer, Bill, Task, Product, Log, Subscriber
from model_radius import Radcheck, Radgroupreply, Radusergroup
from flask_wtf import FlaskForm
from datetime import datetime, date, timedelta
#import pymysql
#pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'vcore@qq.com'
babel = Babel(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost:3306/radius?charset=utf8'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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
    customer_v = db.session.query(Customer).filter_by(id=customer_id).first()
    sub_customer = db.session.query(Subscriber).filter_by(customerid=customer_id).first()
    return render_template('customer_view.html', cus=customer_v, sub_customer=sub_customer)

@app.route('/customer/modify/<customer_id>', methods=['GET', 'POST'])
@login_required
def customer_m(customer_id):
    cus = db.session.query(Customer).filter_by(id=customer_id).first()
    sub = db.session.query(Subscriber).filter_by(customerid=cus.id).first()
    if request.method == 'POST':
        print(request.form['name'])
        print(request.form['address'])
        print(request.form['tel'])
        cus.name =request.form['name']
        cus.address = request.form['address']
        cus.tel =request.form['tel']
        db.session.merge(cus)
        db.session.flush()
        if sub is not None:
            radc = db.session.query(Radcheck).filter_by(username=sub.pppoename).first()
            sub.pppoename = request.form['pppoename']
            sub.pppoepassword = request.form['pppoepassword']
            db.session.merge(sub)
            radc.username = request.form['pppoename']
            radc.value = request.form['pppoepassword']
            db.session.merge(radc)
            db.session.flush()
        return redirect(url_for('view_customer', customer_id=customer_id))
    return render_template('customer_modify.html', cus=cus, sub=sub)

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
        c = Customer(name=request.form['name'], address=request.form['address'], tel=request.form['tel'])
        db.session.add(c)
        db.session.flush()
        print(c.id)
        return render_template('customer_new_result.html', cus=c)
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
            results = db.session.query(Customer).filter(Customer.name.contains(search.data['search'])).all()
            #results = Customer.query.filter(Customer.name.contains(search.data['search'])).all()
        elif search.data['select'] == 'address':
            results = db.session.query(Customer).filter(Customer.address.contains(search.data['search'])).all()
            #results = Customer.query.filter(Customer.address.contains(search.data['search'])).all()
        elif search.data['select'] == 'tel':
            results = db.session.query(Customer).filter(Customer.tel.contains(search.data['search'])).all()
            #results = Customer.query.filter(Customer.tel.contains(search.data['search'])).all()
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
    product_v = db.session.query(Product).filter_by(id=product_id).first()
    if request.method == 'POST':
 #       product_v.name = request.form['name']
        product_v.usetime = request.form['usetime']
        product_v.value = request.form['value']
        print(request.form['value'])
        product_v.upbandwidth = request.form['upbandwidth']
        product_v.downbandwidth = request.form['downbandwidth']
        db.session.merge(product_v)
        rad_pdt_up = db.session.query(Radgroupreply).filter_by(name=product_v.id, attribute='RP-Upstream-Speed-Limit').first()
        rad_pdt_up.value = product_v.upbandwidth
        rad_pdt_down = db.session.query(Radgroupreply).filter_by(name=product_v.id, attribute='RP-Downstream-Speed-Limit').first()
        rad_pdt_down.value = product_v.downbandwidth
        db.session.merge(rad_pdt_up)
        db.session.merge(rad_pdt_down)
        db.session.commit()
        flash(request.form['name']+u'  产品信息修改完成','success')
        return redirect(url_for('product_search'))
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
        product_n_test = db.session.query(Product).filter_by(name=form.data['name']).first()
        print(product_n_test)
       # print(product_n_test)
        if product_n_test is None:
            p = Product(name=form.data['name'], usetime=form.data['usetime'], value=form.data['value'], upbandwidth=form.data['upbandwidth'], downbandwidth=form.data['downbandwidth'])
            db.session.add(p)
            db.session.commit()
            db.session.add(Radgroupreply(groupname=p.id, attribute='RP-Upstream-Speed-Limit', value=p.upbandwidth))
            db.session.add(Radgroupreply(groupname=p.id, attribute='RP-Downstream-Speed-Limit', value=p.downbandwidth))
            db.session.commit()
            product_n = db.session.query(Product).filter_by(name=form.data['name']).first()
            print(product_n)
            flash(u'产品： '+form.data['name']+u'      完成创建，请继续添加产品', 'success')
        else:
            flash(u'产品： '+form.data['name']+u'      已存在,请修改产品名称后重新提交', 'error')
 #       return render_template('product_new_result.html', cus=customer_n)
    return render_template('product_new.html', form=form)

@app.route('/product_search', methods=['GET', 'POST'])
@login_required
def product_search():
    results = db.session.query(Product).all()
    return render_template('product_search_result.html', result=results)

@app.route('/customerbuy/<customer_id>', methods=['GET', 'POST'])
@login_required
def customerbuy(customer_id):
    product = db.session.query(Product).all()
    customer_v = db.session.query(Customer).filter_by(id=customer_id).first()
    if len(product) == 0:
        flash(u'未找到可用的宽带产品，请先添加宽带产品，再办理业务!!!','error')
        return redirect(url_for('product_new'))
    else:
        return render_template('customer_buy.html', product=product, cus=customer_v)
    if request.method == 'POST':
        pppoeendtime = date.today().replace(year=date.today().year + int(request.form['productbuynum-'+request.form['product_selected']]), day=date.today().day + 1)
        return redirect(url_for('customerbuyconfirm', customer_id=customer_id)+'?productid='+request.form['product_selected']+'&productbuynum='+request.form['productbuynum-'+request.form['product_selected']]+'&pppoename='+request.form['pppoename']+'&pppoepassword='+request.form['pppoepassword']+'&onusn='+request.form['onusn'])

@app.route('/customerbuynext/<customer_id>', methods=['GET', 'POST'])
@login_required
def customerbuynext(customer_id):
    product = db.session.query(Product).all()
    customer_v = db.session.query(Customer).filter_by(id=customer_id).first()
    sub_customer = db.session.query(Subscriber).filter_by(customerid=customer_id).first()
    if len(product) == 0:
        flash(u'未找到可用的宽带产品，请先添加宽带产品，再办理业务!!!','error')
        return redirect(url_for('product_new'))
    else:
        return render_template('customer_buy_next.html', product=product, cus=customer_v, sub_customer=sub_customer)
    if request.method == 'POST':
        pppoeendtime = date.today().replace(year=date.today().year + int(request.form['productbuynum-'+request.form['product_selected']]), day=date.today().day + 1)
        return redirect(url_for('customerbuyconfirm', customer_id=customer_id)+'?productid='+request.form['product_selected']+'&productbuynum='+request.form['productbuynum-'+request.form['product_selected']]+'&pppoename='+request.form['pppoename']+'&pppoepassword='+request.form['pppoepassword']+'&onusn='+request.form['onusn'])


@app.route('/customerbuyconfirm/<customer_id>', methods=['GET', 'POST'])
@login_required
def customerbuyconfirm(customer_id):
    product_c =  db.session.query(Product).filter_by(id=request.args.get('productid')).first_or_404()
    customer_c = db.session.query(Customer).filter_by(id=customer_id).first_or_404()
    money = product_c.value*int(request.args.get('productbuynum'))
    print(money)
    if request.method == 'POST':
        print('POST')
        if request.args.get('pppoename') is not None and request.args.get('pppoepassword') is not None and request.args.get('productbuynum') is not None:
            print(request.args.get('onusn'))
            pppoeendtime = date.today().replace(year=date.today().year + int(request.args.get('productbuynum')), day=date.today().day + 1)
            print(pppoeendtime)
            sub = Subscriber(customerid=customer_id, onusn=request.args.get('onusn'), pppoename=request.args.get('pppoename'), pppoepassword=request.args.get('pppoepassword'), productid=product_c.id, pppoeendtime=pppoeendtime, status=1)
            db.session.add(sub)
            db.session.commit()
            bill = Bill(userid=current_user.id, customerid=customer_id, subscriberid=sub.id, billtime=datetime.now(), money=money, productid=product_c.id, productbuynum=int(request.args.get('productbuynum')))
            db.session.add(bill)
            db.session.commit()
            db.session.add(Radcheck(username=sub.pppoename, attribute='Cleartext-Password', op=':=', value=sub.pppoepassword))
            db.session.add(Radusergroup(username=sub.pppoename, groupname=product_c.id))
            db.session.add(Task(name='add', userid=current_user.id, customerid=customer_id, subscriberid=sub.id, billid=bill.id, productid=product_c.id, status=1))
            db.session.add(
                Task(name='del', userid=current_user.id, customerid=customer_id, subscriberid=sub.id, billid=bill.id,
                     productid=product_c.id, status=0, crontime=pppoeendtime))
            db.session.commit()
            return redirect(url_for('customer_detail', customer_id=customer_id))
    return render_template('customer_buy_confirm.html', product=product_c, customer=customer_c, productbuynum=request.args.get('productbuynum'), pppoename=request.args.get('pppoename'), pppoepassword=request.args.get('pppoepassword'), onusn=request.args.get('onusn'), total=money)

@app.route('/customer_detail/<customer_id>', methods=['GET', 'POST'])
@login_required
def customer_detail(customer_id):
    customer_v = db.session.query(Customer).filter_by(id=customer_id).first()
    subscriber_d = db.session.query(Subscriber).filter_by(customerid=customer_id).first()
    if subscriber_d is not None:
        product_d = db.session.query(Product).filter_by(id=subscriber_d.productid).first_or_404()
        bill_d = db.session.query(Bill).filter_by(subscriberid=subscriber_d.id).first_or_404()
        return render_template('customer_detail.html', cus=customer_v, product_d=product_d, subscriber_d=subscriber_d,
                               bill_d=bill_d)
    else:
        flash(u'该客户未订购宽带产品','error')
        return redirect(url_for('view_customer', customer_id=customer_id))

class billsearchresult:
    cus_name = str()
    pdt_name = str()
    pdt_buynum = str()
    bill_money = int()
    bill_time = str()
    user_name = str()

@app.route('/billsearch', methods=['GET', 'POST'])
@login_required
def billsearch():
    if request.method == 'POST':
        start = datetime.strptime(request.form['start'],"%Y-%m-%d")
        end = datetime.strptime(request.form['end'], "%Y-%m-%d")
        bills = db.session.query(Bill).filter(Bill.billtime >= start, Bill.billtime <= (end+ timedelta(days=1)))
        results = []
        for b in bills:
            bsr = billsearchresult()
            c = db.session.query(Customer).filter_by(id=b.customerid).first()
            bsr.cus_name = c.name
            p = db.session.query(Product).filter_by(id=b.productid).first()
            bsr.pdt_name = p.name
            u = db.session.query(User).filter_by(id=b.userid).first()
            bsr.user_name = u.username
            bsr.pdt_buynum = str(b.productbuynum) + usetime_convert(p.usetime)
            bsr.bill_money = b.money
            bsr.bill_time = b.billtime
            results.append(bsr)
        print(results)
        return render_template('bill_search_result.html',results=results, start=start.date(),end=end.date())
    return render_template('bill_search.html')

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    return render_template('log.html')

class tasksearchresult:
    cus_name = str()
    pdt_name = str()
    task_name = str()
    status = str()
    createtime = str()
    crontime = str()
    finishtime = str()
    user_name = str()

@app.route('/tasksearch', methods=['GET', 'POST'])
@login_required
def tasksearch():
    if request.method == 'POST':
        start = datetime.strptime(request.form['start'],"%Y-%m-%d")
        end = datetime.strptime(request.form['end'], "%Y-%m-%d")
        tasks = db.session.query(Task).filter(Task.createtime >= start, Task.createtime <= (end+ timedelta(days=1)))
        results = []
        for t in tasks:
            trs = tasksearchresult()
            c = db.session.query(Customer).filter_by(id=t.customerid).first()
            trs.cus_name = c.name
            p = db.session.query(Product).filter_by(id=t.productid).first()
            trs.pdt_name = p.name
            u = db.session.query(User).filter_by(id=t.userid).first()
            trs.user_name = u.username
            trs.task_name = taskname_convert(t.name)
            trs.status = taskstatus_convert(t.status)
            trs.createtime = t.createtime
            trs.finishtime = t.finishtime
            trs.crontime = t.crontime
            results.append(trs)
        print(results)
        return render_template('task_search.html', results=results, start=start.date(), end=end.date())
    return render_template('task_search.html')

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
    def taskname_convert(name):
        if name == 'add':
            name_c = u'激活'
        elif name == 'del':
            name_c = u'停机'
        else:
            name_c = u'未知'
        return name_c
    return dict(usetime_convert=usetime_convert, taskname_convert=taskname_convert)

def usetime_convert(usetime):
    if usetime == 'year':
        usetime_c = u'年'
    elif usetime == 'month':
        usetime_c = u'月'
    elif usetime == 'day':
        usetime_c = u'日'
    return usetime_c

def taskname_convert(name):
    if name == 'add':
        name_c = u'激活'
    elif name == 'del':
        name_c = u'停机'
    else:
        name_c = u'未知'
    return name_c

def taskstatus_convert(status):
    if status == 0:
        status_c = u'未执行'
    elif status == 1:
        status_c = u'执行成功'
    elif status == 2:
        status_c = u'执行失败'
    else:
        status_c = u'未知'
    return status_c

if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.stock import bp
from app.models import Good, Vendor, Stock, Depot
from app.main.forms import QSForm, StockForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    q = QSForm()
    query = db.session.query(Good.good_id, Good.good_label, Good.good_code, Vendor.vendor_label,
                             Stock.in_stock, Stock.depot_tprice, Depot.depot_id, Depot.depot_label)\
                                 .join(Vendor).join(Stock).join(Depot)            
    if q.validate_on_submit():
        search = q.q.data
        if search:
            query = query.filter(db.or_(Good.good_label.like(f'%{search}%'),
                                        Good.good_code.like(f'%{search}%'),
                                        Vendor.vendor_label.like(f'%{search}%'),
                                        Depot.depot_label.like(f'%{search}%')))
    return render_template("stock/index.html",
                        title='Goods',
                        data=query.all(), 
                        query_form=q,
                        table_name='Stock List',
                        add='stock.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    query1 = Good.query.all()
    query2 = Depot.query.all()
    form = StockForm()
    form.good_id.choices = [good.to_touple() for good in query1]
    form.depot_id.choices = [depot.to_touple() for depot in query2]
    if form.validate_on_submit():
        g = Good.query.get_or_404(form.good_id.data)
        d = Depot.query.get_or_404(form.depot_id.data)
        s = Stock(good_id=g.good_id, depot_id=d.depot_id, depot_tprice=form.depot_tprice.data, in_stock=form.in_stock.data)
        g.stock.append(s)
        d.stock.append(s)
        try:
            db.session.commit()
            flash('Stock added!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Stock', form=form)


@bp.route('/edit/<int:gid>/<int:did>', methods=['GET', 'POST'])
@login_required
def edit(gid, did):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    stock = db.session.query(Good.good_id, Good.good_label, 
                             Good.good_code, Vendor.vendor_label,
                             Stock.in_stock, Stock.depot_tprice,
                             Depot.depot_id, Depot.depot_label)\
                             .join(Vendor).join(Stock).join(Depot)\
                             .filter(Stock.good_id==gid, Stock.depot_id==did).first()
    form = StockForm(depot_tprice=stock.depot_tprice, in_stock=stock.in_stock, state='update')
    form.good_id.choices = [(stock.good_id,stock.good_label)]
    form.depot_id.choices = [(stock.depot_id,stock.depot_label)]
    if form.validate_on_submit():
        g = Good.query.get_or_404(form.good_id.data)
        d = Depot.query.get_or_404(form.depot_id.data)
        s1 = Stock.query.filter(Stock.good_id==gid, Stock.depot_id==did).first()
        db.session.delete(s1)
        db.session.commit()
        s = Stock(good_id=g.good_id, depot_id=d.depot_id, 
                  depot_tprice=form.depot_tprice.data, 
                  in_stock=form.in_stock.data)
        g.stock.append(s)
        d.stock.append(s)
        try:
            db.session.commit()
            flash('Stock updated!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Update Stock', form=form)
  
  
@bp.route('/delete/<int:gid>/<int:did>')
@login_required
def delete(gid, did):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    stock_to_delete = Stock.query.filter(Stock.good_id==gid, Stock.depot_id==did).first()
    try:
        db.session.delete(stock_to_delete)
        db.session.commit()
    except Exception as e:
        flash( f'Deleting error: {e}')
    return redirect(url_for('.index'))

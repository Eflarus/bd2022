from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.goods import bp
from app.models import Vendor, Good
from app.main.forms import QSForm, GoodForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QSForm()
    query = db.session.query(Good.good_id, Good.good_label, Good.good_code, Vendor.vendor_label).join(Vendor)
    if request.method == "POST":            
        if q.validate_on_submit():
            search = q.q.data
            if search:
                query = query.filter(db.or_(Good.good_label.like(f'%{search}%'),
                                            Good.good_code.like(f'%{search}%'),
                                            Vendor.vendor_label.like(f'{search}')))
    return render_template("goods/index.html",
                        title='Goods',
                        data=query.all(), 
                        query_form=q,
                        table_name='Goods List',
                        add='goods.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    query = Vendor.query.all()
    form = GoodForm()
    form.vendor_id.choices = [vendor.to_touple() for vendor in query]
    if form.validate_on_submit():
        good = Good(good_label=form.label.data,
                    vendor_id=form.vendor_id.data,
                    good_code=form.good_code.data)
        try:
            db.session.add(good)
            db.session.commit()
            flash('Good added!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Good', form=form)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    good = Good.query.get_or_404(id)
    try:
        db.session.delete(good)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete Product while it using')
    return redirect(url_for('.index'))
  

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    good = Good.query.get_or_404(id)
    form = GoodForm(label=good.good_label,
                    good_code=good.good_code,
                    gcode=good.good_code)
    vendor = Vendor.query.get(good.vendor_id)
    form.vendor_id.choices = [vendor.to_touple()]
    if form.validate_on_submit():
        good.good_code = form.good_code.data
        if good.good_label != form.label.data:
            good.good_label = form.label.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit Good', form=form)
  
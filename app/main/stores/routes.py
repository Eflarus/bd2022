from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.stores import bp
from app.models import Store
from app.main.forms import QSForm, IncForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QSForm()
    query = Store.query         
    if q.validate_on_submit():
        search = q.q.data
        if search:
            query = query.filter(db.or_(Store.store_label.like(f'%{search}%'),
                                        Store.store_address.like(f'%{search}%')))
    return render_template("stores/index.html",
                        title='Store',
                        data=query.all(), 
                        query_form=q,
                        table_name='Stores',
                        add='stores.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    form = IncForm(inc='store')
    if form.validate_on_submit():
        s = Store(store_label=form.label.data, store_address=form.address.data)
        try:
            db.session.add(s)
            db.session.commit()
            flash('Store added!')
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Store', form=form)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    store = Store.query.get_or_404(id)
    try:
        db.session.delete(store)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete store while it using')
    return redirect(url_for('.index'))
  

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    store = Store.query.get_or_404(id)
    form = IncForm(label=store.store_label, address=store.store_address, inc='store', old=store.store_label)
    if form.validate_on_submit():
        store.store_label = form.label.data
        store.store_address = form.address.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit Store', form=form)
  
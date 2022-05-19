from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.depots import bp
from app.models import Depot
from app.main.forms import QSForm, IncForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QSForm()
    query = Depot.query            
    if q.validate_on_submit():
        search = q.q.data
        if search:
            query = query.filter(db.or_(Depot.depot_label.like(f'%{search}%'),
                                        Depot.depot_address.like(f'%{search}%')))
    return render_template("depots/index.html",
                        title='Depots',
                        data=query.all(), 
                        query_form=q,
                        table_name='Depots',
                        add='depots.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    form = IncForm(inc='depot')
    if form.validate_on_submit():
        depot = Depot(depot_label=form.label.data, depot_address=form.address.data)
        try:
            db.session.add(depot)
            db.session.commit()
            flash('Depot added!')
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Depot', form=form)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    depot = Depot.query.get_or_404(id)
    try:
        db.session.delete(depot)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete depot while it using')
    return redirect(url_for('.index'))
  

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    depot = Depot.query.get_or_404(id)
    form = IncForm(label=depot.depot_label, address=depot.depot_address, inc='depot')
    if form.validate_on_submit() and depot.depot_label != form.label.data:
        depot.depot_label = form.label.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit Depot', form=form)

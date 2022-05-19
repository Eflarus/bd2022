from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.stuff import bp
from app.models import Reciever
from app.main.forms import QSForm, RecieverForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QSForm()
    query = Reciever.query          
    if q.validate_on_submit():
        search = q.q.data
        if search:
            query = query.filter(db.or_(Reciever.name.like(f'%{search}%'),
                                        Reciever.surname.like(f'%{search}%')))
    return render_template("stuff/index.html",
                        title='Recievers',
                        data=query.all(), 
                        query_form=q,
                        table_name='Recievers',
                        add='stuff.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    form = RecieverForm()
    if form.validate_on_submit():
        r = Reciever(name=form.name.data, surname=form.surname.data)
        try:
            db.session.add(r)
            db.session.commit()
            flash('Reciever added!')
        except Exception as e:
            flash(f'Adding error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Reciever', form=form)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    reciever = Reciever.query.get_or_404(id)
    try:
        db.session.delete(reciever)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete reciever while it using')
    return redirect(url_for('.index'))
  
  
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    r = Reciever.query.get_or_404(id)
    form = RecieverForm(name=r.name, surname=r.surname)
    if form.validate_on_submit():
        r.name = form.name.data
        r.surname = form.surname.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit Reciever', form=form)

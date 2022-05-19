from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.admin import bp
from app.models import User
from app.main.forms import QMForm
from app.auth.forms import RegistrationForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QMForm()
    query =  User.query  
    if q.validate_on_submit():
            print(q.dt_start.data, q.dt_end.data, q.q.data)
            search = q.q.data
            start = q.dt_start.data
            end = q.dt_end.data
            if search:                    
                query = query.filter(User.username.like(f'%{search}%'))
            if start:
                query = query.filter(User.created_at >= start)
            if end:
                    query = query.filter(User.created_at <= end)
    return render_template("admin/index.html",
                            title='Users',
                            data=query.all(), 
                            query_form=q,
                            table_name='Users',
                            add='admin.add')


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    try:
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('.index'))
    except Exception as e:
        return f'Deleting error: {e}'


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User added!')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add user', form=form)


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    user = User.query.get_or_404(id)
    form = RegistrationForm(username=user.username, email=user.email)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit user', form=form)
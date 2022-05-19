from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.vendors import bp
from app.models import Vendor
from app.main.forms import QSForm, VendorForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    q = QSForm()
    query = Vendor.query           
    if q.validate_on_submit():
        search = q.q.data
        if search:
            query = query.filter(Vendor.vendor_label.like(f'%{search}%'))
    return render_template("vendors/index.html",
                        title='Vendors',
                        data=query.all(), 
                        query_form=q,
                        table_name='Vendors',
                        add='vendors.add')
    
  
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    form = VendorForm()
    if form.validate_on_submit():
        vendor = Vendor(vendor_label=form.label.data)
        try:
            db.session.add(vendor)
            db.session.commit()
            flash('Vendor added!')
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Vendor', form=form)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    vendor = Vendor.query.get_or_404(id)
    try:
        db.session.delete(vendor)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete vendor while it using')
    return redirect(url_for('.index'))
  

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    if 'admin' not in str(current_user.roles):  return redirect(url_for('index'))
    vendor = Vendor.query.get_or_404(id)
    form = VendorForm(label=vendor.vendor_label)
    if form.validate_on_submit() and vendor.vendor_label != form.label.data:
        vendor.vendor_label = form.label.data
        try:
            db.session.commit()
        except Exception as e:
            flash(f'Updating error: {e}')
        return redirect(url_for('.index'))
    else:
        return render_template('form.html', title='Edit Vendor', form=form)
  
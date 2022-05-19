from flask import request, redirect, render_template, url_for, flash
from flask_login import login_required
from app import db
from app.main.returns import bp
from app.models import ReturnAct, Vendor, Good, InvoiceAct, Depot, Store, Reciever
from app.main.forms import QLForm, ReturnForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    q = QLForm()
    query = db.session.query(ReturnAct, InvoiceAct, Good, Vendor, Depot, Store, Reciever)\
        .join(InvoiceAct, InvoiceAct.invoice_id==ReturnAct.invoice_id)\
        .join(Good, Good.good_id==InvoiceAct.good_id)\
        .join(Vendor, Vendor.vendor_id==Good.vendor_id)\
        .join(Depot, InvoiceAct.depot_id==Depot.depot_id)\
        .join(Store, InvoiceAct.store_id==Store.store_id)\
        .join(Reciever, Reciever.reciever_id==InvoiceAct.reciever_id)
    if request.method == "POST":            
        if q.submit.data and q.validate():
            filter1 = q.q.data
            filter2 = q.q2.data
            start = q.dt_start.data
            end = q.dt_end.data
            for search in [filter1, filter2]:
                if search:                
                    query = query.filter(db.or_(Good.good_label.like(f'%{search}%'),
                                                Vendor.vendor_label.like(f'%{search}%'),
                                                Store.store_label.like(f'%{search}%'),
                                                Depot.depot_label.like(f'%{search}%')))
            if start:
                    query = query.filter(ReturnAct.returned_at >= start)
            if end:
                query = query.filter(ReturnAct.returned_at <= end)
    return render_template("returns/index.html",
                            title='Returns',
                            data=query.all(), 
                            query_form=q,
                            table_name='Returns List')
    

@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    r = ReturnAct.query.get_or_404(id)
    try:
        db.session.delete(r)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete Return while it using')
    return redirect(url_for('.index'))


@bp.route('/add/<int:id>', methods=['GET', 'POST'])
@login_required
def returning(id):
    invoice = InvoiceAct.query.get_or_404(id)
    f = ReturnForm()
    f.invoice_id.choices = [(id,f'Invoice Act № {id}')]
    f.product_id.choices = [Good.query.get_or_404(invoice.good_id).to_touple()]
    f.reciever_id.choices = [Reciever.query.get_or_404(invoice.reciever_id).to_touple()]
    returned=0
    for row in ReturnAct.query.filter(ReturnAct.invoice_id==id).all():
        returned+=row.return_quantity
    f.size.data = invoice.invoice_quantity - returned
    if f.validate_on_submit():
        r = ReturnAct(invoice_id=f.invoice_id.data,
                       return_quantity=f.quantity.data)
        try:
            db.session.add(r)
            db.session.commit()
            flash('Return added!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Return Act', form=f)
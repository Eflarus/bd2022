from flask import request, redirect, render_template, url_for, flash
from flask_login import current_user, login_required
from app import db
from app.main.invoices import bp
from app.models import Vendor, Good, InvoiceAct, Depot, Store, Reciever, Stock
from app.main.forms import QLForm, InvoiceDepotForm, InvoiceForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    q = QLForm()
    addform = InvoiceDepotForm()
    depots = Stock.query.with_entities(Stock.depot_id).distinct()
    addform.depot_id.choices = [Depot.query.get_or_404(row.depot_id).to_touple() for row in depots.all()]
    query = db.session.query(InvoiceAct, Good, Vendor, Depot, Store, Reciever)\
        .join(Good, Good.good_id==InvoiceAct.good_id)\
        .join(Vendor, Vendor.vendor_id==Good.vendor_id)\
        .join(Depot, InvoiceAct.depot_id==Depot.depot_id)\
        .join(Store, InvoiceAct.store_id==Store.store_id)\
        .join(Reciever, InvoiceAct.reciever_id==Reciever.reciever_id)
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
                                                Reciever.reciever_id.like(f'%{search}%'),
                                                Reciever.surname.like(f'%{search}%'),
                                                Depot.depot_label.like(f'%{search}%')))
            if start:
                    query = query.filter(InvoiceAct.recieved_at >= start)
            if end:
                query = query.filter(InvoiceAct.recieved_at <= end)
        if addform.submit1.data and addform.validate():
            depot_id = addform.depot_id.data
            return redirect(url_for('.add', id=depot_id))
    return render_template("invoices/index.html",
                            title='Invoices',
                            data=query.all(), 
                            query_form=q,
                            add_form=addform,
                            table_name='Invoice List')
    

@bp.route('/add/<int:id>', methods=['GET', 'POST'])
@login_required
def add(id):
    query = db.session.query(Good.good_id, Good.good_label,
                             Vendor.vendor_label,
                             Stock.in_stock, Depot.depot_id)\
                                 .join(Vendor).join(Stock).join(Depot)\
                                 .filter(Depot.depot_id==id, Stock.in_stock==True)
    recievers = Reciever.query.all()
    stores = Store.query.all()
    f = InvoiceForm()
    f.good_id.choices = [(item[0], f'{item[1]} ({item[2]})') for item in query]
    f.depot_id.choices = [Depot.query.get_or_404(id).to_touple()]
    f.store_id.choices = [store.to_touple() for store in stores]
    f.reciever_id.choices = [reciever.to_touple() for reciever in recievers]
    if f.validate_on_submit():
        i = InvoiceAct(good_id=f.good_id.data, 
                       depot_id=f.depot_id.data,
                       store_id=f.store_id.data,
                       reciever_id=f.reciever_id.data,
                       invoice_quantity=f.quantity.data, 
                       invoice_tprice=f.tprice.data)
        try:
            db.session.add(i)
            db.session.commit()
            flash('Invoice added!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Invoice', form=f)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    invoice = InvoiceAct.query.get_or_404(id)
    try:
        db.session.delete(invoice)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete Act while it using')
    return redirect(url_for('.index'))



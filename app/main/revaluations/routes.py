from flask import request, redirect, render_template, url_for, flash
from flask_login import login_required
from app import db
from app.main.revaluations import bp
from app.models import RevaluationAct, Vendor, Good, InvoiceAct
from app.main.forms import QMForm, RevForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    q = QMForm()
    query = db.session.query(RevaluationAct, Good, Vendor)\
        .join(Good, Good.good_id==RevaluationAct.good_id)\
        .join(Vendor, Vendor.vendor_id==Good.vendor_id)            
    if q.validate_on_submit():
        search = q.q.data
        start = q.dt_start.data
        end = q.dt_end.data
        if search:                
            query = query.filter(db.or_(Good.good_label.like(f'%{search}%'),
                                        Vendor.vendor_label.like(f'%{search}%')))
        if start:
                query = query.filter(RevaluationAct.revaluated_at >= start)
        if end:
            query = query.filter(RevaluationAct.revaluated_at <= end)
    return render_template("revaluations/index.html",
                            title='Revaluations',
                            data=query.all(), 
                            query_form=q,
                            table_name='Revaluations List',
                            add='revaluations.add')
    

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    query = InvoiceAct.query.with_entities(InvoiceAct.good_id).distinct()
    f = RevForm()
    f.good_id.choices = [Good.query.get_or_404(row.good_id).to_touple() for row in query.all()]
    if f.validate_on_submit():
        act = RevaluationAct(good_id=f.good_id.data,
                             retail_price=f.price.data)
        try:
            db.session.add(act)
            db.session.commit()
            flash('Act added!')
        except Exception as e:
            flash(f'Add error: {e}')
        return redirect(url_for('.index'))
    return render_template('form.html', title='Add Act', form=f)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    r = RevaluationAct.query.get_or_404(id)
    try:
        db.session.delete(r)
        db.session.commit()
    except Exception as e:
        flash( f'Imposible to delete Revaluation Act while it using')
    return redirect(url_for('.index'))
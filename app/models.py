from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', 
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User {}>'.format(self.username) 
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'roles': str(self.roles),
            'created_at': self.created_at
        }


class Role(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    
    def __repr__(self):
        return '{}'.format(self.name)


class UserRoles(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class InvoiceAct(db.Model):
    
    invoice_id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('good.good_id'), nullable=False)
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.depot_id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    reciever_id = db.Column(db.Integer, db.ForeignKey('reciever.reciever_id'), nullable=False)
    invoice_quantity = db.Column(db.Integer, nullable=False)
    invoice_tprice = db.Column(db.Float, nullable=False)
    recieved_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    
    return_acts = db.relationship('ReturnAct', backref='invoice_act', lazy=True)
    
    def __repr__(self):
        return '{}'.format(self.invoice_id, 'at', self.recieved_at)
    
    
class ReturnAct(db.Model):
    
    return_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice_act.invoice_id'), nullable=False)
    return_quantity = db.Column(db.Integer, nullable=False)
    returned_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return '{}'.format(self.return_id, 'at', self.returned_at)
    

class RevaluationAct(db.Model):
    
    revaluation_id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, db.ForeignKey('good.good_id'), nullable=False)
    retail_price = db.Column(db.Float, nullable=False)
    revaluated_at = db.Column(db.DateTime(), default=datetime.utcnow)
    

class Stock(db.Model):
                            
    good_id = db.Column(db.Integer, db.ForeignKey('good.good_id'), primary_key=True)
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.depot_id'), primary_key=True)
    depot_tprice = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Boolean, default=False, nullable=False)
    

class Good(db.Model):
    
    good_id = db.Column(db.Integer(), primary_key=True)
    good_label = db.Column(db.String(120), unique=True, nullable=False)
    vendor_id = db.Column(db.Integer(), db.ForeignKey('vendor.vendor_id'), nullable=False)
    good_code = db.Column(db.String(120), unique=True, nullable=False)
    
    invoice_acts = db.relationship('InvoiceAct', backref='good', primaryjoin=good_id == InvoiceAct.good_id)
    revaluation_acts = db.relationship('RevaluationAct', backref='good', primaryjoin=good_id == RevaluationAct.good_id)
    
    stock = db.relationship('Stock', backref='good', primaryjoin=good_id == Stock.good_id)
    
    def __repr__(self):
        return f'Good: {self.good_label}'
    
    def to_touple(self):
        return (self.good_id, self.good_label)
    

class Vendor(db.Model):
    
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_label = db.Column(db.String(120), unique=True, nullable=False)
    goods =db.relationship('Good', backref='vendor', lazy='dynamic', primaryjoin=vendor_id == Good.vendor_id)
    
    def __repr__(self):
        return '{}'.format(self.vendor_label)
    
    def to_touple(self):
        return (self.vendor_id, self.vendor_label)
    
    
class Depot(db.Model):
    
    depot_id = db.Column(db.Integer, primary_key=True)
    depot_label = db.Column(db.String(120), index=True, unique=True, nullable=False)
    depot_address = db.Column(db.String(255))
    
    invoice_acts = db.relationship('InvoiceAct', backref='depot', primaryjoin=depot_id == InvoiceAct.depot_id)
    stock = db.relationship('Stock', backref='depot', primaryjoin=depot_id == Stock.depot_id)
    
    def __repr__(self):
        return f'Depot: {self.depot_label}'
    
    def to_touple(self):
        return (self.depot_id, self.depot_label)
    

class Store(db.Model):
    
    store_id = db.Column(db.Integer, primary_key=True)
    store_label = db.Column(db.String(120), unique=True, nullable=False)
    store_address = db.Column(db.String(255))

    invoice_acts = db.relationship('InvoiceAct', backref='store', primaryjoin=store_id == InvoiceAct.store_id)

    def __repr__(self):
        return '{}'.format(self.store_label)
    
    def to_touple(self):
        return (self.store_id, self.store_label)
    

class Reciever(db.Model):
    
    reciever_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    
    invoice_acts = db.relationship('InvoiceAct', backref='reciever', primaryjoin=reciever_id == InvoiceAct.reciever_id)
    
    def __repr__(self):
        return '{}'.format(self.name, self.surname)
    
    def to_touple(self):
        return (self.reciever_id, f'{self.surname} {self.name} (id:{self.reciever_id})')
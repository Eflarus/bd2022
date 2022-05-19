from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import DevConfig, ProdConfig


app = Flask(__name__)
app.config.from_object(ProdConfig)

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'auth.login'

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main.vendors import bp as vendor_bp
app.register_blueprint(vendor_bp, url_prefix='/vendors')

from app.main.goods import bp as good_bp
app.register_blueprint(good_bp, url_prefix='/goods')

from app.main.depots import bp as depot_bp
app.register_blueprint(depot_bp, url_prefix='/depots')

from app.main.stores import bp as store_bp
app.register_blueprint(store_bp, url_prefix='/stores')

from app.main.stuff import bp as stuff_bp
app.register_blueprint(stuff_bp, url_prefix='/stuff')

from app.main.stock import bp as stock_bp
app.register_blueprint(stock_bp, url_prefix='/stock')

from app.admin import bp as admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

from app.main.invoices import bp as invoice_bp
app.register_blueprint(invoice_bp, url_prefix='/invoices')

from app.main.returns import bp as return_bp
app.register_blueprint(return_bp, url_prefix='/returns')

from app.main.revaluations import bp as revaluation_bp
app.register_blueprint(revaluation_bp, url_prefix='/revaluations')

from app import routes, models

db.create_all()
print('Created')




def crt():
    try:
        admin_role = models.Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()
    except:
        admin_role = models.Role.query.get(1)

    try: 
        user1 = models.User(username='a', email='admin@example.com')
        user1.set_password('a')
        user1.roles = [admin_role,]

        db.session.add(user1)
        db.session.commit()
        print('Admin added')
    except:
        pass
    
from random import randrange
from faker import Faker
fake = Faker('en_GB')    
    
def addit():
    lim = 15
    for i in range(1,lim):
        v = models.Vendor(vendor_label=f'Vendor-{i}')
        db.session.add(v)
    db.session.commit()
    
    for i in range(1,lim):
        g = models.Good(good_label=f'Product-{i}', vendor_id=randrange(lim-1), good_code=randrange(99999))
        db.session.add(g)
    db.session.commit()

    for i in range(1,lim):
        d = models.Depot(depot_label=f'Depot-{i}', depot_address=fake.address())
        db.session.add(d)
    db.session.commit()
    
    for i in range(1,lim):
        s = models.Store(store_label=f'Store-{i}', store_address=fake.address())
        db.session.add(s)
    db.session.commit()
    
    for i in range(1,lim//2):
        s = models.Reciever(name=fake.first_name_male(), surname=fake.last_name_male())
        db.session.add(s)
    db.session.commit()
        
# from app import db, addit, crt
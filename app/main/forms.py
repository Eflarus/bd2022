from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField, IntegerField, HiddenField, DateField, FloatField
from wtforms.validators import ValidationError, DataRequired, Optional, NumberRange
from app.models import Depot, Good, Stock, Store, Vendor


class QSForm(FlaskForm):
    q = StringField('Filter:', validators=[Optional()])
    submit = SubmitField('Find')
   
    
class QMForm(QSForm):    
    dt_start = DateField('From:', format='%Y-%m-%d', validators=[Optional()])
    dt_end = DateField('Until:', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Find')
    
    
class QLForm(QMForm):
    q2 = StringField('Filter:', validators=[Optional()])
    submit = SubmitField('Find')
    
class VendorForm(FlaskForm):
    label = StringField('Vendor name', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def validate_label(self, label):
        vendor = Vendor.query.filter_by(vendor_label=label.data).first()
        if vendor is not None:
            raise ValidationError('Please use a different name.')
        
        
class GoodForm(FlaskForm):
    label = StringField('Good Label', validators=[DataRequired()])
    good_code = StringField('Good Code', validators=[DataRequired()])
    gcode = HiddenField('GCodeOld')
    vendor_id = SelectField('Vendor', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def validate_label(self, label):
        good = Good.query.filter_by(good_label=label.data).first()
        if good is not None:
            raise ValidationError('Please use a different label')
        
    def validate_good_code(self, good_code):
        if self.gcode.data != good_code.data:
            code = Good.query.filter_by(good_code=good_code.data).first()
            if code is not None:
                raise ValidationError('Please use a different code')
    
   
            
            
class IncForm(FlaskForm):
    inc = HiddenField('IncType')
    old = HiddenField('Old label')
    label = StringField('Label', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def validate_label(self, label):
        if self.old.data != label.data:
            if self.inc.data == 'depot':
                tmp = Depot.query.filter_by(depot_label=label.data).first()
            elif self.inc.data == 'store':
                tmp = Store.query.filter_by(store_label=label.data).first()
            else: tmp = None
            if tmp is not None:
                raise ValidationError('Please use a different label.')

    
class RecieverForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    submit = SubmitField('Save')


class StockForm(FlaskForm):
    state = HiddenField('State')
    depot_id = SelectField('Depot', validators=[DataRequired()])
    good_id = SelectField('Product', validators=[DataRequired()])
    depot_tprice = FloatField('Trade Price', validators=[DataRequired(), NumberRange(min=0)])
    in_stock = BooleanField('In Stock')
    submit = SubmitField('Save')
    
    def validate_depot_id(self, depot_id):
        if self.state.data != 'update':
            item = Stock.query.filter(Stock.good_id==self.good_id.data,
                                    Stock.depot_id==depot_id.data).first()
            if item is not None:
                raise ValidationError('Please use a different combination.')
    

class InvoiceDepotForm(FlaskForm):
    depot_id = SelectField('Select Depot', validators=[DataRequired()])
    submit1 = SubmitField('Create Invoice')
        
class InvoiceForm(FlaskForm):
    good_id = SelectField('Product', validators=[DataRequired()])
    depot_id = SelectField('Depot', validators=[DataRequired()])
    store_id = SelectField('Store', validators=[DataRequired()])
    reciever_id = SelectField('Reciever', validators=[DataRequired()])
    quantity = IntegerField('Lot size', validators=[DataRequired()])
    tprice = FloatField('Trade Price', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    
class RevForm(FlaskForm):
    good_id = SelectField('Product', validators=[DataRequired()])
    price = FloatField('Retail Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save')
    
    
class ReturnForm(FlaskForm):
    size = HiddenField('State')
    invoice_id = SelectField('Invoice', validators=[DataRequired()])
    product_id = SelectField('Product', validators=[DataRequired()])
    reciever_id = SelectField('Reciever', validators=[DataRequired()])
    quantity = IntegerField('Returning Lot size', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')
    
    def validate_quantity(self, quantity):
        if quantity.data > self.size.data:
            print(f'Max lot size id {self.size.data}')
            raise ValidationError(f'Max lot size is {self.size.data}')

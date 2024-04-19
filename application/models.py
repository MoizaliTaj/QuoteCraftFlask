from application.database import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey


class Lastupdated(db.Model):
    __tablename__ = 'lastupdated'
    last = db.Column(db.String, primary_key=True)


class NavBar(db.Model):
    __tablename__ = 'navbar'
    pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String, nullable=False)
    page_name = db.Column(db.String, nullable=False)
    page_address = db.Column(db.String, nullable=False)


class Master(db.Model):
    __tablename__ = 'master'
    primarykey = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code_value = db.Column(db.String)
    description_sheet = db.Column(db.String)
    description_stock = db.Column(db.String)
    brand_val = db.Column(db.String)
    size_val = db.Column(db.String)
    packaging_val = db.Column(db.String)
    unit_val = db.Column(db.String)
    cash_val = db.Column(db.String)
    sale_val = db.Column(db.String)
    quantity = db.Column(db.String)
    image = db.Column(db.String)
    tally_rate = db.Column(db.String)


class Image(db.Model):
    __tablename__ = 'image'
    code = db.Column(db.String, primary_key=True, )
    link = db.Column(db.String, nullable=False)


class DBSqliteSequence(db.Model):
    __tablename__ = 'sqlite_sequence'
    name = db.Column(primary_key=True, )
    seq = db.Column()


# Proforma Database


class CustomerDetails(db.Model):
    __bind_key__ = 'quotes'
    __tablename__ = 'customer_det'
    primarykey = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_group = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String)
    total_amount = db.Column(db.Integer)
    salesman_id = db.Column(db.Integer, ForeignKey("salesman_details.salesman_id"))
    salesman_name = db.Column(db.String)
    children = relationship("InvoiceIndex")



class InvoiceContent(db.Model):
    __bind_key__ = 'quotes'
    __tablename__ = 'invoice_content'
    primarykey = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.Integer, ForeignKey("invoice_index.invoice_id"))
    entry_order = db.Column(db.Integer)
    code = db.Column(db.String)
    description = db.Column(db.String)
    size = db.Column(db.String)
    packing = db.Column(db.String)
    price = db.Column(db.String)
    quantity = db.Column(db.String)
    notes = db.Column(db.String)
    unit = db.Column(db.String)
    total = db.Column(db.String)
    sp = db.Column(db.String)
    stock = db.Column(db.String)
    purchase_price = db.Column(db.Integer)
    image_path = db.Column(db.String)
    added_edited_by = db.Column(db.String)


class InvoiceIndex(db.Model):
    __bind_key__ = 'quotes'
    __tablename__ = 'invoice_index'
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, ForeignKey("customer_det.primarykey"))
    user_name = db.Column(db.String, nullable=False)
    user_group = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    payment_terms = db.Column(db.String)
    attention_to = db.Column(db.String)
    narration = db.Column(db.String)
    narration_external = db.Column(db.String)
    invoice_amount = db.Column(db.Integer)
    children = relationship("InvoiceContent")



class User(db.Model):
    __bind_key__ = 'quotes'
    __tablename__ = 'user'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False, unique=True)
    user_full_name = db.Column(db.String, nullable=False)
    user_group = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    password_status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)


class SalesmanDetails(db.Model):
    __bind_key__ = 'quotes'
    __tablename__ = 'salesman_details'
    salesman_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salesman_name = db.Column(db.String, nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    landline_no = db.Column(db.String, nullable=False)
    email_id = db.Column(db.String, nullable=False)
    group = db.Column(db.String, nullable=False)
    children = relationship("CustomerDetails")


#################################################



class PhoneIndex(db.Model):
    __bind_key__ = 'phone_book'
    __tablename__ = 'phone_index'
    phonebook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_name = db.Column(db.String, nullable=False)
    segment = db.Column(db.String, nullable=False)


class PhoneNumber(db.Model):
    __bind_key__ = 'phone_book'
    __tablename__ = 'phone_number'
    number_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phonebook_id = db.Column(db.Integer, ForeignKey("phone_index.phonebook_id"))
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)

########################

class GameScore(db.Model):
    __bind_key__ = 'other'
    __tablename__ = 'game_score'
    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, nullable=False)
    game = db.Column(db.Integer, nullable=False)
    score = db.Column(db.String, nullable=False)


###############################33

class LogsInvoice(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs_invoice'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)


class LogsCustomer(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs_customer'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)


class LogsSalesman(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs_salesman'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    salesman_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)


class LogsUser(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs_user'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=False)
    date_time = db.Column(db.String, nullable=False)


class LogsLoginLogout(db.Model):
    __bind_key__ = 'logs'
    __tablename__ = 'logs_login_logout'
    primary_key = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_time = db.Column(db.String, nullable=False)
    user = db.Column(db.String, nullable=False)
    ip_address = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)

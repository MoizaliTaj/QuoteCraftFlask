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


class Store(db.Model):
    __tablename__ = 'store'
    Store_Name = db.Column(db.String, primary_key=True)
    Display_Name = db.Column(db.String, nullable=False)
    Landline = db.Column(db.String, nullable=False)
    Mobile = db.Column(db.String, nullable=False)
    TRN = db.Column(db.String, nullable=False)
    fax = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)


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
    __bind_key__ = 'performa'
    __tablename__ = 'customer_det'
    primarykey = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_name = db.Column(db.String, nullable=False)
    user_name = db.Column(db.String, nullable=False)
    user_group = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String)
    salesman_name = db.Column(db.String)
    children = relationship("InvoiceIndex")


class InvoiceContent(db.Model):
    __bind_key__ = 'performa'
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
    stock = db.Column(db.String)
    purchase_price = db.Column(db.Integer)
    image_path = db.Column(db.String)


class InvoiceIndex(db.Model):
    __bind_key__ = 'performa'
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
    children = relationship("InvoiceContent")


class Logs(db.Model):
    __bind_key__ = 'performa'
    __tablename__ = 'logs'
    sr = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String)
    delete_type = db.Column(db.String)
    date_time = db.Column(db.String)
    info = db.Column(db.String)


class User(db.Model):
    __bind_key__ = 'performa'
    __tablename__ = 'user'
    user_name = db.Column(db.String, primary_key=True, nullable=False)
    user_group = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    password_status = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    store = db.Column(db.String, nullable=False)


class PhoneIndex(db.Model):
    __bind_key__ = 'performa'
    __tablename__ = 'phone_index'
    phonebook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    business_name = db.Column(db.String, nullable=False)
    segment = db.Column(db.String, nullable=False)


class PhoneNumber(db.Model):
    __bind_key__ = 'performa'
    __tablename__ = 'phone_number'
    number_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phonebook_id = db.Column(db.Integer, ForeignKey("phone_index.phonebook_id"))
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)

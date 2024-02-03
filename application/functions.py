import string
import random
from application.models import Lastupdated, User, NavBar, InvoiceContent, Master
from application.models import Logs, InvoiceIndex, CustomerDetails, SalesmanDetails
from application.database import db
import hashlib
from flask import render_template, session, request, redirect, make_response
from functools import wraps
import os
import pandas as pd
from sqlalchemy import or_, desc, asc
from pytz import timezone
from datetime import datetime
from num2words import num2words
from PIL import Image


def navbar():
    user_type = User.query.filter_by(user_name=session.get('username')).with_entities(User.type).first()
    if user_type is None:
        return []
    else:
        return NavBar.query.filter_by(user_type=user_type[0]).with_entities(NavBar.page_name,NavBar.page_address).order_by(NavBar.pk.asc()).all()


def last_update_date_time():
    return Lastupdated.query.with_entities(Lastupdated.last).distinct()[0][0]


def random_password_generator(length_of_password):
    characters = string.ascii_letters + string.digits + '!@#$%^&*()_-'
    new_password = ''
    for iteration in range(length_of_password):
        new_password += characters[random.randint(0, len(characters) - 1)]
    return new_password


def request_args(key):
    return request.args.get(key)


def hasher(hash_string):
    signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return signature


def user_group(user_name):
    return User.query.filter_by(user_name=user_name).first().user_group.lower()


def proper(input_string):
    if len(input_string) > 1:
        return input_string[0].upper() + input_string[1:]
    else:
        return input_string


def splitting_action(input_string):
    return " ".join(str(input_string).split()).upper()


def code_remove_zero_prefix(input_string):
    input_string_removespace = " ".join(str(input_string).split()).upper()
    input_string_to_list = input_string_removespace.split(" ")
    if len(input_string_to_list) == 1:
        try:
            number_has_occurred = False
            output_string = ""
            for character in input_string_removespace:
                if character != "0":
                    if character in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        number_has_occurred = True
                    output_string = output_string + character
                elif (character == "0") and (number_has_occurred is True):
                    output_string = output_string + character
            return output_string
        except:
            print("function code_remove_ZeroPrefix triggered an error")
            return input_string_removespace
    else:
        return input_string_removespace


def check_password_condition(proposed_password):
    proposed_password = str(proposed_password)
    if len(proposed_password) < 8: return False
    check_requirements = {
        'upper_case': False,
        'lower_case': False,
        'numbers': False,
        'special_characters_present': False
    }
    special_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', ]
    for character in proposed_password:
        if character.isupper():
            check_requirements['upper_case'] = True
        if character.islower():
            check_requirements['lower_case'] = True
        if character.isnumeric():
            check_requirements['numbers'] = True
        if character in special_characters:
            check_requirements['special_characters_present'] = True

    for key in check_requirements.keys():
        if not check_requirements[key]:
            return False
    return True


def delete_image_function(image_path):
    if image_path:
        try:
            try:
                os.remove("/home/MamsWeb/mysite/static/" + image_path)
            except:
                os.remove("static/" + image_path)
        except:
            print("delete_image_function triggered an error")


def time_string():
    uae_time = timezone('Asia/Dubai')
    uae_time = datetime.now(uae_time).strftime('%Y-%m-%d_%H-%M-%S')
    timestring = str(uae_time)
    timestring = timestring[8:10] + "-" + timestring[5:7] + "-" + timestring[0:4] + " " + timestring[11:13] + ":" + timestring[14:16]
    return timestring


def amount_in_words(amount):
    pre_decimal = int(amount)
    post_decimal = round((amount % 1) * 100)
    if post_decimal > 0:
        return "Dirham " + num2words(pre_decimal).title() + " and " + num2words(post_decimal).title() + " Fils Only"
    else:
        return "Dirham " + num2words(pre_decimal).title() + " Only"


def login_required(f):
    @wraps(f)
    def decorated_function_login(*args, **kwargs):
        if 'username' not in session:
            return login()
        return f(*args, **kwargs)
    return decorated_function_login


def admin_required(f):
    @wraps(f)
    def decorated_function_admin(*args, **kwargs):
        if User.query.filter_by(user_name=session.get('username')).first().type.lower() != "admin":
            return render_template("Admin.html", last=last_update_date_time(), type="not_admin", title="Error - Mams Product App")
        return f(*args, **kwargs)
    return decorated_function_admin


def error(**kwargs):
    return render_template("error.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def security(**kwargs):
    return render_template("security.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def admin_(**kwargs):
    return render_template("admin.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def customer_invoice(**kwargs):
    return render_template("customer_invoice.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def login():
    if request.method == 'GET':
        return security(type="login", title="Login - Mams Product App")
    if request.method == 'POST':
        user_name = request.form["user"].lower()
        password = request.form["password"]
        userinfo = User.query.filter(User.user_name.ilike(user_name)).first()
        if userinfo is not None:
            if (userinfo.user_name.lower() == user_name) and (userinfo.password == hasher(password)) and (userinfo.password_status == 'active'):
                session['username'] = user_name
                return redirect(request.referrer)
            elif (userinfo.user_name.lower() == user_name) and (userinfo.password == hasher(password)) and (userinfo.password_status == 'expired'):
                return security(type="password_expired", title="Change your password - Mams Product App", user_name=user_name)
        return render_template("error.html", title="Login Error - Mams Product App", type="login", redirect_link=request.referrer)


def logout():
    session.pop('username', None)
    return redirect(request.referrer)


def find_product_function(source_optional=None, query_optional=None):
    display_type = request_args('type') if request_args('type') is not None else "indi"
    query = request_args('query') if request_args('query') is not None else ""
    sort = request_args('sort') if request_args('query') is not None else ""
    special = request_args('special')
    special_invoice_id = request_args('invoice_id')
    if source_optional is not None:
        display_type = source_optional
    if query_optional is not None:
        query = query_optional
    if query:
        query = code_remove_zero_prefix(query)
        if sort:
            data_raw = Master.query.filter(
                or_(Master.code_value.like("%" + query + "%"), Master.description_sheet.like("%" + query + "%"),
                    Master.description_stock.like("%" + query + "%"), Master.brand_val.like("%" + query + "%"),
                    Master.size_val.like("%" + query + "%"), Master.packaging_val.like("%" + query + "%"),
                    Master.unit_val.like("%" + query + "%"), Master.cash_val.like("%" + query + "%"),
                    Master.sale_val.like("%" + query + "%"), Master.quantity.like("%" + query + "%"), )
            ).order_by(sort, 'brand_val', 'size_val')
        else:
            data_raw = Master.query.filter(
                or_(Master.code_value.like("%" + query + "%"), Master.description_sheet.like("%" + query + "%"),
                    Master.description_stock.like("%" + query + "%"), Master.brand_val.like("%" + query + "%"),
                    Master.size_val.like("%" + query + "%"), Master.packaging_val.like("%" + query + "%"),
                    Master.unit_val.like("%" + query + "%"), Master.cash_val.like("%" + query + "%"),
                    Master.sale_val.like("%" + query + "%"), Master.quantity.like("%" + query + "%"), )
            ).order_by('description_sheet', 'brand_val', 'size_val')
        if (data_raw.count() > 0) and (data_raw.count() < 4):
            if data_raw.first().description_sheet:
                primary_string = data_raw.first().description_sheet.strip().split(" ")
            else:
                primary_string = data_raw.first().description_stock.strip().split(" ")
            if len(primary_string) > 3:
                search_string = str(primary_string[0]) + str(" ") + str(primary_string[1])
            else:
                search_string = str(primary_string[0])
        else:
            search_string = ""
        if special:
            return render_template("search_special.html", type="search", last=last_update_date_time(),title="Product Search - Mams Product App", sub_type=display_type,data=data_raw.all(), query=query, related=search_string,special_invoice_id=special_invoice_id)
        return render_template("search.html", type="search", last=last_update_date_time(), navbar=navbar(),title="Product Search - Mams Product App", sub_type=display_type, data=data_raw.all(),query=query, related=search_string)

    else:
        if special:
            return render_template("search_special.html", type="search", last=last_update_date_time(), navbar=navbar(),title="Product Search - Mams Product App", sub_type=display_type, data="",special_invoice_id=special_invoice_id)
        return render_template("search.html", type="search", last=last_update_date_time(), navbar=navbar(),title="Product Search - Mams Product App", sub_type=display_type, data="")


def add_customer():
    if request.method == 'GET':
        salesman_list = SalesmanDetails.query.order_by(SalesmanDetails.salesman_name.asc()).all()
        return customer_invoice(type='add_customer', title="Add new customer - Mams Product App",salesman_list=salesman_list)
    if request.method == 'POST':
        cust_name = company_name_formatter(request.form['cust_name'].strip())
        contact_no = request.form['contact_no'].strip()
        salesman_id = request.form['salesman_id'].strip()
        customer_details = CustomerDetails.query.filter_by(user_group=user_group(session.get('username'))).filter(CustomerDetails.customer_name.ilike(cust_name)).first()
        if customer_details:
            return error(title="Error Duplicate Customer - Mams Product App", type="customer_name_clash")
        else:
            salesman_name = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first().salesman_name
            new_entry = CustomerDetails(customer_name=cust_name, user_name=session.get('username'),user_group=user_group(session.get('username')), contact_number=contact_no,total_amount=0, salesman_id=salesman_id, salesman_name=salesman_name)
            db.session.add(new_entry)
            db.session.commit()
            new_customer_id = CustomerDetails.query.filter_by(user_group=user_group(session.get('username')),customer_name=cust_name).first().primarykey
            return redirect("/invoice?view=invoice_list&customer_id=" + str(new_customer_id))


def add_salesman():
    if request.method == 'GET':
        cust_id = request_args('customer_id') if request_args('customer_id') is not None else ""
        return customer_invoice(type="add_salesman", title="Add New Salesman - Mams Product App", customer_id=cust_id)
    if request.method == 'POST':
        salesman_name = request.form['salesman_name'].strip()
        mobile_number = request.form['mobile_no'].strip()
        email_id = request.form['email'].strip()
        customer_id = request.form['customer_id'].strip()
        salesman_data = SalesmanDetails.query.filter_by(salesman_name=salesman_name).all()
        if not salesman_data:
            new_entry = SalesmanDetails(salesman_name=salesman_name, mobile_number=mobile_number, email_id=email_id)
            db.session.add(new_entry)
            db.session.commit()
            if len(customer_id) > 0:
                return error(type="salesman_added", redirect_link="/invoice?view=update_customer&customer_id=" + str(customer_id))
            else:
                return error(type="salesman_added", redirect_link="/invoice?view=customer_list")
        return error(type="duplicate_salesman")


def edit_salesman():
    salesman_id = request_args('salesman_id')
    cust_id = request_args('customer_id') if request_args('customer_id') is not None else ""
    if request.method == 'GET':
        if salesman_id is None:
            return error(type="invoice_master_no_match")
        salesman_detail = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first()
        return customer_invoice(type="edit_salesman", title="Edit Salesman Details - Mams Product App",customer_id=cust_id, salesman_detail=salesman_detail)
    if request.method == 'POST':
        customer_id = request.form['customer_id'].strip()
        salesman_id = request.form['salesman_id'].strip()
        salesman_name = request.form['salesman_name'].strip()
        mobile_number = request.form['mobile_no'].strip()
        email_id = request.form['email'].strip()
        salesman_data = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first()
        if salesman_data.salesman_name == salesman_name:
            salesman_data.mobile_number = mobile_number
            salesman_data.email_id = email_id
            db.session.commit()
            if len(customer_id) > 0:
                return error(type="salesman_added", redirect_link="/invoice?view=invoice_list&customer_id=" + str(customer_id))
            else:
                return error(type="salesman_added", redirect_link="/invoice?view=customer_list")
        else:
            salesman_data_ = SalesmanDetails.query.filter_by(salesman_name=salesman_name).all()
            if not salesman_data_:
                salesman_data.salesman_name = salesman_name
                salesman_data.mobile_number = mobile_number
                salesman_data.email_id = email_id
                customer_data = CustomerDetails.query.filter_by(salesman_id=salesman_id).all()
                for customer in customer_data:
                    customer.salesman_name = salesman_name
                db.session.commit()
                if len(customer_id) > 0:
                    return error(type="salesman_added", redirect_link="/invoice?view=invoice_list&customer_id=" + str(customer_id))
                else:
                    return error(type="salesman_added", redirect_link="/invoice?view=customer_list")
            else:
                return error(type="duplicate_salesman")


def update_customer_details():
    cust_id = request_args('customer_id')
    if cust_id is None:
        return error(type="invoice_master_no_match")
    if request.method == 'GET':
        customer_details = CustomerDetails.query.filter_by(primarykey=cust_id, user_group=user_group(session.get('username'))).first()
        if customer_details:
            salesman_list = SalesmanDetails.query.order_by(SalesmanDetails.salesman_name.asc()).all()
            current_salesman_detail = SalesmanDetails.query.filter_by(salesman_id=customer_details.salesman_id).first()
            return customer_invoice(type="update_customer", title="Update customer Details - Mams Product App", customer_details=customer_details, salesman_list=salesman_list, current_salesman_detail=current_salesman_detail)
        else:
            return not_found()
    if request.method == 'POST':
        cust_name = company_name_formatter(request.form['cust_name'].strip())
        contact_no = request.form['contact_no'].strip()
        salesman_id = request.form['salesman_id'].strip()
        customer_data = CustomerDetails.query.filter_by(primarykey=cust_id, user_group=user_group(session.get('username'))).first()
        if cust_name.lower() != customer_data.customer_name.lower():
            customer_details = CustomerDetails.query.filter_by(user_group=user_group(session.get('username'))).filter(CustomerDetails.customer_name.ilike(cust_name)).first()
            if customer_details:
                return error(title="Error Duplicate Customer - Mams Product App", type="customer_name_clash_update", customername=customer_details.customer_name, cust_name=cust_name, customerID=customer_details.primarykey, contact_no=contact_no)
        if customer_data:
            customer_data.customer_name = cust_name
            customer_data.contact_number = contact_no
            salesman_name = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first().salesman_name
            customer_data.salesman_id = salesman_id
            customer_data.salesman_name = salesman_name
            db.session.commit()
            return redirect("/invoice?view=invoice_list&customer_id=" + str(cust_id))
        else:
            return error(title="Error No Customer Found - Mams Product App", type="no_customer")


def add_invoice():
    cust_id = request_args('customer_id')
    if cust_id is None:
        return error(type="invoice_master_no_match")
    if request.method == 'GET':
        customer_det = CustomerDetails.query.filter_by(primarykey=cust_id, user_group=user_group(session.get('username'))).first()
        payment_terms = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), customer_id=customer_det.primarykey).order_by(InvoiceIndex.invoice_id.desc()).first()
        if payment_terms:
            payment_terms = payment_terms.payment_terms
        else:
            payment_terms = ""
        return customer_invoice(type='add_invoice', title="Add Invoice for " + customer_det.customer_name + " - Mams Product App", customername=customer_det.customer_name, cust_id=cust_id, date=datetime.now(timezone('Asia/Dubai')).strftime('%Y-%m-%d'), payment_terms=payment_terms)
    if request.method == 'POST':
        date = splitting_action(request.form['date'].strip())
        payment_terms = splitting_action(request.form['payment_terms'].strip())
        attention_to = splitting_action(request.form['attention_to'].strip())
        narration = splitting_action(request.form['narration'].strip())
        narration_external = request.form['narration_external']
        new_entry = InvoiceIndex(customer_id=cust_id, user_name=session.get('username'), user_group=user_group(session.get('username')),date=date, payment_terms=payment_terms, attention_to=attention_to, narration=narration,narration_external=narration_external)
        db.session.add(new_entry)
        db.session.commit()
        new_invoice_id = InvoiceIndex.query.filter_by(customer_id=cust_id).order_by(InvoiceIndex.invoice_id.desc()).first().invoice_id
        return redirect("/invoice?view=invoice_manager&invoice_id=" + str(new_invoice_id))


def update_invoice_details():
    invoice_id = request_args('invoice_id')
    if invoice_id is None:
        return error(type="invoice_master_no_match")
    if request.method == 'GET':
        invoice_index_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
        if invoice_index_data:
            return customer_invoice(type="update_invoice", title="Update Invoice # " + str(invoice_index_data.invoice_id) + " - Mams Product App", InvoiceIndexData=invoice_index_data)
    if request.method == 'POST':
        invoice_index_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
        if invoice_index_data:
            invoice_index_data.date = splitting_action(request.form['date'].strip())
            invoice_index_data.payment_terms = splitting_action(request.form['payment_terms'].strip())
            invoice_index_data.attention_to = splitting_action(request.form['attention_to'].strip())
            invoice_index_data.narration = splitting_action(request.form['narration'].strip())
            invoice_index_data.narration_external = request.form['narration_external'].strip()
            db.session.commit()
            return redirect("/invoice?view=invoice_manager&invoice_id=" + str(invoice_id))


def delete_invoice_details():
    invoice_id = request_args('invoice_id')
    if invoice_id is None:
        return error(type="invoice_master_no_match")
    if request.method == 'GET':
        invoice_index_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
        customer_details = CustomerDetails.query.filter_by(user_group=user_group(session.get('username')), primarykey=invoice_index_data.customer_id).first()
        if invoice_index_data:
            return error(type="invoice_delete", title="Delete Invoice # " + str(invoice_index_data.invoice_id) + " - " + str(customer_details.customer_name) + " - Mams Product App", invoiceid=invoice_index_data.invoice_id, customername=customer_details.customer_name, cust_id=invoice_index_data.customer_id)
    if request.method == 'POST':
        invoice_index_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
        customer_id = str(invoice_index_data.customer_id)
        customer_name = CustomerDetails.query.filter_by(user_group=user_group(session.get('username')), primarykey=invoice_index_data.customer_id).first().customer_name
        entries = InvoiceContent.query.filter_by(invoice_id=invoice_id).all()
        if invoice_index_data:
            info = "Customer Name: " + str(customer_name) + "\n" + "Invoice ID: " + str(
                invoice_index_data.invoice_id) + "\n\n"
            for entry in entries:
                info = info + "Code: " + str(entry.code) + "\n" + "Description: " + str(
                    entry.description) + "\n" + "Size: " + str(entry.size) + "\n" + "Packing: " + str(
                    entry.packing) + "\n" + "Price: " + str(entry.price) + "\n" + "Quantity: " + str(
                    entry.quantity) + "\n" + "Notes: " + str(entry.notes) + "\n" + "Unit: " + str(
                    entry.unit) + "\n" + "Total: " + str(entry.total) + "\n" + "Stock: " + str(entry.stock) + "\n\n"
                delete_image_function(entry.image_path)
            logtime = datetime.now(timezone('Asia/Dubai')).strftime('%Y-%m-%d_%H-%M-%S')
            logtime = logtime[:10] + " " + logtime[11:13] + ":" + logtime[14:16] + ":" + logtime[17:19]
            new_log = Logs(user=session.get('username'), delete_type="Performa Delete", date_time=logtime, info=info)
            db.session.add(new_log)
            db.session.query(InvoiceContent).filter_by(invoice_id=invoice_id).delete()
            db.session.query(InvoiceIndex).filter_by(invoice_id=invoice_id).delete()
            db.session.commit()
            return error(type="invoice_deleted_done", title="Invoice Deleted - Mams Product App", custid=customer_id)


def add_product_function(primary_key, query, source):
    if request.method == 'GET':
        special = request_args('special')
        special_invoice_id = request_args('invoice_id')
        data = Master.query.filter_by(primarykey=primary_key).first()
        data_cust = InvoiceIndex.query \
            .join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey) \
            .with_entities(CustomerDetails.customer_name, InvoiceIndex.invoice_id) \
            .filter_by(user_group=user_group(session.get('username'))).distinct() \
            .order_by(InvoiceIndex.invoice_id.desc()).limit(200).all()
        if source == "indi":
            search_type = "indi"
        else:
            search_type = "table"
        if special:
            return render_template("product_add_edit_special.html", title="Add to Proforma - Mams Product App", navbar=navbar(), dataadd=data, last=last_update_date_time(), custdetails=data_cust, query=query, type="add_product", search_type=search_type, special_invoice_id=special_invoice_id)
        return render_template("product_add_edit.html", title="Add to Proforma - Mams Product App", navbar=navbar(), dataadd=data, last=last_update_date_time(), custdetails=data_cust, query=query, type="add_product", search_type=search_type)
    if request.method == 'POST':
        special = request_args('special')
        invoice_id = request.form['invoice_id']
        code = splitting_action(request.form['code'])
        description = splitting_action(request.form['description'])
        size = splitting_action(request.form['size'])
        packing = splitting_action(request.form['packing'])
        price = format(float(request.form['price']), ".2f")
        quantity = request.form['quantity']
        notes = request.form['notes']
        unit = splitting_action(request.form['unit'].upper())
        total = float(quantity) * float(price)
        total = format(total, ".2f")
        entry_order = InvoiceContent.query.filter_by(invoice_id=invoice_id, ).count() + 1
        valid_entry = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
        purchase_price = request.form['purchase_price']
        try:
            purchase_price = format(float(purchase_price), ".4f")
        except:
            purchase_price = ''
        if valid_entry:
            new_entry = InvoiceContent(invoice_id=invoice_id, entry_order=entry_order, code=code, description=description, size=size, packing=packing, price=price, quantity=quantity, notes=notes, unit=unit, total=total, purchase_price=purchase_price)
            db.session.add(new_entry)
            db.session.commit()
            update_invoice_amount(invoice_id)
            if special:
                redirect_url = "/find?special=yes&invoice_id=" + str(invoice_id) + "&type=" + source + "&query=" + query
                return redirect(redirect_url)
            return find_product_function(source, query)
        else:
            return not_found()


def edit_invoice_content():
    primary_key = request_args('content_id')
    if primary_key is None:
        return error(type="invoice_master_no_match")

    def log_edit_invoice_content(invoice_id_log, current_data_list, new_data_list):
        headers = ['Entry Order #', 'Code', 'Description', 'Size', 'Packing', 'Price', 'Unit', 'Quantity', 'Purchase Price', 'Notes']
        output_string = ""
        for index in range(len(current_data_list)):
            if str(current_data_list[index]) != str(new_data_list[index]):
                output_string = output_string + headers[index] + " Changed from '" + str(current_data_list[index]) + "' to '" + str(new_data_list[index]) + "'\n"
        if len(output_string) > 0:
            log_string = "Invoice ID: " + str(invoice_id_log) + "\n\n" + "Code: " + current_data_list[1] + "\n\n" + output_string
            logtime = datetime.now(timezone('Asia/Dubai')).strftime('%Y-%m-%d_%H-%M-%S')
            logtime = logtime[:10] + " " + logtime[11:13] + ":" + logtime[14:16] + ":" + logtime[17:19]
            new_log = Logs(user=session.get('username'), delete_type="Item Edited", date_time=logtime, info=log_string)
            db.session.add(new_log)
            db.session.commit()

    if request.method == 'POST':
        invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
        validation_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_content.invoice_id).first()
        if validation_data:
            entry_order = splitting_action(request.form['entry_order'])
            code = splitting_action(request.form['code'])
            description = splitting_action(request.form['description'])
            size = splitting_action(request.form['size'])
            packing = splitting_action(request.form['packing'])
            price = splitting_action(request.form['price'])
            unit = splitting_action(request.form['unit'])
            quantity = splitting_action(request.form['quantity'])
            purchase_price = splitting_action(request.form['purchase_price'])
            try:
                purchase_price = format(float(purchase_price), ".4f")
            except:
                purchase_price = ''
            notes = splitting_action(request.form['notes'])
            log_edit_invoice_content(
                invoice_content.invoice_id,
                [invoice_content.entry_order, invoice_content.code, invoice_content.description, invoice_content.size,
                 invoice_content.packing, invoice_content.price, invoice_content.unit, invoice_content.quantity,
                 invoice_content.purchase_price, invoice_content.notes],
                [entry_order, code, description, size, packing, price, unit, quantity, purchase_price, notes]
            )
            invoice_content.entry_order = entry_order
            invoice_content.code = code
            invoice_content.description = description
            invoice_content.size = size
            invoice_content.packing = packing
            invoice_content.price = price
            invoice_content.unit = unit
            invoice_content.quantity = quantity
            invoice_content.purchase_price = purchase_price
            invoice_content.notes = notes
            total = float(request.form['quantity']) * float(request.form['price'])
            invoice_content.total = float("{:.2f}".format(total))
            db.session.commit()
            update_invoice_amount(validation_data.invoice_id)
            return redirect("/invoice?view=invoice_manager&invoice_id=" + str(invoice_content.invoice_id))


def delete_invoice_content():
    primary_key = request_args('content_id')
    if primary_key is None:
        return error(type="invoice_master_no_match")
    if request.method == 'POST':
        invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
        invoice_id = str(InvoiceContent.query.filter_by(primarykey=primary_key).first().invoice_id)
        validation_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_content.invoice_id).first()
        if validation_data:
            customer_name = CustomerDetails.query.filter_by(primarykey=validation_data.customer_id).first().customer_name
            logtime = datetime.now(timezone('Asia/Dubai')).strftime('%Y-%m-%d_%H-%M-%S')
            logtime = logtime[:10] + " " + logtime[11:13] + ":" + logtime[14:16] + ":" + logtime[17:19]
            new_log = Logs(user=session.get('username'), delete_type="Item Delete", date_time=logtime,
                           info="Customer Name: " + str(customer_name) + "\n" +
                                "Invoice ID: " + str(invoice_content.invoice_id) + "\n\n" +
                                "Code: " + invoice_content.code + "\n" +
                                "Description: " + invoice_content.description + "\n" +
                                "Size: " + invoice_content.size + "\n" +
                                "Packing: " + invoice_content.packing + "\n" +
                                "Price: " + invoice_content.price + "\n" +
                                "Quantity: " + invoice_content.quantity + "\n" +
                                "Notes: " + invoice_content.notes + "\n" +
                                "Unit: " + invoice_content.unit + "\n" +
                                "Total: " + invoice_content.total + "\n" +
                                "Stock: " + invoice_content.stock)
            db.session.add(new_log)
            image_path = invoice_content.image_path
            delete_image_function(image_path)
            db.session.query(InvoiceContent).filter_by(primarykey=primary_key).delete()
            db.session.commit()
            update_invoice_amount(invoice_id)
            return redirect("/invoice?view=invoice_manager&invoice_id=" + invoice_id)


def admin_add_user():
    if request.method == 'GET':
        return admin_(type="admin_add", title="Add New user - Mams Product App")
    if request.method == 'POST':
        user_name = request.form['user'].lower()
        user_group_ = request.form['usergroup']
        user_type = request.form['type']
        userdata = User.query.filter_by(user_name=user_name).first()
        if userdata:
            return admin_(type="user_duplicate", title="Add New user - Mams Product App")
        else:
            password_new = random_password_generator(10)
            new_entry = User(user_name=user_name, user_group=user_group_, password=hasher(password_new), type=user_type, password_status='expired')
            db.session.add(new_entry)
            db.session.commit()
            return admin_(type="add_success", title="Add New user - Mams Product App", user_name=user_name, new_password=password_new)


def admin_update_user_change_password():
    user_name_string = request_args('user')
    if request.method == 'GET':
        return admin_(type="change_password_permission", title="Add New user - Mams Product App",
                      user_name=user_name_string)
    if request.method == 'POST':
        userdata = User.query.filter_by(user_name=user_name_string).first()
        new_password = random_password_generator(10)
        userdata.password = hasher(new_password)
        userdata.password_status = 'expired'
        db.session.commit()
        return admin_(type="change_password_confirmation", title="Add New user - Mams Product App", user_name=user_name_string, new_password=new_password)


def admin_update_user():
    if request.method == 'GET':
        user_name_string = request_args('user')
        if user_name_string:
            userdata = User.query.filter_by(user_name=user_name_string).first()
            return admin_(type="user_edit", title="Add New user - Mams Product App", userdata=userdata)
        else:
            userdata = User.query.order_by('user_name').all()
            return admin_(type="admin_update", title="Update user - Mams Product App", data=userdata)
    if request.method == 'POST':
        username = request.form['user'].lower()
        new_user_group = request.form['usergroup']
        new_user_type = request.form['type']
        userdata = User.query.filter_by(user_name=username).first()
        if userdata:
            userdata.user_group = new_user_group
            userdata.type = new_user_type
            db.session.commit()
            return admin_(type="user_update_success", title="Add New user - Mams Product App")
        else:
            return admin_(type="user_update_no_user", title="Add New user - Mams Product App")


def admin_logs():
    logs_data = Logs.query.order_by(Logs.sr.desc()).limit(500).all()
    return admin_(type="logs", title="Admin Logs - Mams Product App", data=logs_data)


def admin_logs_excel():
    logs_data = Logs.query.order_by(Logs.sr.desc()).all()
    logs_dict = {"sr": [], "user": [], "delete_type": [], "date_time": [], "info": []}
    for logs in logs_data:
        logs_dict["sr"].append(logs.sr)
        logs_dict["user"].append(logs.user)
        logs_dict["delete_type"].append(logs.delete_type)
        logs_dict["date_time"].append(logs.date_time)
        logs_dict["info"].append(logs.info)
    csv_df = pd.DataFrame(logs_dict)
    resp = make_response(csv_df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


def db_update():
    if request.method == 'GET':
        return render_template(
            "db_update.html", last=last_update_date_time(), type="upload", title="Update Date Base - Mams Product App",
            navbar=navbar(), )
    if request.method == 'POST':
        files = request.files.getlist("files")
        for file in files:
            try:
                file.save('/home/MamsWeb/mysite/db_directory/excel_files/' + file.filename)
            except:
                file.save('db_directory/excel_files/' + file.filename)
        return render_template(
            "db_update.html", last=last_update_date_time(), type="update", title="Update Date Base - Mams Product App", navbar=navbar())


def history():
    search_query = request_args('query')
    if search_query is not None:
        query = code_remove_zero_prefix(search_query)
        data = InvoiceIndex.query \
            .filter_by(user_group=user_group(session.get('username'))) \
            .join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey) \
            .join(InvoiceContent, InvoiceContent.invoice_id == InvoiceIndex.invoice_id) \
            .with_entities(CustomerDetails.primarykey, CustomerDetails.customer_name, InvoiceIndex.invoice_id,
                           InvoiceContent.code, InvoiceContent.description, InvoiceContent.size,
                           InvoiceContent.packing, InvoiceContent.price, InvoiceContent.quantity,
                           InvoiceContent.notes, InvoiceContent.unit, InvoiceContent.total, InvoiceContent.purchase_price) \
            .filter(or_(CustomerDetails.customer_name.like("%" + query + "%"),
                        InvoiceContent.code.like("%" + query + "%"),
                        InvoiceContent.description.like("%" + query + "%"),
                        InvoiceContent.size.like("%" + query + "%"), InvoiceContent.packing.like("%" + query + "%"),
                        InvoiceContent.price.like("%" + query + "%"), InvoiceContent.quantity.like("%" + query + "%"),
                        InvoiceContent.notes.like("%" + query + "%"), InvoiceContent.unit.like("%" + query + "%"),
                        InvoiceContent.total.like("%" + query + "%"), )) \
            .distinct().order_by(InvoiceContent.code.asc(), InvoiceContent.invoice_id.desc()).all()
    else:
        query = ""
        data = []
    return render_template(
        "search.html", type="history", last=last_update_date_time(), navbar=navbar(), title="Invoice List - Mams Product App", data=data, query=query)


def add_image():
    primary_key = request_args('content_id')
    if primary_key is None:
        return error(type="invoice_master_no_match")

    def image_resize_function(image_file, w=600, h=300):
        max_size = (w, h)
        image_file.thumbnail(max_size)
        return image_file

    def image_save(file_input, path):
        image = Image.open(file_input)
        image = image_resize_function(image)
        image.save(path)

    if request.method == 'POST':
        invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
        validation_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')),
                                                       invoice_id=invoice_content.invoice_id).first()
        if validation_data:
            if 'image' not in request.files:
                return 'No file part1'
            file = request.files['image']
            if file.filename == '':
                return 'No file part2'
            file_path_db = 'invoice_content_images/' + primary_key + '.png'
            try:
                image_save(file, '/home/MamsWeb/mysite/static/invoice_content_images/' + primary_key + '.png')
            except:
                image_save(file, 'static/invoice_content_images/' + primary_key + '.png')
            invoice_content.image_path = file_path_db
            db.session.commit()
            return redirect("/invoice?view=invoice_manager&invoice_id=" + str(invoice_content.invoice_id))


def delete_image():
    primary_key = request_args('content_id')
    if primary_key is None:
        return error(type="invoice_master_no_match")

    if request.method == 'POST':
        invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
        validation_data = InvoiceIndex.query.filter_by(user_group=user_group(session.get('username')),
                                                       invoice_id=invoice_content.invoice_id).first()
        if validation_data:
            delete_image_function(invoice_content.image_path)
            invoice_content.image_path = None
            db.session.commit()
            return redirect("/invoice?view=invoice_manager&invoice_id=" + str(invoice_content.invoice_id))


def change_expired_password():
    user_name = request.form["user"].lower()
    password_current = request.form["password_current"]
    password_new = request.form["password_new"]
    password_new_re = request.form["password_new_re"]
    userinfo = User.query.filter_by(user_name=user_name).first()
    if userinfo.password != hasher(password_current):
        return security(type="password_expired", title="Change your password - Mams Product App",
                        message="Incorrect details entered", user_name=user_name)
    elif password_new != password_new_re:
        return security(type="password_expired", title="Change Your Password - Mams Product App",
                        message="New password and re-entered new password did not match. Please try again",
                        user_name=user_name)
    elif check_password_condition(password_new) is False:
        return security(type="password_expired", title="Change Your Password - Mams Product App",
                        message="New password does not meet minimum requirements", user_name=user_name)
    else:
        userinfo.password = hasher(password_new)
        userinfo.password_status = 'active'
        db.session.commit()
        return error(title="Password Changed - Mams Product App", type="password_changed")


def proforma():
    sort_string = request_args('sort') if request_args('sort') is not None else "customer_name"
    sort_by = request_args('sort_by') if request_args('sort_by') != 'none' else None
    next_sort_value = 'desc'
    if sort_by == 'asc':
        next_sort_value = 'desc'
    else:
        next_sort_value = 'asc'
    if sort_by == 'desc':
        sort_by = desc
    else:
        sort_by = asc

    customer_details = (CustomerDetails.query.
                        filter_by(user_group=user_group(session.get('username'))).
                        order_by(sort_by(sort_string)).
                        with_entities(CustomerDetails.customer_name, CustomerDetails.primarykey,CustomerDetails.salesman_id).distinct())
    salesman_list = SalesmanDetails.query.all()
    return customer_invoice(type="invoice_home", title="Proforma - Mams Product App", data=customer_details, salesman_list=salesman_list, sort_by=next_sort_value)


def invoice_manager():
    invoice_id = request_args('invoice_id')
    if invoice_id is None:
        return error(type="invoice_master_no_match")
    validation_data = InvoiceIndex.query \
        .filter_by(user_group=user_group(session.get('username')), invoice_id=invoice_id).first()
    if validation_data:
        for_stock_update = InvoiceContent.query.filter_by(invoice_id=invoice_id).all()
        for i in for_stock_update:
            master_data = Master.query.filter_by(code_value=code_remove_zero_prefix(i.code)).first()
            try:
                i.stock = master_data.quantity
            except:
                i.stock = "Unknown"
            try:
                i.sp = master_data.sale_val + " / " + master_data.unit_val
            except:
                i.sp = "Unknown"
        db.session.commit()
        sort_string = request_args('sort') if request_args('sort') is not None else "entry_order"
        data = InvoiceContent.query.filter_by(invoice_id=invoice_id).order_by(sort_string).all()
        g_total = 0
        for i in data: g_total += float(i.total)
        vat = float("{:.2f}".format(g_total * 0.05))
        final_total = float("{:.2f}".format(g_total + vat))
        margin_percent = 0
        total_bill_amount = 0
        total_profit_amount = 0
        for f in data:
            if isinstance(f.purchase_price, int) or isinstance(f.purchase_price, float):
                try:
                    profit_rate = float(f.price) - f.purchase_price
                    profit_amount = profit_rate * float(f.quantity)
                    total_profit_amount += profit_amount
                    total_bill_amount += float(f.total)
                except:
                    print(f)
        profit_percent = round((total_profit_amount / total_bill_amount) * 100, 2) if total_bill_amount > 0 else 0
        try:
            total_principle_amount = total_bill_amount - total_profit_amount
            margin_percent = round((total_profit_amount / total_principle_amount) * 100, 2)
        except:
            pass
        total_bill_amount = round(total_bill_amount, 2)
        total_profit_amount = round(total_profit_amount, 2)
        invoice_data = InvoiceIndex.query.filter_by(invoice_id=invoice_id).first()
        customer_data = CustomerDetails.query.filter_by(primarykey=invoice_data.customer_id).first()
        return render_template(
            "invoice_manager.html", title="Invoice " + str(invoice_data.invoice_id) + " - " +
                                          str(customer_data.customer_name) + " - Mams Product App", navbar=navbar(),
            customername=customer_data.customer_name, customer_id=customer_data.primarykey,
            invoice_data=invoice_data, data=data, last=last_update_date_time(), Gtotal=g_total, VAT=vat,
            FinalTotal=final_total, sorter=sort_string, date_quote=invoice_data.date, profit_percent=profit_percent,
            margin_percent=margin_percent,
            total_bill_amount=total_bill_amount, total_profit_amount=total_profit_amount,
            created_by=proper(invoice_data.user_name))
    else:
        return not_found()


def not_found():
    return error(type="404", title="404 Not Found - Mams Product App", )


def update_customer_total(customer_id):
    invoice_data = InvoiceIndex.query.filter_by(customer_id=customer_id).with_entities(
        InvoiceIndex.invoice_amount).all()
    total_amount = 0
    for amount in invoice_data:
        try:
            total_amount = total_amount + float(amount[0])
        except:
            pass
    total_amount = round(total_amount * 1.05, 2)

    customer_data = CustomerDetails.query.filter_by(primarykey=customer_id).first()
    customer_data.total_amount = total_amount
    db.session.commit()


def update_invoice_amount(invoice_id):
    data = InvoiceContent.query.filter_by(invoice_id=invoice_id).with_entities(InvoiceContent.total).all()
    total_amount = 0.00
    for amount in data:
        total_amount = total_amount + float(amount[0])
    total_amount = round((total_amount * 1.05), 2)
    data = InvoiceIndex.query.filter_by(invoice_id=invoice_id).first()
    data.invoice_amount = total_amount
    db.session.commit()
    update_customer_total(InvoiceIndex.query.filter_by(invoice_id=invoice_id).first().customer_id)


def invoice():
    cust_id = request_args('customer_id')
    if cust_id is None:
        return error(type="invoice_master_no_match")
    customer_details = CustomerDetails.query.filter_by(primarykey=cust_id, user_group=user_group(session.get('username'))).first()
    customer_name = customer_details.customer_name
    data = InvoiceIndex.query.order_by(InvoiceIndex.invoice_id.desc()).filter_by(user_group=user_group(session.get('username')), customer_id=cust_id).all()
    return customer_invoice(type='invoice_list', title=customer_name + " Invoice List - Mams Product App", customername=customer_name, cust_id=cust_id, data=data, total_amount=customer_details.total_amount)


def invoice_list():
    sort_string = request_args('sort') if request_args('sort') != 'none' else None
    sort_by = request_args('sort_by') if request_args('sort_by') != 'none' else None
    next_sort_value = 'desc'
    if sort_by == 'asc':
        next_sort_value = 'desc'
    else:
        next_sort_value = 'asc'
    if sort_by == 'desc':
        sort_by = desc
    else:
        sort_by = asc


    invoice_index_data = (InvoiceIndex.query.
                          join(CustomerDetails,InvoiceIndex.customer_id == CustomerDetails.primarykey).
                          with_entities(InvoiceIndex.invoice_id, CustomerDetails.customer_name, CustomerDetails.salesman_id,InvoiceIndex.date, InvoiceIndex.invoice_amount).
                          filter_by(user_group=user_group(session.get('username'))).distinct().
                          order_by(sort_by(sort_string), InvoiceIndex.invoice_id.desc()).all())
    salesman_list = SalesmanDetails.query.all()
    return customer_invoice(type="complete_invoice_list", title="Invoice List - Mams Product App",
                            data=invoice_index_data, salesman_list=salesman_list, sort_by=next_sort_value)


def invoice_print():
    invoice_id = request_args('invoice_id')
    sort_by = request_args('sort_by') if request_args('sort_by') is not None else "entry_order"
    print_type = request_args('print_type') if request_args('print_type') is not None else 'normal'
    if invoice_id is None:
        return error(type="invoice_master_no_match")

    data = db.session.query(CustomerDetails, InvoiceIndex, InvoiceContent) \
        .join(InvoiceIndex, CustomerDetails.primarykey == InvoiceIndex.customer_id) \
        .join(InvoiceContent, InvoiceIndex.invoice_id == InvoiceContent.invoice_id) \
        .filter(CustomerDetails.user_group == user_group(session.get('username')),
                InvoiceContent.invoice_id == invoice_id).order_by(sort_by).all()

    if data:
        customer_details = data[0][0]
        invoice_details = data[0][1]
        salesman_id = customer_details.salesman_id
        date_print = str(invoice_details.date[8:]) + "-" + str(invoice_details.date[5:7]) + "-" + str(
            invoice_details.date[0:4])
        salesman_data = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first()
        if print_type == "normal":
            g_total = 0
            for (customer_det, invoice_index, invoice_cont) in data:
                g_total = g_total + float(invoice_cont.total)
            g_total = format(g_total, ".2f")
            vat = format(float(g_total) * 0.05, ".2f")
            final_total = format(float(g_total) + float(vat), ".2f")
            return render_template("invoice_print.html", type='invoice_normal', CustomerDetails=customer_details, data=data,last=last_update_date_time(), Gtotal=g_total, VAT=vat, FinalTotal=final_total,print=time_string(), InvoiceDetails=invoice_details, Date_print=date_print,amount_in_words=amount_in_words(float(final_total)),title="Ref # " + str(invoice_id) + " - " + str(customer_details.customer_name) + " " + time_string()[:10], salesman_data=salesman_data)
        elif print_type == "without_quantity":
            return render_template("invoice_print.html", type='invoice_exception', CustomerDetails=customer_details, data=data,last=last_update_date_time(),print=time_string(), InvoiceDetails=invoice_details, Date_print=date_print,title="Ref # " + str(invoice_id) + " - " + str(customer_details.customer_name) + " " + time_string()[:10],salesman_data=salesman_data)
    else:
        return not_found()


def company_name_formatter(input_str):
    def title_case(word_):
        word_ = word_.strip()
        if len(word_) > 1:
            return word_[0].upper() + word_[1:].lower()
        elif len(word_) > 0:
            return word_[0].upper()
        return

    input_str_list = input_str.strip().split(" ")
    output_string = ""
    for word in input_str_list:
        if (word[0] == "'") and (word[-1] == "'"):
            output_string = output_string + word[1:-1] + " "
        else:
            output_string = output_string + title_case(word) + " "

    output_string = output_string.strip()
    return output_string

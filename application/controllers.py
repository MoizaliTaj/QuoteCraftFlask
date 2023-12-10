from application.functions import *
from flask import current_app as app, jsonify
from application.models import PhoneIndex, PhoneNumber, Logs

app.secret_key = '4c3680e76fc3c7b14495e39f474667fde0fddccasd1238ba19798e8fffb2b8f9b763241'

@app.route("/login", methods=["GET", "POST"])
def login_():
    if request_args("view") == "change_password":
        return change_expired_password()
    return login()

@app.route("/logout")
def logout_():
    return logout()

@app.route("/")
@login_required
def home():
    return render_template("index.html", last=last_update_date_time(), navbar=navbar(), title="Home - Company Name")

@app.route("/find", methods=["GET", "POST"])
@login_required
def find_product():
    if (request.args.get('type') == 'table') or (request.args.get('type') == 'indi'):
        return find_product_function()
    elif request.args.get('type') == 'history':
        return history()
    else:
        return not_found()

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_product_to_invoice():
    product_id = request.args.get('product_id')
    search_query = request.args.get('search_query')
    search_type = request.args.get('search_type')
    return add_product_function(product_id, search_query, search_type)

@app.route("/invoice", methods=["GET", "POST"])
@login_required
def invoice_master():
    # Customer list page.
    if request.args.get('view') == "customer_list":
        return proforma()

    # Add a new customer
    elif request.args.get('view') == "add_customer":
        return add_customer()

    # Update existing customer details
    elif request.args.get('view') == "update_customer":
        return update_customer_details()

    # All invoices on one page, most recent on top.
    elif request.args.get('view') == "all_invoice_list":
        return invoice_list()

    # All invoices for a particular customer.
    elif request.args.get('view') == "invoice_list":
        return invoice()

    # Add new invoice for an existing customer.
    elif request.args.get('view') == "invoice_add":
        return add_invoice()

    # Edit existing invoice meta details.
    elif request.args.get('view') == "invoice_edit":
        return update_invoice_details()

    # Delete invoice.
    elif request.args.get('view') == "invoice_delete":
        return delete_invoice_details()

    # Page where invoice summary can be viewed and edited.
    elif request.args.get('view') == "invoice_manager":
        return invoice_manager()

    # Edit invoice content.
    elif request.args.get('view') == "edit_invoice_content":
        return edit_invoice_content()

    # Delete invoice entry.
    elif request.args.get('view') == "delete_invoice_content":
        return delete_invoice_content()

    # Add Image.
    elif request.args.get('view') == "add_image":
        return add_image()

    # Delete Image.
    elif request.args.get('view') == "del_image":
        return delete_image()

    # Print the invoice, which can be saved as pdf via browser
    elif request.args.get('view') == "invoice_print":
        return invoice_print()

    else:
        return error(type="invoice_master_no_match")



@app.route("/phone", methods=["GET", "POST"])
@login_required
def phone():
    view = request.args.get('view')
    query = request.args.get("query")
    if view == "search":
        data_combined = db.session.query(PhoneIndex, PhoneNumber).join(PhoneIndex,PhoneIndex.phonebook_id == PhoneNumber.phonebook_id).filter(or_(PhoneIndex.business_name.like("%" + query + "%"),PhoneIndex.segment.like("%" + query + "%"), PhoneNumber.name.like("%" + query + "%"),PhoneNumber.phone_number.like("%" + query + "%"))).all()
        return render_template("phone.html", title="Phone Book | Company Name", navbar=navbar(), type="result", data=data_combined, query=query)
    elif view == "add_business":
        if request.method == 'GET':
            return render_template("phone.html", title="Phone Book | Add New Business | Company Name", navbar=navbar(), type="add_business")
        if request.method == 'POST':
            new_business_name = request.form['business_name']
            new_segment = request.form['segment']
            check_duplicate = PhoneIndex.query.filter_by(business_name=new_business_name).all()
            if check_duplicate:
                return error(title="Error Duplicate Customer -  Company Name", type="phone_index_clash")
            new_business_entry = PhoneIndex(business_name=new_business_name, segment=new_segment)
            db.session.add(new_business_entry)
            db.session.commit()
            new_phonebook_id = PhoneIndex.query.filter_by(business_name=new_business_name).first().phonebook_id
            # return error(title="Error Duplicate Customer - Company Name", type="phone_index_added")
            return redirect("/phone?view=view_business&business_id=" + str(new_phonebook_id))
    elif view == "add_number":
        if request.method == 'GET':
            business_id = request.args.get('business_id')
            business_data = PhoneIndex.query.filter_by(phonebook_id=business_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Company Name", navbar=navbar(), type="add_number", data=business_data)
        if request.method == 'POST':
            business_id = request.args.get('business_id')
            new_contact_name = request.form['contact_name']
            new_contact_number = request.form['contact_number']
            new_number_entry = PhoneNumber(phonebook_id=business_id,name=new_contact_name,phone_number=new_contact_number)
            db.session.add(new_number_entry)
            db.session.commit()
            # return error(title="Number added to phone book - Company Name", type="number_added", redirect_link="/phone?view=view_business&business_id=" + str(business_id))
            return redirect("/phone?view=view_business&business_id=" + str(business_id))
    elif view == "edit_number":
        if request.method == 'GET':
            number_id = request.args.get('number_id')
            number_data = PhoneNumber.query.filter_by(number_id=number_id).first()
            business_data = PhoneIndex.query.filter_by(phonebook_id=number_data.phonebook_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Company Name", navbar=navbar(), type="edit_number", number_data=number_data, business_data=business_data)
        if request.method == 'POST':
            number_id = request.args.get('number_id')
            
            updated_contact_name = request.form['contact_name']
            updated_contact_number = request.form['contact_number']
            
            updated_business_name = request.form['business_name']
            updated_segment = request.form['segment']
            
            number_data = PhoneNumber.query.filter_by(number_id=number_id).first()
            business_data = PhoneIndex.query.filter_by(phonebook_id=number_data.phonebook_id).first()
            
            number_data.name = updated_contact_name
            number_data.phone_number = updated_contact_number
            
            business_data.business_name = updated_business_name
            business_data.segment = updated_segment
            
            db.session.commit()
            # return error(title="Phone Number Updated - Company Name", type="number_updated", redirect_link="/phone?view=view_business&business_id=" + str(number_data.phonebook_id))
            return redirect("/phone?view=view_business&business_id=" + str(number_data.phonebook_id))
    elif view == "delete_number":
        if request.method == 'GET':
            number_id = request.args.get('number_id')
            number_data = PhoneNumber.query.filter_by(number_id=number_id).first()
            business_data = PhoneIndex.query.filter_by(phonebook_id=number_data.phonebook_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Company Name", navbar=navbar(), type="delete_number", number_data=number_data, business_data=business_data)
        if request.method == 'POST':
            number_id = request.args.get('number_id')
            phonebook_id = str(PhoneNumber.query.filter_by(number_id=number_id).first().phonebook_id)
            db.session.query(PhoneNumber).filter_by(number_id=number_id).delete()
            db.session.commit()
            return error(title="Phone Number Deleted - Company Name", type="number_deleted", redirect_link="/phone?view=view_business&business_id=" + phonebook_id)
    elif view == "view_business":
        business_id = request.args.get('business_id')
        business_data = PhoneIndex.query.filter_by(phonebook_id=business_id).first()
        number_data = PhoneNumber.query.filter_by(phonebook_id=business_id).all()
        return render_template("phone.html", title="Phone Book | Company Name", navbar=navbar(), type="business_home", data=number_data, business_data=business_data)
    data_business = PhoneIndex.query.order_by(PhoneIndex.business_name.asc()).all()
    return render_template("phone.html", title="Phone Book | Company Name", navbar=navbar(), type="home", data=data_business)

@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin():
    if request.args.get('view') == "add_user":
        return admin_add_user()
    elif request.args.get('view') == "update_user":
        return admin_update_user()
    elif request.args.get('view') == "update_user_password":
        return admin_update_user_change_password()
    elif request.args.get('view') == "logs":
        return admin_logs()
    elif request.args.get('view') == "logs_excel":
        return admin_logs_excel()
    elif request.args.get('view') == "db_update":
        return db_update()
    return admin_(type="admin_home", title="Admin Page - Company Name")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == 'GET':
        return security(type="change_password", title="Change Your Password - Company Name",
                        message="")
    if request.method == 'POST':
        password_current = request.form["password_current"]
        password_new = request.form["password_new"]
        password_new_re = request.form["password_new_re"]
        userinfo = User.query.filter_by(user_name=session.get('username')).first()
        if userinfo.password != hasher(password_current):
            logout()
            return error(title="Something went wrong - Company Name", type="current_password_incorrect")
        elif password_new != password_new_re:
            return security(type="change_password", title="Change Your Password - Company Name",
                            message="New password and re-entered new password did not match. Please try again")
        elif check_password_condition(password_new) is False:
            return security(type="change_password", title="Change Your Password - Company Name",
                            message="New password does not meet minimum requirements")
        else:
            userinfo.password = hasher(password_new)
            db.session.commit()
            logout()
            return error(title="Password Changed - Company Name", type="password_changed")

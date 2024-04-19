from application.function import *
from application.pdf_printer import *

@app.route("/login", methods=["GET", "POST"])
def login_():
    def change_expired_password():
        user_name = request.form["user"].lower()
        password_current = request.form["password_current"]
        password_new = request.form["password_new"]
        password_new_re = request.form["password_new_re"]
        userinfo = User.query.filter_by(user_name=user_name).first()
        if userinfo.password != hasher(password_current):
            return security(type="password_expired", title="Change your password - Generic Product App",
                            message="Incorrect details entered", user_name=user_name)
        elif password_new != password_new_re:
            return security(type="password_expired", title="Change Your Password - Generic Product App",
                            message="New password and re-entered new password did not match. Please try again",
                            user_name=user_name)
        elif check_password_condition(password_new) is False:
            return security(type="password_expired", title="Change Your Password - Generic Product App",
                            message="New password does not meet minimum requirements", user_name=user_name)
        else:
            userinfo.password = hasher(password_new)
            userinfo.password_status = 'active'
            db.session.commit()
            return error(title="Password Changed - Generic Product App", type="password_changed")

    if request_args("view") == "change_password":
        return change_expired_password()
    return login()


@app.route("/logout")
def logout_():
    return logout()


@app.route("/")
@login_required
def home():
    return render_template("index.html", last=last_update_date_time(), navbar=navbar(), title="Home - Generic Product App")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == 'GET':
        return security(type="change_password", title="Change Your Password - Generic Product App", message="")
    if request.method == 'POST':
        password_current = request.form["password_current"]
        password_new = request.form["password_new"]
        password_new_re = request.form["password_new_re"]
        userinfo = User.query.filter_by(user_name=session.get('username')).first()
        if userinfo.password != hasher(password_current):
            logout()
            return error(title="Something went wrong - Generic Product App", type="current_password_incorrect")
        elif password_new != password_new_re:
            return security(type="change_password", title="Change Your Password - Generic Product App", message="New password and re-entered new password did not match. Please try again")
        elif check_password_condition(password_new) is False:
            return security(type="change_password", title="Change Your Password - Generic Product App", message="New password does not meet minimum requirements")
        else:
            userinfo.password = hasher(password_new)
            db.session.commit()
            logout()
            return error(title="Password Changed - Generic Product App", type="password_changed")


@app.route("/quotations")
@login_required
def quotations():
    return render_template("quotations.html", title="Quotations - Generic Product App", last=last_update_date_time(), navbar=navbar())


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    search_query = request_args('query')
    if (search_query is not None) and (len(splitting_action(search_query)) > 0):
        query = code_remove_zero_prefix(splitting_action(search_query))
        data = InvoiceIndex.query \
            .filter_by(user_group=get_user_group(get_user_name())) \
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
            .distinct().order_by(InvoiceContent.code.asc(), InvoiceContent.invoice_id.asc()).all()
    else:
        query = ""
        data = []
    return render_template(
        "history.html", last=last_update_date_time(), navbar=navbar(), title="History - Generic Product App", data=data, query=query)


@app.route("/specific_history")
@login_required
def specific_history():
    customer_id = request_args('customer_id')
    code = request_args('code')
    description = request_args('description')
    data = InvoiceIndex.query \
        .filter_by(user_group=get_user_group(get_user_name()), ) \
        .join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey) \
        .join(InvoiceContent, InvoiceContent.invoice_id == InvoiceIndex.invoice_id) \
        .with_entities(InvoiceContent.invoice_id,
            InvoiceContent.code,
            InvoiceContent.description,
            InvoiceContent.size,
            InvoiceContent.packing,
            InvoiceContent.price,
            InvoiceContent.quantity,
            InvoiceContent.notes,
            InvoiceContent.unit,
            InvoiceContent.purchase_price,
            InvoiceIndex.date,)
    if (len(code) > 0) and (len(description) > 0):
        data = data.filter(CustomerDetails.primarykey == customer_id, or_(InvoiceContent.code.like("%" + code + "%"), InvoiceContent.description.like("%" + description + "%"), )).distinct().order_by(InvoiceContent.invoice_id.desc()).all()
    elif len(code) > 0:
        data = data.filter(CustomerDetails.primarykey == customer_id, InvoiceContent.code.like("%" + code + "%")).distinct().order_by(InvoiceContent.invoice_id.desc()).all()
    elif len(description) > 0:
        data = data.filter(CustomerDetails.primarykey == customer_id, InvoiceContent.description.like("%" + description + "%")).distinct().order_by(InvoiceContent.invoice_id.desc()).all()
    else:
        data = []
    result = []
    for entry in data:
        result.append({
            'invoice_id': entry[0],
            'code': entry[1],
            'description': entry[2],
            'size': entry[3],
            'packing': entry[4],
            'rate': entry[5],
            'quantity': entry[6],
            'notes': entry[7],
            'unit': entry[8],
            'purchase_price': entry[9],
            'date': entry[10],
        })
    return jsonify(result)

@app.route("/invoice_logs", methods=["GET", "POST"])
@login_required
def invoice_logs():
    if request.method == 'GET':
        return customer_invoice(type="invoice_logs", title="Invoice Logs - Generic Product App", logs_data=[])
    if request.method == 'POST':
        invoice_id = request.form["invoice_id"].strip()
        logs_data = LogsInvoice.query.filter_by(invoice_id=invoice_id).all()
        return customer_invoice(type="invoice_logs", title="Invoice Logs - Generic Product App", logs_data=logs_data, user_dict=user_data_dict(), invoice_id=invoice_id)


@app.route("/games", methods=["GET", "POST"])
@login_required
def games():
    if request.args.get('view') == "tic_tac":
        return render_template("games_tictac.html", title="Games | Tic-Tac-Toe - Generic Product App", navbar=navbar())
    elif request.args.get('view') == "dino":
        game_data = GameScore.query.filter_by(game="dino").order_by(desc('score')).all()
        return render_template("games_dino.html", title="Games | Dino - Generic Product App", navbar=navbar(),data=game_data)
    return render_template("games.html", title="Games | Generic Product App", navbar=navbar())


@app.route("/phone", methods=["GET", "POST"])
@login_required
def phone():
    view = request.args.get('view')
    query = request.args.get("query")
    if view == "search":
        data_combined = db.session.query(PhoneIndex, PhoneNumber).join(PhoneIndex,PhoneIndex.phonebook_id == PhoneNumber.phonebook_id).filter(or_(PhoneIndex.business_name.like("%" + query + "%"), PhoneIndex.segment.like("%" + query + "%"),PhoneNumber.name.like("%" + query + "%"), PhoneNumber.phone_number.like("%" + query + "%"))).all()
        return render_template("phone.html", title="Phone Book | Generic Product App", navbar=navbar(), type="result",data=data_combined, query=query)
    elif view == "add_business":
        if request.method == 'GET':
            return render_template("phone.html", title="Phone Book | Add New Business | Generic Product App",navbar=navbar(), type="add_business")
        if request.method == 'POST':
            new_business_name = request.form['business_name']
            new_segment = request.form['segment']
            check_duplicate = PhoneIndex.query.filter_by(business_name=new_business_name).all()
            if check_duplicate:
                return error(title="Error Duplicate Customer - Generic Product App", type="phone_index_clash")
            new_business_entry = PhoneIndex(business_name=new_business_name, segment=new_segment)
            db.session.add(new_business_entry)
            db.session.commit()
            new_phonebook_id = PhoneIndex.query.filter_by(business_name=new_business_name).first().phonebook_id
            return redirect("/phone?view=view_business&business_id=" + str(new_phonebook_id))
    elif view == "add_number":
        if request.method == 'GET':
            business_id = request.args.get('business_id')
            business_data = PhoneIndex.query.filter_by(phonebook_id=business_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Generic Product App",navbar=navbar(), type="add_number", data=business_data)
        if request.method == 'POST':
            business_id = request.args.get('business_id')
            new_contact_name = request.form['contact_name']
            new_contact_number = request.form['contact_number']
            new_number_entry = PhoneNumber(phonebook_id=business_id, name=new_contact_name,phone_number=new_contact_number)
            db.session.add(new_number_entry)
            db.session.commit()
            return redirect("/phone?view=view_business&business_id=" + str(business_id))
    elif view == "edit_number":
        if request.method == 'GET':
            number_id = request.args.get('number_id')
            number_data = PhoneNumber.query.filter_by(number_id=number_id).first()
            business_data = PhoneIndex.query.filter_by(phonebook_id=number_data.phonebook_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Generic Product App",navbar=navbar(), type="edit_number", number_data=number_data,business_data=business_data)
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
            return redirect("/phone?view=view_business&business_id=" + str(number_data.phonebook_id))
    elif view == "delete_number":
        if request.method == 'GET':
            number_id = request.args.get('number_id')
            number_data = PhoneNumber.query.filter_by(number_id=number_id).first()
            business_data = PhoneIndex.query.filter_by(phonebook_id=number_data.phonebook_id).first()
            return render_template("phone.html", title="Phone Book | Add New Business | Generic Product App",navbar=navbar(), type="delete_number", number_data=number_data,business_data=business_data)
        if request.method == 'POST':
            number_id = request.args.get('number_id')
            phonebook_id = str(PhoneNumber.query.filter_by(number_id=number_id).first().phonebook_id)
            db.session.query(PhoneNumber).filter_by(number_id=number_id).delete()
            db.session.commit()
            return redirect("/phone?view=view_business&business_id=" + phonebook_id)
    elif view == "view_business":
        business_id = request.args.get('business_id')
        business_data = PhoneIndex.query.filter_by(phonebook_id=business_id).first()
        number_data = PhoneNumber.query.filter_by(phonebook_id=business_id).all()
        return render_template("phone.html", title="Phone Book | Generic Product App", navbar=navbar(),type="business_home", data=number_data, business_data=business_data)
    data_business = PhoneIndex.query.order_by(PhoneIndex.business_name.asc()).all()
    return render_template("phone.html", title="Phone Book | Generic Product App", navbar=navbar(), type="home",data=data_business)


@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin():
    def db_update():
        if request.method == 'GET':
            return render_template("db_update.html", last=last_update_date_time(), type="upload", title="Update Date Base - Generic Product App", navbar=navbar())
        if request.method == 'POST':
            vachet_file = request.files["vachet"]
            sanitary_file = request.files["sanitary"]
            stock_file = request.files["stock"]
            try:
                vachet_file.save('/home/generic/mysite/db_directory/excel_files/' + "vachet.xls")
                sanitary_file.save('/home/generic/mysite/db_directory/excel_files/' + "sanitary.xlsx")
                stock_file.save('/home/generic/mysite/db_directory/excel_files/' + "stock.xlsx")
            except:
                vachet_file.save('db_directory/excel_files/' + "vachet.xls")
                sanitary_file.save('db_directory/excel_files/' + "sanitary.xlsx")
                stock_file.save('db_directory/excel_files/' + "stock.xlsx")
            return render_template("db_update.html", last=last_update_date_time(), type="update", title="Update Date Base - Generic Product App", navbar=navbar())

    def admin_add_user():
        if request.method == 'GET':
            return admin_(type="admin_add", title="Add New user - Generic Product App")
        if request.method == 'POST':
            user_name = request.form['user'].lower()
            user_full_name = request.form['user_full_name']
            user_group_ = request.form['usergroup']
            user_type = request.form['type']
            userdata = User.query.filter_by(user_name=user_name).first()
            if userdata:
                return admin_(type="user_duplicate", title="Add New user - Generic Product App")
            else:
                password_new = random_password_generator(10)
                new_entry = User(user_name=user_name, user_full_name=user_full_name, user_group=user_group_, password=hasher(password_new), type=user_type, password_status='expired')
                db.session.add(new_entry)
                db.session.commit()
                log_string = "User id: " + user_name + "\nFull Name: " + user_full_name + "\nUser Group: " + user_group_ + "\nUser Type: " + user_type
                user_logs_save(user_name, "User Added", log_string)
                return admin_(type="add_success", title="Add New user - Generic Product App", user_name=user_name, new_password=password_new)

    def admin_update_user():
        if request.method == 'GET':
            user_pk = request_args('user_pk')
            if user_pk:
                userdata = User.query.filter_by(primary_key=user_pk).first()
                logs_data = LogsUser.query.filter_by(user_name=userdata.user_name).order_by(LogsUser.primary_key.desc()).all()
                return admin_(type="user_edit", title="Add New user - Generic Product App", userdata=userdata, logs_data=logs_data, user_dict=user_data_dict())
            else:
                userdata = User.query.order_by('user_group', 'user_name').all()
                return admin_(type="admin_update", title="Update user - Generic Product App", data=userdata)
        if request.method == 'POST':
            primary_key = request.form['primary_key'].lower()
            user_full_name = request.form['user_full_name']
            user_group = request.form['user_group']
            type = request.form['type']
            userdata = User.query.filter_by(primary_key=primary_key).first()
            if userdata:
                log_string = ""
                if userdata.user_full_name != user_full_name:
                    log_string += "User full name changed from " + userdata.user_full_name + " to " + user_full_name + "\n"
                if userdata.user_group != user_group:
                    log_string += "User group changed from " + userdata.user_group + " to " + user_group + "\n"
                if userdata.type != type:
                    log_string += "User type changed from " + userdata.type + " to " + type + "\n"
                userdata.user_full_name = user_full_name
                userdata.user_group = user_group
                userdata.type = type
                db.session.commit()
                if len(log_string) > 0:
                    log_string = "User id: " + userdata.user_name + "\n\n" + log_string
                    user_logs_save(userdata.user_name, "User Details Changed", log_string)
                return redirect("/admin?view=update_user&user_pk=" + str(userdata.primary_key))
            else:
                return admin_(type="user_update_no_user", title="Add New user - Generic Product App")

    def admin_update_user_change_password():
        user_pk = request_args('user_pk')
        if request.method == 'GET':
            user_data = User.query.filter_by(primary_key=user_pk).first()
            return admin_(type="change_password_permission", title="Add New user - Generic Product App", user_data=user_data)
        if request.method == 'POST':
            primary_key = request.form['primary_key'].lower()
            user_data = User.query.filter_by(primary_key=primary_key).first()
            if user_data:
                new_password = random_password_generator(10)
                user_data.password = hasher(new_password)
                user_data.password_status = 'expired'
                db.session.commit()
                user_logs_save(user_data.user_name, "Password Reset", "User ID: " + user_data.user_name + "\n" + "User Name: " + user_data.user_full_name)
                return admin_(type="change_password_confirmation", title="Add New user - Generic Product App", user_data=user_data, new_password=new_password)
            else:
                not_found()

    def admin_logs():
        logs_data = LogsLoginLogout.query.order_by(LogsLoginLogout.primary_key.desc()).limit(500).all()
        return admin_(type="logs", title="Admin Logs - Generic Product App", logs_data=logs_data, user_dict=user_data_dict())

    def admin_logs_excel():
        logs_data = LogsLoginLogout.query.order_by(LogsLoginLogout.primary_key.desc()).all()
        logs_dict = {"sr": [], "date_time": [], "user": [], "ip_address": [], "type": []}
        for logs in logs_data:
            logs_dict["sr"].append(logs.primary_key)
            logs_dict["date_time"].append(logs.date_time)
            logs_dict["user"].append(logs.user)
            logs_dict["ip_address"].append(logs.ip_address)
            logs_dict["type"].append(logs.type)
        csv_df = pd.DataFrame(logs_dict)
        resp = make_response(csv_df.to_csv())
        resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp

    if request.args.get('view') == "db_update":
        return db_update()
    elif request.args.get('view') == "add_user":
        return admin_add_user()
    elif request.args.get('view') == "update_user":
        return admin_update_user()
    elif request.args.get('view') == "update_user_password":
        return admin_update_user_change_password()
    elif request.args.get('view') == "logs":
        return admin_logs()
    elif request.args.get('view') == "logs_excel":
        return admin_logs_excel()
    return admin_(type="admin_home", title="Admin Page - Generic Product App")


@app.route("/invoice", methods=["GET", "POST"])
@login_required
def invoice_master():

    def update_customer_details():
        cust_id = request_args('customer_id')
        if cust_id is None:
            return error(type="invoice_master_no_match")
        if request.method == 'GET':
            customer_details = CustomerDetails.query.filter_by(primarykey=cust_id,
                                                               user_group=get_user_group(get_user_name())).first()
            if customer_details:
                salesman_list = SalesmanDetails.query.filter_by(group=get_user_group(get_user_name())).order_by(SalesmanDetails.salesman_name.asc()).all()
                current_salesman_detail = SalesmanDetails.query.filter_by(salesman_id=customer_details.salesman_id).first()
                return customer_invoice(type="update_customer", title="Update customer Details - Generic Product App", customer_details=customer_details, salesman_list=salesman_list, current_salesman_detail=current_salesman_detail)
            else:
                return not_found()
        if request.method == 'POST':
            cust_name = request.form['cust_name'].strip()
            contact_no = request.form['contact_no'].strip()
            salesman_id = request.form['salesman_id'].strip()
            customer_data = CustomerDetails.query.filter_by(primarykey=cust_id, user_group=get_user_group(get_user_name())).first()
            if cust_name.lower() != customer_data.customer_name.lower():
                customer_details = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name())).filter(CustomerDetails.customer_name.ilike(cust_name), CustomerDetails.primarykey != cust_id).first()
                if customer_details:
                    return error(title="Error Duplicate Customer - Generic Product App", type="customer_name_clash_update", customername=customer_details.customer_name, cust_name=cust_name, customerID=customer_details.primarykey, contact_no=contact_no)
            if customer_data:
                salesman_name = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first().salesman_name
                log_string = ""
                if customer_data.customer_name != cust_name:
                    log_string += "Customer name changed from " + customer_data.customer_name + " to " + cust_name + "\n"
                if customer_data.contact_number != contact_no:
                    log_string += "Contact Number changed from " + customer_data.contact_number + " to " + contact_no + "\n"
                if int(customer_data.salesman_id) != int(salesman_id):
                    log_string += "Salesman ID changed from " + str(customer_data.salesman_id) + " to " + str(
                        salesman_id) + "\n"
                    log_string += "Salesman Name changed from " + customer_data.salesman_name + " to " + salesman_name + "\n"
                if len(log_string) > 0:
                    customer_logs_save(cust_id, "Meta Data Changed", log_string)
                customer_data.customer_name = cust_name
                customer_data.contact_number = contact_no
                customer_data.salesman_id = salesman_id
                customer_data.salesman_name = salesman_name
                db.session.commit()
                return redirect("/quotations#" + str(cust_id))
            else:
                return error(title="Error No Customer Found - Generic Product App", type="no_customer")


    def delete_invoice_details():
        invoice_id = request_args('invoice_id')
        if invoice_id is None:
            return error(type="invoice_master_no_match")
        if request.method == 'GET':
            invoice_index_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()),
                                                              invoice_id=invoice_id).first()
            customer_details = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name()),
                                                               primarykey=invoice_index_data.customer_id).first()
            if invoice_index_data:
                return error(type="invoice_delete",
                             title="Delete Invoice # " + str(invoice_index_data.invoice_id) + " - " + str(
                                 customer_details.customer_name) + " - Generic Product App",
                             invoiceid=invoice_index_data.invoice_id, customername=customer_details.customer_name,
                             cust_id=invoice_index_data.customer_id)
        if request.method == 'POST':
            invoice_index_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()),
                                                              invoice_id=invoice_id).first()
            customer_id = str(invoice_index_data.customer_id)
            customer_name = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name()),
                                                            primarykey=invoice_index_data.customer_id).first().customer_name
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
                customer_logs_save(customer_id, "Invoice Deleted", info)
                invoice_logs_save(invoice_id, "Invoice Deleted", info)
                db.session.query(InvoiceContent).filter_by(invoice_id=invoice_id).delete()
                db.session.query(InvoiceIndex).filter_by(invoice_id=invoice_id).delete()
                db.session.commit()

                update_customer_total(customer_id)
                return redirect('/quotations#' + str(customer_id))

    def invoice_manager():
        invoice_id = request_args('invoice_id')
        if invoice_id is None:
            return error(type="invoice_master_no_match")
        validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()),
                                                       invoice_id=invoice_id).first()
        if validation_data:
            invoice_data = InvoiceIndex.query.filter_by(invoice_id=invoice_id).first()
            customer_data = CustomerDetails.query.filter_by(primarykey=invoice_data.customer_id).first()
            created_by = User.query.filter_by(user_name=invoice_data.user_name).first()
            if created_by is not None:
                created_by = created_by.user_full_name
            else:
                created_by = "Unknown"
            return render_template("invoice_manager.html",
                                   title="Invoice " + str(invoice_data.invoice_id) + " - " + str(
                                       customer_data.customer_name) + " - Generic Product App", navbar=navbar(),
                                   customer_data=customer_data, invoice_data=invoice_data, last=last_update_date_time(),
                                   created_by=created_by)
        else:
            return not_found()

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
            validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()),
                                                           invoice_id=invoice_content.invoice_id).first()
            if validation_data:
                if 'image' not in request.files:
                    return 'No file part1'
                file = request.files['image']
                if file.filename == '':
                    return 'No file part2'
                file_path_db = 'invoice_content_images/' + primary_key + '.png'
                try:
                    image_save(file, '/home/generic/mysite/static/invoice_content_images/' + primary_key + '.png')
                except:
                    image_save(file, 'static/invoice_content_images/' + primary_key + '.png')
                invoice_content.image_path = file_path_db
                invoice_content.added_edited_by = get_user_name()
                db.session.commit()
                invoice_logs_save(invoice_content.invoice_id, "Image Added",
                                  "Image added to Code: " + invoice_content.code)
                return redirect("/invoice?view=invoice_manager&invoice_id=" + str(invoice_content.invoice_id))

    def delete_image():
        primary_key = request_args('content_id')
        if primary_key is None:
            return jsonify("Error")

        invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
        validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()),
                                                       invoice_id=invoice_content.invoice_id).first()
        if validation_data:
            delete_image_function(invoice_content.image_path)
            invoice_content.image_path = None
            invoice_content.added_edited_by = get_user_name()
            db.session.commit()
            invoice_logs_save(invoice_content.invoice_id, "Image Deleted",
                              "Image delete for Code: " + invoice_content.code)
            return jsonify("Done")
        else:
            return jsonify("Error")

    def invoice_print_special():
        def scrub_index(invoice_id_function):
            new_index = 1
            scrub_data = InvoiceContent.query.filter_by(invoice_id=invoice_id_function).order_by('entry_order').all()
            for entry in scrub_data:
                entry.entry_order = new_index
                new_index += 1
            db.session.commit()

        invoice_id = request_args('invoice_id')
        print_type = request_args('print_type')
        if invoice_id is None:
            return error(type="invoice_master_no_match")

        data = db.session.query(CustomerDetails, InvoiceIndex, InvoiceContent).join(InvoiceIndex, CustomerDetails.primarykey == InvoiceIndex.customer_id).join(InvoiceContent, InvoiceIndex.invoice_id == InvoiceContent.invoice_id).filter(CustomerDetails.user_group == get_user_group(get_user_name()), InvoiceContent.invoice_id == invoice_id).order_by('entry_order').all()
        if data:
            customer_details = data[0][0]
            invoice_details = data[0][1]
            invoice_content = InvoiceContent.query.filter_by(invoice_id=invoice_id).order_by('entry_order').all()
            salesman_id = customer_details.salesman_id
            salesman_data = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first()
            scrub_index(invoice_id)
            pdf_file_name = "Ref # " + str(invoice_id) + " - " + str(customer_details.customer_name) + " " + get_current_date_time(print_format=True)[:10] + '.pdf'
            files = os.listdir(base + 'static/pdf_files/')
            for file in files:
                os.remove(base + 'static/pdf_files/' + file)
            printer_invoice(invoice_details,customer_details,salesman_data, get_current_date_time(print_format=True), invoice_content, pdf_file_name, print_type)
            return send_file(base +'static/pdf_files/' + pdf_file_name, as_attachment=True)
            # return render_template("tester.html", invoice_id=invoice_id, print_type=print_type)

    def invoice_print():
        def scrub_index(invoice_id_function):
            new_index = 1
            scrub_data = InvoiceContent.query.filter_by(invoice_id=invoice_id_function).order_by('entry_order').all()
            for entry in scrub_data:
                entry.entry_order = new_index
                new_index += 1
            db.session.commit()

        invoice_id = request_args('invoice_id')
        sort_by = request_args('sort_by') if request_args('sort_by') is not None else "entry_order"
        print_type = request_args('print_type') if request_args('print_type') is not None else 'normal'
        if invoice_id is None:
            return error(type="invoice_master_no_match")

        data = db.session.query(CustomerDetails, InvoiceIndex, InvoiceContent) \
            .join(InvoiceIndex, CustomerDetails.primarykey == InvoiceIndex.customer_id) \
            .join(InvoiceContent, InvoiceIndex.invoice_id == InvoiceContent.invoice_id) \
            .filter(CustomerDetails.user_group == get_user_group(get_user_name()),
                    InvoiceContent.invoice_id == invoice_id).order_by(sort_by).all()

        if data:
            customer_details = data[0][0]
            invoice_details = data[0][1]

            salesman_id = customer_details.salesman_id
            date_print = str(invoice_details.date[8:]) + "-" + str(invoice_details.date[5:7]) + "-" + str(
                invoice_details.date[0:4])
            salesman_data = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first()
            scrub_index(invoice_id)
            return render_template("invoice_print.html", type=print_type, CustomerDetails=customer_details, data=data, last=last_update_date_time(), print=get_current_date_time(print_format=True), InvoiceDetails=invoice_details, Date_print=date_print, title="Ref # " + str(invoice_id) + " - " + str(customer_details.customer_name) + " " + get_current_date_time(print_format=True)[:10], salesman_data=salesman_data)
        else:
            return not_found()

    def add_salesman():
        if request.method == 'GET':
            cust_id = request_args('customer_id') if request_args('customer_id') is not None else ""
            return customer_invoice(type="add_salesman", title="Add New Salesman - Generic Product App",
                                    customer_id=cust_id)
        if request.method == 'POST':
            salesman_name = request.form['salesman_name'].strip()
            mobile_number = request.form['mobile_no'].strip()
            landline_no = request.form['landline_no']
            email_id = request.form['email'].strip()
            customer_id = request.form['customer_id'].strip()
            salesman_data = SalesmanDetails.query.filter_by(salesman_name=salesman_name,
                                                            group=get_user_group(get_user_name())).all()
            if not salesman_data:
                new_entry = SalesmanDetails(salesman_name=salesman_name, mobile_number=mobile_number, email_id=email_id,
                                            landline_no=landline_no, group=get_user_group(get_user_name()))
                db.session.add(new_entry)
                db.session.commit()
                new_salesman_id = SalesmanDetails.query.filter_by(salesman_name=salesman_name, group=get_user_group(
                    get_user_name())).first().salesman_id
                log_string = "New Salesman Added\n" + "Salesman Name: " + salesman_name + "\nMobile Number: " + mobile_number + "\nLand Line: " + landline_no + "\nEmail ID: " + email_id

                salesman_logs_save(new_salesman_id, "Initialization", log_string)
                if len(customer_id) > 0:
                    return error(type="salesman_added",
                                 redirect_link="/invoice?view=update_customer&customer_id=" + str(customer_id))
                else:
                    return error(type="salesman_added", redirect_link="/quotations")
            return error(type="duplicate_salesman")

    def edit_salesman():
        salesman_id = request_args('salesman_id')
        cust_id = request_args('customer_id') if request_args('customer_id') is not None else ""
        if request.method == 'GET':
            if salesman_id is None:
                return error(type="invoice_master_no_match")
            salesman_detail = SalesmanDetails.query.filter_by(salesman_id=salesman_id, group=get_user_group(get_user_name())).first()
            logs_data = LogsSalesman.query.filter_by(salesman_id=salesman_id).all()
            return customer_invoice(type="edit_salesman", title="Edit Salesman Details - Generic Product App", customer_id=cust_id, salesman_detail=salesman_detail, logs_data=logs_data, user_dict=user_data_dict())
        if request.method == 'POST':
            customer_id = request.form['customer_id'].strip()
            salesman_id = request.form['salesman_id'].strip()
            salesman_name = request.form['salesman_name'].strip()
            mobile_number = request.form['mobile_no'].strip()
            landline_no = request.form['landline_no']
            email_id = request.form['email'].strip()
            salesman_data = SalesmanDetails.query.filter_by(salesman_id=salesman_id, group=get_user_group(get_user_name())).first()
            log_string = ""
            if salesman_data.salesman_name != salesman_name:
                log_string += "Salesman name changed from " + salesman_data.salesman_name + " to " + salesman_name + "\n"
            if salesman_data.mobile_number != mobile_number:
                log_string += "Salesman mobile number changed from " + salesman_data.mobile_number + " to " + mobile_number + "\n"
            if salesman_data.landline_no != landline_no:
                log_string += "Landline number changed from " + salesman_data.landline_no + " to " + landline_no + "\n"
            if salesman_data.email_id != email_id:
                log_string += "Email ID changed from " + salesman_data.email_id + " to " + email_id + "\n"
            if salesman_data:
                if salesman_data.salesman_name == salesman_name:
                    salesman_data.mobile_number = mobile_number
                    salesman_data.landline_no = landline_no
                    salesman_data.email_id = email_id
                    db.session.commit()
                    if len(log_string) > 0:
                        salesman_logs_save(salesman_id, "Details Updated", log_string)
                    if len(customer_id) > 0:
                        return error(type="salesman_added", redirect_link="/quotations#" + str(customer_id))
                    else:
                        return error(type="salesman_added", redirect_link="/quotations")
                else:
                    salesman_data_ = SalesmanDetails.query.filter_by(salesman_name=salesman_name, group=get_user_group(get_user_name())).all()
                    if not salesman_data_:
                        salesman_data.salesman_name = salesman_name
                        salesman_data.mobile_number = mobile_number
                        salesman_data.landline_no = landline_no
                        salesman_data.email_id = email_id
                        customer_data = CustomerDetails.query.filter_by(salesman_id=salesman_id).all()
                        for customer in customer_data:
                            customer.salesman_name = salesman_name
                        db.session.commit()
                        if len(log_string) > 0:
                            salesman_logs_save(salesman_id, "Details Updated", log_string)
                        if len(customer_id) > 0:
                            return error(type="salesman_added", redirect_link="/quotations#" + str(customer_id))
                        else:
                            return error(type="salesman_added", redirect_link="/quotations")
                    else:
                        return error(type="duplicate_salesman")

    # Update existing customer details
    if request.args.get('view') == "update_customer":
        return update_customer_details()


    # Delete invoice.
    elif request.args.get('view') == "invoice_delete":
        return delete_invoice_details()

    # Page where invoice summary can be viewed and edited.
    elif request.args.get('view') == "invoice_manager":
        return invoice_manager()

    # Add Image.
    elif request.args.get('view') == "add_image":
        return add_image()

    # Delete Image.
    elif request.args.get('view') == "del_image":
        return delete_image()

    # Print the invoice, which can be saved as pdf via browser
    elif request.args.get('view') == "invoice_print":
        if request.args.get('category') == 'special':
            return invoice_print_special()
        return invoice_print()
    # Add new salesman
    elif request.args.get('view') == "add_salesman":
        return add_salesman()

    # Edit existing salesman details
    elif request.args.get('view') == "edit_salesman":
        return edit_salesman()

    else:
        return error(type="invoice_master_no_match")


@app.route("/add_invoice")
@login_required
def add_invoice():
    cust_id = request_args('customer_id')
    date = request_args('date')
    payment_terms = splitting_action(request_args('payment_terms'))
    attention_to = splitting_action(request_args('attention_to'))
    narration = splitting_action(request_args('narration'))
    narration_external = request_args('narration_external')
    customer_data = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name())).first()
    if customer_data:
        new_entry = InvoiceIndex(customer_id=cust_id, user_name=get_user_name(), user_group=get_user_group(get_user_name()),date=date, payment_terms=payment_terms, attention_to=attention_to, narration=narration,narration_external=narration_external, invoice_amount=0)
        db.session.add(new_entry)
        db.session.commit()
        new_invoice_id = InvoiceIndex.query.filter_by(customer_id=cust_id).order_by(InvoiceIndex.invoice_id.desc()).first().invoice_id
        string_log = "New Invoice Added\nInvoice ID: " + str(new_invoice_id) + "\nDate: " + date + "\n"
        if len(payment_terms) > 0:
            string_log += "Payment Terms: " + payment_terms + "\n"
        if len(attention_to) > 0:
            string_log += "Attention to: " + attention_to + "\n"
        if len(narration) > 0:
            string_log += "Narration: " + narration + "\n"
        if len(narration_external) > 0:
            string_log += "\nNarration External: " + narration_external + "\n"
        customer_logs_save(cust_id,"Invoice Added", string_log)
        return jsonify(new_invoice_id)
    else:
        return jsonify("Error")


@app.route("/salesman_details")
@login_required
def salesman_details():
    salesman_data = SalesmanDetails.query.filter_by(group=get_user_group(get_user_name())).order_by(asc('salesman_name')).all()
    if salesman_data:
        result = []
        for salesman in salesman_data:
            result.append({
                    'salesman_id': salesman.salesman_id,
                    'salesman_name': salesman.salesman_name,
                    'mobile_number': salesman.mobile_number,
                    'landline_no': salesman.landline_no,
                    'email_id': salesman.email_id,
                })
        return jsonify(result)
    else:
        return jsonify("Error")


@app.route("/add_customer")
@login_required
def add_customer():
    customer_name = request_args('customer_name')
    contact_number = request_args('contact_number')
    salesman_id = request_args('salesman_id')
    customer_details = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name())).filter(CustomerDetails.customer_name.ilike(customer_name)).first()
    if customer_details:
        return jsonify("Duplicate")
    else:
        salesman_name = SalesmanDetails.query.filter_by(salesman_id=salesman_id).first().salesman_name
        new_entry = CustomerDetails(customer_name=customer_name, user_name=get_user_name(),user_group=get_user_group(get_user_name()), contact_number=contact_number,total_amount=0, salesman_id=salesman_id, salesman_name=salesman_name)
        db.session.add(new_entry)
        db.session.commit()
        new_customer_id = CustomerDetails.query.filter_by(customer_name=customer_name, user_name=get_user_name(),user_group=get_user_group(get_user_name())).first().primarykey
        customer_logs_save(new_customer_id,"Initialization", "New customer added.")
        return jsonify(new_customer_id)

@app.route("/get_specific_invoice_data")
@login_required
def update_invoice_details():
    invoice_id = request_args('invoice_id')
    if invoice_id is None:
        return jsonify("invoice_master_no_match")

    invoice_index_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).first()
    if invoice_index_data:
        all_customer_data = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name())).order_by(CustomerDetails.customer_name).all()
        result_customer_list = []
        for customer in all_customer_data:
            result_customer_list.append({
                    'customer_id': customer.primarykey,
                    'customer_name': customer.customer_name,
                })
        current_customer_data = InvoiceIndex.query.filter_by(invoice_id=invoice_id).join(CustomerDetails, CustomerDetails.primarykey == InvoiceIndex.customer_id).with_entities(
            CustomerDetails.primarykey,
            CustomerDetails.customer_name,
            InvoiceIndex.invoice_id,
            InvoiceIndex.date,
            InvoiceIndex.payment_terms,
            InvoiceIndex.attention_to,
            InvoiceIndex.narration,
            InvoiceIndex.narration_external
        ).first()
        result_current_customer_info = {
            'customer_id': current_customer_data[0],
            'customer_name': current_customer_data[1],
            'invoice_id': current_customer_data[2],
            'date': current_customer_data[3],
            'payment_terms': current_customer_data[4],
            'attention_to': current_customer_data[5],
            'narration': current_customer_data[6],
            'narration_external': current_customer_data[7]
        }
        return jsonify([result_customer_list, result_current_customer_info])

@app.route("/update_invoice_data")
@login_required
def update_invoice_data():
    def get_customer_name(customer_id):
        customer_data = CustomerDetails.query.filter_by(primarykey=customer_id).first()
        return customer_data.customer_name
    invoice_id = request_args('invoice_id')
    customer_id = request_args('customer_id')
    date = splitting_action(request_args('date'))
    payment_terms = splitting_action(request_args('payment_terms'))
    attention_to = splitting_action(request_args('attention_to'))
    narration = splitting_action(request_args('narration'))
    narration_external = request_args('narration_external')
    invoice_index_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).first()
    invoice_data_old = {
        'customer_id': invoice_index_data.customer_id,
        'date': invoice_index_data.date,
        'payment_terms': invoice_index_data.payment_terms,
        'attention_to': invoice_index_data.attention_to,
        'narration': invoice_index_data.narration,
        'narration_external': invoice_index_data.narration_external,
    }
    if invoice_index_data:
        invoice_index_data.customer_id = customer_id
        invoice_index_data.date = date
        invoice_index_data.payment_terms = payment_terms
        invoice_index_data.attention_to = attention_to
        invoice_index_data.narration = narration
        invoice_index_data.narration_external = narration_external
        db.session.commit()
        log_string = ""

        if int(invoice_data_old['customer_id']) != int(invoice_index_data.customer_id):
            customer_logs_save(invoice_data_old['customer_id'], "Invoice Moved Out", "Invoice ID: " + str(
                invoice_id) + "\nInvoice was moved out to another customer.\nNew Customer ID: " + str(
                invoice_index_data.customer_id) + "\nNew Customer Name: " + get_customer_name(
                int(invoice_index_data.customer_id)))
            customer_logs_save(int(invoice_index_data.customer_id), "Invoice Moved In", "Invoice ID: " + str(
                invoice_id) + "\nInvoice was moved in from another customer.\nOld Customer ID: " + str(
                invoice_data_old['customer_id']) + "\nOld Customer Name: " + get_customer_name(
                invoice_data_old['customer_id']))
            log_string += "Invoice was moved\nfrom Customer: " + get_customer_name(
                int(invoice_data_old['customer_id'])) + "\nTo Customer: " + get_customer_name(
                int(invoice_index_data.customer_id)) + "\n\n"
        if invoice_data_old['date'] != invoice_index_data.date:
            log_string += "Date changed from " + invoice_data_old[
                'date'] + " to " + invoice_index_data.date + "\n\n"
        if invoice_data_old['payment_terms'] != invoice_index_data.payment_terms:
            log_string += "Payment terms changed from " + invoice_data_old[
                'payment_terms'] + " to " + invoice_index_data.payment_terms + "\n\n"
        if invoice_data_old['attention_to'] != invoice_index_data.attention_to:
            log_string += "Attention changed from " + invoice_data_old[
                'attention_to'] + "to " + invoice_index_data.attention_to + "\n\n"
        if invoice_data_old['narration'] != invoice_index_data.narration:
            log_string += "Internal Narration changed\nfrom " + invoice_data_old[
                'narration'] + "\nto " + invoice_index_data.narration + "\n\n"
        if invoice_data_old['narration_external'] != invoice_index_data.narration_external:
            log_string += "Internal Narration changed\nfrom " + invoice_data_old[
                'narration_external'] + "\nto " + invoice_index_data.narration_external + "\n\n"

        if len(log_string) > 0:
            invoice_logs_save(invoice_id, "Meta Data Changed", log_string)
        update_customer_total(invoice_index_data.customer_id)
        update_customer_total(int(invoice_data_old['customer_id']))
        return jsonify('Done')
    else:
        return jsonify("Error")



@app.route("/invoice_details")
@login_required
def invoice_details():
    sort_string = request_args('sort') if request_args('sort') != None else "invoice_id"
    sort_by = request_args('sort_by') if request_args('sort_by') != None else asc
    customer_id = request_args('customer_id')
    if sort_by == 'desc':
        sort_by = desc
    else:
        sort_by = asc
    if customer_id:
        invoice_index_data = (InvoiceIndex.query.join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey).
                              filter_by(user_group=get_user_group(get_user_name()), primarykey=customer_id).
                              with_entities(
            InvoiceIndex.invoice_id,
            InvoiceIndex.date,
            CustomerDetails.primarykey,
            CustomerDetails.customer_name,
            CustomerDetails.salesman_name,
            InvoiceIndex.user_name,
            InvoiceIndex.invoice_amount,
            InvoiceIndex.payment_terms).distinct().
                              order_by(sort_by(sort_string), InvoiceIndex.invoice_id.desc()).all())
    else:
        invoice_index_data = (
            InvoiceIndex.query.join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey).
            filter_by(user_group=get_user_group(get_user_name())).
            with_entities(
                InvoiceIndex.invoice_id,
                InvoiceIndex.date,
                CustomerDetails.primarykey,
                CustomerDetails.customer_name,
                CustomerDetails.salesman_name,
                InvoiceIndex.user_name,
                InvoiceIndex.invoice_amount,
                InvoiceIndex.payment_terms).distinct().
            order_by(sort_by(sort_string), InvoiceIndex.invoice_id.desc()).all())
    result = []
    user_dict = user_data_dict()
    for row in invoice_index_data:
        if row[5] in user_dict.keys():
            user_name = user_dict[row[5]]
        else:
            user_name = 'N/A'
        result.append({
            'invoice_id': row[0],
            'date': row[1],
            'customer_id': row[2],
            'customer_name': row[3],
            'salesman_name': row[4],
            'user_name': user_name,
            'invoice_amount': row[6],
            "payment_terms": row[7]
        })
    return jsonify(result)


@app.route("/add")
@login_required
def add_item():
    def logger(invoice_id_, code_, description_, size_, packing_, price_, unit_, quantity_, notes_, purchase_price_):
        details = "Code: " + code_ + "\n"
        details += "Description: " + description_ + "\n"
        details += "Size: " + size_ + "\n"
        details += "Packing: " + packing_ + "\n"
        details += "Price: " + price_ + "\n"
        details += "Unit: " + unit_ + "\n"
        details += "Quantity: " + quantity_ + "\n"
        details += "Notes: " + notes_ + "\n"
        details += "Purchase Price: " + purchase_price_ + "\n"
        invoice_logs_save(invoice_id_, "Item Added", details)

    invoice_id = request_args('invoice_id')
    code = splitting_action(request_args('code'))
    description = splitting_action(request_args('description'))
    size = splitting_action(request_args('size'))
    packing = splitting_action(request_args('packing'))
    price = format(float(request_args('price')), ".2f")
    unit = splitting_action(request_args('unit').upper())
    quantity = request_args('quantity')
    purchase_price = request_args('purchase_price')
    try:
        purchase_price = format(float(purchase_price), ".4f")
    except:
        purchase_price = ''
    notes = splitting_action(request_args('notes'))
    total = float(quantity) * float(price)
    total = format(total, ".2f")
    entry_order = InvoiceContent.query.filter_by(invoice_id=invoice_id, ).count() + 1
    valid_entry = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).first()
    if valid_entry:
        logger(invoice_id, code, description, size, packing, price, unit, quantity, notes, purchase_price)
        new_entry = InvoiceContent(invoice_id=invoice_id, entry_order=entry_order, code=code, description=description, size=size, packing=packing, price=price, quantity=quantity, notes=notes, unit=unit, total=total, purchase_price=purchase_price, added_edited_by=get_user_name())
        db.session.add(new_entry)
        db.session.commit()
        update_invoice_amount(invoice_id)
        return jsonify("Done")
    return jsonify("Error")


@app.route("/invoice_data_json/<invoice_id>")
@login_required
def invoice_data_json(invoice_id):
    validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).first()
    if validation_data:
        sort_string = request_args('sort') if request_args('sort') is not None else "entry_number"
        sort_by = request_args('sort_by') if request_args('sort_by') != 'none' else None
        if sort_by == 'desc':
            sort_by = desc
        else:
            sort_by = asc
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
        invoice_content = InvoiceContent.query.filter_by(invoice_id=invoice_id).order_by(sort_by(sort_string)).all()
        result = []
        for row in invoice_content:
            result.append({
                'primarykey': row.primarykey,
                'invoice_id': row.invoice_id,
                'entry_order': row.entry_order,
                'code': row.code,
                'description': row.description,
                'size': row.size,
                'packing': row.packing,
                'price': row.price,
                'quantity': row.quantity,
                'notes': row.notes,
                'unit': row.unit,
                'total': row.total,
                'sp': row.sp,
                'stock': row.stock,
                'purchase_price': row.purchase_price,
                'image_path': row.image_path,
                'added_edited_by': row.added_edited_by
            })
        return jsonify(result)
    else:
        return jsonify("Error")


@app.route("/invoice_logs_json/<invoice_id>")
@login_required
def invoice_logs_json(invoice_id):
    validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).first()
    if validation_data:
        logs_data = LogsInvoice.query.filter_by(invoice_id=invoice_id).all()
        result = []
        user_dict = user_data_dict()
        for row in logs_data:
            result.append({
                'primary_key': row.primary_key,
                'invoice_id': row.invoice_id,
                'type': row.type,
                'user': row.user,
                'user_full_name': user_dict[row.user],
                'details': row.details,
                'date_time': row.date_time,
            })
        return jsonify(result)
    else:
        return jsonify("Error")


@app.route("/customer_logs_json/<customer_id>")
@login_required
def customer_logs_json(customer_id):
    validation_data = CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name()), primarykey=customer_id).first()
    if validation_data:
        logs_data = LogsCustomer.query.filter_by(customer_id=customer_id).all()
        result = []
        user_dict = user_data_dict()
        for row in logs_data:
            result.append({
                'primary_key': row.primary_key,
                'customer_id': row.customer_id,
                'type': row.type,
                'user': row.user,
                'user_full_name': user_dict[row.user],
                'details': row.details,
                'date_time': row.date_time,
            })
        return jsonify(result)
    else:
        return jsonify("Error")


@app.route("/customer_details")
@login_required
def customer_details():
    sort_string = request_args('sort') if request_args('sort') is not None else "customer_name"
    sort_by = request_args('sort_by') if request_args('sort_by') != 'none' else None
    customer_id = request_args('customer_id')
    if sort_by == 'desc':
        sort_by = desc
    else:
        sort_by = asc
    if customer_id:
        customer_data = (CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name()), primarykey=customer_id).order_by(
            sort_by(sort_string)).first())
        if customer_data:
            result = {
                    'primarykey': customer_data.primarykey,
                    'customer_name': customer_data.customer_name,
                    'contact_number': customer_data.contact_number,
                    'total_amount': customer_data.total_amount,
                    'salesman_id': customer_data.salesman_id,
                    'salesman_name': customer_data.salesman_name,
                }
            return jsonify(result)
        else:
            return jsonify("Error")
    customer_data = (CustomerDetails.query.filter_by(user_group=get_user_group(get_user_name())).order_by(sort_by(sort_string)).distinct())
    if customer_data:
        result = []
        for row in customer_data:
            result.append({
                'primarykey': row.primarykey,
                'customer_name': row.customer_name,
                'contact_number': row.contact_number,
                'total_amount': row.total_amount,
                'salesman_id': row.salesman_id,
                'salesman_name': row.salesman_name,
            })
        return jsonify(result)
    else:
        return jsonify("Error")


@app.route("/invoice_index_details")
@login_required
def invoice_index_details():
    invoice_id = request_args('invoice_id')
    user_dictionary = user_data_dict()
    invoice_index_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_id).join(CustomerDetails, InvoiceIndex.customer_id == CustomerDetails.primarykey).with_entities(
        CustomerDetails.primarykey,
        InvoiceIndex.invoice_id,
        CustomerDetails.customer_name,
        CustomerDetails.user_name,
        InvoiceIndex.user_name,
        CustomerDetails.user_group,
        CustomerDetails.contact_number,
        CustomerDetails.total_amount,
        CustomerDetails.salesman_id,
        CustomerDetails.salesman_name,
        InvoiceIndex.date,
        InvoiceIndex.payment_terms,
        InvoiceIndex.attention_to,
        InvoiceIndex.narration,
        InvoiceIndex.narration_external,
        InvoiceIndex.invoice_amount,
    ).first()
    if invoice_index_data:
        if invoice_index_data[4] in user_dictionary.keys():
            invoice_user_full_name = user_dictionary[invoice_index_data[4]]
        else:
            invoice_user_full_name = ''
        result = {
            'customer_id': invoice_index_data[0],
            'invoice_id': invoice_index_data[1],
            'customer_name': invoice_index_data[2],
            'customer_user_name': invoice_index_data[3],
            'invoice_user_name': invoice_index_data[4],
            'invoice_user_full_name':invoice_user_full_name,
            'user_group': invoice_index_data[5],
            'contact_number': invoice_index_data[6],
            'total_amount': invoice_index_data[7],
            'salesman_id': invoice_index_data[8],
            'salesman_name': invoice_index_data[9],
            'date': invoice_index_data[10],
            'payment_terms': invoice_index_data[11],
            'attention_to': invoice_index_data[12],
            'narration': invoice_index_data[13],
            'narration_external': invoice_index_data[14],
            'invoice_amount': invoice_index_data[15],
        }
        return jsonify(result)
    return jsonify("error")



@app.route("/score_submit")
@login_required
def score():
    score = request.args.get('score')
    game = request.args.get('game')
    game_data = GameScore.query.filter_by(user_name=session.get('username'), game=game).first()
    if game_data:
        if int(score) > int(game_data.score):
            game_data.score = score
            db.session.commit()
    else:
        new_entry = GameScore(user_name=session.get('username'), game=game, score=score)
        db.session.add(new_entry)
        db.session.commit()
    return "done"


@app.route("/product_search")
@login_required
def product_search():
    query = request_args('query') if request_args('query') is not None else ""
    sort = request_args('sort') if request_args('query') is not None else ""
    query = splitting_action(code_remove_zero_prefix(query))
    if len(query) > 0:
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
        data = data_raw.all()
        result = []
        for row in data:
            result.append({
                'primarykey': row.primarykey,
                'code_value': row.code_value,
                'description_sheet': row.description_sheet,
                'description_stock': row.description_stock,
                'brand_val': row.brand_val,
                'size_val': row.size_val,
                'packaging_val': row.packaging_val,
                'unit_val': row.unit_val,
                'cash_val': row.cash_val,
                'sale_val': row.sale_val,
                'quantity': row.quantity,
                'image': row.image,
                'tally_rate': row.tally_rate,
            })
        return jsonify(result)
    else:
        return jsonify([])


@app.route("/fetch_product_details")
@login_required
def fetch_product_details():
    product_id = request_args('product_id')
    data = Master.query.filter_by(primarykey=product_id).first()
    if data:
        result = {
            'primarykey': data.primarykey,
            'code_value': data.code_value,
            'description_sheet': data.description_sheet,
            'description_stock': data.description_stock,
            'brand_val': data.brand_val,
            'size_val': data.size_val,
            'packaging_val': data.packaging_val,
            'unit_val': data.unit_val,
            'cash_val': data.cash_val,
            'sale_val': data.sale_val,
            'quantity': data.quantity,
            'image': data.image,
            'tally_rate': data.tally_rate,
        }
        return jsonify(result)
    else:
        return jsonify({})


@app.route("/edit_invoice_content")
@login_required
def edit_invoice_content():
    primary_key = request_args('content_id')
    if primary_key is None:
        return jsonify("Error")

    def log_edit_invoice_content(invoice_id_log, current_data_list, new_data_list):
        headers = ['Entry Order #', 'Code', 'Description', 'Size', 'Packing', 'Price', 'Unit', 'Quantity', 'Purchase Price', 'Notes']
        output_string = ""
        for index in range(len(current_data_list)):
            if str(current_data_list[index]) != str(new_data_list[index]):
                output_string = output_string + headers[index] + " Changed from '" + str(current_data_list[index]) + "' to '" + str(new_data_list[index]) + "'\n"
        if len(output_string) > 0:
            log_string = "Code: " + current_data_list[1] + "\n\n" + output_string
            invoice_logs_save(invoice_id_log, "Item Edited", log_string)

    invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
    validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_content.invoice_id).first()
    if validation_data:
        entry_order = splitting_action(request_args('entry_order'))
        code = splitting_action(request_args('code'))
        description = splitting_action(request_args('description'))
        size = splitting_action(request_args('size'))
        packing = splitting_action(request_args('packing'))
        price = splitting_action(request_args('price'))
        unit = splitting_action(request_args('unit'))
        quantity = splitting_action(request_args('quantity'))
        purchase_price = splitting_action(request_args('purchase_price'))
        try:
            purchase_price = format(float(purchase_price), ".4f")
        except:
            purchase_price = ''
        notes = splitting_action(request_args('notes'))
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
        total = float(request_args('quantity')) * float(request_args('price'))
        invoice_content.total = float("{:.2f}".format(total))
        invoice_content.added_edited_by = get_user_name()
        db.session.commit()
        update_invoice_amount(validation_data.invoice_id)
        return jsonify("Done")
    else:
        return jsonify("Error")


@app.route("/delete_invoice_content")
@login_required
def delete_invoice_content():
    primary_key = request_args('content_id')
    if primary_key is None:
        return jsonify("Error")
    invoice_content = InvoiceContent.query.filter_by(primarykey=primary_key).first()
    invoice_id = str(InvoiceContent.query.filter_by(primarykey=primary_key).first().invoice_id)
    validation_data = InvoiceIndex.query.filter_by(user_group=get_user_group(get_user_name()), invoice_id=invoice_content.invoice_id).first()
    if validation_data:
        customer_name = CustomerDetails.query.filter_by(primarykey=validation_data.customer_id).first().customer_name
        invoice_logs_save(invoice_id, "Item Deleted", "Customer Name: " + str(customer_name) + "\n" +
                            "Invoice ID: " + str(invoice_content.invoice_id) + "\n\n" +
                            "Code: " + invoice_content.code + "\n" +
                            "Description: " + invoice_content.description + "\n" +
                            "Size: " + invoice_content.size + "\n" +
                            "Packing: " + invoice_content.packing + "\n" +
                            "Price: " + invoice_content.price + "\n" +
                            "Unit: " + invoice_content.unit + "\n" +
                            "Quantity: " + invoice_content.quantity + "\n" +
                            "Notes: " + invoice_content.notes + "\n" +
                            "Total: " + invoice_content.total + "\n" +
                            "Stock: " + invoice_content.stock)
        image_path = invoice_content.image_path
        delete_image_function(image_path)
        db.session.query(InvoiceContent).filter_by(primarykey=primary_key).delete()
        db.session.commit()
        update_invoice_amount(invoice_id)
        return jsonify("Done")
    else:
        return jsonify("Error")

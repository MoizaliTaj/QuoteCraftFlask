import string
import random
from application.models import Lastupdated, User, NavBar, InvoiceContent, Master
from application.models import InvoiceIndex, CustomerDetails, SalesmanDetails, LogsInvoice, LogsCustomer, LogsSalesman, LogsUser, LogsLoginLogout
from application.database import db
import hashlib
from flask import render_template, session, request, redirect, make_response, send_file
from functools import wraps
import os
import pandas as pd
from sqlalchemy import or_, desc, asc
from pytz import timezone
from datetime import datetime
from PIL import Image
from flask import current_app as app, jsonify
from application.models import PhoneIndex, PhoneNumber, GameScore
app.secret_key = '4c3680e76fc3c7b14495e39f474667fde0fddccasd1238ba19798e8fffb2b8f9b763241'


def login():
    if request.method == 'GET':
        return security(type="login", title="Login - Generic Product App")
    if request.method == 'POST':
        user_name = request.form["user"].lower()
        password = request.form["password"]
        userinfo = User.query.filter(User.user_name.ilike(user_name)).first()
        if userinfo is not None:
            if (userinfo.user_name.lower() == user_name) and (userinfo.password == hasher(password)) and (userinfo.password_status == 'active'):
                session['username'] = user_name
                login_logout_logs_save("Login")
                return redirect(request.referrer)
            elif (userinfo.user_name.lower() == user_name) and (userinfo.password == hasher(password)) and (userinfo.password_status == 'expired'):
                return security(type="password_expired", title="Change your password - Generic Product App", user_name=user_name)
        return error(title="Login Error - Generic Product App", type="login", redirect_link=request.referrer)


def logout():
    login_logout_logs_save("Logout")
    session.pop('username', None)
    return redirect(request.referrer)


def login_required(f):
    # This is used as a decorator function in controller.
    # It checks if current user is logged in then it lets it continue with the function.
    # If user is not logged in then it redirect to the login function.
    @wraps(f)
    def decorated_function_login(*args, **kwargs):
        if 'username' not in session:
            return login()
        return f(*args, **kwargs)
    return decorated_function_login


def admin_required(f):
    # This is used as a decorator function in controller.
    # It checks if current user is an admin user.
    # If user is not admin then it gives an error.
    @wraps(f)
    def decorated_function_admin(*args, **kwargs):
        if User.query.filter_by(user_name=get_user_name()).first().type.lower() != "admin":
            return error(type="not_admin", title="Error - Generic Product App")
        return f(*args, **kwargs)
    return decorated_function_admin


def navbar():
    # This function checks for the user type. As per user type it provides the list of links available for that user.
    # This data is then used to create links in navigation bar
    user_type = User.query.filter_by(user_name=session.get('username')).with_entities(User.type).first()
    if user_type is None:
        # If a user type is None then it returns an empty list to avoid errors in template.
        return []
    else:
        print(NavBar.query.filter_by(user_type=user_type[0]).with_entities(NavBar.page_name,NavBar.page_address).order_by(NavBar.pk.asc()).all())
        return NavBar.query.filter_by(user_type=user_type[0]).with_entities(NavBar.page_name,NavBar.page_address).order_by(NavBar.pk.asc()).all()


def last_update_date_time():
    # This data will be used in the footer.
    return Lastupdated.query.with_entities(Lastupdated.last).distinct()[0][0]


def random_password_generator(length_of_password):
    # This function generates a random password. This is used in add user and update user functionality.
    characters = string.ascii_letters + string.digits + '!@#$%^&*()_-'
    new_password = ''
    for iteration in range(length_of_password):
        new_password += characters[random.randint(0, len(characters) - 1)]
    return new_password


def request_args(key):
    return request.args.get(key)


def hasher(input_string):
    # This function takes input string and passes it through a hash function.
    # Result of this is used to save password in the database and to validate passwords.
    return hashlib.sha256(input_string.encode()).hexdigest()


def get_user_group(user_name):
    # This function provides the user group for the given user name
    return User.query.filter_by(user_name=user_name).first().user_group.lower()


def get_user_name():
    # returns the current username.
    return session.get('username')



def splitting_action(input_string):
    # This function removes extra spaces from the string and converts the entire string to upper case.
    return " ".join(str(input_string).split()).upper()


def code_remove_zero_prefix(input_string):
    # some product codes that people search have an additional zero. This function is used to rectify such code.
    # For example a product code is G53A but in some places it could be passed as G053A. This function will change it back to G53A
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
    # This function is used in change password option or when user setus new password after account creation or password reset.
    # This function checks if a given password meets the minimum password requirement.
    proposed_password = str(proposed_password)
    if len(proposed_password) < 8:
        return False
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
                os.remove("/home/generic/mysite/static/" + image_path)
            except:
                os.remove("static/" + image_path)
        except:
            print("delete_image_function triggered an error")


def get_current_date_time(print_format=False):
    # Provides current date and time for UAE
    current_data_time = datetime.now(timezone('Asia/Dubai')).strftime('%Y-%m-%d_%H-%M-%S')
    if print_format:
        # This provides details in dd-mm-yyyy hh:mm format
        return current_data_time[8:10] + "-" + current_data_time[5:7] + "-" + current_data_time[0:4] + " " + current_data_time[11:13] + ":" + current_data_time[14:16]
    else:
        # This provides details in yyyy-mm-dd hh:mm:ss format
        return current_data_time[:10] + " " + current_data_time[11:13] + ":" + current_data_time[14:16] + ":" + current_data_time[17:19]


def customer_logs_save(customer_id, type_of_log, details):
    new_entry = LogsCustomer(customer_id=customer_id, type=type_of_log, details=details, user=get_user_name(), date_time=get_current_date_time())
    db.session.add(new_entry)
    db.session.commit()


def invoice_logs_save(invoice_id, type_of_log, details):
    new_entry = LogsInvoice(invoice_id=invoice_id, type=type_of_log, details=details, user=get_user_name(), date_time=get_current_date_time())
    db.session.add(new_entry)
    db.session.commit()


def salesman_logs_save(salesman_id, type_of_log, details):
    new_entry = LogsSalesman(salesman_id=salesman_id, type=type_of_log, details=details, user=get_user_name(), date_time=get_current_date_time())
    db.session.add(new_entry)
    db.session.commit()


def user_logs_save(user_name, type_of_log, details):
    new_entry = LogsUser(user_name=user_name, type=type_of_log, details=details, user=get_user_name(), date_time=get_current_date_time())
    db.session.add(new_entry)
    db.session.commit()


def login_logout_logs_save(type_of_log):
    new_entry = LogsLoginLogout(date_time=get_current_date_time(), user=get_user_name(), ip_address=get_users_ip(), type=type_of_log)
    db.session.add(new_entry)
    db.session.commit()


def update_customer_total(customer_id):
    invoice_data = InvoiceIndex.query.filter_by(customer_id=customer_id).with_entities(InvoiceIndex.invoice_amount).all()
    total_amount = 0.00
    for amount in invoice_data:
        try:
            total_amount = total_amount + float(amount[0])
        except:
            pass
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


def user_data_dict():
    dictionary_object = {}
    user_data = User.query.all()
    for user in user_data:
        dictionary_object[user.user_name] = user.user_full_name
    return dictionary_object


def get_users_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy


def error(**kwargs):
    return render_template("error.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def security(**kwargs):
    return render_template("security.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def admin_(**kwargs):
    return render_template("admin.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def customer_invoice(**kwargs):
    return render_template("customer_invoice.html", navbar=navbar(), last=last_update_date_time(), **kwargs)


def not_found():
    return error(type="404", title="404 Not Found - Generic Product App", )


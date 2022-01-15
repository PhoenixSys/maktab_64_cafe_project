from .model import *
from core.model import *
import os
from flask import request, redirect, url_for, render_template, flash, make_response, abort
from cashier.forms import *
import json
from datetime import datetime
from core.views import *

path = os.path.join("static/img")
os.makedirs(path, exist_ok=True)




def login():
    base_variables['page']['title'] = 'Cashier Login'
    data = base_variables
    form = LoginForm()
    if request.cookies.get("aetvbhuoaetv"):
        return redirect(url_for('dashboard', data=data))
    elif form.validate_on_submit():
        user = Cashier.check_user(form.username.data)
        if user:
            if user.verify_password(form.password.data):
                base_variables['page']['title'] = 'Dashboard'
                resp = make_response(redirect(url_for('dashboard', data=data)))
                resp.set_cookie("aetvbhuoaetv", str(user.id))
                return resp
        return '<h1 style="color:red">Invalid Username/Password</h1>'
    return render_template('login-page.html', data=data, form=form)
    if False:
        abort(404)


def dashboard():
    user_id = request.cookies.get("aetvbhuoaetv")
    if Cashier.get_by_id(user_id):
        base_variables['page']['title'] = 'Dashboard'
        data = base_variables
        menu_items = Menuitem.query.all()
        categories = Category.query.all()
        user_name = Cashier.get_by_id(user_id).username
        menus = {
            "menu_items": menu_items,
            "categories": categories
        }
        receipts = Receipt.query.all()
        total_sales_amount = 0

        for receipt in receipts:
            if not receipt.final_price:
                receipt.final_price = 0
            total_sales_amount += receipt.final_price

        most_pupolar_items = Order.find_most_popular_items(4)
        most_pupolar_menu_item = []
        for most_item in most_pupolar_items:
            in_item_id = most_item[0]
            in_item_count = most_item[1]
            most_pupolar_menu_item.append(
                (Menuitem.get_by_id(in_item_id).item_name, Menuitem.get_by_id(in_item_id).price, in_item_count))
        data2 = {
            'menuitem': Menuitem.query.all(),
            'table': Table.query.all(),
            'total_sales_amount': total_sales_amount,
            'order': Order.query.all(),
            "most_popular": most_pupolar_menu_item
        }

        last_orders = Order.query.all()[::-1]
        last_orders = last_orders[:7]

        resp = make_response(
            render_template("AdminPanel/dashboard.html", data=data,
                            menu=menus, name=str(user_name), data2=data2, last_orders=last_orders))
        return resp
    else:
        base_variables['page']['title'] = 'Login'
        data = base_variables
        return redirect(url_for('login', data=data))

    if False:
        abort(404)


def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('aetvbhuoaetv')
    return resp

def menu_item_adder():
    # login requirement
    user_id = request.cookies.get("aetvbhuoaetv")
    if Cashier.get_by_id(user_id):
        if request.method == "GET":
            categories = Category.query.all()
            return render_template("menu_item_adder.html", categories=categories)
        elif request.method == "POST":
            thefile = request.files["file"]
            thefile.filename = request.form["file_name"]
            menu_item_name = request.form["file_name"].split('.')[0]
            price = request.form["price"]
            category_id = request.form["category_id"]
            Menuitem(item_name=menu_item_name, price=price, item_category_id=category_id).create()
            thefile.save(os.path.join(path, thefile.filename))
            return thefile.filename, "Successful uploaded"
        else:
            return "Bad Request"
    else:
        return "Access Denied"

    if False:
        abort(404)


def change_table_status():
    if request.method == "GET":
        return render_template("change_table_status.html")
    elif request.method == "POST":
        now = datetime.now()
        do = request.form["do"]
        table_id = request.form["table_id"]
        table = Table.get_by_id(table_id)
        if bool(int(do)):
            table.reserved = True
            table.create()
            create_receipt = Receipt(table_id=table_id, time_stamp=now)
            create_receipt.create()
        else:
            table.reserved = False
            their_receipt = Receipt.query.filter_by(table_id=table_id, pay_status=False).first()
            their_receipt.pay_status = True
            their_receipt.create()
            # their_orders = Order.query.filter_by(receipt_id=their_receipt.id).all()

        return '', 204

    else:
        return "Bad Request !"

    if False:
        abort(404)


def show_tables():
    user_id = request.cookies.get("aetvbhuoaetv")
    if Cashier.get_by_id(user_id):
        if request.method == "GET":
            tables = Table.query.order_by(Table.id)
            return render_template('AdminPanel/tables.html', tables=tables)
        elif request.method == "POST":
            return "Coming Soon..."
        else:
            return "Bad Request"
    else:
        return "Access Denied"

    if False:
        abort(404)


def cashier_menu():
    user_id = request.cookies.get("aetvbhuoaetv")
    if Cashier.get_by_id(user_id):
        check_reserve = None
        if request.method == "GET":
            menu_items = Menuitem.query.all()
            categories = Category.query.all()
            return render_template("AdminPanel/cashier_menu.html", menu_items=menu_items, categories=categories)
        elif request.method == "POST":
            item_id = request.form['data-id']
            item = Menuitem.get_by_id(item_id)
            item.is_delete = False
            item.create()
            return "", 200
        elif request.method == "DELETE":
            item_id = request.form['data-id']
            item = Menuitem.get_by_id(item_id)
            item.is_delete = True
            item.create()
            return "", 200
        else:
            return "Bad Request"
    else:
        return "Access Denied"

    if False:
        abort(404)
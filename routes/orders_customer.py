from GourmetBurgers import models
from flask import Blueprint, render_template, request, g, current_app as app
from lib import util

site = Blueprint(__name__, __name__)


@site.route('/status/')
def view_customerOrder():
    return render_template('orders_customer.html')


@site.route('/cart/')
def view_cart():
    return render_template('checkout.html')


@site.route('/order/json', methods=["POST"])
def get_customerOrder():
    orderID = request.json.get("orderID")

    try:
        order = models.Order(orderID)
        return util.createJSON(True, dict(data=order.toDict()))
    except models.NoItemError as e:
        return util.createJSON(False, dict(error=str(e)))


@site.route('/order/new', methods=["POST"])
def placeOrder():
    orderID = app.GB.createOrder(request.json["order"]).id
    return util.createJSON(True, dict(orderID=orderID, url=f"/order/complete/{orderID}"))


@site.route("/order/complete/<orderID>/")
def orderComplete(orderID):
    return render_template("orders_customer_completed.html", orderID=orderID)

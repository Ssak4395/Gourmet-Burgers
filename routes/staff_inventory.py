from lib import util
from flask import Blueprint, render_template, request, redirect, g, current_app as app

site = Blueprint(__name__, __name__)


@site.route('/staff/inventory/')
def view_inventory():
    return render_template('staff_inventory.html', inventory=app.GB.getInventoryMap())


@site.route('/staff/inventory/update', methods=['POST'])
def update_inventory():
    try:
        ingredientID = request.form['id']
        ingredient = app.GB.getIngredient(ingredientID)

        if "update_stock" in request.form:
            newLevel = int(request.form['new_stock'])
            if 0 <= newLevel <= ingredient.quantity_max:
                ingredient.updateStock(int(request.form['new_stock']))
        elif "enable" in request.form and ingredient.quantity is not 0:
            ingredient.available = True
        elif "disable" in request.form:
            ingredient.available = False
    finally:
        return redirect("/staff/inventory/")

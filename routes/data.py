from flask import Blueprint, render_template, g, current_app as app

from lib import util


site = Blueprint(__name__, __name__)

# Get inventory as JSON
@site.route('/data/inventory.json')
def getInventoryJSON():
    inventory = {}

    for item in app.GB.inventory:
        inventory[item.id] = item.toDict()

    return util.createJSON(True, dict(data=inventory))

# Get menu as JSON
@site.route('/data/menu.json')
def getMenuJSON():

    menu = {}

    for item in app.GB.menu:
        menu[item.id] = item.toDict()

    return util.createJSON(True, dict(data=menu))

# Get category name map as JSON
@site.route('/data/categories.json')
def getCategoriesJSON():
    return util.createJSON(True, dict(data=app.GB.categories))

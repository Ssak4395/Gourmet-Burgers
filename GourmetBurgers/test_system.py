import pytest

import os
import sqlite3

from . import GBSystem
from .models.Exceptions import *


@pytest.fixture
def sys():
    with sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/test_db.sqlite3") as _db:
        queries = list(_db.iterdump())
    sys = GBSystem(':memory:')
    for line in queries:
        try:
            sys._db._conn.executescript(line)
        except sqlite3.OperationalError as e:
            pass
    return sys


def test_inventory(sys):
    inventory = list(sys.inventory)
    assert len(inventory) == 5


def test_inventoryMap(sys):
    inventoryMap = sys.getInventoryMap()
    assert len(inventoryMap) == 5

    ids = list(inventoryMap.keys())
    for id in ids:
        assert inventoryMap[id].id == id


def test_getIngredient(sys):
    id = 1

    ingredient = sys.getIngredient(id)
    assert ingredient.id == id


def test_getIngredient_error(sys):
    with pytest.raises(NoItemError) as e:
        sys.getIngredient(None)


def test_updateIngredientAvailability(sys):
    id = 1

    assert sys.getIngredient(id).available == True

    sys.updateIngredientAvailability(id, False)
    assert sys.getIngredient(id).available == False

    sys.updateIngredientAvailability(id, True)
    assert sys.getIngredient(id).available == True


def test_updateIngredientStock(sys):
    id = 1

    assert sys.getIngredient(id).quantity == 1
    assert sys.getIngredient(id).available == True

    sys.updateIngredientStock(id, 25)
    assert sys.getIngredient(id).quantity == 25
    assert sys.getIngredient(id).available == True


def test_updateIngredienStock_zero(sys):
    id = 1

    assert sys.getIngredient(id).quantity == 1
    assert sys.getIngredient(id).available == True

    sys.updateIngredientStock(id, -1)
    assert sys.getIngredient(id).quantity == 0
    assert sys.getIngredient(id).available == False


def test_menu(sys):
    menu = list(sys.menu)
    assert len(menu) == 5


def test_menuMap(sys):
    menuMap = sys.getMenuMap()
    assert len(menuMap) == 5

    ids = list(menuMap.keys())
    for id in ids:
        assert menuMap[id].id == id


def test_getMenuItem(sys):
    id = 1

    menu = sys.getMenuItem(id)
    assert menu.id == id


def test_getMenuItem_error(sys):
    with pytest.raises(NoItemError):
        sys.getMenuItem(None)


def test_updateMenuAvailability(sys):
    id = 3

    assert sys.getMenuItem(id).available == True
    assert sys.getMenuItem(id)._is_available == True

    sys.updateMenuAvailability(id, False)
    assert sys.getMenuItem(id).available == False
    assert sys.getMenuItem(id)._is_available == False

    sys.updateMenuAvailability(id, True)
    assert sys.getMenuItem(id).available == True
    assert sys.getMenuItem(id)._is_available == True


def test_updateMenuAvailability_insufficientIngredients(sys):
    id = 1

    assert sys.getMenuItem(id).available == False
    assert sys.getMenuItem(id)._is_available == True

    sys.updateMenuAvailability(id, False)
    assert sys.getMenuItem(id).available == False
    assert sys.getMenuItem(id)._is_available == False

    sys.updateMenuAvailability(id, True)
    # Availability is still False as the ingredients are insufficient
    assert sys.getMenuItem(id).available == False
    assert sys.getMenuItem(id)._is_available == True


def test_categories(sys):
    categories = list(sys.categories)
    assert len(categories) == 5


def test_orders(sys):
    orders = list(sys.getOrders())
    assert len(orders) == 1

    orders = list(sys.getOrders(False))
    assert len(orders) == 1


def test_orders_all(sys):
    # Includes completed orders
    orders = list(sys.getOrders(True))
    assert len(orders) == 2


def test_getOrder(sys):
    id = 1

    order = sys.getOrder(id)
    assert order.id == id


def test_getOrder_error(sys):
    with pytest.raises(NoItemError):
        sys.getOrder(None)

    with pytest.raises(NoItemError):
        sys.getOrder(999)


def test_updateOrder(sys):
    id = 1

    assert sys.getOrder(id).status == False
    sys.updateOrder(id)
    assert sys.getOrder(id).status == True


def test_updateOrder_no_item(sys):
    with pytest.raises(NoItemError) as e:
        sys.updateOrder(999)

    with pytest.raises(NoItemError) as e:
        sys.updateOrder(None)


def test_createOrder(sys):
    order = sys.createOrder([
        dict(
            id=3,
            qty=1,
        ),
        dict(
            id=5,
            qty=1,
            custom=True,
            items={
                5: 1
            })
    ])
    assert order.id == 3


def test_createOrder_bad_menuID(sys):
    with pytest.raises(NoItemError):
        sys.createOrder([
            dict(
                id=22,
                qty=1,
            )
        ])


def test_createOrder_outOfStock(sys):
    with pytest.raises(OutOfStockError):
        sys.createOrder([
            dict(
                id=1,
                qty=999,
            )
        ])


def test_createOrder_client_error(sys):
    # Empty Order
    with pytest.raises(IntegrityError):
        sys.createOrder(None)

    # Empty Order
    with pytest.raises(IntegrityError):
        sys.createOrder([])

    # Empty custom item list
    with pytest.raises(IntegrityError):
        sys.createOrder([
            dict(
                id=3,
                qty=1,
                custom=True
            )
        ])

    # Custom item usage is zero
    with pytest.raises(IntegrityError):
        sys.createOrder([
            dict(
                id=5,
                qty=1,
                custom=True,
                items={
                        5: 0
                        }
            )
        ])

    # Custom item usage exceeds allowable
    with pytest.raises(IntegrityError):
        sys.createOrder([
            dict(
                id=5,
                qty=1,
                custom=True,
                items={
                        5: 15
                        }
            )
        ])

    # Custom item not in allowable custom list
    with pytest.raises(IntegrityError):
        sys.createOrder([
            dict(
                id=5,
                qty=1,
                custom=True,
                items={
                        1: 1
                        }
            )
        ])


def test_client(sys):
    """ Create first order """
    # Check menu ID 3
    menuItem = list(sys.menu)[3-1]
    assert menuItem.available == True

    # Create the order
    orderData = [dict(id=menuItem.id)]
    order = sys.createOrder(orderData)

    assert order.id == 3
    assert order.price == 3
    assert order.status == False
    order.completeOrder()
    assert order.status == True

    """ Create second order, with extra items """
    # Check menu ID 5
    menuItem = list(sys.menu)[4]
    assert menuItem.available == True

    # Create the order
    orderData = [dict(id=menuItem.id, custom=True, items={5: 10})]
    order = sys.createOrder(orderData)
    assert order.id == 4
    assert order.price == 5 + 5 * 5 # Base price + 5x ID 5
    assert order.status == False
    order.completeOrder()
    assert order.status == True

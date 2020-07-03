import pytest

import os
import sqlite3

from GourmetBurgers import GBSystem


@pytest.fixture
def sys():
    with sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/GourmetBurgers/test_db.sqlite3") as _db:
        queries = list(_db.iterdump())
    sys = GBSystem(':memory:')
    for line in queries:
        try:
            sys._db._conn.executescript(line)
        except sqlite3.OperationalError as e:
            pass
    return sys


""" Client Side """  # User Story One - Browse food items
class Test_US1:
    def test_at_least_one_item_is_disabled(self, sys):
        status = False
        for item in sys.menu:
            if not item.available:
                status = True
        if not status:
            assert False

    def test_items_have_a_price(self, sys):
        for item in sys.menu:
            assert item.price > 0


""" Client Side """  # User Story Two - Add food items
class Test_US2:
    pass


""" Client Side """  # User Story Three - Search food items
class Test_US3:
    def test_search_for_Menu(self, sys):
        menu = sys.menu
        search = list(filter(lambda m: "Menu" in m.name, menu))
        assert len(search) == 5

    def test_search_for_One(self, sys):
        menu = sys.menu
        search = list(filter(lambda m: "One" in m.name, menu))
        assert len(search) == 1

    def test_search_for_Six(self, sys):
        menu = sys.menu
        search = list(filter(lambda m: "Six" in m.name, menu))
        assert len(search) == 0


""" Client Side """  # User Story Four - Customise
class Test_US4:
    def test(self, sys):
        for item in sys.menu:
            if item.can_customise:
                for component in item.components:
                    assert component.price > 0


# User Story Five - Checkout Order
class Test_US5:
    def test(self, sys):
        # Item one: ID 3
        menuItem = list(sys.menu)[3-1]
        assert menuItem.available == True
        _data1 = dict(id=menuItem.id, qty=1)

        # Item two: ID 5, custom
        menuItem = list(sys.menu)[4]
        assert menuItem.available == True
        _data2 = dict(id=menuItem.id, custom=True, items={5: 10})

        # Place the order
        order = sys.createOrder([_data1, _data2])

        assert order.id == 3
        assert order.price == 33
        assert order.status == False

        # Check max item limit
        with pytest.raises(Exception):
            menuItem = list(sys.menu)[4]
            assert menuItem.available == False
            _data3 = dict(id=menuItem.id, custom=True, items={5: 15})
            sys.createOrder([_data3])

# User Story Six - Order Status
class Test_US6:
    def test_order1(self, sys):
        order = sys.getOrder(1)
        assert order.status == False
        assert order.price == 16
        assert len(order.items) == 2

    def test_order2(self, sys):
        order = sys.getOrder(2)
        assert order.status == True
        assert order.price == 1
        assert len(order.items) == 1

    def test_order3__(self, sys):
        Test_US5.test(self, sys)
        order = sys.getOrder(3)

        assert order.id == 3
        assert order.price == 33
        assert order.status == False

    def test_order_error(self, sys):
        with pytest.raises(Exception):
            sys.getOrder(None)

        with pytest.raises(Exception):
            sys.getOrder(999)

# User Story Seven - Manage Order
class Test_US7:
    def test_order1(self, sys):
        order = sys.getOrder(1)
        assert order.status == False
        order.completeOrder()
        assert order.status == True
        # Ensure it is updated in the system, and not just in the data object
        assert sys.getOrder(1).status == True

    def test_order3__(self, sys):
        Test_US5.test(self, sys)
        order = sys.getOrder(3)
        assert order.status == False
        order.completeOrder()
        assert order.status == True
        # Ensure it is updated in the system, and not just in the data object
        assert sys.getOrder(3).status == True


# User Story Eight - Manage Inventory
class Test_US8:
    def test(self, sys):
        inventory = list(sys.inventory)
        assert len(inventory) == 5

        for ingredient in inventory:
            assert ingredient.suffix is not None

    def test_disable_item(self, sys):
        ingredient = sys.getIngredient(1)
        assert ingredient.available == True
        ingredient.available = False
        assert ingredient.available == False
        assert sys.getIngredient(1).available == False

    def test_enable_item(self, sys):
        ingredient = sys.getIngredient(2)
        assert ingredient.available == False
        ingredient.available = True
        assert ingredient.available == True
        assert sys.getIngredient(2).available == True

    def test_update_level_to_disable(self, sys):
        ingredient = sys.getIngredient(5)
        assert ingredient.available == True
        assert ingredient.quantity == 21

        ingredient.updateStock(-21)
        assert ingredient.available == False
        assert ingredient.quantity == 0
        assert sys.getIngredient(5).available == False
        assert sys.getIngredient(5).quantity == 0

    def test_update_level(self, sys):
        ingredient = sys.getIngredient(4)
        assert ingredient.available == False
        assert ingredient.quantity == 0

        ingredient.updateStock(30)
        assert ingredient.available == True
        assert ingredient.quantity == 30
        assert sys.getIngredient(4).available == True
        assert sys.getIngredient(4).quantity == 30

    def test_low_stock(self, sys):
        assert sys.getIngredient(1).checkLowStock() == True
        assert sys.getIngredient(2).checkLowStock() == False
        assert sys.getIngredient(3).checkLowStock() == True
        assert sys.getIngredient(4).checkLowStock() == True
        assert sys.getIngredient(5).checkLowStock() == True

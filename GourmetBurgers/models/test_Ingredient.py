import pytest

import os
import sqlite3
from ..system import GBSystem
from . import *


@pytest.fixture
def sys():
    with sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/../test_db.sqlite3") as _db:
        queries = list(_db.iterdump())
    sys = GBSystem(':memory:')
    for line in queries:
        try:
            sys._db._conn.executescript(line)
        except sqlite3.OperationalError as e:
            pass
    return sys


def test_ingredient_property(sys):
    ingredient = Ingredient(1)
    assert ingredient.name == "InventoryOne"
    assert ingredient.price == 1
    assert ingredient.suffix == "QuantityOne"
    assert ingredient.quantity == 1
    assert ingredient.quantity_max == 30
    assert ingredient.available == True

    ingredient = Ingredient(3)
    assert ingredient.name == "InventoryThree"
    assert ingredient.price == 3
    assert ingredient.suffix == "QuantityThree"
    assert ingredient.quantity == 3
    assert ingredient.quantity_max == 80
    assert ingredient.available == False


def test_no_item(sys):
    with pytest.raises(NoItemError):
        Ingredient(999)

    with pytest.raises(NoItemError):
        Ingredient(None)


def test_updateAvailability(sys):
    assert Ingredient(1).available == True

    Ingredient(1).available = False
    assert Ingredient(1).available == False

    Ingredient(1).available = True
    assert Ingredient(1).available == True


def test_updateStock_decrement(sys):
    assert Ingredient(5).quantity == 21
    assert Ingredient(5).available == True

    Ingredient(5).updateStock(-21)
    assert Ingredient(5).quantity == 0
    assert Ingredient(5).available == False


def test_updateStock_increment(sys):
    assert Ingredient(4).quantity == 0
    assert Ingredient(4).available == False

    Ingredient(4).updateStock(10)
    assert Ingredient(4).quantity == 10
    print(Ingredient(4).available)
    assert Ingredient(4).available == True


def test_updateStock_set(sys):
    assert Ingredient(5).quantity == 21
    assert Ingredient(5).available == True

    Ingredient(5).updateStock(25)
    assert Ingredient(5).quantity == 25
    assert Ingredient(5).available == True


def test_lowStock_normal(sys):
    assert Ingredient(5).checkLowStock() == True
    Ingredient(5).updateStock(40)
    assert Ingredient(5).checkLowStock() == False


def test_lowStock_low(sys):
    assert Ingredient(5).checkLowStock() == True
    Ingredient(5).updateStock(5)
    assert Ingredient(5).checkLowStock() == True

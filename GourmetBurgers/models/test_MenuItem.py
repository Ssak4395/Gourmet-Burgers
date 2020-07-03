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


def test_item(sys):
    a = MenuItem(2)
    b = MenuItem(3)
    c = MenuItem(4)

    assert a.id == 2
    assert a.name == "MenuTwo"
    assert a.description == "MenuTwo"
    assert a.price == 2

    assert b.id == 3
    assert b.name == "MenuThree"
    assert b.description == "MenuThree"
    assert b.price == 3

    assert c.id == 4
    assert c.name == "MenuFour"
    assert c.description == "MenuFour"
    assert c.price == 4


def test_can_customise(sys):
    item_a = MenuItem(1)
    item_b = MenuItem(2)
    item_c = MenuItem(5)

    assert item_a.can_customise == True
    assert item_b.can_customise == False
    assert item_c.can_customise == True


def test_components(sys):
    item_a = MenuItem(1)
    for component in item_a.components:
        assert type(component) is MenuIngredient

    assert item_a.components[0].id == 1


def test_available(sys):
    item_a = MenuItem(1)
    item_b = MenuItem(2)
    item_c = MenuItem(3)
    item_d = MenuItem(4)
    item_e = MenuItem(5)

    # item_a and item_d is available but there are not enough ingredients
    assert item_a.available == False
    assert item_d.available == False


    assert item_b.available == False
    assert item_c.available == True
    assert item_e.available == True


def test_no_item(sys):
    with pytest.raises(NoItemError):
        MenuItem(6)

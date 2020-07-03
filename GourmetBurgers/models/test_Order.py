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


def test_orders_id(sys):
    a = Order(1)
    b = Order(2)

    assert a.id == 1
    assert b.id == 2


def test_orders_date(sys):
    order = Order(1)
    assert order.date.year == 2019
    assert order.date.month == 4
    assert order.date.day == 2
    assert order.date.hour == 21
    assert order.date.minute == 19
    assert order.date.second == 11


def test_orders_status(sys):
    a = Order(1)
    b = Order(2)
    assert a.status == False
    assert b.status == True


def test_orders_price(sys):
    a = Order(1)
    b = Order(2)
    assert a.price == 16
    assert b.price == 1


def test_orders_items(sys):
    order = Order(1)
    assert len(order.items) == 2

    MenuItem_1 = order.items[0]
    assert MenuItem_1.price == 8
    assert MenuItem_1.quantity == 1
    assert MenuItem_1.is_custom == False

    MenuItem_2 = order.items[1]
    assert MenuItem_2.price == 8
    assert MenuItem_2.quantity == 1
    assert MenuItem_2.is_custom == True


def test_complete_order(sys):
    a = Order(1)
    assert a.status == False

    a.completeOrder()
    assert a.status == True


def test_no_order(sys):
    with pytest.raises(NoItemError):
        Order(3)

import pytest
from .Exceptions import NoItemError, OutOfStockError, IntegrityError


def test_no_item():
    with pytest.raises(NoItemError):
        raise NoItemError


def test_out_of_stock():
    with pytest.raises(OutOfStockError):
        raise OutOfStockError


def test_integrity():
    with pytest.raises(IntegrityError):
        raise IntegrityError

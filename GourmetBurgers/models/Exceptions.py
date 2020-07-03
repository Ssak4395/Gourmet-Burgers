class NoItemError(Exception):
    # When an item does not exist
    pass

class OutOfStockError(Exception):
    # When an item is out of stock / unavailable
    pass

class IntegrityError(Exception):
    # When data... doesn't seem right
    # (ie customising a non-customisable menu item)
    pass

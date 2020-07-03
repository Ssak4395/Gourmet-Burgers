from abc import ABC, abstractmethod
from .Exceptions import NoItemError
from ._SQLBase import SQLBase


class IngredientBase(SQLBase, ABC):
    @abstractmethod
    def __init__(self, inventoryID):
        # Fetch data from database
        query = self._db.fetchOne(
            self._SQL.INVENTORY.GET_INVENTORY_ITEM, (inventoryID,))
        if not query:
            raise NoItemError(f"No inventory item with id: {inventoryID}")

        self._id = inventoryID
        self._name, self._suffix, self._price, self._quantity, self._quantity_max = query

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def suffix(self):
        return self._suffix

    @property
    def price(self):
        return self._price

    @property
    def quantity(self):
        return self._quantity

    @property
    def quantity_max(self):
        return self._quantity_max

    # Serialise object into dict
    def toDict(self):
        return dict(
            id=self._id,
            name=self._name,
            suffix=self._suffix,
            price=self._price,
            quantity=self._quantity,
        )


class MenuIngredient(IngredientBase):
    def __init__(self, inventoryID, quantity, quantity_max):
        super().__init__(inventoryID)
        self._quantity = quantity
        self._quantity_max = quantity_max

    def toDict(self):
        resp = super().toDict()
        resp.update(dict(quantity_max=self._quantity_max))
        return resp

class HistoricalIngredient(IngredientBase):
    def __init__(self, inventoryID, quantity):
        super().__init__(inventoryID)
        self._quantity = quantity
        self._quantity_max = None

class Ingredient(IngredientBase):
    def __init__(self, inventoryID):
        super().__init__(inventoryID)

        query = self._db.fetchOne(
            self._SQL.INVENTORY.GET_AVAILABLE, (inventoryID,))
        self._is_available = bool(query[0])

    @property
    def available(self):
        return self._quantity and self._is_available

    @available.setter
    def available(self, state):
        state = bool(state)
        self._is_available = state
        self._db.update(
            self._SQL.INVENTORY.ENABLE_ITEM if state else self._SQL.INVENTORY.DISABLE_ITEM, (self._id,))

    # Update inventory levels
    def updateStock(self, change):
        if change < 0:
            change = abs(change)
            self._quantity -= change
            if self._quantity <= 0:
                self.available = False
            self._db.update(self._SQL.INVENTORY.DECREMENT_INVENTORY, (change, self._id))
        else:
            self._quantity = change
            self.available = change > 0
            self._db.update(self._SQL.INVENTORY.SET_INVENTORY, (change, self._id))

    # Check if there is the available stock is 30% or less than the maximum stock
    def checkLowStock(self):
        return self._quantity / self._quantity_max <= 0.3 if self._quantity_max else False

    def toDict(self):
        resp = super().toDict()

        # Set quantity to 0 if the ingredient is not available
        resp.update(dict(quantity=self._quantity if self._is_available else 0))

        return resp

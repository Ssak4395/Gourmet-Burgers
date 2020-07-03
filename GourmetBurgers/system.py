from . import SQL, models, utils


class GBSystem:
    def __init__(self, db: str = None):
        print("=== Initialising GourmetBurgers System ===")

        # Initialise database
        models._SQLBase.SQLBase._db = self._db = SQL.Database(db)
        models._SQLBase.SQLBase._SQL = self._SQL = SQL
        print(f"Database: {self._db._db_file}")

        # Create SQL tables
        for value in SQL.TableQueries.values():
            self._db.create_table(value)

    """ Ingredients / Inventory """
    # Get all ingredients
    @property
    def inventory(self):
        for inventoryItem in self._db.fetchAll(SQL.INVENTORY.GET_INVENTORY_IDS):
            yield models.Ingredient(inventoryItem[0])

    # Get ingredient dictionary (key: ID)
    def getInventoryMap(self):
        inventory = {}
        for item in self.inventory:
            inventory[item.id] = item
        return inventory

    def getIngredient(self, ingredientID):
        return models.Ingredient(ingredientID)

    def updateIngredientAvailability(self, ingredientID, status):
        self.getIngredient(ingredientID).available = status

    def updateIngredientStock(self, ingredientID, change):
        self.getIngredient(ingredientID).updateStock(change)

    def updateMenuAvailability(self, menuID, status):
        self.getMenuItem(menuID).available = status

    """ Menu """
    # Get all menu items
    @property
    def menu(self):
        for menuItem in self._db.fetchAll(SQL.MENU.GET_MENU_ID):
            yield models.MenuItem(menuItem[0])

    # Get menu dictionary (key: ID)
    def getMenuMap(self):
        menu = {}
        for item in self.menu:
            menu[item.id] = item
        return menu

    def getMenuItem(self, menuID):
        return models.MenuItem(menuID)

    """ Categories """
    # Get category name mapping dictionary
    @property
    def categories(self):
        data = {}

        for categoryRecord in self._db.fetchAll(SQL.MENU.GET_CATEGORY_DATA):
            id, name = categoryRecord
            data[id] = name

        return data

    """ Orders """
    # Get all past orders

    def getOrders(self, fetchAll=False):
        if fetchAll:
            query = self._db.fetchAll(SQL.ORDERS.GET_ALL_ORDERS)
        else:
            query = self._db.fetchAll(SQL.ORDERS.GET_ORDERS)

        for order in query:
            yield models.Order(order[0])

    # Get order by orderID
    def getOrder(self, orderID):
        return models.Order(orderID)

    # Create an order
    def createOrder(self, orderData: list):
        """
        # orderData structure
        [
            {
                id: <id: int>,
                qty: <quantity: int>,
                custom: <isCustom: true/false>
                items: {
                    ingredientID: <quantity: int>
                }
            }
        ]

        """
        if type(orderData) is not list:
            raise models.IntegrityError("Bad input data")

        if len(orderData) == 0:
            raise models.IntegrityError("No order items")

        _inventoryMap = self.getInventoryMap()
        _menuMap = self.getMenuMap()

        prices = []

        """
        VALIDATION
        """

        # Get inventory stock levels
        _inventoryLevels = {}
        for ingredient in _inventoryMap.values():
            _inventoryLevels[ingredient.id] = ingredient.quantity

        # Validate each food item
        for foodItem in orderData:
            menuID = int(foodItem["id"])

            quantity = int(foodItem.get("qty", 1))
            custom = bool(foodItem.get("custom", 0))

            ingredients = foodItem.get("items", {})
            # Convert key from str to int
            ingredients = dict([(int(key), val)
                                for key, val in ingredients.items()])

            # Check that menuID exists
            if int(menuID) not in _menuMap:
                raise models.NoItemError(menuID)

            # Check that the item is available
            if not _menuMap[menuID].available:
                raise models.OutOfStockError(menuID)

            defaultIngredients = _menuMap[menuID].getComponentUsage()

            price = _menuMap[menuID].price

            # Check validity for custom items
            if custom:
                # Check if it is customisable
                if not self._db.fetchOne(SQL.MENU.CAN_CUSTOMISE, (menuID,)):
                    raise models.IntegrityError(
                        f"Menu item {menuID} not customisable")

                # Check that there are ingredients
                if len(ingredients) == 0 or sum(list(ingredients.values())) == 0:
                    raise models.IntegrityError(
                        "No ingredients in custom order item")

                # Check that the quantities of each ingredient do not exceed their maximum allowable quantity
                """ Translate array into ID dict """
                maxQuantities = {}
                for ingredient in _menuMap[menuID].components:
                    maxQuantities[ingredient.id] = ingredient.quantity_max

                # Calculate menu delta
                delta = {}

                for id in ingredients.keys():
                    if id not in defaultIngredients:
                        raise models.IntegrityError(
                            f"Ingredient {id} is not part of menu item {menuID}")

                    if ingredients[id] > maxQuantities[id]:
                        raise models.IntegrityError(
                            f"Ingredient limit exceeded {ingredients[id]} > {maxQuantities[id]} for ingredient {id} of menu {menuID}"
                        )

                for id, qty in defaultIngredients.items():
                    delta[id] = ingredients.get(id, 0) - qty

                for id, qty in delta.items():
                    # Only consider additional items
                    if qty > 0:
                        price += models.Ingredient(id).price * qty
            else:
                ingredients = defaultIngredients

            # Check that each ingredient exists, and has enough stock
            for ingredientID in ingredients:
                # Check if it exists
                if int(ingredientID) not in _inventoryLevels:
                    raise models.NoItemError(ingredientID)

                # Check there is enough stock for all orders
                ingredientID = int(ingredientID)
                _inventoryLevels[ingredientID] -= ingredients[ingredientID] * quantity

                if _inventoryLevels[int(ingredientID)] < 0:
                    raise models.OutOfStockError(
                        f"Not enough stock for ingredient {ingredientID}")

            prices.append(price)

        """
        TRANSACTION
        """

        # Get timestamp (epoch)
        ts = utils.getTime()

        # Create SQL rows
        orderID = self._db.insert(SQL.ORDERS.CREATE_ORDER, (ts,))
        for foodItem in orderData:
            menuID = int(foodItem["id"])
            quantity = int(foodItem.get("qty", 1))

            custom = bool(foodItem.get("custom", 0))
            ingredients = foodItem.get(
                "items", {}) if custom else _menuMap[menuID].getComponentUsage()

            # Decrease inventory stock
            for ingredientID, qty in ingredients.items():
                if qty > 0:
                    _inventoryMap[int(ingredientID)
                                  ].updateStock(-1 * quantity * qty)

            # Create custom order data
            if custom:
                customID = self._db.insert(
                    SQL.ORDERS.CREATE_CUSTOM_MAIN, (menuID,))
                for ingredientID in ingredients:
                    self._db.insert(SQL.ORDERS.CREATE_LINK_CUSTOM_MAINS,
                                    (customID, ingredientID, ingredients[ingredientID]))
                self._db.insert(SQL.ORDERS.CREATE_LINK_ORDER__CUSTOM,
                                (orderID, customID, quantity, prices[0]))
            else:
                self._db.insert(SQL.ORDERS.CREATE_LINK_ORDER,
                                (orderID, menuID, quantity, prices[0]))

            del prices[0]

        return models.Order(orderID)

        """
        CREATE_ORDER
        for each item:
            if custom:
                CREATE_CUSTOM_MAIN
                for each ingredient:
                    CREATE_LINK_CUSTOM_ORDERS
                CREATE_LINK_ORDER__CUSTOM
            else:
                CREATE_LINK_ORDER
        """

    # Complete an order
    def updateOrder(self, orderID):
        self.getOrder(orderID).completeOrder()

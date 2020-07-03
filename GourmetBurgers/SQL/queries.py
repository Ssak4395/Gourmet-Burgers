class ORDERS:
    # Get orders in the queue
    GET_ORDERS = "SELECT orderID FROM orders WHERE status = 0"

    # Get all orders
    GET_ALL_ORDERS = "SELECT orderID FROM orders"

    # Get order by ID
    GET_ORDER = "SELECT date, status FROM orders WHERE orderID = ?"

    """
    # TODO: Remove in production
    """
    # Get order price
    ORDER_TOTAL = "SELECT SUM (price * quantity) FROM link_orders WHERE orderID = ?"

    # Get items of order
    ORDER_ITEMS = "SELECT is_custom, customID, menuID, quantity, price FROM link_orders WHERE orderID = ?"

    # Set an order as completed
    COMPLETE_ORDER = "UPDATE orders SET status = 1 WHERE orderID = ?"

    # Place an order
    CREATE_ORDER = "INSERT INTO orders (date, status) VALUES (?, 0)"
    CREATE_CUSTOM_MAIN = "INSERT INTO custom_mains (mainID) VALUES (?)"
    CREATE_LINK_CUSTOM_MAINS = "INSERT INTO link_custom_mains (customID, inventoryID, quantity) VALUES (?, ?, ?)"
    CREATE_LINK_ORDER__CUSTOM = "INSERT INTO link_orders (orderID, is_custom, customID, quantity, price) VALUES (?, 1, ?, ?, ?)"
    CREATE_LINK_ORDER = "INSERT INTO link_orders (orderID, is_custom, menuID, quantity, price) VALUES (?, 0, ?, ?, ?)"

    # Get the ingredients of a custom order
    GET_CUSTOM_COMPONENTS = "SELECT inventoryID, quantity FROM link_custom_mains WHERE customID = ?"


class MENU:
    GET_MENU_ID = "SELECT menuID FROM menu"

    GET_MENU_ITEM = "SELECT name, price, can_customise, is_available, description FROM menu WHERE menuID = ?"
    GET_MENU_ITEM_BASE = "SELECT name, price FROM menu WHERE menuID = ?"
    GET_MENU_ITEM_OPTIONS = "SELECT can_customise, is_available, description FROM menu WHERE menuID = ?"

    CAN_CUSTOMISE = "SELECT 1 FROM menu WHERE menuID = ? AND can_customise = 1"

    # Toggle availability
    DISABLE_ITEM = "UPDATE menu SET is_available = 0 WHERE menuID = ?"
    ENABLE_ITEM = "UPDATE menu SET is_available = 1 WHERE menuID = ?"

    # Get menuID of a custom meal
    RESOLVE_CUSTOM_TO_MENU = "SELECT menuID, name, price FROM menu, custom_mains WHERE customID = ? AND mainID = menuID"

    # Get components (and possible components) of a menu item
    GET_MAIN_COMPONENTS = "SELECT inventoryID, quantity, max FROM link_menu WHERE menuID = ?"

    # Category information
    GET_CATEGORY_DATA = "SELECT categoryID, name from categories"
    GET_CATEGORIES = "SELECT categoryID, level FROM link_categories WHERE menuID = ?"


class INVENTORY:
    GET_INVENTORY = "SELECT inventoryID, name, suffix, price, quantity, stock_max FROM inventory, quantity_types WHERE inventory.quantity_type = quantity_types.quantityID"
    GET_INVENTORY_IDS = "SELECT inventoryID FROM inventory"
    GET_INVENTORY_ITEM = "SELECT name, suffix, price, quantity, stock_max FROM inventory, quantity_types WHERE inventory.quantity_type = quantity_types.quantityID AND inventory.inventoryID = ?"

    # Update quantity
    DECREMENT_INVENTORY = "UPDATE inventory SET quantity = quantity - ? WHERE inventoryID = ?"
    SET_INVENTORY = "UPDATE inventory SET quantity = ? WHERE inventoryID = ?"

    # Toggle availability
    DISABLE_ITEM = "UPDATE inventory SET is_available = 0 WHERE inventoryID = ?"
    ENABLE_ITEM = "UPDATE inventory SET is_available = 1 WHERE inventoryID = ?"

    GET_AVAILABLE = "SELECT is_available FROM inventory WHERE inventoryID = ?"

data = dict(
  orders = """
  CREATE TABLE IF NOT EXISTS orders (
    orderID INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATETIME NOT NULL,
    status INTEGER NOT NULL
  );""",
  
  link_orders = """
  CREATE TABLE IF NOT EXISTS link_orders (
    orderID INTEGER NOT NULL,
    is_custom BOOLEAN NOT NULL CHECK (is_custom IN (0,1)),
    customID INTEGER,
    menuID INTEGER,
    quantity INTEGER NOT NULL,
    price INTEGER NOT NULL,
    
    FOREIGN KEY (orderID) REFERENCES orders (orderID),
    FOREIGN KEY (customID) REFERENCES custom_mains (customID),
    FOREIGN KEY (menuID) REFERENCES menu (menuID)
  );""", 
  # customID INTEGER CHECK ((is_custom = 0) or (is_custom = 1 and not customID = '')),
  # menuID INTEGER CHECK ((is_custom = 1) or (is_custom = 0 and not menuID = '')),

  # We have this table rather than just linking from `link_orders` to conform to PK FK pairing
  custom_mains = """
  CREATE TABLE IF NOT EXISTS custom_mains (
    customID INTEGER PRIMARY KEY AUTOINCREMENT,
    mainID INTEGER NOT NULL,
    
    FOREIGN KEY (mainID) REFERENCES menu (menuID)
  );""", 

  link_custom_mains = """
  CREATE TABLE IF NOT EXISTS link_custom_mains (
    customID INTEGER NOT NULL,
    inventoryID INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    
    FOREIGN KEY (customID) REFERENCES custom_mains (customID),
    FOREIGN KEY (inventoryID) REFERENCES inventory (inventoryID)
  );""", 

  menu = """
  CREATE TABLE IF NOT EXISTS menu (
    menuID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    can_customise BOOLEAN NOT NULL CHECK (can_customise IN (0,1)),
    is_available BOOLEAN NOT NULL CHECK (is_available IN (0,1))
  );""", 

  link_menu = """
  CREATE TABLE IF NOT EXISTS link_menu (
    menuID INTEGER NOT NULL,
    inventoryID INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    max INTEGER NOT NULL,
    
    FOREIGN KEY (menuID) REFERENCES menu (menuID),
    FOREIGN KEY (inventoryID) REFERENCES inventory (inventoryID)
  );""", 

  categories = """
  CREATE TABLE IF NOT EXISTS categories (
    categoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
  );""", 

  link_categories = """
  CREATE TABLE IF NOT EXISTS link_categories (
    menuID INTEGER NOT NULL,
    categoryID INTEGER NOT NULL,
    level INTEGER NOT NULL,
    
    FOREIGN KEY (menuID) REFERENCES menu (menuID),
    FOREIGN KEY (categoryID) REFERENCES categories (categoryID)
  );""", 

  quantity_types = """
  CREATE TABLE IF NOT EXISTS quantity_types (
    quantityID INTEGER PRIMARY KEY AUTOINCREMENT,
    suffix TEXT NOT NULL
  );""", 

  inventory = """
  CREATE TABLE IF NOT EXISTS inventory (
    inventoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER,
    quantity_type INTGEGER NOT NULL,
    quantity INTEGER NOT NULL,
    stock_max INTEGER NOT NULL,
    is_available BOOLEAN NOT NULL CHECK (is_available IN (0,1)),
    
    FOREIGN KEY (quantity_type) REFERENCES inventory (inventoryID)
  );"""  
)
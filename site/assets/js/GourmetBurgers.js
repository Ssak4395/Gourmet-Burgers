/*
  GourmetBurgers system object
*/

let GourmetBurgers;
(async () => {
  // JSON Fetch Promise
  const fetchGET = async url =>
    fetch(url)
      .then(resp => resp.json())
      .then(res => {
        if (res.status) return res.data;
      });

  // Self-reference
  let self;

  GourmetBurgers = {
    // Get system data
    _menu: await fetchGET("/data/menu.json"),
    _categories: await fetchGET("/data/categories.json"),
    _inventory: await fetchGET("/data/inventory.json"),

    // Promise: Get the order data for `orderID`
    // Returns a `dict` if the order exists, otherwise _null_
    getOrder: async orderID =>
      fetch("/order/json", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ orderID: orderID })
      })
        .then(resp => resp.json())
        .then(json => (json.status ? json.data : null)),

    // Calculate order total
    cart: {
      calculate: () => {
        let sum = 0;

        for (let item of self.cart._data) {
          sum += self.cart._calculate(item) * item.qty;
        }

        return sum;
      },

      // Calculate the price of an individual order item
      // Does not account for quantity
      _calculate: item => {
        let price = self._menu[item.id].price;

        // If the item is not a custom item, then return the base price
        if (!item.custom) {
          return price;
        }

        // Structure check
        if (typeof item.items !== "object") throw Error("Bad item.items");

        // For custom items, calculate the ingredient delta
        let delta = {};
        let defaults = Object.values(self._menu[item.id].components);
        for (let ingredient of defaults) {
          delta[ingredient.id] =
            (item.items[ingredient.id] || 0) - ingredient.quantity;
        }

        // For added ingredients, add the price of each ingredient
        for (let id in delta) {
          if (delta[id] > 0) {
            price += self._inventory[id].price * delta[id];
          }
        }
        return price;
      },

      // Submit order
      submitOrder: async () => {
        return fetch("/order/new", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            order: self.cart._data
          })
        })
          .then(resp => resp.json())
          .then(json => {
            if (json.status) {
              self.cart._data = [];
              self.cart._updateOrder();
              return json;
            } else {
              return false;
            }
          });
      },

      // Add `id` into the order
      // If `data` is present, the order is a custom order
      addToOrder: function(id, data) {
        self.cart.__addToOrder(id, data);
        self.cart._updateOrder();
      },

      __addToOrder: function(id, data) {
        // Validate `id` and `data`
        if (!(id in self._menu)) throw Error(`Invalid id ${id}`);
        if (data && !self._menu[id].can_customise)
          throw Error(`Cannot customise id ${id}`);

        // Check if there are enough ingredients
        let componentUsage = {};

        // Calculate component usage of current items
        for (let orderItem of self.cart._data) {
          if (orderItem.custom) {
            components = orderItem.items;
          } else {
            components = {};
            for (let component of Object.values(
              self._menu[orderItem.id].components
            )) {
              components[component.id] = component.quantity;
            }
          }
          for (let componentID in components) {
            componentUsage[componentID] =
              ((componentUsage[componentID] || 0) + components[componentID]) *
              orderItem.qty;
          }
        }

        // Add the component usage for the current item
        if (data) {
          components = data;
        } else {
          components = {};
          for (let component of Object.values(self._menu[id].components)) {
            components[component.id] = component.quantity;
          }
        }

        for (let componentID in components) {
          componentUsage[componentID] =
            (componentUsage[componentID] || 0) + components[componentID];
        }

        // Check that there is enough stock for the component usage
        for (let componentID in componentUsage) {
          if (!(componentID in self._inventory)) {
            throw Error(`No ingredient ${componentID} found`);
          }
          if (
            self._inventory[componentID].quantity < componentUsage[componentID]
          ) {
            throw Error(
              "Your order uses too many ingredients which we don't have enough of :'("
            );
          }
        }

        // Check if the menu item has been added before, if so increase the quantity
        for (let item of self.cart._data) {
          if (item.id !== id) continue;
          if (data && !item.custom) continue;
          if (data && item.items.toSource() != data.toSource()) continue;

          item.qty += 1;
          return;
        }

        // New menu item into the order
        let orderEntry = {
          id: id,
          qty: 1
        };

        // Check if custom
        if (data) {
          orderEntry.custom = true;
          orderEntry.items = data;
        }

        // Add to order
        self.cart._data.push(orderEntry);
      },

      // On init, load localStorage into _data
      _data: (() => {
        try {
          return JSON.parse(localStorage.getItem("_gbOrder")) || [];
        } catch {
          return [];
        }
      })(),

      // Store _data into localStorage
      _updateOrder: function() {
        localStorage.setItem("_gbOrder", JSON.stringify(this._data));
      }
    }
  };

  // Reference
  self = GourmetBurgers;

  // Execute callback when the system loads
  typeof ready === "function" && ready();
})();

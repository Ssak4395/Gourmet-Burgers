const checkOrder = function(orderID) {
  GourmetBurgers.getOrder(orderID).then(orderData => {
    document.getElementById("error").innerText = orderData
      ? ""
      : "No such order";

    document
      .querySelector("section[name=status]")
      .classList.toggle("active", true);

    if (orderData) {
      let itemsContainer = document.querySelector("div[name=items]");
      itemsContainer.innerHTML = "";

      document.querySelector("span[name=orderID]").innerText = orderData.id;
      document.querySelector("span[name=time]").innerText = new Date(
        orderData.date * 1000
      ).toLocaleString();
      document.querySelector("span[name=status]").innerText = orderData.status
        ? "Ready for Pickup"
        : "Preparing";
      for (let elem of document.querySelectorAll("span[name=total]")) {
        elem.innerText = priceToDecimal(orderData.price);
      }

      for (let item of orderData.items) {
        let elem = document.createElement("div");
        elem.classList.add("orderItem");
        let qtyElem = document.createElement("div");
        qtyElem.innerText = item.quantity;
        elem.appendChild(qtyElem);

        let dataElem = document.createElement("div");
        let dataElem_name = document.createElement("span");
        dataElem_name.innerText = item.name;
        dataElem.appendChild(dataElem_name);

        if (item.custom) {
          elem.classList.add("custom");

          let dataElem_cust = document.createElement("span");
          let builder = [];
          for (let ingredientID in item.components) {
            if (!(ingredientID in GourmetBurgers._inventory)) continue;
            let quantity = item.components[ingredientID];
            if (quantity == 0) continue;
            let ingredient = GourmetBurgers._inventory[ingredientID];
            builder.push(`${quantity}${ingredient.suffix} ${ingredient.name}`);
          }
          dataElem_cust.innerHTML = builder.join("<br>");
          dataElem.appendChild(dataElem_cust);
        }

        elem.appendChild(dataElem);

        let priceElem = document.createElement("div");
        priceElem.innerText = priceToDecimal(item.quantity * item.price);
        elem.appendChild(priceElem);

        itemsContainer.appendChild(elem);
      }
    }
  });
};

document.querySelector("form").addEventListener("submit", evt => {
  evt.preventDefault();
  let orderID = evt.target.orderID.value.trim();

  location.hash = "";
  location.hash = orderID;
});

window.addEventListener("hashchange", evt => {
  let orderID = evt.newURL.split("#", 2)[1].trim();
  if (!orderID) return;

  document.querySelector("form").orderID.value = orderID;
  checkOrder(orderID);
});

function ready() {
  if (location.hash) {
    let orderID = location.hash.substr(1);
    document.querySelector("form").orderID.value = orderID;
    checkOrder(orderID);
  }

  updateTotal();
}

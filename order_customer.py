from typing import List, Any
from menu_items import MenuItem
from billing import Bill
from patterns import OrderObserver


class Order:
    def __init__(self, customer: "Customer"):
        self.order_id = str(id(self))
        self.customer = customer
        self.items: List[MenuItem] = []
        self.status = "New"
        self.totalCost = 0.0
        self._observers: List[OrderObserver] = []

    def add_observer(self, observer: OrderObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: OrderObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event: str, data: Any = None) -> None:
        for obs in self._observers:
            obs.update(event, self, data)

    def addItem(self, item: MenuItem):
        self.items.append(item)
        self._notify("ITEM_ADDED", {"item": item.name, "price": item.price})

    def removeOne(self, item: MenuItem) -> bool:
        try:
            self.items.remove(item)
            self._notify("ITEM_REMOVED", {"item": item.name})
            return True
        except ValueError:
            return False

    def clear(self):
        self.items.clear()
        self._notify("ORDER_CLEARED")

    def calculateTotal(self):
        self.totalCost = sum(item.getPrice() for item in self.items)
        self._notify("TOTAL_CALCULATED", {"total": self.totalCost})
        return self.totalCost

    def generateBill(self, tax_rate: float = 0.20):
        total = self.calculateTotal()
        tax = total * tax_rate
        bill = Bill(self.order_id, self.customer.name, total, tax)
        self._notify("BILL_GENERATED", {"total": total, "tax": tax})
        return bill

    def updateStatus(self, new_status: str):
        old = self.status
        self.status = new_status
        self._notify("STATUS_CHANGED", {"from": old, "to": new_status})


class Customer:
    def __init__(self, customer_id: str, name: str, contact: str, email: str):
        self.customer_id = customer_id
        self.name = name
        self.contact = contact
        self.email = email
        self.orderHistory: List[Order] = []

    def viewOrderHistory(self):
        return [order.order_id for order in self.orderHistory]

    def placeOrder(self, order: Order):
        self.orderHistory.append(order)
        order._notify("ORDER_PLACED", {"customer": self.name})
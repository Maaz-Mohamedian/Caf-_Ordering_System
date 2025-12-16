import re
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Protocol, Any


# =========================
# Core domain classes
# =========================

class MenuItem:
    def __init__(self, category: str, name: str, price: float, description: str):
        self.category = category
        self.name = name
        self.price = price
        self.description = description

    def getPrice(self) -> float:
        return self.price

    def getDescription(self) -> str:
        return self.description

    def displayMenuItem(self):
        return f"{self.name} ({self.category}): {self.description} - ${self.price:.2f}"


class FoodItem(MenuItem):
    def __init__(self, name: str, price: float, description: str, allergens: List[str], is_vegetarian: bool):
        super().__init__("Food", name, price, description)
        self.allergens = allergens
        self.is_vegetarian = is_vegetarian

    def getDetails(self):
        allergens = ", ".join(self.allergens) if self.allergens else "None"
        return f"{self.name} - Vegetarian: {self.is_vegetarian}, Allergens: {allergens}"


class DrinkItem(MenuItem):
    def __init__(self, name: str, price: float, description: str, is_cold: bool, is_hot: bool, size: str):
        super().__init__("Drink", name, price, description)
        self.isCold = is_cold
        self.isHot = is_hot
        self.size = size

    def getDetails(self):
        return f"{self.name} - Size: {self.size}, Cold: {self.isCold}, Hot: {self.isHot}"


class ComboItem(MenuItem):
    def __init__(self, name: str, price: float, description: str, items: List[MenuItem]):
        super().__init__("Combo", name, price, description)
        self.items = items

    def getDetails(self):
        item_details = [item.getDescription() for item in self.items]
        return f"{self.name} - Combo includes: {', '.join(item_details)}"


class Delivery:
    """
    Coming Soon: Delivery functionality is not implemented yet.
    """
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("Delivery feature is coming soon.")

    @staticmethod
    def getDeliveryDetails():
        raise NotImplementedError("Delivery feature is coming soon.")


class Bill:
    def __init__(self, order_id: str, name: str, totalAmount: float, taxAmount: float):
        self.order_id = order_id
        self.name = name
        self.totalAmount = totalAmount
        self.taxAmount = taxAmount
        self.finalAmount = totalAmount + taxAmount
        self.discount = 0.0
        self.tip = 0.0

    def applyDiscount(self, discount: float):
        self.discount = max(0.0, float(discount))
        self.finalAmount -= self.discount

    def addTip(self, tip: float):
        self.tip = max(0.0, float(tip))
        self.finalAmount += self.tip

    def generateBillDetails(self):
        bill_details = f"--- Bill for Order {self.order_id} ---\n"
        bill_details += f"Customer: {self.name}\n"
        bill_details += f"Total Amount: ${self.totalAmount:.2f}\n"
        bill_details += f"Tax: ${self.taxAmount:.2f}\n"
        bill_details += f"Discount: ${self.discount:.2f}\n"
        bill_details += f"Tip: ${self.tip:.2f}\n"
        bill_details += f"Final Amount: ${self.finalAmount:.2f}\n"
        return bill_details


class ValidationHelper:
    @staticmethod
    def validateMenuItem(item: MenuItem):
        if not isinstance(item, MenuItem):
            raise ValueError(f"Invalid Menu Item: {item}")

    @staticmethod
    def validateOrder(order: 'Order'):
        if not order.items:
            raise ValueError("Order cannot be empty.")

    @staticmethod
    def validateNonEmptyString(value: str, field_name: str):
        if not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")


# =========================
# DESIGN PATTERN 1: FACTORY
# =========================

class MenuItemFactory:
    @staticmethod
    def create_item(category: str, **kwargs) -> MenuItem:
        cat = category.strip().lower()

        if cat == "food":
            return FoodItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                allergens=kwargs.get("allergens", []),
                is_vegetarian=bool(kwargs.get("is_vegetarian", False)),
            )

        if cat == "drink":
            return DrinkItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                is_cold=bool(kwargs.get("is_cold", True)),
                is_hot=bool(kwargs.get("is_hot", False)),
                size=kwargs.get("size", "Standard"),
            )

        if cat == "combo":
            return ComboItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                items=kwargs.get("items", []),
            )

        raise ValueError(f"Unknown menu category: {category}")


# =========================
# DESIGN PATTERN 2: OBSERVER
# =========================

class OrderObserver(Protocol):
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        ...


class OrderAuditLogger:
    """Concrete Observer: logs order events (system notification)."""
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        print(f"[ORDER EVENT] {event} | OrderID={order.order_id} | Status={order.status} | Data={data}")


class TkStatusObserver:
    """
    Concrete Observer (GUI): updates a Tkinter StringVar whenever the Order changes.
    This visually demonstrates the Observer pattern in the UI.
    """
    def __init__(self, root: tk.Tk, status_var: tk.StringVar):
        self.root = root
        self.status_var = status_var

    def update(self, event: str, order: "Order", data: Any = None) -> None:
        msg = f"{event} | Status={order.status}"
        if isinstance(data, dict):
            if "item" in data:
                msg += f" | Item={data['item']}"
            if "total" in data:
                msg += f" | Total=${float(data['total']):.2f}"
        self.root.after(0, lambda: self.status_var.set(msg))


class Order:
    def __init__(self, customer: 'Customer'):
        self.order_id = str(id(self))
        self.customer = customer
        self.items: List[MenuItem] = []
        self.status = "New"
        self.totalCost = 0.0

        # Observer list
        self._observers: List[OrderObserver] = []

    # ---- Observer methods ----
    def add_observer(self, observer: OrderObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: OrderObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event: str, data: Any = None) -> None:
        for obs in self._observers:
            obs.update(event, self, data)

    # ---- Business methods ----
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


# =========================
# Tkinter GUI
# =========================

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def build_sample_menu() -> List[MenuItem]:
    # Using FACTORY PATTERN here
    return [
        MenuItemFactory.create_item(
            "food", name="Pizza", price=12.50, description="Cheese pizza",
            allergens=[], is_vegetarian=True
        ),
        MenuItemFactory.create_item(
            "food", name="Chicken Burger", price=8.99, description="Grilled chicken burger",
            allergens=["gluten"], is_vegetarian=False
        ),
        MenuItemFactory.create_item(
            "food", name="Chips", price=3.50, description="Crispy fries",
            allergens=[], is_vegetarian=True
        ),
        MenuItemFactory.create_item(
            "drink", name="Coke", price=2.00, description="Soda drink",
            is_cold=True, is_hot=False, size="500ml"
        ),
        MenuItemFactory.create_item(
            "drink", name="Latte", price=3.20, description="Coffee with milk",
            is_cold=False, is_hot=True, size="12oz"
        ),
    ]


class CafeApp(tk.Tk):
    TAX_RATE = 0.20

    def __init__(self):
        super().__init__()
        self.title("Maaz Cafe Ordering System")
        self.geometry("980x640")
        self.minsize(940, 600)

        self.menu_items = build_sample_menu()
        self.customer: Customer | None = None
        self.order: Order | None = None
        self.current_bill: Bill | None = None

        # GUI observer status var (created early so observers can use it)
        self.ui_status_var = tk.StringVar(value="Observer: waiting for order events...")

        self._build_ui()

    def _build_ui(self):
        title = ttk.Label(self, text="Maaz Cafe Ordering System", font=("Segoe UI", 18, "bold"))
        title.pack(pady=10)

        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=2)
        container.columnconfigure(2, weight=2)
        container.rowconfigure(0, weight=1)

        self._build_customer_panel(container)
        self._build_menu_panel(container)
        self._build_cart_panel(container)

        bottom = ttk.Frame(self, padding=(10, 0, 10, 10))
        bottom.pack(fill="x")
        self._build_bill_panel(bottom)

    def _build_customer_panel(self, parent: ttk.Frame):
        frame = ttk.LabelFrame(parent, text="Customer Details", padding=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Contact (11 digits):").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="Email:").grid(row=4, column=0, sticky="w")

        self.name_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.email_var = tk.StringVar()

        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.contact_var).grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.email_var).grid(row=5, column=0, sticky="ew", pady=(0, 8))

        btns = ttk.Frame(frame)
        btns.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)

        ttk.Button(btns, text="Create / Update Customer", command=self.create_customer).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(btns, text="Delivery (Coming Soon)", command=self.delivery_coming_soon).grid(
            row=0, column=1, sticky="ew", padx=(5, 0)
        )

        frame.columnconfigure(0, weight=1)

    def _build_menu_panel(self, parent: ttk.Frame):
        frame = ttk.LabelFrame(parent, text="Menu", padding=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10))

        cols = ("Category", "Name", "Price", "Description")
        self.menu_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        for c in cols:
            self.menu_tree.heading(c, text=c)
            self.menu_tree.column(c, width=120 if c != "Description" else 240, anchor="w")
        self.menu_tree.pack(fill="both", expand=True)

        for idx, item in enumerate(self.menu_items):
            self.menu_tree.insert(
                "", "end", iid=str(idx),
                values=(item.category, item.name, f"${item.price:.2f}", item.description)
            )

        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(10, 0))
        ttk.Label(controls, text="Quantity:").pack(side="left")

        self.qty_var = tk.IntVar(value=1)
        self.qty_spin = ttk.Spinbox(controls, from_=1, to=50, textvariable=self.qty_var, width=6)
        self.qty_spin.pack(side="left", padx=(5, 10))

        ttk.Button(controls, text="Add to Cart", command=self.add_to_cart).pack(side="left")
        ttk.Button(controls, text="View Item Details", command=self.view_item_details).pack(
            side="left", padx=(10, 0)
        )

    def _build_cart_panel(self, parent: ttk.Frame):
        frame = ttk.LabelFrame(parent, text="Cart", padding=10)
        frame.grid(row=0, column=2, sticky="nsew")

        cols = ("Name", "Category", "Unit Price", "Qty", "Line Total", "Idx")
        self.cart_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)

        for c in cols:
            self.cart_tree.heading(c, text=c)
            self.cart_tree.column(c, width=120, anchor="w")

        self.cart_tree.column("Qty", width=60, anchor="center")
        self.cart_tree.column("Line Total", width=100, anchor="e")
        self.cart_tree.column("Idx", width=0, stretch=False)  # hide

        self.cart_tree["displaycolumns"] = ("Name", "Category", "Unit Price", "Qty", "Line Total")
        self.cart_tree.pack(fill="both", expand=True)

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Remove Selected", command=self.remove_selected).pack(side="left")
        ttk.Button(actions, text="Clear Cart", command=self.clear_cart).pack(side="left", padx=(10, 0))

        self.cart_total_var = tk.StringVar(value="Subtotal: $0.00")
        ttk.Label(frame, textvariable=self.cart_total_var, font=("Segoe UI", 11, "bold")).pack(
            anchor="e", pady=(10, 0)
        )

    def _build_bill_panel(self, parent: ttk.Frame):
        frame = ttk.LabelFrame(parent, text="Billing / Payment", padding=10)
        frame.pack(fill="x")

        left = ttk.Frame(frame)
        left.pack(side="left", fill="x", expand=True)

        ttk.Label(left, text="Discount ($):").grid(row=0, column=0, sticky="w")
        ttk.Label(left, text="Tip ($):").grid(row=1, column=0, sticky="w")

        self.discount_var = tk.StringVar(value="0")
        self.tip_var = tk.StringVar(value="0")

        ttk.Entry(left, textvariable=self.discount_var, width=10).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Entry(left, textvariable=self.tip_var, width=10).grid(row=1, column=1, sticky="w", padx=(8, 20))

        ttk.Label(left, text=f"Tax Rate: {int(self.TAX_RATE * 100)}%").grid(row=0, column=2, sticky="w")

        btns = ttk.Frame(frame)
        btns.pack(side="right")

        ttk.Button(btns, text="Generate Bill", command=self.generate_bill).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Confirm Payment", command=self.confirm_payment).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="New Order", command=self.new_order).pack(side="left")

        # GUI Observer output label (shows latest order event)
        ttk.Label(frame, textvariable=self.ui_status_var, font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(8, 0))

        self.bill_text = tk.Text(frame, height=8, wrap="word")
        self.bill_text.pack(fill="x", pady=(10, 0))
        self.bill_text.insert("1.0", "Bill will appear here after you click 'Generate Bill'.")
        self.bill_text.config(state="disabled")

    # ---------- Core actions ----------

    def create_customer(self):
        name = self.name_var.get().strip()
        contact_raw = self.contact_var.get().strip()
        email = self.email_var.get().strip()

        try:
            ValidationHelper.validateNonEmptyString(name, "Name")

            digits_only = re.sub(r"\D", "", contact_raw)
            if len(digits_only) != 11:
                raise ValueError("Contact number must be 11 digits.")

            if not EMAIL_REGEX.match(email):
                raise ValueError("Invalid email format. Example: name@example.com")

            self.customer = Customer(customer_id="1", name=name, contact=digits_only, email=email)

            # Observer Pattern: attach BOTH observers when creating order
            self.order = Order(self.customer)
            self.order.add_observer(OrderAuditLogger())
            self.order.add_observer(TkStatusObserver(self, self.ui_status_var))

            self.current_bill = None
            self._refresh_cart()
            self._write_bill_text("Customer created/updated. You can now add items to cart.")

        except ValueError as e:
            messagebox.showerror("Invalid Customer Details", str(e))

    def delivery_coming_soon(self):
        messagebox.showinfo("Delivery", "Delivery feature is coming soon.")

    def _require_order(self) -> bool:
        if self.customer is None or self.order is None:
            messagebox.showwarning("Customer Required", "Please create/update customer details first.")
            return False
        return True

    def view_item_details(self):
        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showinfo("Menu", "Please select a menu item first.")
            return
        item = self.menu_items[int(sel[0])]
        details = item.getDetails() if hasattr(item, "getDetails") else item.displayMenuItem()
        messagebox.showinfo("Item Details", details)

    def add_to_cart(self):
        if not self._require_order():
            return

        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showinfo("Menu", "Please select a menu item to add.")
            return

        try:
            qty = int(self.qty_var.get())
            if qty < 1 or qty > 50:
                raise ValueError
        except Exception:
            messagebox.showerror("Quantity Error", "Quantity must be a valid number between 1 and 50.")
            return

        item = self.menu_items[int(sel[0])]
        for _ in range(qty):
            self.order.addItem(item)

        self.order.updateStatus("Building Order")
        self.current_bill = None
        self._refresh_cart()

    def remove_selected(self):
        if not self._require_order():
            return

        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showinfo("Cart", "Please select a cart row to remove.")
            return

        iid = sel[0]
        values = self.cart_tree.item(iid, "values")
        item_idx = int(values[5])  # hidden Idx
        item = self.menu_items[item_idx]

        removed = self.order.removeOne(item)
        if not removed:
            messagebox.showwarning("Remove", "Item could not be removed.")

        self.current_bill = None
        self._refresh_cart()

    def clear_cart(self):
        if not self._require_order():
            return
        self.order.clear()
        self.order.updateStatus("New")
        self.current_bill = None
        self._refresh_cart()

    def generate_bill(self):
        if not self._require_order():
            return
        try:
            ValidationHelper.validateOrder(self.order)
        except ValueError as e:
            messagebox.showerror("Order Error", str(e))
            return

        bill = self.order.generateBill(self.TAX_RATE)

        discount = self._safe_money(self.discount_var.get())
        tip = self._safe_money(self.tip_var.get())

        bill.applyDiscount(discount)
        bill.addTip(tip)

        if bill.finalAmount < 0:
            messagebox.showerror("Billing Error", "Discount is too large. Final amount cannot be negative.")
            return

        self.current_bill = bill
        self.order.updateStatus("Pending Payment")
        self._write_bill_text(bill.generateBillDetails())

    def confirm_payment(self):
        if not self._require_order():
            return
        if self.current_bill is None:
            messagebox.showwarning("Payment", "Please generate the bill first.")
            return

        self.order.updateStatus("Paid")
        self.customer.placeOrder(self.order)

        messagebox.showinfo("Payment", "Payment confirmed. Thank you.")
        self._write_bill_text(self.current_bill.generateBillDetails() + "\nStatus: Paid")

    def new_order(self):
        if self.customer is None:
            self.order = None
            self.current_bill = None
            self._refresh_cart()
            self._write_bill_text("Create customer details to start a new order.")
            return

        # Observer Pattern: attach BOTH observers for each new order
        self.order = Order(self.customer)
        self.order.add_observer(OrderAuditLogger())
        self.order.add_observer(TkStatusObserver(self, self.ui_status_var))

        self.current_bill = None
        self.discount_var.set("0")
        self.tip_var.set("0")
        self._refresh_cart()
        self._write_bill_text("New order started. Add items to cart.")

    # ---------- Utilities ----------

    def _safe_money(self, value: str) -> float:
        value = (value or "").strip()
        if value == "":
            return 0.0
        try:
            x = float(value)
            if x < 0:
                raise ValueError
            return x
        except ValueError:
            raise ValueError("Discount/Tip must be a non-negative number.")

    def _write_bill_text(self, text: str):
        self.bill_text.config(state="normal")
        self.bill_text.delete("1.0", "end")
        self.bill_text.insert("1.0", text)
        self.bill_text.config(state="disabled")

    def _refresh_cart(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)

        if self.order is None:
            self.cart_total_var.set("Subtotal: $0.00")
            return

        counts: dict[int, int] = {}
        for it in self.order.items:
            idx = self.menu_items.index(it)
            counts[idx] = counts.get(idx, 0) + 1

        subtotal = 0.0
        for idx, qty in counts.items():
            it = self.menu_items[idx]
            line_total = it.price * qty
            subtotal += line_total

            self.cart_tree.insert(
                "", "end",
                values=(it.name, it.category, f"${it.price:.2f}", qty, f"${line_total:.2f}", idx)
            )

        self.cart_total_var.set(f"Subtotal: ${subtotal:.2f}")


# =========================
# Run the GUI
# =========================

if __name__ == "__main__":
    app = CafeApp()
    app.mainloop()

# Import necessary modules and types
import re  # Regular expressions for validation
import tkinter as tk  # GUI framework
from tkinter import ttk, messagebox  # Tkinter widgets and dialog boxes
from typing import List, Protocol, Any  # Type hints for better code clarity


# =========================
# Core domain classes (Business logic and data models)
# =========================

class MenuItem:
    """
    Base class for all menu items in the cafe.
    Represents a generic item that can be ordered.
    """
    def __init__(self, category: str, name: str, price: float, description: str):
        self.category = category  # Food, Drink, or Combo
        self.name = name  # Display name of the item
        self.price = price  # Price in currency units
        self.description = description  # Brief description of the item

    def getPrice(self) -> float:
        """Returns the price of the menu item."""
        return self.price

    def getDescription(self) -> str:
        """Returns the description of the menu item."""
        return self.description

    def displayMenuItem(self):
        """Returns a formatted string representation of the menu item."""
        return f"{self.name} ({self.category}): {self.description} - ${self.price:.2f}"


class FoodItem(MenuItem):
    """
    Represents a food item on the menu.
    Extends MenuItem with food-specific properties.
    """
    def __init__(self, name: str, price: float, description: str, 
                 allergens: List[str], is_vegetarian: bool):
        # Call parent constructor with "Food" as category
        super().__init__("Food", name, price, description)
        self.allergens = allergens  # List of allergens (e.g., ["gluten", "nuts"])
        self.is_vegetarian = is_vegetarian  # Boolean flag for vegetarian status

    def getDetails(self):
        """Returns detailed information about the food item."""
        # Format allergens list or show "None" if empty
        allergens = ", ".join(self.allergens) if self.allergens else "None"
        return f"{self.name} - Vegetarian: {self.is_vegetarian}, Allergens: {allergens}"


class DrinkItem(MenuItem):
    """
    Represents a drink item on the menu.
    Extends MenuItem with drink-specific properties.
    """
    def __init__(self, name: str, price: float, description: str, 
                 is_cold: bool, is_hot: bool, size: str):
        # Call parent constructor with "Drink" as category
        super().__init__("Drink", name, price, description)
        self.isCold = is_cold  # Whether the drink is served cold
        self.isHot = is_hot  # Whether the drink is served hot
        self.size = size  # Size of the drink (e.g., "500ml", "12oz")

    def getDetails(self):
        """Returns detailed information about the drink item."""
        return f"{self.name} - Size: {self.size}, Cold: {self.isCold}, Hot: {self.isHot}"


class ComboItem(MenuItem):
    """
    Represents a combo meal consisting of multiple menu items.
    Extends MenuItem with combo-specific properties.
    """
    def __init__(self, name: str, price: float, description: str, items: List[MenuItem]):
        # Call parent constructor with "Combo" as category
        super().__init__("Combo", name, price, description)
        self.items = items  # List of MenuItem objects included in the combo

    def getDetails(self):
        """Returns detailed information about the combo item."""
        # Extract descriptions from each item in the combo
        item_details = [item.getDescription() for item in self.items]
        return f"{self.name} - Combo includes: {', '.join(item_details)}"


class Delivery:
    """
    Placeholder for delivery functionality.
    Demonstrates planned but not yet implemented feature.
    """
    def __init__(self, *args, **kwargs):
        # Raise error to indicate this feature is not ready
        raise NotImplementedError("Delivery feature is coming soon.")

    @staticmethod
    def getDeliveryDetails():
        """Placeholder method for delivery details."""
        raise NotImplementedError("Delivery feature is coming soon.")


class Bill:
    """
    Represents a bill for an order.
    Handles calculations for totals, taxes, discounts, and tips.
    """
    def __init__(self, order_id: str, name: str, totalAmount: float, taxAmount: float):
        self.order_id = order_id  # Unique identifier for the order
        self.name = name  # Customer name
        self.totalAmount = totalAmount  # Subtotal before tax
        self.taxAmount = taxAmount  # Tax amount
        self.finalAmount = totalAmount + taxAmount  # Initial total with tax
        self.discount = 0.0  # Discount amount (default 0)
        self.tip = 0.0  # Tip amount (default 0)

    def applyDiscount(self, discount: float):
        """
        Applies a discount to the bill.
        
        Args:
            discount: The discount amount in currency units
        """
        self.discount = max(0.0, float(discount))  # Ensure discount is non-negative
        self.finalAmount -= self.discount  # Subtract discount from final amount

    def addTip(self, tip: float):
        """
        Adds a tip to the bill.
        
        Args:
            tip: The tip amount in currency units
        """
        self.tip = max(0.0, float(tip))  # Ensure tip is non-negative
        self.finalAmount += self.tip  # Add tip to final amount

    def generateBillDetails(self):
        """Generates a formatted string with all bill details."""
        bill_details = f"--- Bill for Order {self.order_id} ---\n"
        bill_details += f"Customer: {self.name}\n"
        bill_details += f"Total Amount: ${self.totalAmount:.2f}\n"
        bill_details += f"Tax: ${self.taxAmount:.2f}\n"
        bill_details += f"Discount: ${self.discount:.2f}\n"
        bill_details += f"Tip: ${self.tip:.2f}\n"
        bill_details += f"Final Amount: ${self.finalAmount:.2f}\n"
        return bill_details


class ValidationHelper:
    """
    Utility class for validation operations.
    Follows the Single Responsibility Principle.
    """
    @staticmethod
    def validateMenuItem(item: MenuItem):
        """Validates that an object is a MenuItem instance."""
        if not isinstance(item, MenuItem):
            raise ValueError(f"Invalid Menu Item: {item}")

    @staticmethod
    def validateOrder(order: 'Order'):
        """Validates that an order contains at least one item."""
        if not order.items:
            raise ValueError("Order cannot be empty.")

    @staticmethod
    def validateNonEmptyString(value: str, field_name: str):
        """Validates that a string is not empty or only whitespace."""
        if not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")


# =========================
# DESIGN PATTERN 1: FACTORY
# =========================

class MenuItemFactory:
    """
    Factory Pattern implementation for creating MenuItem objects.
    Centralizes object creation logic and simplifies client code.
    """
    @staticmethod
    def create_item(category: str, **kwargs) -> MenuItem:
        """
        Creates and returns a MenuItem based on the category.
        
        Args:
            category: Type of menu item ("food", "drink", or "combo")
            **kwargs: Additional parameters specific to each item type
            
        Returns:
            A MenuItem object of the appropriate subclass
            
        Raises:
            ValueError: If category is not recognized
        """
        cat = category.strip().lower()  # Normalize category input

        # Create FoodItem
        if cat == "food":
            return FoodItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                allergens=kwargs.get("allergens", []),
                is_vegetarian=bool(kwargs.get("is_vegetarian", False)),
            )

        # Create DrinkItem
        if cat == "drink":
            return DrinkItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                is_cold=bool(kwargs.get("is_cold", True)),
                is_hot=bool(kwargs.get("is_hot", False)),
                size=kwargs.get("size", "Standard"),
            )

        # Create ComboItem
        if cat == "combo":
            return ComboItem(
                name=kwargs["name"],
                price=float(kwargs["price"]),
                description=kwargs.get("description", ""),
                items=kwargs.get("items", []),
            )

        # Handle unknown category
        raise ValueError(f"Unknown menu category: {category}")


# =========================
# DESIGN PATTERN 2: OBSERVER
# =========================

class OrderObserver(Protocol):
    """
    Observer Protocol (Interface) for the Observer Pattern.
    Defines the update method that all observers must implement.
    """
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        """
        Method called when the observed subject (Order) changes.
        
        Args:
            event: Type of event that occurred (e.g., "ITEM_ADDED")
            order: The Order object that triggered the event
            data: Additional data related to the event
        """
        ...


class OrderAuditLogger:
    """
    Concrete Observer: logs order events to the console.
    Used for system monitoring and debugging.
    """
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        """Logs order events to the console."""
        print(f"[ORDER EVENT] {event} | OrderID={order.order_id} | Status={order.status} | Data={data}")


class TkStatusObserver:
    """
    Concrete Observer (GUI): updates a Tkinter StringVar when Order changes.
    Demonstrates the Observer Pattern in the user interface.
    """
    def __init__(self, root: tk.Tk, status_var: tk.StringVar):
        """
        Initializes the GUI observer.
        
        Args:
            root: The main Tkinter window
            status_var: StringVar to update with status messages
        """
        self.root = root
        self.status_var = status_var

    def update(self, event: str, order: "Order", data: Any = None) -> None:
        """
        Updates the GUI status label with event information.
        Uses root.after() to ensure thread-safe GUI updates.
        """
        # Build status message
        msg = f"{event} | Status={order.status}"
        if isinstance(data, dict):
            if "item" in data:
                msg += f" | Item={data['item']}"
            if "total" in data:
                msg += f" | Total=${float(data['total']):.2f}"
        
        # Schedule GUI update on main thread
        self.root.after(0, lambda: self.status_var.set(msg))


class Order:
    """
    Represents a customer's order.
    Acts as the Subject in the Observer Pattern.
    """
    def __init__(self, customer: 'Customer'):
        self.order_id = str(id(self))  # Generate unique ID from object memory address
        self.customer = customer  # Customer who placed the order
        self.items: List[MenuItem] = []  # List of items in the order
        self.status = "New"  # Current status of the order
        self.totalCost = 0.0  # Calculated total cost

        # Observer list - stores all observers watching this order
        self._observers: List[OrderObserver] = []

    # ---- Observer Pattern methods ----
    def add_observer(self, observer: OrderObserver) -> None:
        """Registers an observer to receive updates."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: OrderObserver) -> None:
        """Unregisters an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event: str, data: Any = None) -> None:
        """Notifies all observers of an event."""
        for obs in self._observers:
            obs.update(event, self, data)

    # ---- Business logic methods ----
    def addItem(self, item: MenuItem):
        """Adds a menu item to the order and notifies observers."""
        self.items.append(item)
        self._notify("ITEM_ADDED", {"item": item.name, "price": item.price})

    def removeOne(self, item: MenuItem) -> bool:
        """
        Removes one instance of an item from the order.
        
        Returns:
            True if item was removed, False if not found
        """
        try:
            self.items.remove(item)
            self._notify("ITEM_REMOVED", {"item": item.name})
            return True
        except ValueError:
            return False

    def clear(self):
        """Removes all items from the order and notifies observers."""
        self.items.clear()
        self._notify("ORDER_CLEARED")

    def calculateTotal(self):
        """Calculates and returns the total cost of all items."""
        self.totalCost = sum(item.getPrice() for item in self.items)
        self._notify("TOTAL_CALCULATED", {"total": self.totalCost})
        return self.totalCost

    def generateBill(self, tax_rate: float = 0.20):
        """
        Generates a Bill object for the order.
        
        Args:
            tax_rate: Tax rate as a decimal (default 20%)
            
        Returns:
            A Bill object with calculated totals
        """
        total = self.calculateTotal()
        tax = total * tax_rate
        bill = Bill(self.order_id, self.customer.name, total, tax)
        self._notify("BILL_GENERATED", {"total": total, "tax": tax})
        return bill

    def updateStatus(self, new_status: str):
        """Updates the order status and notifies observers."""
        old = self.status
        self.status = new_status
        self._notify("STATUS_CHANGED", {"from": old, "to": new_status})


class Customer:
    """Represents a cafe customer."""
    def __init__(self, customer_id: str, name: str, contact: str, email: str):
        self.customer_id = customer_id  # Unique customer identifier
        self.name = name  # Customer's full name
        self.contact = contact  # Contact phone number
        self.email = email  # Customer's email address
        self.orderHistory: List[Order] = []  # List of past orders

    def viewOrderHistory(self):
        """Returns a list of order IDs from the customer's history."""
        return [order.order_id for order in self.orderHistory]

    def placeOrder(self, order: Order):
        """Adds an order to the customer's order history."""
        self.orderHistory.append(order)


# =========================
# Tkinter GUI
# =========================

# Regular expression for validating email addresses
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def build_sample_menu() -> List[MenuItem]:
    """
    Creates and returns a sample menu using the FACTORY PATTERN.
    The factory pattern creates objects without specifying the exact class,
    allowing flexible creation of different menu item types.
    
    Returns:
        List[MenuItem]: A list of menu items including both food and drinks
    """
    # Using FACTORY PATTERN here to create different types of menu items
    return [
        # Create a food item using the factory
        MenuItemFactory.create_item(
            "food",  # Item type/category
            name="Pizza",  # Display name
            price=12.50,  # Price in currency units
            description="Cheese pizza",  # Item description
            allergens=[],  # List of allergens (empty for pizza)
            is_vegetarian=True  # Vegetarian flag
        ),
        # Create another food item with allergens
        MenuItemFactory.create_item(
            "food",
            name="Chicken Burger",
            price=8.99,
            description="Grilled chicken burger",
            allergens=["gluten"],  # Contains gluten allergen
            is_vegetarian=False  # Not vegetarian
        ),
        # Create a vegetarian food item
        MenuItemFactory.create_item(
            "food",
            name="Chips",
            price=3.50,
            description="Crispy fries",
            allergens=[],  # No allergens
            is_vegetarian=True
        ),
        # Create a drink item with drink-specific properties
        MenuItemFactory.create_item(
            "drink",  # Different type - drink
            name="Coke",
            price=2.00,
            description="Soda drink",
            is_cold=True,  # Drink temperature property
            is_hot=False,
            size="500ml"  # Drink size
        ),
        # Create another drink item (hot drink)
        MenuItemFactory.create_item(
            "drink",
            name="Latte",
            price=3.20,
            description="Coffee with milk",
            is_cold=False,
            is_hot=True,  # Hot drink
            size="12oz"  # Different size format
        ),
    ]


class CafeApp(tk.Tk):  # Inherits from tk.Tk (main Tkinter window)
    """
    Main application class for the cafe ordering system.
    Implements the GUI and business logic for ordering.
    """
    
    TAX_RATE = 0.20  # Class constant for tax rate (20%)
    
    def __init__(self):
        """Initialize the cafe application window and components."""
        super().__init__()  # Initialize parent tk.Tk class
        
        # Window configuration
        self.title("Maaz Cafe Ordering System")  # Window title
        self.geometry("980x640")  # Initial window size
        self.minsize(940, 600)  # Minimum window size
        
        # Business data initialization
        self.menu_items = build_sample_menu()  # Load sample menu using factory
        self.customer: Customer | None = None  # Customer instance (optional)
        self.order: Order | None = None  # Current order (optional)
        self.current_bill: Bill | None = None  # Current bill (optional)
        
        # GUI observer status variable - tracks order events
        # Created early so observers can reference it
        self.ui_status_var = tk.StringVar(value="Observer: waiting for order events...")
        
        self._build_ui()  # Build the user interface

    def _build_ui(self):
        """Constructs the main user interface layout."""
        # Main title label
        title = ttk.Label(self, text="Maaz Cafe Ordering System", 
                         font=("Segoe UI", 18, "bold"))
        title.pack(pady=10)  # Add vertical padding
        
        # Main container frame for three panels
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)  # Fill available space
        
        # Configure grid columns with different weights (relative sizes)
        container.columnconfigure(0, weight=1)  # Customer panel (smallest)
        container.columnconfigure(1, weight=2)  # Menu panel
        container.columnconfigure(2, weight=2)  # Cart panel
        container.rowconfigure(0, weight=1)  # Single row that expands
        
        # Build the three main panels
        self._build_customer_panel(container)
        self._build_menu_panel(container)
        self._build_cart_panel(container)
        
        # Bottom section for billing
        bottom = ttk.Frame(self, padding=(10, 0, 10, 10))
        bottom.pack(fill="x")  # Fill horizontally
        self._build_bill_panel(bottom)

    def _build_customer_panel(self, parent: ttk.Frame):
        """Builds the customer details input panel."""
        # Create labeled frame for customer details
        frame = ttk.LabelFrame(parent, text="Customer Details", padding=10)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))  # Position in grid
        
        # Labels for input fields
        ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="Contact (11 digits):").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="Email:").grid(row=4, column=0, sticky="w")
        
        # String variables to store user input
        self.name_var = tk.StringVar()
        self.contact_var = tk.StringVar()
        self.email_var = tk.StringVar()
        
        # Entry fields bound to the string variables
        ttk.Entry(frame, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.contact_var).grid(row=3, column=0, sticky="ew", pady=(0, 8))
        ttk.Entry(frame, textvariable=self.email_var).grid(row=5, column=0, sticky="ew", pady=(0, 8))
        
        # Button container frame
        btns = ttk.Frame(frame)
        btns.grid(row=7, column=0, sticky="ew", pady=(10, 0))
        btns.columnconfigure(0, weight=1)  # Equal width buttons
        btns.columnconfigure(1, weight=1)
        
        # Action buttons
        ttk.Button(btns, text="Create / Update Customer", 
                  command=self.create_customer).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(btns, text="Delivery (Coming Soon)", 
                  command=self.delivery_coming_soon).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Make the single column expand horizontally
        frame.columnconfigure(0, weight=1)

    def _build_menu_panel(self, parent: ttk.Frame):
        """Builds the menu display panel with items and controls."""
        frame = ttk.LabelFrame(parent, text="Menu", padding=10)
        frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10))
        
        # Define column names for the menu treeview (table)
        cols = ("Category", "Name", "Price", "Description")
        self.menu_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        
        # Configure column headings
        for c in cols:
            self.menu_tree.heading(c, text=c)  # Column title
            # Set column widths (wider for description)
            self.menu_tree.column(c, width=120 if c != "Description" else 240, anchor="w")
        self.menu_tree.pack(fill="both", expand=True)  # Fill available space
        
        # Populate the menu with items from build_sample_menu()
        for idx, item in enumerate(self.menu_items):
            self.menu_tree.insert(
                "", "end", iid=str(idx),  # Empty parent, end position, index as ID
                values=(item.category, item.name, f"${item.price:.2f}", item.description)
            )
        
        # Control panel below the menu tree
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(10, 0))
        
        # Quantity selector
        ttk.Label(controls, text="Quantity:").pack(side="left")
        self.qty_var = tk.IntVar(value=1)  # Default quantity is 1
        self.qty_spin = ttk.Spinbox(controls, from_=1, to=50, 
                                   textvariable=self.qty_var, width=6)
        self.qty_spin.pack(side="left", padx=(5, 10))
        
        # Action buttons
        ttk.Button(controls, text="Add to Cart", command=self.add_to_cart).pack(side="left")
        ttk.Button(controls, text="View Item Details", 
                  command=self.view_item_details).pack(side="left", padx=(10, 0))

    def _build_cart_panel(self, parent: ttk.Frame):
        """Builds the shopping cart display panel."""
        frame = ttk.LabelFrame(parent, text="Cart", padding=10)
        frame.grid(row=0, column=2, sticky="nsew")
        
        # Define columns (including hidden index column)
        cols = ("Name", "Category", "Unit Price", "Qty", "Line Total", "Idx")
        self.cart_tree = ttk.Treeview(frame, columns=cols, show="headings", height=16)
        
        # Configure all columns
        for c in cols:
            self.cart_tree.heading(c, text=c)
            self.cart_tree.column(c, width=120, anchor="w")
        
        # Customize specific columns
        self.cart_tree.column("Qty", width=60, anchor="center")  # Center quantity
        self.cart_tree.column("Line Total", width=100, anchor="e")  # Right-align price
        self.cart_tree.column("Idx", width=0, stretch=False)  # Hide index column
        
        # Only show these columns to user (Idx is hidden)
        self.cart_tree["displaycolumns"] = ("Name", "Category", "Unit Price", "Qty", "Line Total")
        self.cart_tree.pack(fill="both", expand=True)
        
        # Cart action buttons
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(actions, text="Remove Selected", 
                  command=self.remove_selected).pack(side="left")
        ttk.Button(actions, text="Clear Cart", 
                  command=self.clear_cart).pack(side="left", padx=(10, 0))
        
        # Cart total display (updates dynamically)
        self.cart_total_var = tk.StringVar(value="Subtotal: $0.00")
        ttk.Label(frame, textvariable=self.cart_total_var, 
                 font=("Segoe UI", 11, "bold")).pack(anchor="e", pady=(10, 0))

    def _build_bill_panel(self, parent: ttk.Frame):
        """Builds the billing and payment panel at the bottom."""
        frame = ttk.LabelFrame(parent, text="Billing / Payment", padding=10)
        frame.pack(fill="x")
        
        # Left side: discount and tip inputs
        left = ttk.Frame(frame)
        left.pack(side="left", fill="x", expand=True)
        
        # Labels for input fields
        ttk.Label(left, text="Discount ($):").grid(row=0, column=0, sticky="w")
        ttk.Label(left, text="Tip ($):").grid(row=1, column=0, sticky="w")
        ttk.Label(left, text=f"Tax Rate: {int(self.TAX_RATE * 100)}%").grid(row=0, column=2, sticky="w")
        
        # Variables for discount and tip
        self.discount_var = tk.StringVar(value="0")  # Default $0 discount
        self.tip_var = tk.StringVar(value="0")  # Default $0 tip
        
        # Entry fields for discount and tip
        ttk.Entry(left, textvariable=self.discount_var, width=10).grid(row=0, column=1, sticky="w", padx=(8, 20))
        ttk.Entry(left, textvariable=self.tip_var, width=10).grid(row=1, column=1, sticky="w", padx=(8, 20))
        
        # Right side: action buttons
        btns = ttk.Frame(frame)
        btns.pack(side="right")
        
        # Billing and payment buttons
        ttk.Button(btns, text="Generate Bill", command=self.generate_bill).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Confirm Payment", command=self.confirm_payment).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="New Order", command=self.new_order).pack(side="left")
        
        # Observer status display (shows real-time order events)
        ttk.Label(frame, textvariable=self.ui_status_var, 
                 font=("Segoe UI", 10, "italic")).pack(anchor="w", pady=(8, 0))
        
        # Bill display text area
        self.bill_text = tk.Text(frame, height=8, wrap="word")
        self.bill_text.pack(fill="x", pady=(10, 0))
        self.bill_text.insert("1.0", "Bill will appear here after you click 'Generate Bill'.")
        self.bill_text.config(state="disabled")  # Make read-only initially

    # ---------- Core action methods ----------

    def create_customer(self):
        """Creates or updates a customer with validated input data."""
        # Get values from input fields
        name = self.name_var.get().strip()
        contact_raw = self.contact_var.get().strip()
        email = self.email_var.get().strip()

        try:
            # Validate inputs using helper methods
            ValidationHelper.validateNonEmptyString(name, "Name")

            # Validate contact number (11 digits)
            digits_only = re.sub(r"\D", "", contact_raw)  # Remove non-digit characters
            if len(digits_only) != 11:
                raise ValueError("Contact number must be 11 digits.")

            # Validate email format using regex
            if not EMAIL_REGEX.match(email):
                raise ValueError("Invalid email format. Example: name@example.com")

            # Create customer object
            self.customer = Customer(customer_id="1", name=name, contact=digits_only, email=email)

            # Observer Pattern: attach BOTH observers when creating order
            self.order = Order(self.customer)
            self.order.add_observer(OrderAuditLogger())  # Console logger
            self.order.add_observer(TkStatusObserver(self, self.ui_status_var))  # GUI observer

            # Reset billing and refresh UI
            self.current_bill = None
            self._refresh_cart()
            self._write_bill_text("Customer created/updated. You can now add items to cart.")

        except ValueError as e:
            # Show error message for invalid inputs
            messagebox.showerror("Invalid Customer Details", str(e))

    def delivery_coming_soon(self):
        """Shows a placeholder message for delivery feature."""
        messagebox.showinfo("Delivery", "Delivery feature is coming soon.")

    def _require_order(self) -> bool:
        """
        Checks if a customer and order exist.
        
        Returns:
            True if order exists, False otherwise (shows warning)
        """
        if self.customer is None or self.order is None:
            messagebox.showwarning("Customer Required", "Please create/update customer details first.")
            return False
        return True

    def view_item_details(self):
        """Displays detailed information about a selected menu item."""
        sel = self.menu_tree.selection()  # Get selected item in menu tree
        if not sel:
            messagebox.showinfo("Menu", "Please select a menu item first.")
            return
        
        # Get the selected menu item
        item = self.menu_items[int(sel[0])]
        
        # Display appropriate details based on item type
        details = item.getDetails() if hasattr(item, "getDetails") else item.displayMenuItem()
        messagebox.showinfo("Item Details", details)

    def add_to_cart(self):
        """Adds selected menu item to the cart with specified quantity."""
        if not self._require_order():
            return

        sel = self.menu_tree.selection()
        if not sel:
            messagebox.showinfo("Menu", "Please select a menu item to add.")
            return

        try:
            # Validate quantity
            qty = int(self.qty_var.get())
            if qty < 1 or qty > 50:
                raise ValueError
        except Exception:
            messagebox.showerror("Quantity Error", "Quantity must be a valid number between 1 and 50.")
            return

        # Get selected item and add it multiple times based on quantity
        item = self.menu_items[int(sel[0])]
        for _ in range(qty):
            self.order.addItem(item)

        # Update order status and refresh UI
        self.order.updateStatus("Building Order")
        self.current_bill = None
        self._refresh_cart()

    def remove_selected(self):
        """Removes selected item from the cart."""
        if not self._require_order():
            return

        sel = self.cart_tree.selection()
        if not sel:
            messagebox.showinfo("Cart", "Please select a cart row to remove.")
            return

        # Get item index from hidden column and remove from order
        iid = sel[0]
        values = self.cart_tree.item(iid, "values")
        item_idx = int(values[5])  # hidden Idx column
        item = self.menu_items[item_idx]

        # Remove item and refresh UI
        removed = self.order.removeOne(item)
        if not removed:
            messagebox.showwarning("Remove", "Item could not be removed.")

        self.current_bill = None
        self._refresh_cart()

    def clear_cart(self):
        """Removes all items from the cart."""
        if not self._require_order():
            return
        self.order.clear()
        self.order.updateStatus("New")
        self.current_bill = None
        self._refresh_cart()

    def generate_bill(self):
        """Generates a bill for the current order with discounts and tips."""
        if not self._require_order():
            return
        
        # Validate order has items
        try:
            ValidationHelper.validateOrder(self.order)
        except ValueError as e:
            messagebox.showerror("Order Error", str(e))
            return

        # Generate initial bill with tax
        bill = self.order.generateBill(self.TAX_RATE)

        # Apply discount and tip
        discount = self._safe_money(self.discount_var.get())
        tip = self._safe_money(self.tip_var.get())

        bill.applyDiscount(discount)
        bill.addTip(tip)

        # Validate final amount is not negative
        if bill.finalAmount < 0:
            messagebox.showerror("Billing Error", "Discount is too large. Final amount cannot be negative.")
            return

        # Store bill and update UI
        self.current_bill = bill
        self.order.updateStatus("Pending Payment")
        self._write_bill_text(bill.generateBillDetails())

    def confirm_payment(self):
        """Confirms payment for the current order."""
        if not self._require_order():
            return
        if self.current_bill is None:
            messagebox.showwarning("Payment", "Please generate the bill first.")
            return

        # Update order status and add to customer history
        self.order.updateStatus("Paid")
        self.customer.placeOrder(self.order)

        # Show confirmation and update bill display
        messagebox.showinfo("Payment", "Payment confirmed. Thank you.")
        self._write_bill_text(self.current_bill.generateBillDetails() + "\nStatus: Paid")

    def new_order(self):
        """Starts a new order while keeping the same customer."""
        if self.customer is None:
            # No customer exists, reset everything
            self.order = None
            self.current_bill = None
            self._refresh_cart()
            self._write_bill_text("Create customer details to start a new order.")
            return

        # Observer Pattern: attach BOTH observers for each new order
        self.order = Order(self.customer)
        self.order.add_observer(OrderAuditLogger())
        self.order.add_observer(TkStatusObserver(self, self.ui_status_var))

        # Reset order data and UI
        self.current_bill = None
        self.discount_var.set("0")
        self.tip_var.set("0")
        self._refresh_cart()
        self._write_bill_text("New order started. Add items to cart.")

    # ---------- Utility methods ----------

    def _safe_money(self, value: str) -> float:
        """
        Safely converts a string to a non-negative money value.
        
        Args:
            value: String representation of money amount
            
        Returns:
            Float value (0.0 if empty string)
            
        Raises:
            ValueError: If value is negative or not a valid number
        """
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
        """Updates the bill text display area."""
        self.bill_text.config(state="normal")  # Enable editing
        self.bill_text.delete("1.0", "end")  # Clear existing text
        self.bill_text.insert("1.0", text)  # Insert new text
        self.bill_text.config(state="disabled")  # Make read-only

    def _refresh_cart(self):
        """Refreshes the cart display with current order items."""
        # Clear existing cart items
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)

        # If no order exists, show empty cart
        if self.order is None:
            self.cart_total_var.set("Subtotal: $0.00")
            return

        # Count quantities of each menu item in the order
        counts: dict[int, int] = {}
        for it in self.order.items:
            idx = self.menu_items.index(it)  # Find index in menu list
            counts[idx] = counts.get(idx, 0) + 1  # Increment count

        # Calculate subtotal and add items to cart display
        subtotal = 0.0
        for idx, qty in counts.items():
            it = self.menu_items[idx]
            line_total = it.price * qty
            subtotal += line_total

            # Add row to cart treeview
            self.cart_tree.insert(
                "", "end",
                values=(it.name, it.category, f"${it.price:.2f}", qty, f"${line_total:.2f}", idx)
            )

        # Update cart total display
        self.cart_total_var.set(f"Subtotal: ${subtotal:.2f}")


# =========================
# Run the GUI application
# =========================

if __name__ == "__main__":
    # Create and run the main application
    app = CafeApp()
    app.mainloop()  # Start Tkinter event loop
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Any
import tkinter as tk
from menu_items import FoodItem, DrinkItem, ComboItem, MenuItem

if TYPE_CHECKING:
        from order_customer import Order # type: ignore


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


class OrderObserver(Protocol):
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        ...

class OrderAuditLogger:
    def update(self, event: str, order: "Order", data: Any = None) -> None:
        print(f"[ORDER EVENT] {event} | OrderID={order.order_id} | Status={order.status} | Data={data}")

class TkStatusObserver:
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

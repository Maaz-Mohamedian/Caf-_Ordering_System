import re
from typing import TYPE_CHECKING
from menu_items import MenuItem
if TYPE_CHECKING:
        from order_customer import Order # type: ignore

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

class ValidationHelper:
    @staticmethod
    def validateMenuItem(item: MenuItem):
        if not isinstance(item, MenuItem):
            raise ValueError(f"Invalid Menu Item: {item}")

    @staticmethod
    def validateOrder(order: "Order"):
        if not order.items:
            raise ValueError("Order cannot be empty.")

    @staticmethod
    def validateNonEmptyString(value: str, field_name: str):
        if not value.strip():
            raise ValueError(f"{field_name} cannot be empty.")

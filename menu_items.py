from __future__ import annotations
from typing import List

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

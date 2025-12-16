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

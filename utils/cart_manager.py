cart = []

def add_to_cart(product):
    cart.append(product)

def calculate_total():
    return sum(item["price"] for item in cart)

def generate_receipt(customer_name, cart, total):
    from reportlab.pdfgen import canvas

    receipt_path = f"assets/receipts/{customer_name}_receipt.pdf"
    c = canvas.Canvas(receipt_path)
    c.drawString(100, 800, "Fish Firm Receipt")
    c.drawString(100, 780, f"Customer: {customer_name}")
    
    y = 750
    for item in cart:
        c.drawString(100, y, f"{item['name']} - BDT{item['price']}")
        y -= 20
    
    c.drawString(100, y - 20, f"Total: BDT{total}")
    c.drawString(100, y - 60, "Signature: ______________________")
    c.drawString(100, y - 80, "Seal: ___________________________")
    c.save()

    return receipt_path

import tkinter as tk
from tkinter import messagebox
from fpdf import FPDF  # Importing FPDF library for creating PDF receipts
from utils.product_manager import fetch_products  # Import the fetch_products function
from PIL import Image, ImageTk  # Import Pillow for image handling
import requests
from io import BytesIO
import random

def customer_panel():
    # Create the main window with specified size
    window = tk.Tk()
    window.title("Customer Panel")
    window.geometry("1000x800")  # Set the window size to 1000x800

    # Title label
    title_label = tk.Label(window, text="Welcome to the Customer Panel", font=("Arial", 20))
    title_label.pack(pady=20)

    # Create a frame for the product grid
    product_frame = tk.Frame(window)
    product_frame.pack(pady=10)

    # Cart list to store added products
    cart = []

    # Function to add product to cart
    def add_to_cart(product):
        cart.append(product)
        messagebox.showinfo("Cart", f"Added {product['name']} to cart!")

    # Function to display cart contents
    def view_cart():
        # Create a new window for the cart
        cart_window = tk.Toplevel(window)
        cart_window.title("Your Cart")

        if not cart:
            tk.Label(cart_window, text="Your cart is empty.", font=("Arial", 14)).pack(pady=20)
        else:
            # Display cart items with images and prices
            row = 0
            total_price = 0
            for item in cart:
                name = item.get("name", "N/A")
                price = float(item.get("price", 0))
                image_url = item.get("image_url", "")

                cart_item_frame = tk.Frame(cart_window)
                cart_item_frame.pack(pady=5)

                # Display image
                if image_url:
                    try:
                        response = requests.get(image_url)
                        img_data = response.content
                        img = Image.open(BytesIO(img_data))
                        img = img.resize((60, 60), Image.Resampling.LANCZOS)  # Resize image
                        img_tk = ImageTk.PhotoImage(img)
                        image_label = tk.Label(cart_item_frame, image=img_tk)
                        image_label.grid(row=0, column=0)
                        image_label.image = img_tk  # Keep a reference to the image
                    except Exception as e:
                        image_label = tk.Label(cart_item_frame, text="No Image")
                        image_label.grid(row=0, column=0)
                else:
                    image_label = tk.Label(cart_item_frame, text="No Image")
                    image_label.grid(row=0, column=0)

                # Product name and price
                name_label = tk.Label(cart_item_frame, text=name, font=("Arial", 12, "bold"))
                name_label.grid(row=0, column=1, padx=10)
                price_label = tk.Label(cart_item_frame, text=f"BDT{price}", font=("Arial", 12))
                price_label.grid(row=0, column=2, padx=10)

                total_price += price

            # Add checkout option
            checkout_button = tk.Button(cart_window, text=f"Checkout - Total: BDT{total_price:.2f}", command=lambda: checkout(total_price), font=("Arial", 12), bg="blue", fg="white")
            checkout_button.pack(pady=10)

        # Button to close cart window
        close_button = tk.Button(cart_window, text="Close", command=cart_window.destroy, font=("Arial", 12))
        close_button.pack(pady=10)

    # Function to handle checkout
    def checkout(total_price):
        if not cart:
            messagebox.showinfo("Checkout", "Your cart is empty. Please add some products to checkout.")
        else:
            # Create a new window to gather customer information
            checkout_window = tk.Toplevel(window)
            checkout_window.title("Checkout")

            # Labels and Entry fields for customer info
            name_label = tk.Label(checkout_window, text="Name: ", font=("Arial", 12))
            name_label.grid(row=0, column=0, padx=10, pady=5)
            name_entry = tk.Entry(checkout_window, font=("Arial", 12))
            name_entry.grid(row=0, column=1, padx=10, pady=5)

            phone_label = tk.Label(checkout_window, text="Phone: ", font=("Arial", 12))
            phone_label.grid(row=1, column=0, padx=10, pady=5)
            phone_entry = tk.Entry(checkout_window, font=("Arial", 12))
            phone_entry.grid(row=1, column=1, padx=10, pady=5)

            address_label = tk.Label(checkout_window, text="Address: ", font=("Arial", 12))
            address_label.grid(row=2, column=0, padx=10, pady=5)
            address_entry = tk.Entry(checkout_window, font=("Arial", 12))
            address_entry.grid(row=2, column=1, padx=10, pady=5)

            # Function to generate the PDF receipt
            def generate_receipt():
                customer_info = {
                    "name": name_entry.get(),
                    "phone": phone_entry.get(),
                    "address": address_entry.get()
                }

                if not customer_info["name"] or not customer_info["phone"]:
                    messagebox.showerror("Error", "Name and Phone number are required.")
                    return

                # Process cart contents and calculate total price
                cart_contents = [(item["name"], float(item["price"]), 1) for item in cart]
                total_price = sum([item[1] for item in cart_contents])

                # Generate PDF receipt
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)

                # Add customer information
                pdf.cell(0, 10, "Receipt", 0, 1, "C")
                pdf.cell(0, 10, f"Name: {customer_info['name']}", 0, 1)
                pdf.cell(0, 10, f"Phone: {customer_info['phone']}", 0, 1)
                pdf.cell(0, 10, f"Address: {customer_info['address']}", 0, 1)
                pdf.cell(0, 10, "", 0, 1)  # Empty line

                # Add cart items
                pdf.set_font("Arial", "", 12)
                for item in cart_contents:
                    pdf.cell(0, 10, f"{item[0]} - BDT{item[1]} x {item[2]}", 0, 1)

                pdf.cell(0, 10, "", 0, 1)  # Empty line
                pdf.cell(0, 10, f"Total Price: BDT{total_price}", 0, 1, "R")

                # Generate a random string for the file name
                random_value = random.randint(1000, 9999)
                pdf_file = f"{customer_info['phone']}_{random_value}.pdf"
                pdf.output(pdf_file)

                messagebox.showinfo("Receipt", f"Receipt has been saved as '{pdf_file}'")

                # Clear the cart after checkout
                cart.clear()
                checkout_window.destroy()

            # Checkout button to generate the receipt
            checkout_button = tk.Button(checkout_window, text="Generate Receipt", command=generate_receipt, font=("Arial", 12), bg="blue", fg="white")
            checkout_button.grid(row=3, columnspan=2, pady=10)

    # Fetch products and display them in grid
    products = fetch_products()
    row = 0
    for product in products:
        name = product.get("name", "N/A")
        price = product.get("price", "N/A")
        image_url = product.get("image_url", "")

        # Create a frame for each product
        product_card = tk.Frame(product_frame, width=200, height=250, relief="solid", borderwidth=1)
        product_card.grid(row=0, column=row, padx=10, pady=10)

        # Image (if available, fetch from URL and load into Tkinter)
        try:
            if image_url:
                response = requests.get(image_url)
                img_data = response.content
                img = Image.open(BytesIO(img_data))
                img = img.resize((100, 100), Image.Resampling.LANCZOS)  # Resize image
                img_tk = ImageTk.PhotoImage(img)
                image_label = tk.Label(product_card, image=img_tk)
                image_label.grid(row=0, column=0)
                image_label.image = img_tk  # Keep a reference to the image
            else:
                image_label = tk.Label(product_card, text="No Image", width=15, height=5)
                image_label.grid(row=0, column=0)
        except Exception as e:
            print(f"Error loading image: {e}")
            image_label = tk.Label(product_card, text="No Image", width=15, height=5)
            image_label.grid(row=0, column=0)

        # Product name and price
        name_label = tk.Label(product_card, text=name, font=("Arial", 12, "bold"))
        name_label.grid(row=1, column=0, padx=10, pady=5)
        price_label = tk.Label(product_card, text=f"BDT{price}", font=("Arial", 12))
        price_label.grid(row=2, column=0, padx=10, pady=5)

        # Add "Add to Cart" button
        add_to_cart_button = tk.Button(product_card, text="Add to Cart", command=lambda product=product: add_to_cart(product))
        add_to_cart_button.grid(row=3, column=0, padx=10, pady=5)

        row += 1

    # Button to view the cart
    view_cart_button = tk.Button(window, text="View Cart", command=view_cart, font=("Arial", 14), bg="green", fg="white")
    view_cart_button.pack(pady=20)

    # Start the Tkinter event loop
    window.mainloop()

# To launch the customer panel, you can call:
# customer_panel()

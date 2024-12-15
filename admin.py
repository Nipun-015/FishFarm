import tkinter as tk
from tkinter import messagebox, filedialog
from firebase_admin import firestore, storage
from PIL import Image, ImageTk
import requests
from io import BytesIO
import firebase_admin
from firebase_admin import credentials
from fpdf import FPDF
import random
import os

# Initialize Firebase
cred = credentials.Certificate("C:/Users/Iftekhar/Desktop/fish/fishfirm-f140d-firebase-adminsdk-w3840-b146178bb1.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'fishfirm-f140d.appspot.com'})

# Initialize Firestore client
db = firestore.client()

# Initialize Firebase Storage bucket
bucket = storage.bucket()

# Fetch products from Firebase
def fetch_products():
    products_ref = db.collection('products_collection')
    products = products_ref.stream()

    product_list = []
    for product in products:
        product_data = product.to_dict()
        product_data['id'] = product.id  # Add product ID
        product_list.append(product_data)
    
    return product_list

# Add product to Firebase
def add_product(name, item_type, details, price, image_url):
    products_ref = db.collection('products_collection')
    product_data = {
        'name': name,
        'type': item_type,
        'details': details,
        'price': price,
        'image_url': image_url,
    }
    products_ref.add(product_data)

# Delete product from Firebase
def delete_product(product_id):
    product_ref = db.collection('products_collection').document(product_id)
    product_ref.delete()

# Add new user to Firebase
def add_user(username, email, password):
    users_ref = db.collection('users')
    user_data = {
        'username': username,
        'email': email,
        'password': password,
    }
    users_ref.add(user_data)

# Add order to Firebase
def add_order(customer_name, customer_address, customer_phone, cart, total_price):
    orders_ref = db.collection('orders')
    order_data = {
        'customer_name': customer_name,
        'address': customer_address,
        'phone': customer_phone,
        'products': cart,
        'total_price': total_price,
    }
    orders_ref.add(order_data)

# Generate a PDF receipt
def generate_receipt(customer_name, customer_address, customer_phone, cart):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Receipt", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Address: {customer_address}", ln=True)
    pdf.cell(200, 10, txt=f"Customer Phone: {customer_phone}", ln=True)

    total_price = 0
    pdf.ln(10)
    for product in cart:
        pdf.cell(200, 10, txt=f"Product: {product['name']}, Price: ${product['price']}, Quantity: {product['quantity']}", ln=True)
        total_price += float(product['price']) * product['quantity']
    
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Price: ${total_price}", ln=True)
    
    receipt_name = f"{customer_phone}_{random.randint(1000, 9999)}.pdf"
    pdf.output(receipt_name)
    messagebox.showinfo("Success", f"Receipt generated: {receipt_name}")

# Confirmation for deleting a product
def confirm_delete(product_id):
    confirmation = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this product?")
    if confirmation:
        delete_product(product_id)
        messagebox.showinfo("Success", "Product deleted successfully.")
        load_products()

# Admin panel UI
def admin_panel():
    def load_products():
        for widget in product_list_frame.winfo_children():
            widget.destroy()

        products = fetch_products()
        for product in products:
            product_name = product.get('name', 'No Name')
            product_price = product.get('price', '0.00')
            product_image_url = product.get('image_url', None)
            product_id = product.get('id', '')

            product_frame = tk.Frame(product_list_frame, borderwidth=1, relief="solid")
            product_frame.grid(sticky='nsew', padx=10, pady=5)

            tk.Label(product_frame, text=f"{product_name} - ${product_price}", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, sticky='w')

            if product_image_url:
                try:
                    response = requests.get(product_image_url)
                    img_data = response.content
                    img = Image.open(BytesIO(img_data))
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img)
                    image_label = tk.Label(product_frame, image=img_tk)
                    image_label.image = img_tk
                    image_label.grid(row=0, column=1, padx=10)
                except Exception as e:
                    print(f"Error loading image: {e}")
                    tk.Label(product_frame, text="No Image", width=15, height=5).grid(row=0, column=1, padx=10)
            else:
                tk.Label(product_frame, text="No Image", width=15, height=5).grid(row=0, column=1, padx=10)

            delete_button = tk.Button(
                product_frame,
                text="Delete",
                bg='red',
                fg='white',
                command=lambda product_id=product_id: confirm_delete(product_id)
            )
            delete_button.grid(row=0, column=2, padx=10)

            select_button = tk.Button(
                product_frame,
                text="Select",
                bg='blue',
                fg='white',
                command=lambda product_id=product_id, product_name=product_name, product_price=product_price: add_to_cart(product_id, product_name, product_price)
            )
            select_button.grid(row=0, column=3, padx=10)

    def add_product_ui():
        name = name_entry.get()
        item_type = type_entry.get()
        details = details_entry.get()
        price = price_entry.get()
        image_url = image_url_entry.get()

        if not all([name, item_type, details, price]):
            messagebox.showerror("Error", "All fields except Image URL are required.")
            return

        if uploaded_image_path.get():
            image_url = uploaded_image_path.get()

        add_product(name, item_type, details, price, image_url)
        messagebox.showinfo("Success", "Product added successfully.")
        load_products()

    def upload_image():
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            try:
                file_name = os.path.basename(file_path)
                blob = bucket.blob(file_name)
                blob.upload_from_filename(file_path)
                blob.make_public()
                image_url = blob.public_url
                uploaded_image_path.set(image_url)
                image_url_entry.delete(0, tk.END)
                image_url_entry.insert(0, image_url)
                messagebox.showinfo("Success", f"Image uploaded successfully. URL: {image_url}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload image: {e}")

    def checkout():
        customer_name = customer_name_entry.get()
        customer_address = address_entry.get()
        customer_phone = phone_entry.get()
        if not all([customer_name, customer_address, customer_phone]):
            messagebox.showerror("Error", "All fields are required for checkout.")
            return

        if not cart:
            messagebox.showerror("Error", "No products selected.")
            return

        total_price = sum(float(product['price']) * product['quantity'] for product in cart)
        generate_receipt(customer_name, customer_address, customer_phone, cart)
        add_order(customer_name, customer_address, customer_phone, cart, total_price)

    def add_to_cart(product_id, product_name, product_price):
        quantity = int(quantity_entry.get()) if quantity_entry.get().isdigit() else 1
        cart.append({"id": product_id, "name": product_name, "price": product_price, "quantity": quantity})
        messagebox.showinfo("Success", f"Added {product_name} (Qty: {quantity}) to cart")

    cart = []

    admin_window = tk.Tk()
    admin_window.title("Admin Panel - Product Management")
    admin_window.geometry("1000x800")

    uploaded_image_path = tk.StringVar()

    tk.Label(admin_window, text="Products:").grid(row=0, column=0, pady=10)

    canvas = tk.Canvas(admin_window)
    scrollbar = tk.Scrollbar(admin_window, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    product_list_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=product_list_frame, anchor='nw')
    canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
    scrollbar.grid(row=1, column=3, sticky='ns')

    def update_scroll_region():
        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    tk.Button(admin_window, text="Load Products", command=load_products).grid(row=2, column=0, pady=10)

    tk.Label(admin_window, text="Product Name:").grid(row=3, column=0)
    name_entry = tk.Entry(admin_window)
    name_entry.grid(row=3, column=1)

    tk.Label(admin_window, text="Product Type:").grid(row=4, column=0)
    type_entry = tk.Entry(admin_window)
    type_entry.grid(row=4, column=1)

    tk.Label(admin_window, text="Product Details:").grid(row=5, column=0)
    details_entry = tk.Entry(admin_window)
    details_entry.grid(row=5, column=1)

    tk.Label(admin_window, text="Product Price:").grid(row=6, column=0)
    price_entry = tk.Entry(admin_window)
    price_entry.grid(row=6, column=1)

    tk.Label(admin_window, text="Image URL (Optional):").grid(row=7, column=0)
    image_url_entry = tk.Entry(admin_window)
    image_url_entry.grid(row=7, column=1)

    tk.Button(admin_window, text="Upload Image", command=upload_image).grid(row=7, column=2)

    tk.Button(admin_window, text="Add Product", command=add_product_ui).grid(row=8, column=0, pady=10)

    tk.Label(admin_window, text="Customer Name:").grid(row=9, column=0)
    customer_name_entry = tk.Entry(admin_window)
    customer_name_entry.grid(row=9, column=1)

    tk.Label(admin_window, text="Customer Address:").grid(row=10, column=0)
    address_entry = tk.Entry(admin_window)
    address_entry.grid(row=10, column=1)

    tk.Label(admin_window, text="Customer Phone:").grid(row=11, column=0)
    phone_entry = tk.Entry(admin_window)
    phone_entry.grid(row=11, column=1)

    tk.Label(admin_window, text="Quantity:").grid(row=12, column=0)
    quantity_entry = tk.Entry(admin_window)
    quantity_entry.grid(row=12, column=1)

    tk.Button(admin_window, text="Checkout", command=checkout).grid(row=13, column=0, pady=20)

    load_products()

    product_list_frame.bind("<Configure>", lambda event: update_scroll_region())

    admin_window.mainloop()



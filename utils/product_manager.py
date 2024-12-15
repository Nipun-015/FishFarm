import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("C:/Users/DELL/OneDrive/Desktop/fish/fishfirm-f140d-firebase-adminsdk-w3840-b146178bb1.json")

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_products():
    try:
        products_ref = db.collection("products_collection")
        return [doc.to_dict() | {"id": doc.id} for doc in products_ref.stream()]
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def add_product(name, item_type, details, price, image_url):
    try:
        db.collection("products").add({
            "name": name,
            "type": item_type,
            "details": details,
            "price": price,
            "image_url": image_url
        })
    except Exception as e:
        print(f"Error adding product: {e}")

def delete_product(product_id):
    try:
        db.collection("products").document(product_id).delete()
    except Exception as e:
        print(f"Error deleting product: {e}")

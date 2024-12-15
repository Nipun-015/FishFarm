import firebase_admin
from firebase_admin import credentials, firestore, storage

# Initialize Firebase
cred = credentials.Certificate("C:/Users/Iftekhar/Desktop/fish/fishfirm-f140d-firebase-adminsdk-w3840-b146178bb1.json")
firebase_admin.initialize_app(cred, {
    "storageBucket": "fishfirm-f140d.appspot.com"
})

# Firestore and Storage references
db = firestore.client()
bucket = storage.bucket()

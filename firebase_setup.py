import firebase_admin
from firebase_admin import credentials, firestore, storage

## privateKey must be from your Firebase project
cred = credentials.Certificate("./serviceAccountKey.json")

## change storageBucket according to your Firebase project
firebase_admin.initialize_app(cred, {
    "storageBucket": "lkukkapalli-cmsc5313.appspot.com"
})

## Firestore and Cloud Storage access
db = firestore.client()
bucket = storage.bucket()
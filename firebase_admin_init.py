import os, json
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load service account from env
service_account_info = json.loads(
    os.environ["FIREBASE_SERVICE_ACCOUNT"]
)

cred = credentials.Certificate(service_account_info)

# Initialize only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# EXPORT THESE 👇
db = firestore.client()

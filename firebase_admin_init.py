'''import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred)

db = firestore.client()
'''

import os, json
from firebase_admin import credentials, initialize_app

service_account_info = json.loads(
    os.environ.get("FIREBASE_SERVICE_ACCOUNT")
)

cred = credentials.Certificate(service_account_info)
initialize_app(cred)

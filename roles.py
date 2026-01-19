from fastapi import Header, HTTPException
from firebase_admin_init import auth, db

def require_role(required_role: str):
    def checker(authorization: str = Header(None)):
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing token")

        token = authorization.split("Bearer ")[-1]
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]

        user_doc = db.collection("users").document(uid).get()
        if not user_doc.exists:
            raise HTTPException(status_code=403, detail="User not registered")

        role = user_doc.to_dict().get("role")
        if role != required_role:
            raise HTTPException(status_code=403, detail="Access denied")

        return uid

    return checker

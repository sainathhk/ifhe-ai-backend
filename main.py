'''from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)







#from fastapi import FastAPI, Header, HTTPException
from firebase_admin_init import auth, db

#app = FastAPI()

from upload import router as upload_router

app.include_router(upload_router)


@app.get("/")
def root():
    return {"message": "IFHE AI Backend is running"}

@app.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split("Bearer ")[-1]

    try:
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]
        email = decoded.get("email")

        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        # First login
        if not user_doc.exists:
            if email.endswith("@ifheindia.org"):
                role = "student"
            else:
                raise HTTPException(status_code=403, detail="Unauthorized email")

            user_ref.set({
                "email": email,
                "role": role
            })

        user_data = user_ref.get().to_dict()

        return {
            "uid": uid,
            "email": email,
            "role": user_data["role"]
        }

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

from fastapi import Depends
from roles import require_role

@app.get("/faculty-only")
def faculty_test(uid=Depends(require_role("faculty"))):
    return {"message": "Faculty access granted"}


from ask import router as ask_router

app.include_router(ask_router)
'''



from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from ask import router as ask_router

# ROUTERS
#app.include_router(upload_router)
app.include_router(ask_router)   # ✅ THIS LINE FIXES 404
#app.include_router(auth_router)  # if exists







#from fastapi import FastAPI, Header, HTTPException
from firebase_admin_init import auth, db

#app = FastAPI()

from upload import router as upload_router

app.include_router(upload_router)


@app.get("/")
def root():
    return {"message": "IFHE AI Backend is running"}




from fastapi import Header, HTTPException
from firebase_admin import auth
from firebase_admin import firestore

db = firestore.client()

@app.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization format")

    token = authorization.replace("Bearer ", "").strip()

    try:
        decoded = auth.verify_id_token(token)

        uid = decoded["uid"]
        email = decoded.get("email")

        if not email:
            raise HTTPException(status_code=401, detail="Email not found in token")

        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        # First login
        if not user_doc.exists:
            if email.endswith("@ifheindia.org"):
                role = "student"   # ✅ FIXED
            else:
                raise HTTPException(status_code=403, detail="Unauthorized email domain")

            user_ref.set({
                "email": email,
                "role": role
            })

        user_data = user_ref.get().to_dict()

        return {
            "uid": uid,
            "email": email,
            "role": user_data["role"]
        }

    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")

    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Expired Firebase token")

    except Exception as e:
        print("AUTH ERROR:", e)
        raise HTTPException(status_code=401, detail="Authentication failed")

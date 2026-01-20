from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from firebase_admin_init import auth, db
from ask import router as ask_router
from upload import router as upload_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ifhe-ai-frontend-6adccoelt-sainaths-projects-321166a5.vercel.app" ,
        "https://ifhe-ai-frontend.vercel.app"# later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "IFHE AI Backend is running"}
'''
@app.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.replace("Bearer ", "").strip()

    try:
        decoded = auth.verify_id_token(token)
        uid = decoded["uid"]
        email = decoded.get("email")

        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            if not email.endswith("@ifheindia.org"):
                raise HTTPException(status_code=403, detail="Unauthorized email")

            user_ref.set({
                "email": email,
                "role": "student"
            })

        return user_ref.get().to_dict() | {"uid": uid}

    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")

# ROUTERS
app.include_router(ask_router)
app.include_router(upload_router)
'''
from fastapi import Header, HTTPException

@app.get("/me")
def get_me(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.replace("Bearer ", "")

    try:
        decoded = auth.verify_id_token(token)
    except Exception as e:
        print("TOKEN VERIFY ERROR:", e)
        raise HTTPException(status_code=401, detail="Invalid token")

    uid = decoded["uid"]
    email = decoded.get("email")

    if not email:
        raise HTTPException(status_code=401, detail="Email not found in token")

    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()

    # FIRST LOGIN ONLY
    if not user_doc.exists:
        if email.endswith("@ifheindia.org"):
            role = "student"   # ✅ DEFAULT
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

# ROUTERS
app.include_router(ask_router)
app.include_router(upload_router)

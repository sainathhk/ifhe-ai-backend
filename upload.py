import uuid
import os
from fastapi import APIRouter, UploadFile, File, Depends
from roles import require_role
from pdf_utils import extract_text_from_pdf
from vector_store import add_document

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    uid=Depends(require_role("faculty"))
):




    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}.pdf"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    text = extract_text_from_pdf(file_path)

    add_document(
        text=text,
        metadata={
            "uploaded_by": uid,
            "filename": file.filename
        },
        doc_id=file_id
    )

    return {
        "message": "Document uploaded and indexed successfully",
        "doc_id": file_id
    }

from io import BytesIO

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pypdf import PdfReader

from app import db
from app.models import Document


documents_bp = Blueprint("documents", __name__)


@documents_bp.post("/documents")
@jwt_required()
def create_document():
    user_id = int(get_jwt_identity())

    text = request.form.get("text")
    title = request.form.get("title")
    file = request.files.get("file")

    if not text and not file:
        return {
            "message": "متن یا فایل PDF الزامی است"
        }, 400

    if text:
        if not title:
            title = "Untitled"

        document = Document(
            user_id=user_id,
            title=title,
            content=text
        )

        db.session.add(document)
        db.session.commit()

        return {
            "message": "متن با موفقیت ذخیره شد",
            "document": {
                "id": document.id,
                "title": document.title,
                "characters": len(document.content)
            }
        }, 201

    if file:
        if not file.filename.lower().endswith(".pdf"):
            return {
                "message": "فقط فایل PDF مجاز است"
            }, 400

        try:
            pdf = PdfReader(BytesIO(file.read()))

            extracted_text = "\n".join(
                page.extract_text() or ""
                for page in pdf.pages
            )

        except Exception:
            return {
                "message": "خواندن فایل PDF ناموفق بود"
            }, 400

        if not extracted_text.strip():
            return {
                "message": "متنی از فایل PDF استخراج نشد"
            }, 400

        document = Document(
            user_id=user_id,
            title=file.filename,
            content=extracted_text
        )

        db.session.add(document)
        db.session.commit()

        return {
            "message": "فایل PDF با موفقیت ذخیره شد",
            "document": {
                "id": document.id,
                "title": document.title,
                "pages": len(pdf.pages),
                "characters": len(document.content)
            }
        }, 201
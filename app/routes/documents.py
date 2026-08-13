from io import BytesIO
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from pypdf import PdfReader

from app import db
from app.models import Document, DocumentChunk
from app.services.chunking import chunk_text
from app.services.document_context_service import DocumentContextService
from app.services.document_ai_service import DocumentAIService


documents_bp = Blueprint("documents", __name__)

UPLOAD_DIR = (
    Path(__file__).resolve().parents[2]
    / "uploads"
    / "documents"
)


def save_uploaded_pdf(file):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    original_filename = file.filename or "document.pdf"

    stored_filename = f"{uuid4().hex}.pdf"
    file_path = UPLOAD_DIR / stored_filename

    file.save(file_path)

    return file_path, original_filename


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

    # -------------------------
    # Create document from text
    # -------------------------
    if text:
        if not title:
            title = "Untitled"

        document = Document(
            user_id=user_id,
            title=title,
            content=text,
            file_type="text",
        )

        db.session.add(document)
        db.session.flush()

        chunks = chunk_text(document.content)

        for index, chunk in enumerate(chunks):
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                characters=len(chunk),
            )

            db.session.add(document_chunk)

        db.session.commit()

        return {
            "message": "متن با موفقیت ذخیره شد",
            "document": {
                "id": document.id,
                "title": document.title,
                "file_type": document.file_type,
                "characters": len(document.content),
                "chunks": len(chunks),
            },
        }, 201

    # -------------------------
    # Create document from PDF
    # -------------------------
    if file:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            return {
                "message": "فقط فایل PDF مجاز است"
            }, 400

        try:
            pdf_bytes = file.read()

            pdf = PdfReader(BytesIO(pdf_bytes))

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

        try:
            file.seek(0)

            stored_path, original_filename = save_uploaded_pdf(file)

        except Exception:
            return {
                "message": "ذخیره فایل PDF ناموفق بود"
            }, 500

        document = Document(
            user_id=user_id,
            title=original_filename,
            content=extracted_text,
            file_type="pdf",
            file_path=str(stored_path),
            original_filename=original_filename,
        )

        db.session.add(document)
        db.session.flush()

        chunks = chunk_text(document.content)

        for index, chunk in enumerate(chunks):
            document_chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                characters=len(chunk),
            )

            db.session.add(document_chunk)

        db.session.commit()

        return {
            "message": "فایل PDF با موفقیت ذخیره شد",
            "document": {
                "id": document.id,
                "title": document.title,
                "file_type": document.file_type,
                "original_filename": document.original_filename,
                "pages": len(pdf.pages),
                "characters": len(document.content),
                "chunks": len(chunks),
            },
        }, 201


@documents_bp.get("/documents")
@jwt_required()
def get_documents():
    user_id = int(get_jwt_identity())

    documents = (
        Document.query
        .filter_by(user_id=user_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return {
        "documents": [
            {
                "id": document.id,
                "title": document.title,
                "file_type": document.file_type,
                "original_filename": document.original_filename,
                "characters": len(document.content),
                "chunks": len(document.chunks),
                "created_at": document.created_at.isoformat(),
            }
            for document in documents
        ]
    }, 200

@documents_bp.get("/documents/<int:document_id>/file")
@jwt_required()
def get_document_file(document_id):
    user_id = int(get_jwt_identity())

    document = Document.query.filter_by(
        id=document_id,
        user_id=user_id,
    ).first()

    if not document:
        return {
            "message": "سند پیدا نشد"
        }, 404

    if document.file_type != "pdf":
        return {
            "message": "این سند فایل PDF ندارد"
        }, 404

    if not document.file_path:
        return {
            "message": "فایل PDF پیدا نشد"
        }, 404

    file_path = Path(document.file_path)

    if not file_path.is_file():
        return {
            "message": "فایل PDF روی سرور پیدا نشد"
        }, 404

    return send_file(
        file_path,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=document.original_filename or document.title,
    )

@documents_bp.get("/documents/<int:document_id>")
@jwt_required()
def get_document(document_id):
    user_id = int(get_jwt_identity())

    document = Document.query.filter_by(
        id=document_id,
        user_id=user_id,
    ).first()

    if not document:
        return {
            "message": "سند پیدا نشد"
        }, 404

    response_document = {
        "id": document.id,
        "title": document.title,
        "file_type": document.file_type,
        "original_filename": document.original_filename,
        "characters": len(document.content),
        "chunks": len(document.chunks),
        "created_at": document.created_at.isoformat(),
    }

    # متن فقط برای اسناد متنی برگردانده شود.
    if document.file_type == "text":
        response_document["content"] = document.content

    return {
        "document": response_document
    }, 200


@documents_bp.post("/documents/<int:document_id>/summarize")
@jwt_required()
def summarize_document(document_id):
    user_id = int(get_jwt_identity())

    chunks = DocumentContextService.get_chunks(
        document_id=document_id,
        user_id=user_id,
    )

    if not chunks:
        return {
            "message": "سند پیدا نشد یا متنی برای خلاصه‌سازی وجود ندارد"
        }, 404

    data = request.get_json(silent=True) or {}
    language = data.get("language", "fa")

    if language not in {"fa", "en"}:
        return {
            "message": "زبان باید fa یا en باشد"
        }, 400

    service = DocumentAIService()

    try:
        summary = service.summarize(
            chunks,
            language=language,
        )
    except Exception as e:
        return {
            "message": "خلاصه‌سازی ناموفق بود",
            "error": str(e),
        }, 500

    return {
        "document_id": document_id,
        "language": language,
        "summary": summary,
    }, 200


@documents_bp.post("/documents/<int:document_id>/ask")
@jwt_required()
def ask_document(document_id):
    user_id = int(get_jwt_identity())

    data = request.get_json(silent=True) or {}

    question = data.get("question")
    language = data.get("language", "fa")

    if not question or not question.strip():
        return {
            "message": "سؤال الزامی است"
        }, 400

    if language not in {"fa", "en"}:
        return {
            "message": "زبان باید fa یا en باشد"
        }, 400

    chunks = DocumentContextService.get_chunks(
        document_id=document_id,
        user_id=user_id,
    )

    if not chunks:
        return {
            "message": "سند پیدا نشد یا متنی برای پاسخ‌گویی وجود ندارد"
        }, 404

    service = DocumentAIService()

    try:
        answer = service.answer_question(
            question,
            chunks,
            language=language,
        )
    except Exception as e:
        return {
            "message": "پاسخ‌گویی ناموفق بود",
            "error": str(e),
        }, 500

    return {
        "document_id": document_id,
        "language": language,
        "question": question,
        "answer": answer,
    }, 200
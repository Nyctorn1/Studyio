from app.models import Document


class DocumentContextService:

    @staticmethod
    def get_chunks(document_id, user_id):
        document = Document.query.filter_by(
            id=document_id,
            user_id=user_id,
        ).first()

        if not document:
            raise ValueError("سند پیدا نشد")

        return [
            chunk.content
            for chunk in document.chunks
        ]

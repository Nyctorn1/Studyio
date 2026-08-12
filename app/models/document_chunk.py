from app import db


class DocumentChunk(db.Model):
    __tablename__ = "document_chunks"

    id = db.Column(db.Integer, primary_key=True)

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    chunk_index = db.Column(
        db.Integer,
        nullable=False,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    characters = db.Column(
        db.Integer,
        nullable=False,
    )

    document = db.relationship(
        "Document",
        back_populates="chunks",
    )
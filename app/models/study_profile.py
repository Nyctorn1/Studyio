from app import db


class StudyProfile(db.Model):
    __tablename__ = "study_profiles"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    level = db.Column(db.String(50), nullable=True)
    daily_goal_minutes = db.Column(db.Integer, nullable=True)

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import StudyProfile


profile_bp = Blueprint("profile", __name__)


@profile_bp.post("/profile")
@jwt_required()
def create_profile():
    user_id = int(get_jwt_identity())

    existing_profile = StudyProfile.query.filter_by(
        user_id=user_id
    ).first()

    if existing_profile:
        return {
            "message": "پروفایل قبلاً ایجاد شده است"
        }, 409

    data = request.get_json() or {}

    level = data.get("level")
    daily_goal_minutes = data.get("daily_goal_minutes")

    profile = StudyProfile(
        user_id=user_id,
        level=level,
        daily_goal_minutes=daily_goal_minutes
    )

    db.session.add(profile)
    db.session.commit()

    return {
        "message": "پروفایل با موفقیت ایجاد شد",
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "level": profile.level,
            "daily_goal_minutes": profile.daily_goal_minutes
        }
    }, 201

@profile_bp.get("/profile")
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())

    profile = StudyProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return {
            "message": "پروفایل پیدا نشد"
        }, 404

    return {
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "level": profile.level,
            "daily_goal_minutes": profile.daily_goal_minutes
        }
    }, 200

@profile_bp.put("/profile")
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())

    profile = StudyProfile.query.filter_by(
        user_id=user_id
    ).first()

    if not profile:
        return {
            "message": "پروفایل پیدا نشد"
        }, 404

    data = request.get_json() or {}

    if "level" in data:
        profile.level = data["level"]

    if "daily_goal_minutes" in data:
        profile.daily_goal_minutes = data["daily_goal_minutes"]

    db.session.commit()

    return {
        "message": "پروفایل با موفقیت به‌روزرسانی شد",
        "profile": {
            "id": profile.id,
            "user_id": profile.user_id,
            "level": profile.level,
            "daily_goal_minutes": profile.daily_goal_minutes
        }
    }, 200
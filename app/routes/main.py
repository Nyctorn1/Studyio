from flask import Blueprint
from sqlalchemy import text
from app import db

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def home():
    return {
        "message": "دستیار مطالعه با موفقیت اجرا شد",
        "status": "فعال"
    }


@main_bp.get("/about")
def about():
    return {
        "message": "این دستیار مطالعه برای یادگیری بهتر ساخته شده است.",
        "status": "فعال"
    }

@main_bp.get("/db-test")
def db_test():
    result = db.session.execute(text("SELECT 1"))
    return {
        "message": "اتصال به PostgreSQL موفق بود",
        "result": result.scalar()
    }
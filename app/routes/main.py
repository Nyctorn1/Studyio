from flask import Blueprint


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
from flask import request

from app import db
from app.auth import auth_bp
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from app.models import User, TokenBlocklist

@auth_bp.post("/register")
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "message": "ایمیل و رمز عبور الزامی هستند"
        }, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {
            "message": "این ایمیل قبلاً ثبت شده است"
        }, 409

    password_hash = generate_password_hash(password)

    user = User(
        email=email,
        password_hash=password_hash
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "کاربر با موفقیت ثبت شد",
        "email": user.email
    }, 201


@auth_bp.post("/login")
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "message": "ایمیل و رمز عبور الزامی هستند"
        }, 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return {
            "message": "ایمیل یا رمز عبور اشتباه است"
        }, 401

    access_token = create_access_token(identity=str(user.id))

    return {
        "message": "ورود موفق بود",
        "email": user.email,
        "access_token": access_token
    }, 200

@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.query.get(int(user_id))

    if not user:
        return {
            "message": "کاربر پیدا نشد"
        }, 404

    return {
        "id": user.id,
        "email": user.email
    }, 200

@auth_bp.post("/logout")
@jwt_required()
def logout():
    jwt_payload = get_jwt()
    jti = jwt_payload["jti"]

    token = TokenBlocklist(jti=jti)

    db.session.add(token)
    db.session.commit()

    return {
        "message": "خروج موفق بود"
    }, 200

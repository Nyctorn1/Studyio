from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from app.models import TokenBlocklist

        jti = jwt_payload["jti"]

        token = TokenBlocklist.query.filter_by(jti=jti).first()

        return token is not None

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.profile import profile_bp
    app.register_blueprint(profile_bp)

    from app.routes.documents import documents_bp
    app.register_blueprint(documents_bp)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.models import User

    return app
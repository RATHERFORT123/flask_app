from flask import Flask, render_template
from dotenv import load_dotenv
import os

from sqlalchemy import text, create_engine

from .extensions import db, migrate, login_manager, csrf
from .models.user import User
import click


from .controllers.common_controller import common_bp
from .controllers.search_controller import search_bp

from .controllers.admin_user_controller import admin_user_bp
from .controllers.admin_brand_controller import admin_brand_bp
from .controllers.admin_category_controller import admin_category_bp
from .controllers.admin_contract_controller import admin_contract_bp
from .controllers.admin_seller_controller import admin_seller_bp

from .controllers.contract_excel_controller import contract_excel_bp
from .controllers.seller_excel_controller import seller_excel_bp

from .controllers.upload_controller import upload_bp


from .controllers.auth_controller import auth_bp
from .controllers.admin_controller import admin_bp
# from .controllers.dashboard_controller import dashboard_bp
from .controllers.user_controller import user_bp
from .controllers.automate_controller import automate_bp
from werkzeug.security import generate_password_hash
def register_cli_commands(app):

    @app.cli.command("create-admin")
    def create_admin_command():
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        from app.extensions import db
    
        # 🔥 Check BOTH username AND email
        admin = User.query.filter(
            (User.username == "admin") | (User.email == "admin@example.com")
        ).first()
    
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                is_admin=True,
                is_verified=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created")
        else:
            print("ℹ️ Admin already exists")

def create_admin():
    admin = User.query.filter_by(username="admin").first()

    if not admin:
        print("🔥 Creating admin user...")

        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
            is_verified=True
        )

        db.session.add(admin)
        db.session.commit()

        print("✅ Admin created (username=admin, password=admin123)")
    else:
        print("ℹ️ Admin already exists")

# --------------------------------------------------
# AUTO-CREATE POSTGRES DATABASE
# --------------------------------------------------
def ensure_database_exists(database_url: str):
    if not database_url.startswith("postgresql"):
        return

    db_name = database_url.rsplit("/", 1)[-1]
    admin_url = database_url.rsplit("/", 1)[0] + "/postgres"

    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name}
        ).scalar()

        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"✅ PostgreSQL database created: {db_name}")


def create_app(config_object="config.DevConfig"):
    load_dotenv()
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(config_object)

    register_cli_commands(app)
    # --------------------------------------------------
    # 🔥 AUTO DETECT BASE PATH
    # --------------------------------------------------
    # BASE PROJECT PATH
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config["BASE_DIR"] = BASE_DIR
    
    # Upload folders
    app.config["CONTRACT_FOLDER"] = os.path.join(BASE_DIR, "app", "contracts_data","pending")
    app.config["SELLER_FOLDER"] = os.path.join(BASE_DIR, "seller_data","pending")
    
    # Create folders if missing
    os.makedirs(app.config["CONTRACT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["SELLER_FOLDER"], exist_ok=True)

    # app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024
    # --------------------------------------------------
    # Ensure DB exists
    # --------------------------------------------------
    ensure_database_exists(app.config["SQLALCHEMY_DATABASE_URI"])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            print(" PostgreSQL connection OK")
        except Exception:
            print("❌ PostgreSQL connection FAILED")
            raise RuntimeError("Database connection failed")
    # try:
    #     with app.app_context():
    #         db.session.execute(text("SELECT 1"))
    #         print(" PostgreSQL connection OK")
    #         # create_admin()
    # except Exception as e:
    #     print("❌ PostgreSQL connection FAILED")
    #     raise RuntimeError("Database connection failed")
        

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    # app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(automate_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(search_bp)

    app.register_blueprint(admin_user_bp)
    app.register_blueprint(admin_brand_bp)
    app.register_blueprint(admin_category_bp)
    app.register_blueprint(admin_contract_bp)
    app.register_blueprint(admin_seller_bp)

    app.register_blueprint(contract_excel_bp)
    app.register_blueprint(seller_excel_bp)

    app.register_blueprint(upload_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    register_errorhandlers(app)
    return app


def register_errorhandlers(app):
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500





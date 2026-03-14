from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "signin"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)  # nullable for Google OAuth users
    profile_pic = db.Column(db.String(256), default="")
    auth_provider = db.Column(db.String(20), default="local")  # "local" or "google"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookmarks = db.relationship("Bookmark", backref="user", lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship("Rating", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # "tool" or "product"
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "item_name", "item_type", name="uq_user_bookmark"),
    )

    def __repr__(self):
        return f"<Bookmark {self.item_name}>"


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tool_name = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1-5
    review_text = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "tool_name", name="uq_user_rating"),
    )

    def __repr__(self):
        return f"<Rating {self.tool_name}: {self.score}>"

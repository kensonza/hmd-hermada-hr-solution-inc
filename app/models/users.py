import uuid
from app.extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from zoneinfo import ZoneInfo  # for PHT

class Users(db.Model):
    __tablename__ = 'hmd_users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_token_id = db.Column(
        db.String(36), 
        unique=True, 
        nullable=False, 
        default=lambda: str(uuid.uuid4())
    )
    
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(25), nullable=False)
    status = db.Column(db.String(12), nullable=False)

    date_created = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(ZoneInfo('Asia/Manila'))
    )

    def __init__(self, first_name, last_name, nickname, email, password, department, role, status):
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.email = email
        self.set_password(password)
        self.department = department
        self.role = role
        self.status = status

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            "id": self.id,
            "user_token_id": self.user_token_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "email": self.email,
            "department": self.department,
            "role": self.role,
            "status": self.status,
            "date_created": self.date_created,
        }

    def __repr__(self):
        return f"<User id={self.id}, email={self.email}>"
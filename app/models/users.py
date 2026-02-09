from app.extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

### User Model ###
class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(20))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    job_title = db.Column(db.String(15))
    department = db.Column(db.String(50))
    role = db.Column(db.String(15))
    status = db.Column(db.String(12))
    created_by = db.Column(db.String(50))
    created_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    modified_by = db.Column(db.String(50))
    modified_date = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def __init__(self, token_id, full_name, email, password, job_title, department, role, status, created_by, modified_by=None):
        self.token_id = token_id
        self.full_name = full_name
        self.email = email
        self.set_password(password)
        self.job_title = job_title
        self.department = department
        self.role = role
        self.status = status
        self.created_by = created_by
        self.created_date = datetime.now(timezone.utc)
        self.modified_by = modified_by
        self.modified_date = datetime.now(timezone.utc)

    # Password security methods
    def set_password(self, password):
        # Hash the password for secure storage.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check a hashed password.
        return check_password_hash(self.password_hash, password)

    # Hide sensitive data in output
    def to_dict(self):
        # Return safe user data for JSON responses.
        return {
            "id": self.id,
            "token_id": self.token_id,
            "full_name": self.full_name,
            "email": self.email,
            "job_title": self.job_title,
            "department": self.department,
            "role": self.role,
            "status": self.status,
            "created_by": self.created_by,
            "created_date": self.created_date,
            "modified_by": self.modified_by,
            "modified_date": self.modified_date,
        }

    def __repr__(self):
        return f"<User id={self.id}>"
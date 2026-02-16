import uuid
from app.extension import db
from datetime import datetime
from zoneinfo import ZoneInfo  # for PHT

class Contact(db.Model):
    __tablename__ = 'hmd_contact'

    id = db.Column(db.Integer, primary_key=True)

    token_id = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)

    # Philippine Time
    date_created = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo('Asia/Manila'))
    )

    def to_dict(self):
        return {
            "id": self.id,
            "token_id": self.token_id,
            "name": self.name,
            "email": self.email,
            "subject": self.subject,
            "message": self.message,
            "date_created": self.date_created,
        }

    def __repr__(self):
        return f"<Contact id={self.id}>"

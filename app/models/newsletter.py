import uuid
from app.extension import db
from datetime import datetime
from zoneinfo import ZoneInfo  # for PHT


class Newsletter(db.Model):
    __tablename__ = 'hmd_newsletter'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    nl_token_id = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    nl_title = db.Column(db.String(255), nullable=False)
    nl_subject = db.Column(db.String(255), nullable=False)
    nl_description = db.Column(db.Text, nullable=False)                     # TinyMCE HTML content
    nl_status = db.Column(db.String(12), nullable=False, default="Active")  # Active / Inactive

    # Philippine Time
    date_created = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo('Asia/Manila'))
    )

    date_updated = db.Column(
        db.DateTime(timezone=True),
        onupdate=lambda: datetime.now(ZoneInfo('Asia/Manila'))
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nl_token_id": self.nl_token_id,
            "nl_title": self.nl_title,
            "nl_subject": self.nl_subject,
            "nl_description": self.nl_description,
            "nl_status": self.nl_status,
            "date_created": self.date_created,
            "date_updated": self.date_updated,
        }

    def __repr__(self):
        return f"<Newsletter id={self.id}, subject={self.nl_subject}>"
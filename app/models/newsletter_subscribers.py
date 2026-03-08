import uuid
from app.extension import db
from datetime import datetime
from zoneinfo import ZoneInfo  # for PHT

class NewsletterSubscribers(db.Model):
    __tablename__ = 'hmd_newsletter_subscribers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    ns_token_id = db.Column(
        db.String(36),
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4())
    )

    ns_email = db.Column(db.String(255), nullable=False)
    ns_status = db.Column(db.String(12), nullable=False, default="Subscribed") # Subscribed and Unsubscribed

    # Philippine Time
    date_created = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo('Asia/Manila'))
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ns_token_id": self.ns_token_id,
            "ns_email": self.ns_email,
            "ns_status": self.ns_status,
            "date_created": self.date_created,
        }

    def __repr__(self):
        return f"<NewsletterSubscriber id={self.id}, ns_email={self.ns_email}>"
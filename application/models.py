from .database import db
from datetime import datetime, timedelta

class Event(db.Model):
    __tablename__ = 'events'  # Customize table name if needed

    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=1))
    is_active = db.Column(db.Boolean, default=True)
    recurrences = db.relationship('Recurrence', backref='event', lazy='dynamic')

class Recurrence(db.Model):
    __tablename__ = 'recurrences'  # Customize table name if needed

    recurrence_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    type = db.Column(db.Enum('daily', 'weekly', 'monthly'), nullable=False)
    interval = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=True)  # 1-7 or None
    month_of_year = db.Column(db.Integer, nullable=True)  # 1-12 or None
    end_date = db.Column(db.DateTime)
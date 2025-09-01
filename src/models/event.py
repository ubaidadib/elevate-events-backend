from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # premium, vip, exclusive
    price = db.Column(db.Float, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False, default=3)
    image_url = db.Column(db.String(500))
    venue_location = db.Column(db.String(200))
    features = db.Column(db.Text)  # JSON string of features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'max_guests': self.max_guests,
            'date': self.date.isoformat() if self.date else None,
            'duration_hours': self.duration_hours,
            'image_url': self.image_url,
            'venue_location': self.venue_location,
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_available_events(category=None):
        query = Event.query.filter_by(is_active=True)
        if category and category != 'all':
            query = query.filter_by(category=category)
        return query.filter(Event.date > datetime.utcnow()).order_by(Event.date).all()
    
    def get_available_spots(self):
        booked_spots = sum([booking.guest_count for booking in self.bookings if booking.status == 'confirmed'])
        return max(0, self.max_guests - booked_spots)
    
    def is_available(self, guest_count=1):
        return self.get_available_spots() >= guest_count and self.date > datetime.utcnow()


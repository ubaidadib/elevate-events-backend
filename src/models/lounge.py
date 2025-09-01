from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class Lounge(db.Model):
    __tablename__ = 'lounges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # standard, premium, vip, exclusive
    capacity = db.Column(db.Integer, nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    minimum_hours = db.Column(db.Integer, default=2)
    maximum_hours = db.Column(db.Integer, default=8)
    
    # Lounge Features
    features = db.Column(db.Text)  # JSON string of features
    amenities = db.Column(db.Text)  # JSON string of amenities
    image_urls = db.Column(db.Text)  # JSON string of image URLs
    
    # Availability
    is_active = db.Column(db.Boolean, default=True)
    operating_hours_start = db.Column(db.String(10), default='18:00')  # 6:00 PM
    operating_hours_end = db.Column(db.String(10), default='02:00')    # 2:00 AM
    
    # Location and Setup
    floor_level = db.Column(db.String(50))
    max_standing = db.Column(db.Integer)
    max_seated = db.Column(db.Integer)
    has_private_bar = db.Column(db.Boolean, default=False)
    has_sound_system = db.Column(db.Boolean, default=True)
    has_lighting_control = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='lounge', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'capacity': self.capacity,
            'hourly_rate': self.hourly_rate,
            'minimum_hours': self.minimum_hours,
            'maximum_hours': self.maximum_hours,
            'features': self.features,
            'amenities': self.amenities,
            'image_urls': self.image_urls,
            'is_active': self.is_active,
            'operating_hours_start': self.operating_hours_start,
            'operating_hours_end': self.operating_hours_end,
            'floor_level': self.floor_level,
            'max_standing': self.max_standing,
            'max_seated': self.max_seated,
            'has_private_bar': self.has_private_bar,
            'has_sound_system': self.has_sound_system,
            'has_lighting_control': self.has_lighting_control,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def get_available_lounges(category=None):
        query = Lounge.query.filter_by(is_active=True)
        if category and category != 'all':
            query = query.filter_by(category=category)
        return query.order_by(Lounge.category, Lounge.hourly_rate).all()
    
    def is_available(self, date, start_time, duration_hours):
        """Check if lounge is available for the specified time slot"""
        from datetime import datetime, timedelta
        from .booking import Booking
        
        # Parse the booking datetime
        booking_start = datetime.combine(date, datetime.strptime(start_time, '%H:%M').time())
        booking_end = booking_start + timedelta(hours=duration_hours)
        
        # Check for conflicting bookings
        conflicting_bookings = Booking.query.filter(
            Booking.lounge_id == self.id,
            Booking.booking_date == date,
            Booking.status.in_(['confirmed', 'checked_in']),
            # Check for time overlap
            db.or_(
                db.and_(
                    Booking.booking_time <= start_time,
                    db.func.time(
                        db.func.datetime(
                            Booking.booking_time, 
                            f'+{Booking.duration_hours} hours'
                        )
                    ) > start_time
                ),
                db.and_(
                    Booking.booking_time < booking_end.strftime('%H:%M'),
                    Booking.booking_time >= start_time
                )
            )
        ).first()
        
        return conflicting_bookings is None
    
    def calculate_total_cost(self, duration_hours):
        """Calculate total cost for booking this lounge"""
        if duration_hours < self.minimum_hours:
            duration_hours = self.minimum_hours
        elif duration_hours > self.maximum_hours:
            duration_hours = self.maximum_hours
        
        return self.hourly_rate * duration_hours


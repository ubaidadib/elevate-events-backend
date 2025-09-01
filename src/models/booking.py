from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
from .user import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(50), unique=True, nullable=False)
    
    # Guest Information
    guest_name = db.Column(db.String(200), nullable=False)
    guest_email = db.Column(db.String(200), nullable=False)
    guest_phone = db.Column(db.String(50))
    guest_count = db.Column(db.Integer, nullable=False, default=1)
    special_requests = db.Column(db.Text)
    
    # Booking Details
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    lounge_id = db.Column(db.Integer, db.ForeignKey('lounges.id'), nullable=True)
    booking_date = db.Column(db.DateTime, nullable=False)
    booking_time = db.Column(db.String(10), nullable=False)  # e.g., "19:00"
    duration_hours = db.Column(db.Integer, nullable=False, default=2)
    
    # Payment Information
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(50), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50))  # stripe, paypal, klarna
    payment_reference = db.Column(db.String(200))
    
    # Status and QR Code
    status = db.Column(db.String(50), default='pending')  # pending, confirmed, cancelled, completed
    qr_code = db.Column(db.String(500))  # QR code data or URL
    check_in_time = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User relationship (optional, for registered users)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
    
    @staticmethod
    def generate_booking_reference():
        return f"EE{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_reference': self.booking_reference,
            'guest_name': self.guest_name,
            'guest_email': self.guest_email,
            'guest_phone': self.guest_phone,
            'guest_count': self.guest_count,
            'special_requests': self.special_requests,
            'event_id': self.event_id,
            'lounge_id': self.lounge_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'booking_time': self.booking_time,
            'duration_hours': self.duration_hours,
            'total_amount': self.total_amount,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'status': self.status,
            'qr_code': self.qr_code,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def generate_qr_code_data(self):
        """Generate QR code data for booking verification"""
        return f"ELEVATE_BOOKING:{self.booking_reference}:{self.guest_name}:{self.booking_date.strftime('%Y-%m-%d')}:{self.booking_time}"
    
    def confirm_booking(self):
        """Confirm the booking and generate QR code"""
        self.status = 'confirmed'
        self.qr_code = self.generate_qr_code_data()
        self.updated_at = datetime.utcnow()
    
    def check_in(self):
        """Check in the guest"""
        self.check_in_time = datetime.utcnow()
        self.status = 'checked_in'
        self.updated_at = datetime.utcnow()


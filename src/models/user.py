from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    
    # Personal Information
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    
    # Preferences
    preferred_language = db.Column(db.String(10), default='en')
    marketing_emails = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    memberships = db.relationship('Membership', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash"""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'preferred_language': self.preferred_language,
            'marketing_emails': self.marketing_emails,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_active_membership(self):
        """Get user's active membership"""
        from .membership import Membership
        return Membership.query.filter_by(
            user_id=self.id,
            is_active=True
        ).filter(
            Membership.end_date > datetime.utcnow()
        ).first()
    
    def has_membership_tier(self, tier_slug):
        """Check if user has specific membership tier"""
        membership = self.get_active_membership()
        return membership and membership.tier.slug == tier_slug if membership else False

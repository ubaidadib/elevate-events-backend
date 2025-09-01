from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from .user import db

class MembershipTier(db.Model):
    __tablename__ = 'membership_tiers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Standard, VIP, Premium Elite
    slug = db.Column(db.String(50), unique=True, nullable=False)  # standard, vip, premium
    description = db.Column(db.Text)
    monthly_price = db.Column(db.Float, nullable=False)
    annual_price = db.Column(db.Float)  # Optional annual pricing
    
    # Benefits
    discount_percentage = db.Column(db.Float, default=0)  # 10%, 20%, 30%
    priority_booking = db.Column(db.Boolean, default=False)
    complimentary_drinks = db.Column(db.Integer, default=0)  # Number per visit
    private_lounge_access = db.Column(db.Boolean, default=False)
    concierge_service = db.Column(db.String(50), default='basic')  # basic, dedicated, personal
    exclusive_events = db.Column(db.Boolean, default=False)
    birthday_perks = db.Column(db.Boolean, default=False)
    transportation_service = db.Column(db.Boolean, default=False)
    
    # Features (JSON string)
    features = db.Column(db.Text)  # JSON list of features
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = db.relationship('Membership', backref='tier', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'monthly_price': self.monthly_price,
            'annual_price': self.annual_price,
            'discount_percentage': self.discount_percentage,
            'priority_booking': self.priority_booking,
            'complimentary_drinks': self.complimentary_drinks,
            'private_lounge_access': self.private_lounge_access,
            'concierge_service': self.concierge_service,
            'exclusive_events': self.exclusive_events,
            'birthday_perks': self.birthday_perks,
            'transportation_service': self.transportation_service,
            'features': self.features,
            'is_active': self.is_active,
            'sort_order': self.sort_order
        }

class Membership(db.Model):
    __tablename__ = 'memberships'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tier_id = db.Column(db.Integer, db.ForeignKey('membership_tiers.id'), nullable=False)
    
    # Membership Details
    membership_number = db.Column(db.String(50), unique=True, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, annual
    
    # Payment Information
    payment_status = db.Column(db.String(50), default='active')  # active, suspended, cancelled, expired
    last_payment_date = db.Column(db.DateTime)
    next_payment_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(50))
    
    # Usage Tracking
    events_attended = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    complimentary_drinks_used = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.membership_number:
            self.membership_number = self.generate_membership_number()
        if not self.end_date:
            self.set_end_date()
    
    def generate_membership_number(self):
        """Generate unique membership number"""
        import uuid
        return f"EE{datetime.now().year}{str(uuid.uuid4())[:8].upper()}"
    
    def set_end_date(self):
        """Set end date based on billing cycle"""
        if self.billing_cycle == 'annual':
            self.end_date = self.start_date + timedelta(days=365)
            self.next_payment_date = self.end_date
        else:  # monthly
            self.end_date = self.start_date + timedelta(days=30)
            self.next_payment_date = self.end_date
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier_id': self.tier_id,
            'membership_number': self.membership_number,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'billing_cycle': self.billing_cycle,
            'payment_status': self.payment_status,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'next_payment_date': self.next_payment_date.isoformat() if self.next_payment_date else None,
            'payment_method': self.payment_method,
            'events_attended': self.events_attended,
            'total_bookings': self.total_bookings,
            'total_spent': self.total_spent,
            'complimentary_drinks_used': self.complimentary_drinks_used,
            'is_active': self.is_active,
            'auto_renew': self.auto_renew,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tier': self.tier.to_dict() if self.tier else None
        }
    
    def is_expired(self):
        """Check if membership is expired"""
        return datetime.utcnow() > self.end_date
    
    def days_until_expiry(self):
        """Get days until membership expires"""
        if self.is_expired():
            return 0
        return (self.end_date - datetime.utcnow()).days
    
    def renew_membership(self):
        """Renew membership for another billing cycle"""
        if self.billing_cycle == 'annual':
            self.end_date = self.end_date + timedelta(days=365)
        else:
            self.end_date = self.end_date + timedelta(days=30)
        
        self.next_payment_date = self.end_date
        self.last_payment_date = datetime.utcnow()
        self.payment_status = 'active'
        self.updated_at = datetime.utcnow()
    
    def apply_discount(self, amount):
        """Apply membership discount to amount"""
        if self.tier and self.is_active and not self.is_expired():
            discount = amount * (self.tier.discount_percentage / 100)
            return amount - discount
        return amount


#!/usr/bin/env python3
"""
Database seeding script for Elevate Events GmbH
Populates the database with sample data for testing and demonstration
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
import json
from src.models.user import db, User
from src.models.event import Event
from src.models.lounge import Lounge
from src.models.membership import MembershipTier, Membership
from src.main import app

def seed_membership_tiers():
    """Create membership tiers"""
    print("Seeding membership tiers...")
    
    tiers = [
        {
            'name': 'Standard',
            'slug': 'standard',
            'description': 'Perfect for occasional luxury experiences',
            'monthly_price': 99.00,
            'annual_price': 999.00,
            'discount_percentage': 10.0,
            'priority_booking': False,
            'complimentary_drinks': 2,
            'private_lounge_access': False,
            'concierge_service': 'basic',
            'exclusive_events': False,
            'birthday_perks': True,
            'transportation_service': False,
            'features': json.dumps([
                '10% discount on all bookings',
                '2 complimentary drinks per visit',
                'Birthday celebration perks',
                'Basic concierge service',
                'Priority customer support'
            ]),
            'sort_order': 1
        },
        {
            'name': 'VIP',
            'slug': 'vip',
            'description': 'Enhanced luxury with exclusive privileges',
            'monthly_price': 199.00,
            'annual_price': 1999.00,
            'discount_percentage': 20.0,
            'priority_booking': True,
            'complimentary_drinks': 4,
            'private_lounge_access': True,
            'concierge_service': 'dedicated',
            'exclusive_events': True,
            'birthday_perks': True,
            'transportation_service': False,
            'features': json.dumps([
                '20% discount on all bookings',
                'Priority booking access',
                '4 complimentary drinks per visit',
                'Private lounge access',
                'Dedicated concierge service',
                'Exclusive VIP events',
                'Birthday celebration package',
                'Guest privileges for +1'
            ]),
            'sort_order': 2
        },
        {
            'name': 'Premium Elite',
            'slug': 'premium',
            'description': 'Ultimate luxury with personalized service',
            'monthly_price': 399.00,
            'annual_price': 3999.00,
            'discount_percentage': 30.0,
            'priority_booking': True,
            'complimentary_drinks': 8,
            'private_lounge_access': True,
            'concierge_service': 'personal',
            'exclusive_events': True,
            'birthday_perks': True,
            'transportation_service': True,
            'features': json.dumps([
                '30% discount on all bookings',
                'First priority booking access',
                '8 complimentary drinks per visit',
                'Private lounge & VIP areas access',
                'Personal concierge service',
                'Exclusive Premium Elite events',
                'Luxury birthday celebration',
                'Complimentary transportation service',
                'Guest privileges for up to 3 guests',
                'Personalized event planning'
            ]),
            'sort_order': 3
        }
    ]
    
    for tier_data in tiers:
        existing_tier = MembershipTier.query.filter_by(slug=tier_data['slug']).first()
        if not existing_tier:
            tier = MembershipTier(**tier_data)
            db.session.add(tier)
    
    db.session.commit()
    print("✅ Membership tiers seeded successfully")

def seed_lounges():
    """Create sample lounges"""
    print("Seeding lounges...")
    
    lounges = [
        {
            'name': 'The Golden Lounge',
            'description': 'Our signature lounge featuring panoramic city views and premium amenities',
            'category': 'premium',
            'capacity': 25,
            'hourly_rate': 150.00,
            'minimum_hours': 2,
            'maximum_hours': 6,
            'features': json.dumps([
                'Panoramic city views',
                'Premium sound system',
                'Dedicated bartender',
                'Climate control',
                'Private restroom'
            ]),
            'amenities': json.dumps([
                'Premium bar selection',
                'Luxury seating',
                'High-speed WiFi',
                'Charging stations',
                'Coat check'
            ]),
            'image_urls': json.dumps([
                '/assets/lounge-golden-1.jpg',
                '/assets/lounge-golden-2.jpg'
            ]),
            'floor_level': '15th Floor',
            'max_standing': 35,
            'max_seated': 25,
            'has_private_bar': True,
            'has_sound_system': True,
            'has_lighting_control': True
        },
        {
            'name': 'VIP Sanctuary',
            'description': 'Exclusive VIP lounge with personalized service and ultimate privacy',
            'category': 'vip',
            'capacity': 15,
            'hourly_rate': 250.00,
            'minimum_hours': 3,
            'maximum_hours': 8,
            'features': json.dumps([
                'Complete privacy',
                'Personal concierge',
                'Premium champagne service',
                'Custom lighting',
                'Private entrance'
            ]),
            'amenities': json.dumps([
                'Exclusive bar collection',
                'Luxury leather seating',
                'Private dining area',
                'Entertainment system',
                'Personal butler service'
            ]),
            'image_urls': json.dumps([
                '/assets/lounge-vip-1.jpg',
                '/assets/lounge-vip-2.jpg'
            ]),
            'floor_level': '20th Floor',
            'max_standing': 20,
            'max_seated': 15,
            'has_private_bar': True,
            'has_sound_system': True,
            'has_lighting_control': True
        },
        {
            'name': 'Elite Penthouse',
            'description': 'Ultimate luxury penthouse lounge for the most discerning guests',
            'category': 'exclusive',
            'capacity': 12,
            'hourly_rate': 500.00,
            'minimum_hours': 4,
            'maximum_hours': 12,
            'features': json.dumps([
                'Penthouse terrace',
                'Personal chef available',
                'Helicopter landing pad access',
                'Private elevator',
                'Luxury spa amenities'
            ]),
            'amenities': json.dumps([
                'Rare spirits collection',
                'Italian leather furniture',
                'Private kitchen',
                'Spa facilities',
                'Personal staff'
            ]),
            'image_urls': json.dumps([
                '/assets/lounge-penthouse-1.jpg',
                '/assets/lounge-penthouse-2.jpg'
            ]),
            'floor_level': 'Penthouse',
            'max_standing': 15,
            'max_seated': 12,
            'has_private_bar': True,
            'has_sound_system': True,
            'has_lighting_control': True
        }
    ]
    
    for lounge_data in lounges:
        existing_lounge = Lounge.query.filter_by(name=lounge_data['name']).first()
        if not existing_lounge:
            lounge = Lounge(**lounge_data)
            db.session.add(lounge)
    
    db.session.commit()
    print("✅ Lounges seeded successfully")

def seed_events():
    """Create sample events"""
    print("Seeding events...")
    
    # Create events for the next 3 months
    base_date = datetime.now() + timedelta(days=7)
    
    events = [
        {
            'title': 'Jazz & Champagne Evening',
            'description': 'An intimate evening featuring live jazz performances with premium champagne tasting',
            'category': 'premium',
            'price': 125.00,
            'max_guests': 40,
            'date': base_date + timedelta(days=5),
            'duration_hours': 4,
            'image_url': '/assets/event-jazz.jpg',
            'venue_location': 'The Golden Lounge',
            'features': json.dumps([
                'Live jazz trio performance',
                'Premium champagne selection',
                'Gourmet canapés',
                'Professional photography',
                'Welcome cocktail'
            ])
        },
        {
            'title': 'Exclusive Wine Tasting',
            'description': 'Private wine tasting featuring rare vintages from renowned vineyards',
            'category': 'vip',
            'price': 200.00,
            'max_guests': 25,
            'date': base_date + timedelta(days=12),
            'duration_hours': 3,
            'image_url': '/assets/event-wine.jpg',
            'venue_location': 'VIP Sanctuary',
            'features': json.dumps([
                'Sommelier-guided tasting',
                'Rare vintage wines',
                'Artisanal cheese pairing',
                'Take-home wine selection',
                'Certificate of participation'
            ])
        },
        {
            'title': 'Michelin Star Chef Experience',
            'description': 'Exclusive dining experience with a Michelin-starred chef',
            'category': 'exclusive',
            'price': 350.00,
            'max_guests': 12,
            'date': base_date + timedelta(days=20),
            'duration_hours': 5,
            'image_url': '/assets/event-chef.jpg',
            'venue_location': 'Elite Penthouse',
            'features': json.dumps([
                'Michelin-starred chef',
                '7-course tasting menu',
                'Wine pairing',
                'Meet & greet with chef',
                'Signed cookbook',
                'Private dining experience'
            ])
        },
        {
            'title': 'Rooftop Sunset Cocktails',
            'description': 'Sophisticated cocktail experience with panoramic sunset views',
            'category': 'premium',
            'price': 85.00,
            'max_guests': 50,
            'date': base_date + timedelta(days=15),
            'duration_hours': 3,
            'image_url': '/assets/event-sunset.jpg',
            'venue_location': 'Rooftop Terrace',
            'features': json.dumps([
                'Panoramic city views',
                'Signature cocktails',
                'Live acoustic music',
                'Sunset timing',
                'Photography service'
            ])
        },
        {
            'title': 'Whiskey & Cigars Night',
            'description': 'Premium whiskey tasting paired with finest cigars in our smoking lounge',
            'category': 'vip',
            'price': 175.00,
            'max_guests': 20,
            'date': base_date + timedelta(days=25),
            'duration_hours': 4,
            'image_url': '/assets/event-whiskey.jpg',
            'venue_location': 'Private Smoking Lounge',
            'features': json.dumps([
                'Premium whiskey selection',
                'Cuban cigars',
                'Whiskey expert guidance',
                'Leather lounge seating',
                'Complimentary humidor'
            ])
        }
    ]
    
    for event_data in events:
        existing_event = Event.query.filter_by(title=event_data['title']).first()
        if not existing_event:
            event = Event(**event_data)
            db.session.add(event)
    
    db.session.commit()
    print("✅ Events seeded successfully")

def seed_sample_users():
    """Create sample users for testing"""
    print("Seeding sample users...")
    
    users = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+49 30 12345678',
            'preferred_language': 'en'
        },
        {
            'username': 'maria_schmidt',
            'email': 'maria@example.com',
            'first_name': 'Maria',
            'last_name': 'Schmidt',
            'phone': '+49 30 87654321',
            'preferred_language': 'de'
        }
    ]
    
    for user_data in users:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(**user_data)
            user.set_password('password123')  # Default password for testing
            db.session.add(user)
    
    db.session.commit()
    print("✅ Sample users seeded successfully")

def main():
    """Main seeding function"""
    print("🌱 Starting database seeding for Elevate Events GmbH...")
    
    with app.app_context():
        try:
            # Seed all data
            seed_membership_tiers()
            seed_lounges()
            seed_events()
            seed_sample_users()
            
            print("\n🎉 Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   • Membership Tiers: {MembershipTier.query.count()}")
            print(f"   • Lounges: {Lounge.query.count()}")
            print(f"   • Events: {Event.query.count()}")
            print(f"   • Users: {User.query.count()}")
            
        except Exception as e:
            print(f"❌ Error during seeding: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    main()


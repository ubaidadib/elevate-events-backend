from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.user import db, User
from src.models.booking import Booking
from src.models.event import Event
from src.models.lounge import Lounge
from src.models.membership import Membership

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['guest_name', 'guest_email', 'guest_count', 'booking_date', 'booking_time']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse booking date
        booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
        
        # Validate booking is in the future
        if booking_date <= datetime.now().date():
            return jsonify({
                'success': False,
                'error': 'Booking date must be in the future'
            }), 400
        
        # Calculate total amount
        total_amount = 0
        event = None
        lounge = None
        
        if 'event_id' in data and data['event_id']:
            event = Event.query.get(data['event_id'])
            if not event or not event.is_available(data['guest_count']):
                return jsonify({
                    'success': False,
                    'error': 'Event not available for requested guest count'
                }), 400
            total_amount = event.price * data['guest_count']
        
        elif 'lounge_id' in data and data['lounge_id']:
            lounge = Lounge.query.get(data['lounge_id'])
            duration_hours = data.get('duration_hours', 2)
            
            if not lounge or not lounge.is_available(booking_date, data['booking_time'], duration_hours):
                return jsonify({
                    'success': False,
                    'error': 'Lounge not available for requested time slot'
                }), 400
            
            total_amount = lounge.calculate_total_cost(duration_hours)
        
        else:
            return jsonify({
                'success': False,
                'error': 'Either event_id or lounge_id must be provided'
            }), 400
        
        # Apply membership discount if user is logged in
        user = None
        if 'user_id' in data and data['user_id']:
            user = User.query.get(data['user_id'])
            if user:
                membership = user.get_active_membership()
                if membership:
                    total_amount = membership.apply_discount(total_amount)
        
        # Create booking
        booking = Booking(
            guest_name=data['guest_name'],
            guest_email=data['guest_email'],
            guest_phone=data.get('guest_phone'),
            guest_count=data['guest_count'],
            special_requests=data.get('special_requests'),
            event_id=data.get('event_id'),
            lounge_id=data.get('lounge_id'),
            booking_date=booking_date,
            booking_time=data['booking_time'],
            duration_hours=data.get('duration_hours', 2),
            total_amount=total_amount,
            user_id=data.get('user_id')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': booking.to_dict(),
            'message': 'Booking created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/bookings/<booking_reference>', methods=['GET'])
def get_booking(booking_reference):
    """Get booking details by reference"""
    try:
        booking = Booking.query.filter_by(booking_reference=booking_reference).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404
        
        booking_dict = booking.to_dict()
        
        # Add event or lounge details
        if booking.event:
            booking_dict['event'] = booking.event.to_dict()
        if booking.lounge:
            booking_dict['lounge'] = booking.lounge.to_dict()
        
        return jsonify({
            'success': True,
            'booking': booking_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/bookings/<booking_reference>/confirm', methods=['POST'])
def confirm_booking(booking_reference):
    """Confirm a booking and generate QR code"""
    try:
        booking = Booking.query.filter_by(booking_reference=booking_reference).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404
        
        if booking.status != 'pending':
            return jsonify({
                'success': False,
                'error': 'Booking cannot be confirmed'
            }), 400
        
        # Update payment status (in real implementation, this would be done by payment webhook)
        data = request.get_json() or {}
        booking.payment_status = 'paid'
        booking.payment_method = data.get('payment_method', 'stripe')
        booking.payment_reference = data.get('payment_reference')
        
        # Confirm booking and generate QR code
        booking.confirm_booking()
        
        # Update membership usage if applicable
        if booking.user:
            membership = booking.user.get_active_membership()
            if membership:
                membership.total_bookings += 1
                membership.total_spent += booking.total_amount
                membership.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': booking.to_dict(),
            'message': 'Booking confirmed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/bookings/<booking_reference>/checkin', methods=['POST'])
def checkin_booking(booking_reference):
    """Check in a guest using booking reference"""
    try:
        booking = Booking.query.filter_by(booking_reference=booking_reference).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404
        
        if booking.status != 'confirmed':
            return jsonify({
                'success': False,
                'error': 'Booking must be confirmed before check-in'
            }), 400
        
        if booking.check_in_time:
            return jsonify({
                'success': False,
                'error': 'Guest already checked in',
                'check_in_time': booking.check_in_time.isoformat()
            }), 400
        
        # Check in the guest
        booking.check_in()
        
        # Update membership usage
        if booking.user:
            membership = booking.user.get_active_membership()
            if membership:
                membership.events_attended += 1
                membership.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': booking.to_dict(),
            'message': 'Guest checked in successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/bookings/<booking_reference>/cancel', methods=['POST'])
def cancel_booking(booking_reference):
    """Cancel a booking"""
    try:
        booking = Booking.query.filter_by(booking_reference=booking_reference).first()
        
        if not booking:
            return jsonify({
                'success': False,
                'error': 'Booking not found'
            }), 404
        
        if booking.status in ['cancelled', 'completed']:
            return jsonify({
                'success': False,
                'error': 'Booking cannot be cancelled'
            }), 400
        
        # Check cancellation policy (24 hours before booking)
        booking_datetime = datetime.combine(booking.booking_date, datetime.strptime(booking.booking_time, '%H:%M').time())
        if datetime.now() > booking_datetime - timedelta(hours=24):
            return jsonify({
                'success': False,
                'error': 'Cancellation must be made at least 24 hours before booking time'
            }), 400
        
        booking.status = 'cancelled'
        booking.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking': booking.to_dict(),
            'message': 'Booking cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/users/<int:user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    """Get all bookings for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
        
        bookings_data = []
        for booking in bookings:
            booking_dict = booking.to_dict()
            if booking.event:
                booking_dict['event'] = booking.event.to_dict()
            if booking.lounge:
                booking_dict['lounge'] = booking.lounge.to_dict()
            bookings_data.append(booking_dict)
        
        return jsonify({
            'success': True,
            'bookings': bookings_data,
            'total': len(bookings_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bookings_bp.route('/availability/lounges', methods=['GET'])
def check_lounge_availability():
    """Check lounge availability for specific date and time"""
    try:
        date_str = request.args.get('date')
        time_str = request.args.get('time')
        duration = int(request.args.get('duration', 2))
        category = request.args.get('category', 'all')
        
        if not date_str or not time_str:
            return jsonify({
                'success': False,
                'error': 'Date and time parameters are required'
            }), 400
        
        booking_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        lounges = Lounge.get_available_lounges(category)
        available_lounges = []
        
        for lounge in lounges:
            if lounge.is_available(booking_date, time_str, duration):
                lounge_dict = lounge.to_dict()
                lounge_dict['total_cost'] = lounge.calculate_total_cost(duration)
                available_lounges.append(lounge_dict)
        
        return jsonify({
            'success': True,
            'available_lounges': available_lounges,
            'date': date_str,
            'time': time_str,
            'duration': duration
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


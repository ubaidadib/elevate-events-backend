from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.user import db
from src.models.event import Event

events_bp = Blueprint('events', __name__)

@events_bp.route('/events', methods=['GET'])
def get_events():
    """Get all available events with optional category filtering"""
    try:
        category = request.args.get('category', 'all')
        events = Event.get_available_events(category)
        
        events_data = []
        for event in events:
            event_dict = event.to_dict()
            event_dict['available_spots'] = event.get_available_spots()
            events_data.append(event_dict)
        
        return jsonify({
            'success': True,
            'events': events_data,
            'total': len(events_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Get specific event details"""
    try:
        event = Event.query.get_or_404(event_id)
        
        if not event.is_active:
            return jsonify({
                'success': False,
                'error': 'Event not found or inactive'
            }), 404
        
        event_dict = event.to_dict()
        event_dict['available_spots'] = event.get_available_spots()
        
        return jsonify({
            'success': True,
            'event': event_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/events/<int:event_id>/availability', methods=['GET'])
def check_event_availability(event_id):
    """Check event availability for specific guest count"""
    try:
        event = Event.query.get_or_404(event_id)
        guest_count = int(request.args.get('guests', 1))
        
        is_available = event.is_available(guest_count)
        available_spots = event.get_available_spots()
        
        return jsonify({
            'success': True,
            'available': is_available,
            'available_spots': available_spots,
            'requested_guests': guest_count,
            'event_date': event.date.isoformat() if event.date else None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/events', methods=['POST'])
def create_event():
    """Create a new event (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category', 'price', 'max_guests', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse date
        event_date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        
        # Create event
        event = Event(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            price=float(data['price']),
            max_guests=int(data['max_guests']),
            date=event_date,
            duration_hours=data.get('duration_hours', 3),
            image_url=data.get('image_url'),
            venue_location=data.get('venue_location'),
            features=data.get('features')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'event': event.to_dict(),
            'message': 'Event created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event (admin only)"""
    try:
        event = Event.query.get_or_404(event_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'category' in data:
            event.category = data['category']
        if 'price' in data:
            event.price = float(data['price'])
        if 'max_guests' in data:
            event.max_guests = int(data['max_guests'])
        if 'date' in data:
            event.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        if 'duration_hours' in data:
            event.duration_hours = int(data['duration_hours'])
        if 'image_url' in data:
            event.image_url = data['image_url']
        if 'venue_location' in data:
            event.venue_location = data['venue_location']
        if 'features' in data:
            event.features = data['features']
        if 'is_active' in data:
            event.is_active = bool(data['is_active'])
        
        event.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'event': event.to_dict(),
            'message': 'Event updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@events_bp.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete an event (admin only)"""
    try:
        event = Event.query.get_or_404(event_id)
        
        # Check if event has bookings
        if event.bookings:
            return jsonify({
                'success': False,
                'error': 'Cannot delete event with existing bookings'
            }), 400
        
        db.session.delete(event)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Event deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


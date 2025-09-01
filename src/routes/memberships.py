from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.user import db, User
from src.models.membership import MembershipTier, Membership

memberships_bp = Blueprint('memberships', __name__)

@memberships_bp.route('/membership-tiers', methods=['GET'])
def get_membership_tiers():
    """Get all available membership tiers"""
    try:
        tiers = MembershipTier.query.filter_by(is_active=True).order_by(MembershipTier.sort_order).all()
        
        tiers_data = [tier.to_dict() for tier in tiers]
        
        return jsonify({
            'success': True,
            'tiers': tiers_data,
            'total': len(tiers_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/membership-tiers/<tier_slug>', methods=['GET'])
def get_membership_tier(tier_slug):
    """Get specific membership tier details"""
    try:
        tier = MembershipTier.query.filter_by(slug=tier_slug, is_active=True).first()
        
        if not tier:
            return jsonify({
                'success': False,
                'error': 'Membership tier not found'
            }), 404
        
        return jsonify({
            'success': True,
            'tier': tier.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/memberships', methods=['POST'])
def create_membership():
    """Create a new membership for a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'tier_id', 'billing_cycle']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Validate tier exists
        tier = MembershipTier.query.get(data['tier_id'])
        if not tier or not tier.is_active:
            return jsonify({
                'success': False,
                'error': 'Membership tier not found or inactive'
            }), 404
        
        # Check if user already has an active membership
        existing_membership = user.get_active_membership()
        if existing_membership:
            return jsonify({
                'success': False,
                'error': 'User already has an active membership'
            }), 400
        
        # Create membership
        membership = Membership(
            user_id=data['user_id'],
            tier_id=data['tier_id'],
            billing_cycle=data['billing_cycle'],
            payment_method=data.get('payment_method')
        )
        
        db.session.add(membership)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'membership': membership.to_dict(),
            'message': 'Membership created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/users/<int:user_id>/membership', methods=['GET'])
def get_user_membership(user_id):
    """Get user's current membership"""
    try:
        user = User.query.get_or_404(user_id)
        membership = user.get_active_membership()
        
        if not membership:
            return jsonify({
                'success': True,
                'membership': None,
                'message': 'User has no active membership'
            }), 200
        
        return jsonify({
            'success': True,
            'membership': membership.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/memberships/<int:membership_id>/renew', methods=['POST'])
def renew_membership(membership_id):
    """Renew a membership"""
    try:
        membership = Membership.query.get_or_404(membership_id)
        
        if not membership.is_active:
            return jsonify({
                'success': False,
                'error': 'Membership is not active'
            }), 400
        
        # Process payment (in real implementation)
        data = request.get_json() or {}
        payment_method = data.get('payment_method', membership.payment_method)
        
        # Renew membership
        membership.renew_membership()
        if payment_method:
            membership.payment_method = payment_method
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'membership': membership.to_dict(),
            'message': 'Membership renewed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/memberships/<int:membership_id>/cancel', methods=['POST'])
def cancel_membership(membership_id):
    """Cancel a membership"""
    try:
        membership = Membership.query.get_or_404(membership_id)
        
        if not membership.is_active:
            return jsonify({
                'success': False,
                'error': 'Membership is already inactive'
            }), 400
        
        membership.is_active = False
        membership.auto_renew = False
        membership.payment_status = 'cancelled'
        membership.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'membership': membership.to_dict(),
            'message': 'Membership cancelled successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/memberships/<int:membership_id>/upgrade', methods=['POST'])
def upgrade_membership(membership_id):
    """Upgrade membership to a higher tier"""
    try:
        membership = Membership.query.get_or_404(membership_id)
        data = request.get_json()
        
        if 'new_tier_id' not in data:
            return jsonify({
                'success': False,
                'error': 'new_tier_id is required'
            }), 400
        
        new_tier = MembershipTier.query.get(data['new_tier_id'])
        if not new_tier or not new_tier.is_active:
            return jsonify({
                'success': False,
                'error': 'New membership tier not found or inactive'
            }), 404
        
        # Validate upgrade (new tier should have higher price)
        if new_tier.monthly_price <= membership.tier.monthly_price:
            return jsonify({
                'success': False,
                'error': 'Can only upgrade to a higher tier'
            }), 400
        
        # Update membership tier
        old_tier_name = membership.tier.name
        membership.tier_id = data['new_tier_id']
        membership.updated_at = datetime.utcnow()
        
        # Process additional payment for upgrade (in real implementation)
        if 'payment_method' in data:
            membership.payment_method = data['payment_method']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'membership': membership.to_dict(),
            'message': f'Membership upgraded from {old_tier_name} to {new_tier.name}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@memberships_bp.route('/users/<int:user_id>/membership/benefits', methods=['GET'])
def get_membership_benefits(user_id):
    """Get user's membership benefits and usage"""
    try:
        user = User.query.get_or_404(user_id)
        membership = user.get_active_membership()
        
        if not membership:
            return jsonify({
                'success': True,
                'has_membership': False,
                'benefits': None
            }), 200
        
        benefits = {
            'has_membership': True,
            'tier': membership.tier.to_dict(),
            'membership_details': {
                'membership_number': membership.membership_number,
                'start_date': membership.start_date.isoformat(),
                'end_date': membership.end_date.isoformat(),
                'days_until_expiry': membership.days_until_expiry(),
                'billing_cycle': membership.billing_cycle,
                'payment_status': membership.payment_status
            },
            'usage_stats': {
                'events_attended': membership.events_attended,
                'total_bookings': membership.total_bookings,
                'total_spent': membership.total_spent,
                'complimentary_drinks_used': membership.complimentary_drinks_used
            },
            'active_benefits': {
                'discount_percentage': membership.tier.discount_percentage,
                'priority_booking': membership.tier.priority_booking,
                'complimentary_drinks': membership.tier.complimentary_drinks,
                'private_lounge_access': membership.tier.private_lounge_access,
                'concierge_service': membership.tier.concierge_service,
                'exclusive_events': membership.tier.exclusive_events,
                'birthday_perks': membership.tier.birthday_perks,
                'transportation_service': membership.tier.transportation_service
            }
        }
        
        return jsonify({
            'success': True,
            'benefits': benefits
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


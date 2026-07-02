"""
Kitchen Routes Blueprint
Handles kitchen dashboard with real-time order updates.
"""

from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models import Order, OrderItem
from functools import wraps

kitchen_bp = Blueprint('kitchen', __name__)


def admin_required(f):
    """Decorator to require admin/kitchen login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Login required.', 'warning')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@kitchen_bp.route('/dashboard')
@admin_required
def dashboard():
    """Kitchen dashboard showing real-time order status."""
    pending_orders = Order.get_by_status(Order.STATUS_PENDING)
    preparing_orders = Order.get_by_status(Order.STATUS_PREPARING)
    ready_orders = Order.get_by_status(Order.STATUS_READY)
    completed_orders = Order.get_by_status(Order.STATUS_COMPLETED)

    # Get all orders with status in kitchen scope
    return render_template('kitchen/dashboard.html',
                           pending_orders=pending_orders,
                           preparing_orders=preparing_orders,
                           ready_orders=ready_orders,
                           completed_orders=completed_orders)


@kitchen_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    """View order details for kitchen."""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('kitchen.dashboard'))
    return render_template('kitchen/order_detail.html', order=order)


@kitchen_bp.route('/orders/<int:order_id>/start-preparing', methods=['POST'])
@admin_required
def start_preparing(order_id):
    """Mark order as preparing."""
    Order.update_status(order_id, Order.STATUS_PREPARING)

    # Notify customer via SocketIO
    try:
        from app import notify_order_update
        notify_order_update(order_id, Order.STATUS_PREPARING)
    except:
        pass

    flash('Order marked as preparing.', 'success')
    return redirect(url_for('kitchen.dashboard'))


@kitchen_bp.route('/orders/<int:order_id>/mark-ready', methods=['POST'])
@admin_required
def mark_ready(order_id):
    """Mark order as ready for pickup/delivery."""
    Order.update_status(order_id, Order.STATUS_READY)

    # Notify customer via SocketIO
    try:
        from app import notify_order_update
        notify_order_update(order_id, Order.STATUS_READY)
    except:
        pass

    flash('Order marked as ready.', 'success')
    return redirect(url_for('kitchen.dashboard'))


@kitchen_bp.route('/orders/<int:order_id>/complete', methods=['POST'])
@admin_required
def complete_order(order_id):
    """Mark order as completed."""
    Order.update_status(order_id, Order.STATUS_COMPLETED)

    # Notify customer via SocketIO
    try:
        from app import notify_order_update
        notify_order_update(order_id, Order.STATUS_COMPLETED)
    except:
        pass

    flash('Order completed.', 'success')
    return redirect(url_for('kitchen.dashboard'))


@kitchen_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
@admin_required
def cancel_order(order_id):
    """Cancel order."""
    Order.update_status(order_id, Order.STATUS_CANCELLED)

    # Notify customer via SocketIO
    try:
        from app import notify_order_update
        notify_order_update(order_id, Order.STATUS_CANCELLED)
    except:
        pass

    flash('Order cancelled.', 'warning')
    return redirect(url_for('kitchen.dashboard'))


@kitchen_bp.route('/pending')
@admin_required
def pending():
    """View pending orders only."""
    orders = Order.get_by_status(Order.STATUS_PENDING)
    return render_template('kitchen/orders_list.html', orders=orders, status='Pending')


@kitchen_bp.route('/preparing')
@admin_required
def preparing():
    """View preparing orders only."""
    orders = Order.get_by_status(Order.STATUS_PREPARING)
    return render_template('kitchen/orders_list.html', orders=orders, status='Preparing')


@kitchen_bp.route('/ready')
@admin_required
def ready():
    """View ready orders only."""
    orders = Order.get_by_status(Order.STATUS_READY)
    return render_template('kitchen/orders_list.html', orders=orders, status='Ready')


@kitchen_bp.route('/completed')
@admin_required
def completed():
    """View completed orders only."""
    orders = Order.get_by_status(Order.STATUS_COMPLETED)
    return render_template('kitchen/orders_list.html', orders=orders, status='Completed')

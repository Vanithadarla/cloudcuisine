"""
Customer Routes Blueprint
Handles customer functionality: menu browsing, cart, checkout, orders.
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify, make_response
from models import User, Category, FoodItem, Order, OrderItem, Payment
from functools import wraps
import json

customer_bp = Blueprint('customer', __name__)


def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard showing recent orders and quick actions."""
    user = User.get_by_id(session['user_id'])
    recent_orders = Order.get_by_user(session['user_id'], limit=5)
    return render_template('customer/dashboard.html', user=user, recent_orders=recent_orders)


@customer_bp.route('/menu')
def menu():
    """Display food menu."""
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '').strip()

    categories = Category.get_all(active_only=True)

    if search:
        food_items = FoodItem.search(search)
    elif category_id:
        food_items = FoodItem.get_by_category(category_id)
    else:
        food_items = FoodItem.get_all(active_only=True)

    selected_category = Category.get_by_id(category_id) if category_id else None

    return render_template('customer/menu.html',
                           food_items=food_items,
                           categories=categories,
                           selected_category=selected_category,
                           search_query=search)


@customer_bp.route('/cart')
def view_cart():
    """Display shopping cart."""
    cart = session.get('cart', {})
    cart_items = []
    total = 0

    for item_id, item in cart.items():
        subtotal = item['price'] * item['quantity']
        cart_items.append({
            'id': item_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image_url': item.get('image_url', ''),
            'subtotal': subtotal
        })
        total += subtotal

    gst = total * 0.18
    service_charge = total * 0.05
    grand_total = total + gst + service_charge

    return render_template('customer/cart.html',
                           cart_items=cart_items,
                           subtotal=total,
                           gst=gst,
                           service_charge=service_charge,
                           grand_total=grand_total)


@customer_bp.route('/cart/add/<int:item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    """Add item to cart."""
    food_item = FoodItem.get_by_id(item_id)
    if not food_item or not food_item.get('is_available'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Item not available'})
        flash('Item not available.', 'error')
        return redirect(url_for('customer.menu'))

    cart = session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        cart[item_id_str]['quantity'] += 1
    else:
        cart[item_id_str] = {
            'name': food_item['name'],
            'price': float(food_item['price']),
            'quantity': 1,
            'image_url': food_item.get('image_url', '')
        }

    session['cart'] = cart
    session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'{food_item["name"]} added to cart',
            'cart_count': sum(item['quantity'] for item in cart.values())
        })

    flash(f'{food_item["name"]} added to cart!', 'success')
    return redirect(url_for('customer.menu'))


@customer_bp.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    """Update cart item quantity."""
    quantity = request.form.get('quantity', type=int, default=1)

    cart = session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        if quantity > 0:
            cart[item_id_str]['quantity'] = quantity
        else:
            del cart[item_id_str]

    session['cart'] = cart
    session.modified = True

    flash('Cart updated.', 'success')
    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart."""
    cart = session.get('cart', {})
    item_id_str = str(item_id)

    if item_id_str in cart:
        item_name = cart[item_id_str]['name']
        del cart[item_id_str]
        session['cart'] = cart
        session.modified = True
        flash(f'{item_name} removed from cart.', 'info')

    return redirect(url_for('customer.view_cart'))


@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page."""
    cart = session.get('cart', {})

    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer.menu'))

    if request.method == 'POST':
        user = User.get_by_id(session['user_id'])
        delivery_address = request.form.get('address') or user.get('address', '')
        payment_method = request.form.get('payment_method', 'cash')
        special_instructions = request.form.get('special_instructions', '')
        discount_code = request.form.get('discount_code', '')

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
        gst = subtotal * 0.18
        service_charge = subtotal * 0.05

        # Apply discount
        discount = 0
        if discount_code == 'WELCOME10':
            discount = subtotal * 0.10
        elif discount_code == 'SAVE20':
            discount = subtotal * 0.20

        grand_total = subtotal + gst + service_charge - discount

        # Create order
        order = Order.create(
            user_id=session['user_id'],
            total_amount=subtotal,
            gst_amount=gst,
            service_charge=service_charge,
            discount=discount,
            grand_total=grand_total,
            delivery_address=delivery_address,
            payment_method=payment_method,
            special_instructions=special_instructions
        )

        order_id = order['id']

        # Add order items
        for item_id, item in cart.items():
            OrderItem.create(
                order_id=order_id,
                food_item_id=int(item_id),
                quantity=item['quantity'],
                price_per_item=item['price']
            )

        # Create payment record
        Payment.create(
            order_id=order_id,
            amount=grand_total,
            payment_method=payment_method
        )

        # Clear cart
        session.pop('cart', None)
        session.modified = True

        # Notify kitchen (imported function)
        try:
            from app import notify_kitchen_new_order
            notify_kitchen_new_order({
                'order_id': order_id,
                'customer': user['username'],
                'items': list(cart.values()),
                'total': grand_total
            })
        except:
            pass

        flash('Order placed successfully!', 'success')
        return redirect(url_for('customer.order_success', order_id=order_id))

    # GET request - show checkout form
    cart_items = []
    subtotal = 0

    for item_id, item in cart.items():
        subtotal_item = item['price'] * item['quantity']
        cart_items.append({
            'id': item_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'image_url': item.get('image_url', ''),
            'subtotal': subtotal_item
        })
        subtotal += subtotal_item

    gst = subtotal * 0.18
    service_charge = subtotal * 0.05
    grand_total = subtotal + gst + service_charge

    user = User.get_by_id(session['user_id'])

    return render_template('customer/checkout.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           gst=gst,
                           service_charge=service_charge,
                           grand_total=grand_total,
                           user=user)


@customer_bp.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    """Order success page."""
    order = Order.get_by_id(order_id)

    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'error')
        return redirect(url_for('customer.orders'))

    return render_template('customer/order_success.html', order=order)


@customer_bp.route('/orders')
@login_required
def orders():
    """View order history."""
    user_orders = Order.get_by_user(session['user_id'])
    return render_template('customer/orders.html', orders=user_orders)


@customer_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details."""
    order = Order.get_by_id(order_id)

    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'error')
        return redirect(url_for('customer.orders'))

    return render_template('customer/order_detail.html', order=order)


@customer_bp.route('/order/<int:order_id>/invoice')
@login_required
def download_invoice(order_id):
    """Download order invoice as PDF."""
    order = Order.get_by_id(order_id)

    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'error')
        return redirect(url_for('customer.orders'))

    from utils.pdf_generator import generate_invoice_pdf
    from flask import make_response

    pdf_data = generate_invoice_pdf(order)

    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'

    return response


@customer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page."""
    user = User.get_by_id(session['user_id'])

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        if username:
            User.update(session['user_id'], username=username, phone=phone, address=address)
            session['username'] = username
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('customer.profile'))

    return render_template('customer/profile.html', user=user)

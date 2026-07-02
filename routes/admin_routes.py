"""
Admin Routes Blueprint
Handles admin functionality: dashboard, menu management, order management.
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from models import Category, FoodItem, Order, OrderItem, User, Analytics, Admin
from functools import wraps
import os
import uuid
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required.', 'warning')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Check if file has allowed extension."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    stats = Analytics.get_dashboard_stats()
    recent_orders = Order.get_all(limit=10)
    best_sellers = OrderItem.get_best_selling(limit=5)
    weekly_sales = Analytics.get_weekly_sales()

    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_orders=recent_orders,
                           best_sellers=best_sellers,
                           weekly_sales=weekly_sales)


# ==================== Category Management ====================

@admin_bp.route('/categories')
@admin_required
def categories():
    """List all categories."""
    all_categories = Category.get_all(active_only=False)
    return render_template('admin/categories.html', categories=all_categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@admin_required
def add_category():
    """Add new category."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/add_category.html')

        # Handle file upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f"uploads/{filename}"

        Category.create(name, description, image_url)
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/add_category.html')


@admin_bp.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_id):
    """Edit category."""
    category = Category.get_by_id(category_id)
    if not category:
        flash('Category not found.', 'error')
        return redirect(url_for('admin.categories'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_active = request.form.get('is_active') == 'on'

        if not name:
            flash('Category name is required.', 'error')
            return render_template('admin/edit_category.html', category=category)

        # Handle file upload
        image_url = category.get('image_url')
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f"uploads/{filename}"

        Category.update(category_id, name=name, description=description,
                       image_url=image_url, is_active=is_active)
        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.categories'))

    return render_template('admin/edit_category.html', category=category)


@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@admin_required
def delete_category(category_id):
    """Delete category (soft delete)."""
    Category.delete(category_id)
    flash('Category deleted.', 'info')
    return redirect(url_for('admin.categories'))


# ==================== Menu Management ====================

@admin_bp.route('/menu')
@admin_required
def menu_items():
    """List all food items."""
    items = FoodItem.get_all(active_only=False)
    categories = Category.get_all(active_only=False)
    return render_template('admin/menu_items.html', items=items, categories=categories)


@admin_bp.route('/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu_item():
    """Add new food item."""
    categories = Category.get_all(active_only=True)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        preparation_time = request.form.get('preparation_time', type=int)
        is_veg = request.form.get('is_veg') == 'on'

        if not all([name, price, category_id]):
            flash('Name, price, and category are required.', 'error')
            return render_template('admin/add_menu_item.html', categories=categories)

        # Handle file upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f"uploads/{filename}"

        FoodItem.create(name, description, price, category_id, image_url, preparation_time, is_veg)
        flash('Food item added successfully!', 'success')
        return redirect(url_for('admin.menu_items'))

    return render_template('admin/add_menu_item.html', categories=categories)


@admin_bp.route('/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu_item(item_id):
    """Edit food item."""
    item = FoodItem.get_by_id(item_id)
    categories = Category.get_all(active_only=True)

    if not item:
        flash('Item not found.', 'error')
        return redirect(url_for('admin.menu_items'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        preparation_time = request.form.get('preparation_time', type=int)
        is_veg = request.form.get('is_veg') == 'on'
        is_available = request.form.get('is_available') == 'on'

        if not all([name, price, category_id]):
            flash('Name, price, and category are required.', 'error')
            return render_template('admin/edit_menu_item.html', item=item, categories=categories)

        # Handle file upload
        image_url = item.get('image_url')
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f"uploads/{filename}"

        FoodItem.update(item_id, name=name, description=description, price=price,
                       category_id=category_id, image_url=image_url,
                       preparation_time=preparation_time, is_veg=is_veg,
                       is_available=is_available)
        flash('Food item updated successfully!', 'success')
        return redirect(url_for('admin.menu_items'))

    return render_template('admin/edit_menu_item.html', item=item, categories=categories)


@admin_bp.route('/menu/delete/<int:item_id>', methods=['POST'])
@admin_required
def delete_menu_item(item_id):
    """Delete food item (soft delete)."""
    FoodItem.delete(item_id)
    flash('Food item removed from menu.', 'info')
    return redirect(url_for('admin.menu_items'))


# ==================== Order Management ====================

@admin_bp.route('/orders')
@admin_required
def orders():
    """List all orders."""
    status = request.args.get('status')
    all_orders = Order.get_all(status=status)
    return render_template('admin/orders.html', orders=all_orders, current_status=status)


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    """View order details."""
    order = Order.get_by_id(order_id)
    if not order:
        flash('Order not found.', 'error')
        return redirect(url_for('admin.orders'))
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status."""
    status = request.form.get('status')
    Order.update_status(order_id, status)

    # Notify customer via SocketIO
    try:
        from app import notify_order_update
        notify_order_update(order_id, status)
    except:
        pass

    flash(f'Order status updated to {status}.', 'success')

    # Check if request came from kitchen dashboard
    if request.referrer and 'kitchen' in request.referrer:
        return redirect(url_for('kitchen.dashboard'))
    return redirect(url_for('admin.order_detail', order_id=order_id))


# ==================== Reports ====================

@admin_bp.route('/reports')
@admin_required
def reports():
    """Sales reports and analytics."""
    period = request.args.get('period', 'daily')

    if period == 'daily':
        sales_data = Analytics.get_daily_sales()
    elif period == 'weekly':
        sales_data = Analytics.get_weekly_sales()
    elif period == 'monthly':
        sales_data = Analytics.get_monthly_sales()
    else:
        sales_data = Analytics.get_daily_sales()

    best_sellers = OrderItem.get_best_selling(limit=10)
    payment_stats = Payment.get_revenue_by_method()

    return render_template('admin/reports.html',
                           sales_data=sales_data,
                           best_sellers=best_sellers,
                           payment_stats=payment_stats,
                           period=period)


# ==================== Customers ====================

@admin_bp.route('/customers')
@admin_required
def customers():
    """List all customers."""
    from models import Database
    customers = Database.execute_query(
        "SELECT id, username, email, phone, address, created_at FROM users ORDER BY created_at DESC",
        fetch_all=True
    )
    return render_template('admin/customers.html', customers=customers)


@admin_bp.route('/customers/<int:user_id>')
@admin_required
def customer_detail(user_id):
    """View customer details and orders."""
    user = User.get_by_id(user_id)
    if not user:
        flash('Customer not found.', 'error')
        return redirect(url_for('admin.customers'))

    orders = Order.get_by_user(user_id)
    return render_template('admin/customer_detail.html', user=user, orders=orders)

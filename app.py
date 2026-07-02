
from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_mysqldb import MySQL
from config import config
from models import mysql, User, Admin, Category, FoodItem, Order, OrderItem, Payment, Analytics
from utils.pdf_generator import generate_invoice_pdf
from functools import wraps
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(config['development'])

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize MySQL
mysql.init_app(app)

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== Decorators ====================

def login_required(f):
    """Decorator to require user login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required.', 'warning')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== Context Processors ====================

@app.context_processor
def inject_categories():
    """Inject categories into all templates."""
    try:
        categories = Category.get_all(active_only=True)
    except:
        categories = []
    return dict(categories=categories)

@app.context_processor
def inject_cart_count():
    """Inject cart item count into all templates."""
    cart = session.get('cart', {})
    count = sum(item.get('quantity', 0) for item in cart.values())
    return dict(cart_count=count)

# ==================== Main Routes ====================

@app.route('/')
def index():
    """Home page route."""
    try:
        featured_items = FoodItem.get_all(active_only=True)[:6]
        categories = Category.get_all(active_only=True)
    except:
        featured_items = []
        categories = []
    return render_template('index.html', featured_items=featured_items, categories=categories)

@app.route('/about')
def about():
    """About page route."""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact page route."""
    return render_template('contact.html')

@app.route('/download/CloudCuisine.zip')
def download_zip():
    """Download the project zip file."""
    from flask import send_file
    zip_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'CloudCuisine.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name='CloudCuisine.zip')
    return "File not found", 404

# ==================== Authentication Routes ====================

# Register blueprint routes inline
from routes.auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

# ==================== Customer Routes ====================

from routes.customer_routes import customer_bp
app.register_blueprint(customer_bp, url_prefix='/customer')

# ==================== Admin Routes ====================

from routes.admin_routes import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# ==================== Kitchen Routes ====================

from routes.kitchen_routes import kitchen_bp
app.register_blueprint(kitchen_bp, url_prefix='/kitchen')

# ==================== API Routes ====================

@app.route('/api/search')
def search():
    """Search food items API."""
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return []
    results = FoodItem.search(query)
    return results

# ==================== SocketIO Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('join_kitchen')
def handle_join_kitchen():
    """Join kitchen room for real-time updates."""
    join_room('kitchen')
    emit('status', {'msg': 'Connected to kitchen dashboard.'})

@socketio.on('join_customer')
def handle_join_customer(data):
    """Join customer room for order updates."""
    if data and 'order_id' in data:
        room = f"order_{data['order_id']}"
        join_room(room)
        emit('status', {'msg': f'Connected to order {data["order_id"]} updates.'})

def notify_kitchen_new_order(order_data):
    """Notify kitchen of new order."""
    socketio.emit('new_order', order_data, room='kitchen')

def notify_order_update(order_id, status):
    """Notify customer of order status update."""
    room = f"order_{order_id}"
    socketio.emit('order_update', {'order_id': order_id, 'status': status}, room=room)

# ==================== Error Handlers ====================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    """Handle 403 errors."""
    return render_template('errors/403.html'), 403

# ==================== Template Filters ====================

@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency."""
    return f"${value:.2f}"

@app.template_filter('datetime')
def datetime_filter(value, format='%Y-%m-%d %H:%M'):
    """Format datetime value."""
    from datetime import datetime as dt
    if isinstance(value, str):
        try:
            value = dt.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            return value
    return value.strftime(format) if value else ''

# ==================== Main Entry Point ====================

if __name__ == '__main__':
    # Run the application with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

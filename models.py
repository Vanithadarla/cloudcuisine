"""
CloudCuisine Models Module
Contains database connection and model classes.
"""

from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import MySQLdb.cursors

mysql = MySQL()

class Database:
    """Database helper class for common operations."""

    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
        """
        Execute a database query with proper error handling.

        Args:
            query: SQL query string
            params: Query parameters (tuple or dict)
            fetch_one: Return single row
            fetch_all: Return all rows
            commit: Commit the transaction

        Returns:
            Query result or cursor
        """
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute(query, params)
            if commit:
                mysql.connection.commit()
                return cursor
            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return cursor
        except Exception as e:
            mysql.connection.rollback()
            raise e
        finally:
            cursor.close()


class User:
    """User model for customer accounts."""

    @staticmethod
    def create(username, email, password, phone=None, address=None):
        """Create a new user account."""
        hashed_password = generate_password_hash(password)
        query = """
            INSERT INTO users (username, email, password, phone, address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        Database.execute_query(query, (username, email, hashed_password, phone, address, datetime.now()), commit=True)
        return Database.execute_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetch_one=True
        )

    @staticmethod
    def get_by_email(email):
        """Get user by email address."""
        return Database.execute_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetch_one=True
        )

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        return Database.execute_query(
            "SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True
        )

    @staticmethod
    def verify_password(email, password):
        """Verify user credentials."""
        user = User.get_by_email(email)
        if user and check_password_hash(user['password'], password):
            return user
        return None

    @staticmethod
    def update(user_id, **kwargs):
        """Update user information."""
        allowed_fields = ['username', 'phone', 'address']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]
        query = f"UPDATE users SET {set_clause} WHERE id = %s"
        Database.execute_query(query, tuple(values), commit=True)
        return True


class Admin:
    """Admin model for restaurant administrators."""

    @staticmethod
    def create(username, email, password):
        """Create a new admin account."""
        hashed_password = generate_password_hash(password)
        query = """
            INSERT INTO admins (username, email, password, created_at)
            VALUES (%s, %s, %s, %s)
        """
        Database.execute_query(query, (username, email, hashed_password, datetime.now()), commit=True)

    @staticmethod
    def get_by_email(email):
        """Get admin by email address."""
        return Database.execute_query(
            "SELECT * FROM admins WHERE email = %s", (email,), fetch_one=True
        )

    @staticmethod
    def verify_password(email, password):
        """Verify admin credentials."""
        admin = Admin.get_by_email(email)
        if admin and check_password_hash(admin['password'], password):
            return admin
        return None


class Category:
    """Category model for food categories."""

    @staticmethod
    def get_all(active_only=True):
        """Get all categories."""
        query = "SELECT * FROM categories"
        if active_only:
            query += " WHERE is_active = TRUE"
        query += " ORDER BY name"
        return Database.execute_query(query, fetch_all=True)

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID."""
        return Database.execute_query(
            "SELECT * FROM categories WHERE id = %s", (category_id,), fetch_one=True
        )

    @staticmethod
    def create(name, description=None, image_url=None):
        """Create a new category."""
        query = """
            INSERT INTO categories (name, description, image_url, created_at, is_active)
            VALUES (%s, %s, %s, %s, TRUE)
        """
        Database.execute_query(query, (name, description, image_url, datetime.now()), commit=True)
        return Database.execute_query("SELECT LAST_INSERT_ID() as id", fetch_one=True)

    @staticmethod
    def update(category_id, **kwargs):
        """Update category information."""
        allowed_fields = ['name', 'description', 'image_url', 'is_active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [category_id]
        query = f"UPDATE categories SET {set_clause} WHERE id = %s"
        Database.execute_query(query, tuple(values), commit=True)
        return True

    @staticmethod
    def delete(category_id):
        """Delete a category (soft delete by setting is_active = False)."""
        query = "UPDATE categories SET is_active = FALSE WHERE id = %s"
        Database.execute_query(query, (category_id,), commit=True)


class FoodItem:
    """FoodItem model for menu items."""

    @staticmethod
    def get_all(active_only=True, category_id=None):
        """Get all food items, optionally filtered by category."""
        query = """
            SELECT fi.*, c.name as category_name
            FROM food_items fi
            LEFT JOIN categories c ON fi.category_id = c.id
        """
        conditions = []
        params = []

        if active_only:
            
            conditions.append("fi.is_available = TRUE")

        if category_id:
            conditions.append("fi.category_id = %s")
            params.append(category_id)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY c.name, fi.name"

        if params:
            return Database.execute_query(query, tuple(params), fetch_all=True)
        return Database.execute_query(query, fetch_all=True)

    @staticmethod
    def search(search_term):
        """Search food items by name or description."""
        query = """
            SELECT fi.*, c.name as category_name
            FROM food_items fi
            LEFT JOIN categories c ON fi.category_id = c.id
            WHERE fi.is_available = TRUE
            AND (fi.name LIKE %s OR fi.description LIKE %s)
            ORDER BY fi.name
        """
        search_pattern = f"%{search_term}%"
        return Database.execute_query(query, (search_pattern, search_pattern), fetch_all=True)

    @staticmethod
    def get_by_id(item_id):
        """Get food item by ID."""
        query = """
            SELECT fi.*, c.name as category_name
            FROM food_items fi
            LEFT JOIN categories c ON fi.category_id = c.id
            WHERE fi.id = %s
        """
        return Database.execute_query(query, (item_id,), fetch_one=True)

    @staticmethod
    def create(name, description, price, category_id, image_url=None, preparation_time=None, is_veg=True):
        """Create a new food item."""
        query = """
            INSERT INTO food_items (name, description, price, category_id, image_url,
                                    preparation_time, is_veg, is_available, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
        """
        Database.execute_query(
            query, (name, description, price, category_id, image_url, preparation_time, is_veg, datetime.now()),
            commit=True
        )
        return Database.execute_query("SELECT LAST_INSERT_ID() as id", fetch_one=True)

    @staticmethod
    def update(item_id, **kwargs):
        """Update food item information."""
        allowed_fields = ['name', 'description', 'price', 'category_id', 'image_url',
                          'preparation_time', 'is_veg', 'is_available']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        if not updates:
            return False

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [item_id]
        query = f"UPDATE food_items SET {set_clause} WHERE id = %s"
        Database.execute_query(query, tuple(values), commit=True)
        return True

    @staticmethod
    def delete(item_id):
        """Delete a food item (soft delete)."""
        query = "UPDATE food_items SET is_available = FALSE WHERE id = %s"
        Database.execute_query(query, (item_id,), commit=True)

    @staticmethod
    def get_by_category(category_id):
        """Get all food items for a specific category."""
        return FoodItem.get_all(active_only=True, category_id=category_id)


class Order:
    """Order model for customer orders."""

    STATUS_PENDING = 'pending'
    STATUS_PREPARING = 'preparing'
    STATUS_READY = 'ready'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    @staticmethod
    def create(user_id, total_amount, gst_amount, service_charge, discount, grand_total,
               delivery_address, payment_method='cash', special_instructions=None):
        """Create a new order."""
        query = """
            INSERT INTO orders (user_id, total_amount, gst_amount, service_charge,
                               discount, grand_total, status, delivery_address,
                               payment_method, special_instructions, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        Database.execute_query(
            query, (user_id, total_amount, gst_amount, service_charge, discount,
                   grand_total, Order.STATUS_PENDING, delivery_address,
                   payment_method, special_instructions, datetime.now()),
            commit=True
        )
        return Database.execute_query("SELECT LAST_INSERT_ID() as id", fetch_one=True)

    @staticmethod
    def get_by_id(order_id):
        """Get order by ID with items."""
        order = Database.execute_query(
            """
            SELECT o.*, u.username, u.email, u.phone
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
            """, (order_id,), fetch_one=True
        )
        if order:
            order['items'] = OrderItem.get_by_order_id(order_id)
        return order

    @staticmethod
    def get_by_user(user_id, limit=None):
        """Get orders by user ID."""
        query = """
            SELECT * FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        return Database.execute_query(query, (user_id,), fetch_all=True)

    @staticmethod
    def get_all(status=None, limit=None):
        """Get all orders, optionally filtered by status."""
        query = """
            SELECT o.*, u.username, u.email, u.phone
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.id
            WHERE 1=1
        """
        params = []

        if status:
            query += " AND o.status = %s"
            params.append(status)

        query += " ORDER BY o.created_at DESC"

        if limit:
            query += f" LIMIT {limit}"

        if params:
            return Database.execute_query(query, tuple(params), fetch_all=True)
        return Database.execute_query(query, fetch_all=True)

    @staticmethod
    def update_status(order_id, status):
        """Update order status."""
        valid_statuses = [Order.STATUS_PENDING, Order.STATUS_PREPARING,
                         Order.STATUS_READY, Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]
        if status not in valid_statuses:
            return False

        query = "UPDATE orders SET status = %s WHERE id = %s"
        Database.execute_query(query, (status, order_id), commit=True)
        return True

    @staticmethod
    def get_by_status(status):
        """Get all orders by status."""
        return Order.get_all(status=status)

    @staticmethod
    def get_order_count_by_status(status):
        """Get count of orders by status."""
        query = "SELECT COUNT(*) as count FROM orders WHERE status = %s"
        result = Database.execute_query(query, (status,), fetch_one=True)
        return result['count'] if result else 0

    @staticmethod
    def get_daily_sales(date=None):
        """Get sales for a specific date."""
        query = """
            SELECT DATE(created_at) as sale_date,
                   COUNT(*) as order_count,
                   SUM(grand_total) as total_revenue
            FROM orders
            WHERE status = %s
        """
        params = [Order.STATUS_COMPLETED]

        if date:
            query += " AND DATE(created_at) = %s"
            params.append(date)

        query += " GROUP BY DATE(created_at) ORDER BY sale_date DESC"
        return Database.execute_query(query, tuple(params), fetch_all=True)

    @staticmethod
    def get_sales_by_period(start_date, end_date):
        """Get sales for a date range."""
        query = """
            SELECT DATE(created_at) as sale_date,
                   COUNT(*) as order_count,
                   SUM(grand_total) as total_revenue,
                   SUM(total_amount) as subtotal,
                   SUM(gst_amount) as total_gst
            FROM orders
            WHERE status = %s
            AND DATE(created_at) BETWEEN %s AND %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date
        """
        return Database.execute_query(
            query, (Order.STATUS_COMPLETED, start_date, end_date), fetch_all=True
        )

    @staticmethod
    def get_peak_hours():
        """Get peak ordering hours."""
        query = """
            SELECT HOUR(created_at) as hour,
                   COUNT(*) as order_count
            FROM orders
            WHERE status = %s
            GROUP BY HOUR(created_at)
            ORDER BY order_count DESC
        """
        return Database.execute_query(query, (Order.STATUS_COMPLETED,), fetch_all=True)


class OrderItem:
    """OrderItem model for items within an order."""

    @staticmethod
    def create(order_id, food_item_id, quantity, price_per_item, special_request=None):
        """Create an order item."""
        subtotal = quantity * price_per_item
        query = """
            INSERT INTO order_items (order_id, food_item_id, quantity,
                                     price_per_item, subtotal, special_request)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        Database.execute_query(
            query, (order_id, food_item_id, quantity, price_per_item, subtotal, special_request),
            commit=True
        )

    @staticmethod
    def get_by_order_id(order_id):
        """Get all items for an order."""
        query = """
            SELECT oi.*, fi.name as item_name, fi.description, fi.image_url
            FROM order_items oi
            LEFT JOIN food_items fi ON oi.food_item_id = fi.id
            WHERE oi.order_id = %s
        """
        return Database.execute_query(query, (order_id,), fetch_all=True)

    @staticmethod
    def get_best_selling(limit=10):
        """Get best selling items."""
        query = """
            SELECT fi.name, fi.image_url,
                   SUM(oi.quantity) as total_sold,
                   SUM(oi.subtotal) as total_revenue
            FROM order_items oi
            LEFT JOIN food_items fi ON oi.food_item_id = fi.id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE o.status = %s
            GROUP BY fi.id, fi.name, fi.image_url
            ORDER BY total_sold DESC
            LIMIT %s
        """
        return Database.execute_query(query, (Order.STATUS_COMPLETED, limit), fetch_all=True)


class Payment:
    """Payment model for order payments."""

    @staticmethod
    def create(order_id, amount, payment_method, transaction_id=None):
        """Create a payment record."""
        query = """
            INSERT INTO payments (order_id, amount, payment_method, transaction_id,
                                  payment_status, created_at)
            VALUES (%s, %s, %s, %s, 'completed', %s)
        """
        Database.execute_query(
            query, (order_id, amount, payment_method, transaction_id, datetime.now()),
            commit=True
        )
        return Database.execute_query("SELECT LAST_INSERT_ID() as id", fetch_one=True)

    @staticmethod
    def get_by_order_id(order_id):
        """Get payment by order ID."""
        return Database.execute_query(
            "SELECT * FROM payments WHERE order_id = %s", (order_id,), fetch_one=True
        )

    @staticmethod
    def get_revenue_by_method(start_date=None, end_date=None):
        """Get revenue grouped by payment method."""
        query = """
            SELECT payment_method,
                   COUNT(*) as transaction_count,
                   SUM(amount) as total_amount
            FROM payments
            WHERE payment_status = 'completed'
        """
        params = []

        if start_date and end_date:
            query += " AND DATE(created_at) BETWEEN %s AND %s"
            params.extend([start_date, end_date])

        query += " GROUP BY payment_method"
        return Database.execute_query(query, tuple(params) if params else None, fetch_all=True)


class Analytics:
    """Analytics helper class for dashboard statistics."""

    @staticmethod
    def get_dashboard_stats():
        """Get general dashboard statistics."""
        stats = {}

        # Total orders today
        query = """
            SELECT COUNT(*) as count FROM orders
            WHERE DATE(created_at) = CURDATE()
        """
        result = Database.execute_query(query, fetch_one=True)
        stats['today_orders'] = result['count'] if result else 0

        # Total revenue today
        query = """
            SELECT COALESCE(SUM(grand_total), 0) as total
            FROM orders
            WHERE DATE(created_at) = CURDATE() AND status = %s
        """
        result = Database.execute_query(query, (Order.STATUS_COMPLETED,), fetch_one=True)
        stats['today_revenue'] = float(result['total']) if result else 0.0

        # Total customers
        query = "SELECT COUNT(*) as count FROM users"
        result = Database.execute_query(query, fetch_one=True)
        stats['total_customers'] = result['count'] if result else 0

        # Total menu items
        query = "SELECT COUNT(*) as count FROM food_items WHERE is_available = TRUE"
        result = Database.execute_query(query, fetch_one=True)
        stats['total_items'] = result['count'] if result else 0

        # Orders by status
        stats['pending_orders'] = Order.get_order_count_by_status(Order.STATUS_PENDING)
        stats['preparing_orders'] = Order.get_order_count_by_status(Order.STATUS_PREPARING)
        stats['ready_orders'] = Order.get_order_count_by_status(Order.STATUS_READY)

        return stats

    @staticmethod
    def get_weekly_sales():
        """Get sales for the last 7 days."""
        query = """
            SELECT DATE(created_at) as sale_date,
                   COUNT(*) as order_count,
                   COALESCE(SUM(grand_total), 0) as total_revenue
            FROM orders
            WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            AND status = %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date
        """
        return Database.execute_query(query, (Order.STATUS_COMPLETED,), fetch_all=True)

    @staticmethod
    def get_monthly_sales():
        """Get sales for the last 30 days."""
        query = """
            SELECT DATE(created_at) as sale_date,
                   COUNT(*) as order_count,
                   COALESCE(SUM(grand_total), 0) as total_revenue
            FROM orders
            WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            AND status = %s
            GROUP BY DATE(created_at)
            ORDER BY sale_date
        """
        return Database.execute_query(query, (Order.STATUS_COMPLETED,), fetch_all=True)

    @staticmethod
    def get_order_status_distribution():
        """Get order count by status."""
        query = """
            SELECT status, COUNT(*) as count
            FROM orders
            GROUP BY status
        """
        return Database.execute_query(query, fetch_all=True)

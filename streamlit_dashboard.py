"""
CloudCuisine Streamlit Analytics Dashboard
Separate analytics dashboard for viewing sales and order insights.

Run with: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pymysql
from pymysql.cursors import DictCursor
import os

# Page configuration
st.set_page_config(
    page_title="CloudCuisine Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection configuration
DB_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DB', 'cloudcuisine'),
    'cursorclass': DictCursor
}


def get_db_connection():
    """Create database connection."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def execute_query(query, params=None):
    """Execute query and return results."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    except Exception as e:
        st.error(f"Query failed: {e}")
        return []
    finally:
        conn.close()


# ==================== Sidebar ====================

st.sidebar.title("CloudCuisine Analytics")
st.sidebar.image("https://via.placeholder.com/200x80/3498db/ffffff?text=CloudCuisine", width=200)

# Date range selection
st.sidebar.header("Date Range")
date_range = st.sidebar.date_input(
    "Select period",
    [datetime.now() - timedelta(days=30), datetime.now()],
    max_value=datetime.now()
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Navigation
st.sidebar.header("Navigation")
view = st.sidebar.radio(
    "Select View",
    ["Dashboard Overview", "Sales Analysis", "Order Insights", "Menu Performance", "Customer Analytics"]
)

# ==================== Helper Functions ====================

def get_daily_sales(start_date, end_date):
    """Get daily sales data for date range."""
    query = """
        SELECT
            DATE(created_at) as date,
            COUNT(*) as orders,
            COALESCE(SUM(grand_total), 0) as revenue,
            COALESCE(SUM(total_amount), 0) as subtotal,
            COALESCE(SUM(gst_amount), 0) as gst
        FROM orders
        WHERE DATE(created_at) BETWEEN %s AND %s
        AND status = 'completed'
        GROUP BY DATE(created_at)
        ORDER BY date
    """
    return execute_query(query, (start_date, end_date))


def get_order_status_distribution():
    """Get order count by status."""
    query = """
        SELECT
            status,
            COUNT(*) as count
        FROM orders
        GROUP BY status
    """
    return execute_query(query)


def get_best_sellers(limit=10):
    """Get best selling items."""
    query = """
        SELECT
            fi.name,
            c.name as category,
            SUM(oi.quantity) as total_sold,
            SUM(oi.subtotal) as total_revenue
        FROM order_items oi
        JOIN food_items fi ON oi.food_item_id = fi.id
        JOIN categories c ON fi.category_id = c.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'completed'
        GROUP BY fi.id, fi.name, c.name
        ORDER BY total_sold DESC
        LIMIT %s
    """
    return execute_query(query, (limit,))


def get_peak_hours():
    """Get orders by hour of day."""
    query = """
        SELECT
            HOUR(created_at) as hour,
            COUNT(*) as orders,
            COALESCE(SUM(grand_total), 0) as revenue
        FROM orders
        WHERE status = 'completed'
        GROUP BY HOUR(created_at)
        ORDER BY hour
    """
    return execute_query(query)


def get_category_sales():
    """Get sales by category."""
    query = """
        SELECT
            c.name as category,
            COUNT(DISTINCT o.id) as orders,
            SUM(oi.quantity) as items_sold,
            SUM(oi.subtotal) as revenue
        FROM order_items oi
        JOIN food_items fi ON oi.food_item_id = fi.id
        JOIN categories c ON fi.category_id = c.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'completed'
        GROUP BY c.id, c.name
        ORDER BY revenue DESC
    """
    return execute_query(query)


def get_customer_stats():
    """Get customer statistics."""
    query = """
        SELECT
            COUNT(DISTINCT u.id) as total_customers,
            COUNT(DISTINCT o.user_id) as active_customers,
            COUNT(o.id) as total_orders,
            COALESCE(AVG(o.grand_total), 0) as avg_order_value
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
    """
    return execute_query(query)


def get_dashboard_stats():
    """Get general dashboard statistics."""
    stats = {}

    # Today's stats
    query = """
        SELECT
            COUNT(*) as orders_today,
            COALESCE(SUM(grand_total), 0) as revenue_today
        FROM orders
        WHERE DATE(created_at) = CURDATE()
    """
    result = execute_query(query)
    if result:
        stats['today_orders'] = result[0]['orders_today']
        stats['today_revenue'] = float(result[0]['revenue_today'])

    # This week's stats
    query = """
        SELECT
            COUNT(*) as week_orders,
            COALESCE(SUM(grand_total), 0) as week_revenue
        FROM orders
        WHERE YEARWEEK(created_at) = YEARWEEK(NOW())
    """
    result = execute_query(query)
    if result:
        stats['week_orders'] = result[0]['week_orders']
        stats['week_revenue'] = float(result[0]['week_revenue'])

    # This month's stats
    query = """
        SELECT
            COUNT(*) as month_orders,
            COALESCE(SUM(grand_total), 0) as month_revenue
        FROM orders
        WHERE YEAR(created_at) = YEAR(NOW())
        AND MONTH(created_at) = MONTH(NOW())
    """
    result = execute_query(query)
    if result:
        stats['month_orders'] = result[0]['month_orders']
        stats['month_revenue'] = float(result[0]['month_revenue'])

    return stats


# ==================== Dashboard Overview ====================

if view == "Dashboard Overview":
    st.title("CloudCuisine Dashboard Overview")
    st.markdown("---")

    # Key metrics
    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Today's Orders",
            value=stats.get('today_orders', 0),
            delta=None
        )

    with col2:
        st.metric(
            label="Today's Revenue",
            value=f"${stats.get('today_revenue', 0):.2f}",
            delta=None
        )

    with col3:
        st.metric(
            label="This Week",
            value=f"${stats.get('week_revenue', 0):.2f}",
            delta=None
        )

    with col4:
        st.metric(
            label="This Month",
            value=f"${stats.get('month_revenue', 0):.2f}",
            delta=None
        )

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        # Order status distribution
        st.subheader("Order Status Distribution")
        status_data = get_order_status_distribution()
        if status_data:
            df_status = pd.DataFrame(status_data)
            fig = px.pie(df_status, values='count', names='status',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No order data available")

    with col2:
        # Peak hours
        st.subheader("Peak Order Hours")
        peak_data = get_peak_hours()
        if peak_data:
            df_peak = pd.DataFrame(peak_data)
            df_peak['hour'] = df_peak['hour'].apply(lambda x: f"{x:02d}:00")
            fig = px.bar(df_peak, x='hour', y='orders',
                        color='revenue',
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No peak hour data available")

    # Top selling items
    st.subheader("Top 5 Best Sellers")
    best_sellers = get_best_sellers(5)
    if best_sellers:
        df_sellers = pd.DataFrame(best_sellers)
        col_names = ['Item', 'Category', 'Units Sold', 'Revenue']
        df_sellers.columns = col_names
        df_sellers['Revenue'] = df_sellers['Revenue'].apply(lambda x: f"${x:.2f}")
        st.dataframe(df_sellers, use_container_width=True, hide_index=True)
    else:
        st.info("No sales data available")


# ==================== Sales Analysis ====================

elif view == "Sales Analysis":
    st.title("Sales Analysis")
    st.markdown("---")

    # Daily sales chart
    st.subheader("Daily Sales Trend")
    sales_data = get_daily_sales(start_date, end_date)

    if sales_data:
        df_sales = pd.DataFrame(sales_data)
        df_sales['date'] = pd.to_datetime(df_sales['date'])
        df_sales['revenue'] = df_sales['revenue'].astype(float)

        fig = px.line(df_sales, x='date', y='revenue',
                     title='Daily Revenue',
                     labels={'revenue': 'Revenue ($)', 'date': 'Date'},
                     markers=True)
        fig.update_traces(line_color='#3498db', line_width=2)
        st.plotly_chart(fig, use_container_width=True)

        # Sales metrics
        total_revenue = df_sales['revenue'].sum()
        total_orders = df_sales['orders'].sum()
        avg_daily = total_revenue / len(df_sales) if len(df_sales) > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Revenue", f"${total_revenue:.2f}")
        col2.metric("Total Orders", total_orders)
        col3.metric("Average Daily", f"${avg_daily:.2f}")

        # Revenue breakdown
        st.subheader("Revenue Breakdown")
        col1, col2 = st.columns(2)

        with col1:
            # Subtotal vs GST vs charges
            breakdown_data = {
                'Category': ['Subtotal', 'GST', 'Service Charge'],
                'Amount': [
                    df_sales['subtotal'].astype(float).sum(),
                    df_sales['gst'].astype(float).sum(),
                    df_sales['subtotal'].astype(float).sum() * 0.05
                ]
            }
            df_breakdown = pd.DataFrame(breakdown_data)
            fig = px.pie(df_breakdown, values='Amount', names='Category',
                        color_discrete_sequence=['#3498db', '#e74c3c', '#f1c40f'])
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Daily order count
            fig = px.bar(df_sales, x='date', y='orders',
                        title='Daily Order Count',
                        color='revenue',
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No sales data available for the selected period")


# ==================== Order Insights ====================

elif view == "Order Insights":
    st.title("Order Insights")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Order Status Distribution")
        status_data = get_order_status_distribution()
        if status_data:
            df_status = pd.DataFrame(status_data)
            fig = px.pie(df_status, values='count', names='status',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    with col2:
        st.subheader("Orders by Hour")
        peak_data = get_peak_hours()
        if peak_data:
            df_peak = pd.DataFrame(peak_data)
            df_peak['hour_label'] = df_peak['hour'].apply(lambda x: f"{x:02d}:00")
            fig = px.bar(df_peak, x='hour_label', y='orders',
                        labels={'hour_label': 'Hour', 'orders': 'Order Count'},
                        color='revenue',
                        color_continuous_scale='Teal')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    # Peak hours heatmap
    st.subheader("Peak Hours Analysis")
    if peak_data:
        df_peak = pd.DataFrame(peak_data)
        df_peak['hour'] = df_peak['hour'].astype(int)

        fig = go.Figure(data=go.Heatmap(
            z=[df_peak['orders'].tolist()],
            x=[f"{h:02d}:00" for h in df_peak['hour']],
            y=['Orders'],
            colorscale='Blues'
        ))
        fig.update_layout(title='Order Distribution by Hour')
        st.plotly_chart(fig, use_container_width=True)


# ==================== Menu Performance ====================

elif view == "Menu Performance":
    st.title("Menu Performance")
    st.markdown("---")

    # Best sellers
    st.subheader("Top 10 Best Selling Items")
    best_sellers = get_best_sellers(10)
    if best_sellers:
        df_sellers = pd.DataFrame(best_sellers)

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(df_sellers, x='name', y='total_sold',
                        title='Units Sold',
                        labels={'name': 'Item', 'total_sold': 'Units Sold'},
                        color='total_revenue',
                        color_continuous_scale='Teal')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(df_sellers, x='name', y='total_revenue',
                        title='Revenue',
                        labels={'name': 'Item', 'total_revenue': 'Revenue ($)'},
                        color='total_sold',
                        color_continuous_scale='Viridis')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        # Table view
        st.subheader("Detailed Breakdown")
        df_display = df_sellers.copy()
        df_display['total_revenue'] = df_display['total_revenue'].apply(lambda x: f"${x:.2f}")
        df_display.columns = ['Item', 'Category', 'Units Sold', 'Revenue']
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    else:
        st.info("No menu performance data available")

    # Category performance
    st.subheader("Category Performance")
    category_data = get_category_sales()
    if category_data:
        df_category = pd.DataFrame(category_data)

        fig = px.pie(df_category, values='revenue', names='category',
                    title='Revenue by Category',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")


# ==================== Customer Analytics ====================

elif view == "Customer Analytics":
    st.title("Customer Analytics")
    st.markdown("---")

    # Customer statistics
    stats = get_customer_stats()
    if stats:
        stats = stats[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", stats.get('total_customers', 0))
        col2.metric("Active Customers", stats.get('active_customers', 0))
        col3.metric("Total Orders", stats.get('total_orders', 0))
        col4.metric("Avg Order Value", f"${float(stats.get('avg_order_value', 0)):.2f}")

    # Top customers
    st.subheader("Top Customers")
    query = """
        SELECT
            u.username,
            u.email,
            COUNT(o.id) as total_orders,
            COALESCE(SUM(o.grand_total), 0) as total_spent,
            COALESCE(AVG(o.grand_total), 0) as avg_order
        FROM users u
        JOIN orders o ON u.id = o.user_id
        GROUP BY u.id, u.username, u.email
        ORDER BY total_spent DESC
        LIMIT 10
    """
    top_customers = execute_query(query)
    if top_customers:
        df_customers = pd.DataFrame(top_customers)
        df_customers['total_spent'] = df_customers['total_spent'].apply(lambda x: f"${float(x):.2f}")
        df_customers['avg_order'] = df_customers['avg_order'].apply(lambda x: f"${float(x):.2f}")
        df_customers.columns = ['Customer', 'Email', 'Orders', 'Total Spent', 'Avg Order']
        st.dataframe(df_customers, use_container_width=True, hide_index=True)
    else:
        st.info("No customer data available")

    # Customer order distribution
    st.subheader("Customer Order Distribution")
    query = """
        SELECT
            CASE
                WHEN order_count = 1 THEN '1 Order'
                WHEN order_count BETWEEN 2 AND 5 THEN '2-5 Orders'
                WHEN order_count BETWEEN 6 AND 10 THEN '6-10 Orders'
                ELSE '10+ Orders'
            END as segment,
            COUNT(*) as customer_count
        FROM (
            SELECT u.id, COUNT(o.id) as order_count
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id
        ) as user_orders
        GROUP BY segment
        ORDER BY FIELD(segment, '1 Order', '2-5 Orders', '6-10 Orders', '10+ Orders')
    """
    segment_data = execute_query(query)
    if segment_data:
        df_segment = pd.DataFrame(segment_data)
        fig = px.pie(df_segment, values='customer_count', names='segment',
                    title='Customer Segments by Order Count',
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No segment data available")


# ==================== Footer ====================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #95a5a6;'>
        <p>CloudCuisine Analytics Dashboard</p>
        <p>Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    unsafe_allow_html=True
)

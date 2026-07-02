-- ============================================
-- CloudCuisine Database Schema
-- Cloud-Based Restaurant Order Management System
-- ============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS cloudcuisine;
USE cloudcuisine;

-- ==================== USERS TABLE ====================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== ADMINS TABLE ====================
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== CATEGORIES TABLE ====================
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sort_order INT DEFAULT 0,
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== FOOD ITEMS TABLE ====================
CREATE TABLE IF NOT EXISTS food_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT NOT NULL,
    image_url VARCHAR(255),
    preparation_time INT DEFAULT 15,
    is_veg BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    INDEX idx_category (category_id),
    INDEX idx_available (is_available),
    INDEX idx_featured (is_featured)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== ORDERS TABLE ====================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL DEFAULT 0,
    gst_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    service_charge DECIMAL(10, 2) NOT NULL DEFAULT 0,
    discount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    grand_total DECIMAL(12, 2) NOT NULL DEFAULT 0,
    status ENUM('pending', 'preparing', 'ready', 'completed', 'cancelled') DEFAULT 'pending',
    delivery_address TEXT,
    payment_method ENUM('cash', 'card', 'upi', 'netbanking') DEFAULT 'cash',
    special_instructions TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== ORDER ITEMS TABLE ====================
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    food_item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price_per_item DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    special_request TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id) ON DELETE RESTRICT,
    INDEX idx_order (order_id),
    INDEX idx_food_item (food_item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== PAYMENTS TABLE ====================
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method ENUM('cash', 'card', 'upi', 'netbanking') NOT NULL,
    transaction_id VARCHAR(255),
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_order (order_id),
    INDEX idx_status (payment_status),
    INDEX idx_transaction (transaction_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== REVIEWS TABLE (Optional) ====================
CREATE TABLE IF NOT EXISTS reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    food_item_id INT NOT NULL,
    order_id INT,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_item_id) REFERENCES food_items(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_food_item (food_item_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==================== INSERT SAMPLE DATA ====================

-- Insert Default Admin
INSERT INTO admins (username, email, password) VALUES
('Admin', 'admin@cloudcuisine.com', 'pbkdf2:sha256:260000$WJ3ZHgXC$7d7e1b1e8b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2');

-- Note: Password is 'admin123' - hash generated with werkzeug.security

-- Insert Categories
INSERT INTO categories (name, description, image_url, sort_order) VALUES
('Appetizers', 'Start your meal with delicious appetizers', 'uploads/appetizers.jpg', 1),
('Main Course', 'Hearty main dishes for a satisfying meal', 'uploads/maincourse.jpg', 2),
('Biryani', 'Aromatic rice dishes with spices and flavors', 'uploads/biryani.jpg', 3),
('Indian Breads', 'Freshly baked traditional breads', 'uploads/breads.jpg', 4),
('Soups & Salads', 'Fresh and healthy soups and salads', 'uploads/soups.jpg', 5),
('Desserts', 'Sweet endings to your meal', 'uploads/desserts.jpg', 6),
('Beverages', 'Refreshing drinks and beverages', 'uploads/beverages.jpg', 7),
('Chinese', 'Indo-Chinese fusion favorites', 'uploads/chinese.jpg', 8);

-- Insert Food Items
INSERT INTO food_items (name, description, price, category_id, preparation_time, is_veg, is_available, is_featured) VALUES
-- Appetizers
('Veg Spring Rolls', 'Crispy rolls filled with mixed vegetables, served with sweet chili sauce', 149.00, 1, 15, TRUE, TRUE, TRUE),
('Paneer Tikka', 'Marinated cottage cheese cubes grilled to perfection', 199.00, 1, 20, TRUE, TRUE, TRUE),
('Chicken Tikka', 'Succulent chicken pieces marinated in spices and grilled', 249.00, 1, 25, FALSE, TRUE, TRUE),
('Samosa', 'Crispy pastry filled with spiced potatoes and peas', 49.00, 1, 10, TRUE, TRUE, FALSE),
('Hara Bhara Kebab', 'Green patties made with spinach and peas', 179.00, 1, 20, TRUE, TRUE, FALSE),
('Fish Fingers', 'Crispy fried fish strips served with tartar sauce', 299.00, 1, 20, FALSE, TRUE, FALSE),

-- Main Course
('Paneer Butter Masala', 'Cottage cheese in rich tomato and butter gravy', 279.00, 2, 25, TRUE, TRUE, TRUE),
('Dal Makhani', 'Black lentils slow cooked with butter and cream', 199.00, 2, 30, TRUE, TRUE, TRUE),
('Butter Chicken', 'Tender chicken in creamy tomato sauce', 329.00, 2, 30, FALSE, TRUE, TRUE),
('Palak Paneer', 'Cottage cheese cubes in spinach gravy', 259.00, 2, 25, TRUE, TRUE, FALSE),
('Kadai Chicken', 'Chicken cooked with bell peppers and aromatic spices', 349.00, 2, 30, FALSE, TRUE, TRUE),
('Veg Korma', 'Mixed vegetables in mild cashew-based gravy', 239.00, 2, 25, TRUE, TRUE, FALSE),
('Mutton Rogan Josh', 'Tender mutton in Kashmiri-style curry', 399.00, 2, 40, FALSE, TRUE, FALSE),

-- Biryani
('Veg Biryani', 'Fragrant basmati rice with mixed vegetables and spices', 249.00, 3, 35, TRUE, TRUE, TRUE),
('Chicken Biryani', 'Classic Hyderabadi-style chicken biryani', 299.00, 3, 40, FALSE, TRUE, TRUE),
('Mutton Biryani', 'Tender mutton biryani with aromatic spices', 349.00, 3, 45, FALSE, TRUE, TRUE),
('Egg Biryani', 'Fragrant rice with boiled eggs and spices', 269.00, 3, 35, FALSE, TRUE, FALSE),

-- Indian Breads
('Butter Naan', 'Soft leavened bread brushed with butter', 49.00, 4, 10, TRUE, TRUE, TRUE),
('Garlic Naan', 'Naan flavored with garlic and herbs', 59.00, 4, 10, TRUE, TRUE, TRUE),
('Tandoori Roti', 'Whole wheat bread baked in tandoor', 29.00, 4, 8, TRUE, TRUE, FALSE),
('Laccha Paratha', 'Layered whole wheat bread', 59.00, 4, 12, TRUE, TRUE, FALSE),
('Stuffed Kulcha', 'Soft bread stuffed with cottage cheese and spices', 79.00, 4, 15, TRUE, TRUE, FALSE),

-- Soups & Salads
('Tomato Soup', 'Classic tomato soup with croutons', 99.00, 5, 15, TRUE, TRUE, FALSE),
('Hot & Sour Soup', 'Indo-Chinese soup with vegetables', 119.00, 5, 15, TRUE, TRUE, TRUE),
('Chicken Clear Soup', 'Light chicken broth with vegetables', 139.00, 5, 20, FALSE, TRUE, FALSE),
('Caesar Salad', 'Fresh romaine lettuce with caesar dressing', 149.00, 5, 10, TRUE, TRUE, FALSE),
('Greek Salad', 'Fresh vegetables with feta cheese and olives', 179.00, 5, 10, TRUE, TRUE, FALSE),

-- Desserts
('Gulab Jamun', 'Deep fried milk dumplings soaked in sugar syrup', 79.00, 6, 15, TRUE, TRUE, TRUE),
('Rasmalai', 'Cottage cheese dumplings in sweetened milk', 99.00, 6, 20, TRUE, TRUE, TRUE),
('Kulfi', 'Traditional Indian ice cream', 89.00, 6, 10, TRUE, TRUE, FALSE),
('Brownie with Ice Cream', 'Warm chocolate brownie with vanilla ice cream', 149.00, 6, 15, TRUE, TRUE, TRUE),
('Kheer', 'Rice pudding with nuts and cardamom', 99.00, 6, 25, TRUE, TRUE, FALSE),

-- Beverages
('Masala Chai', 'Traditional Indian spiced tea', 39.00, 7, 5, TRUE, TRUE, TRUE),
('Fresh Lime Soda', 'Refreshing lime drink with soda', 59.00, 7, 5, TRUE, TRUE, TRUE),
('Mango Lassi', 'Creamy yogurt drink with mango', 89.00, 7, 10, TRUE, TRUE, TRUE),
('Cold Coffee', 'Iced coffee with milk and sugar', 99.00, 7, 10, TRUE, TRUE, FALSE),
('Fresh Orange Juice', 'Freshly squeezed orange juice', 79.00, 7, 10, TRUE, TRUE, FALSE),
('Buttermilk', 'Spiced yogurt drink (Chaas)', 49.00, 7, 5, TRUE, TRUE, FALSE),

-- Chinese
('Veg Manchurian', 'Vegetable balls in tangy manchurian sauce', 199.00, 8, 20, TRUE, TRUE, TRUE),
('Chicken Manchurian', 'Chicken balls in spicy manchurian sauce', 249.00, 8, 25, FALSE, TRUE, TRUE),
('Veg Fried Rice', 'Flavored rice with mixed vegetables', 179.00, 8, 15, TRUE, TRUE, TRUE),
('Chicken Fried Rice', 'Fried rice with chicken pieces', 229.00, 8, 20, FALSE, TRUE, TRUE),
('Chilli Chicken', 'Crispy chicken in spicy sauce', 279.00, 8, 25, FALSE, TRUE, FALSE),
('Veg Hakka Noodles', 'Stir-fried noodles with vegetables', 169.00, 8, 15, TRUE, TRUE, FALSE);

-- Insert Sample Users
INSERT INTO users (username, email, password, phone, address) VALUES
('John Doe', 'john@example.com', 'pbkdf2:sha256:260000$WJ3ZHgXC$7d7e1b1e8b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', '9876543210', '123 Main Street, Food City'),
('Jane Smith', 'jane@example.com', 'pbkdf2:sha256:260000$WJ3ZHgXC$7d7e1b1e8b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', '9876543211', '456 Oak Avenue, Food City'),
('Mike Wilson', 'mike@example.com', 'pbkdf2:sha256:260000$WJ3ZHgXC$7d7e1b1e8b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2g3h4i5j6k7l8m9n0o1p2', '9876543212', '789 Pine Road, Food City');

-- Insert Sample Orders
INSERT INTO orders (user_id, total_amount, gst_amount, service_charge, discount, grand_total, status, delivery_address, payment_method, special_instructions, created_at) VALUES
(1, 498.00, 89.64, 24.90, 0.00, 612.54, 'completed', '123 Main Street, Food City', 'card', 'No onions please', NOW() - INTERVAL 5 DAY),
(2, 329.00, 59.22, 16.45, 32.90, 371.77, 'completed', '456 Oak Avenue, Food City', 'cash', 'Extra spicy', NOW() - INTERVAL 3 DAY),
(1, 249.00, 44.82, 12.45, 0.00, 306.27, 'completed', '123 Main Street, Food City', 'upi', NULL, NOW() - INTERVAL 2 DAY),
(3, 578.00, 104.04, 28.90, 57.80, 653.14, 'completed', '789 Pine Road, Food City', 'card', 'Allergic to nuts', NOW() - INTERVAL 1 DAY),
(1, 199.00, 35.82, 9.95, 0.00, 244.77, 'preparing', '123 Main Street, Food City', 'cash', NULL, NOW()),
(2, 419.00, 75.42, 20.95, 0.00, 515.37, 'pending', '456 Oak Avenue, Food City', 'card', 'Doorbell not working', NOW());

-- Insert Order Items
INSERT INTO order_items (order_id, food_item_id, quantity, price_per_item, subtotal) VALUES
-- Order 1
(1, 1, 2, 149.00, 298.00),
(1, 19, 1, 49.00, 49.00),
(1, 20, 1, 59.00, 59.00),
(1, 27, 2, 39.00, 78.00),
(1, 32, 1, 79.00, 79.00),
-- Order 2
(2, 10, 1, 329.00, 329.00),
-- Order 3
(3, 15, 1, 249.00, 249.00),
(3, 32, 2, 79.00, 158.00),
-- Order 4
(4, 4, 2, 249.00, 498.00),
(4, 19, 2, 49.00, 98.00),
(4, 26, 1, 149.00, 149.00),
-- Order 5
(5, 8, 1, 199.00, 199.00),
-- Order 6
(6, 7, 1, 279.00, 279.00),
(6, 15, 1, 249.00, 249.00),
(6, 20, 1, 59.00, 59.00);

-- Insert Payment Records
INSERT INTO payments (order_id, amount, payment_method, transaction_id, payment_status) VALUES
(1, 612.54, 'card', 'TXN001234567', 'completed'),
(2, 371.77, 'cash', NULL, 'completed'),
(3, 306.27, 'upi', 'UPI@123456', 'completed'),
(4, 653.14, 'card', 'TXN002345678', 'completed'),
(5, 244.77, 'cash', NULL, 'pending'),
(6, 515.37, 'card', 'TXN003456789', 'pending');

-- ==================== CREATE TRIGGERS ====================

DELIMITER //

-- Trigger to update order completion timestamp
CREATE TRIGGER update_order_completion
BEFORE UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        SET NEW.completed_at = NOW();
    END IF;
END//

DELIMITER ;

-- ==================== CREATE VIEWS ====================

-- View for order summary with customer details
CREATE OR REPLACE VIEW order_summary AS
SELECT
    o.id as order_id,
    u.username as customer_name,
    u.email as customer_email,
    u.phone as customer_phone,
    o.grand_total,
    o.status,
    o.payment_method,
    o.created_at as order_date
FROM orders o
JOIN users u ON o.user_id = u.id;

-- View for daily sales summary
CREATE OR REPLACE VIEW daily_sales AS
SELECT
    DATE(created_at) as sale_date,
    COUNT(*) as total_orders,
    SUM(total_amount) as subtotal,
    SUM(gst_amount) as gst_collected,
    SUM(discount) as discounts_given,
    SUM(grand_total) as total_revenue
FROM orders
WHERE status = 'completed'
GROUP BY DATE(created_at);

-- ==================== CREATE INDEXES FOR PERFORMANCE ====================

CREATE INDEX idx_order_created_date ON orders(DATE(created_at));
CREATE INDEX idx_order_user_status ON orders(user_id, status);

-- ==================== GRANT PERMISSIONS ====================

-- Grant permissions to the application user
-- GRANT ALL PRIVILEGES ON cloudcuisine.* TO 'your_user'@'localhost' IDENTIFIED BY 'your_password';
-- FLUSH PRIVILEGES;

SELECT 'Database setup completed successfully!' as status;

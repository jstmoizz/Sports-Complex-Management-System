-- ===============================
-- SPORTS COMPLEX MANAGEMENT SYSTEM
-- ===============================

DROP DATABASE IF EXISTS sports_complex;
CREATE DATABASE sports_complex;
USE sports_complex;

-- ===============================
-- USERS TABLE
-- ===============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cms_id VARCHAR(6) UNIQUE NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','user') DEFAULT 'user',

    membership_status ENUM('inactive','active','cancelled') DEFAULT 'inactive',
    membership_start DATE NULL,
    membership_end DATE NULL,
    
    medical_conditions TEXT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ===============================
-- FACILITIES TABLE
-- ===============================
CREATE TABLE facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    monthly_fee INT DEFAULT 1000,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO facilities (name) VALUES
('Swimming'),
('Gym'),
('Horse Riding');

-- ===============================
-- USER FACILITIES (M:N RELATION)
-- ===============================
CREATE TABLE user_facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    facility_id INT NOT NULL,

    start_date DATE NOT NULL,
    last_payment_date DATE NOT NULL,

    UNIQUE (user_id, facility_id),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (facility_id) REFERENCES facilities(id) ON DELETE CASCADE
);

-- ===============================
-- PAYMENTS TABLE
-- ===============================
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    amount INT NOT NULL,
    payment_type ENUM('membership','facility') NOT NULL,
    transaction_id VARCHAR(16),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===============================
-- GROUNDS TABLE
-- ===============================
CREATE TABLE grounds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO grounds (name) VALUES
('Football'),
('Basketball'),
('Volleyball'),
('Tennis'),
('Badminton');

-- ===============================
-- GROUND BOOKINGS TABLE
-- ===============================
CREATE TABLE ground_bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    ground_id INT NOT NULL,
    
    booking_date DATE NOT NULL,
    booking_time VARCHAR(5) NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE (ground_id, booking_date, booking_time),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ground_id) REFERENCES grounds(id) ON DELETE CASCADE
);

-- ===============================
-- ADMIN DEFAULT ACCOUNT
-- ===============================
INSERT INTO users (full_name, email, password, role)
VALUES (
    'Admin',
    'admin@sports.com',
    SHA2('admin123', 256),
    'admin'
);
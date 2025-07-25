CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash TEXT,
    role ENUM('client', 'handyman', 'admin') DEFAULT 'client',
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE handyman_profiles (
    handyman_id INT PRIMARY KEY,
    category VARCHAR(50), -- e.g., 'electrician', 'plumber'
    experience_years INT,
    bio TEXT,
    rating FLOAT DEFAULT 0,
    jobs_completed INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    subscription_plan ENUM('free', 'premium') DEFAULT 'free',
    FOREIGN KEY (handyman_id) REFERENCES users(user_id)
);

CREATE TABLE job_requests (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    handyman_id INT,
    category VARCHAR(50),
    job_description TEXT,
    job_location VARCHAR(100),
    preferred_date DATE,
    status ENUM('pending', 'accepted', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users(user_id),
    FOREIGN KEY (handyman_id) REFERENCES users(user_id)
);

CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT,
    client_id INT,
    handyman_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job_requests(job_id),
    FOREIGN KEY (client_id) REFERENCES users(user_id),
    FOREIGN KEY (handyman_id) REFERENCES users(user_id)
);


CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    amount DECIMAL(10,2),
    purpose ENUM('job_commission', 'subscription', 'ad_payment'),
    reference_code VARCHAR(100),
    payment_method VARCHAR(50),
    status ENUM('pending', 'successful', 'failed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE job_ads (
    ad_id INT PRIMARY KEY AUTO_INCREMENT,
    handyman_id INT,
    title VARCHAR(100),
    ad_description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (handyman_id) REFERENCES users(user_id)
);

CREATE TABLE sms_logs (
    sms_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    message TEXT,
    phone VARCHAR(20),
    status ENUM('sent', 'failed'),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- Bonus Admin Table
CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password_hash TEXT,
    email VARCHAR(100)
);

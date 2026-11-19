CREATE DATABASE IF NOT EXISTS QFlow;
USE QFlow;

CREATE TABLE Businesses (
    business_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    phone VARCHAR(15)
);

CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    business_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff', 'customer') NOT NULL,

    CONSTRAINT fk_users_business
        FOREIGN KEY (business_id) REFERENCES Businesses(business_id)
);

CREATE TABLE Services (
    service_id INT PRIMARY KEY AUTO_INCREMENT,
    business_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    estimated_time INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_services_estimated_time
        CHECK (estimated_time > 0),

    CONSTRAINT fk_services_business
        FOREIGN KEY (business_id) REFERENCES Businesses(business_id)
);

CREATE TABLE Counters (
    counter_id INT PRIMARY KEY AUTO_INCREMENT,
    business_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_counters_business
        FOREIGN KEY (business_id) REFERENCES Businesses(business_id)
);

CREATE TABLE Queues (
    queue_id INT PRIMARY KEY AUTO_INCREMENT,
    service_id INT NOT NULL,
    queue_date DATE NOT NULL,
    status ENUM('Active', 'Paused', 'Closed') NOT NULL DEFAULT 'Active',

    CONSTRAINT fk_queues_service
        FOREIGN KEY (service_id) REFERENCES Services(service_id)
);

CREATE TABLE Tokens (
    token_id INT PRIMARY KEY AUTO_INCREMENT,
    queue_id INT NOT NULL,
    customer_id INT NOT NULL,
    counter_id INT,
    token_number INT NOT NULL,
    status ENUM('Waiting', 'Called', 'Completed', 'Cancelled', 'Skipped')
        NOT NULL DEFAULT 'Waiting',
    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    called_at DATETIME,
    completed_at DATETIME,

    CONSTRAINT chk_tokens_token_number
        CHECK (token_number > 0),

    CONSTRAINT uq_tokens_queue_number
        UNIQUE (queue_id, token_number),

    CONSTRAINT fk_tokens_queue
        FOREIGN KEY (queue_id) REFERENCES Queues(queue_id),

    CONSTRAINT fk_tokens_customer
        FOREIGN KEY (customer_id) REFERENCES Users(user_id),

    CONSTRAINT fk_tokens_counter
        FOREIGN KEY (counter_id) REFERENCES Counters(counter_id)
);

CREATE TABLE Queue_History (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    token_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    action_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_queue_history_token
        FOREIGN KEY (token_id) REFERENCES Tokens(token_id)
);

INSERT INTO Businesses (name, type, address, phone)
VALUES
('City Care Hospital', 'Hospital', 'Kukatpally, Hyderabad', '9876543210'),
('QuickBite Restaurant', 'Restaurant', 'Miyapur, Hyderabad', '9876543211');

-- Classroom sample values only.
-- In a real application, store a securely generated password hash here.
INSERT INTO Users (business_id, name, email, password, role)
VALUES
(1, 'Raj Admin', 'admin@citycare.com', 'admin123', 'admin'),
(1, 'Dr. Kumar', 'kumar@citycare.com', 'doctor123', 'staff'),
(1, 'Ravi', 'ravi@gmail.com', 'ravi123', 'customer'),
(1, 'Arjun', 'arjun@gmail.com', 'arjun123', 'customer'),
(1, 'Priya', 'priya@gmail.com', 'priya123', 'customer'),
(2, 'Restaurant Admin', 'admin@quickbite.com', 'admin456', 'admin'),
(2, 'Rahul', 'rahul@gmail.com', 'rahul123', 'customer');

INSERT INTO Services (business_id, name, estimated_time, is_active)
VALUES
(1, 'General Checkup', 10, TRUE),
(1, 'Dental Checkup', 20, TRUE),
(2, 'Food Ordering', 15, TRUE);

INSERT INTO Counters (business_id, name, is_active)
VALUES
(1, 'Counter 1', TRUE),
(1, 'Counter 2', TRUE),
(2, 'Counter 1', TRUE);

INSERT INTO Queues (service_id, queue_date, status)
VALUES
(1, CURDATE(), 'Active'),
(2, CURDATE(), 'Active'),
(3, CURDATE(), 'Active');

SHOW TABLES;

DESC Businesses;
DESC Users;
DESC Services;
DESC Counters;
DESC Queues;
DESC Tokens;
DESC Queue_History;


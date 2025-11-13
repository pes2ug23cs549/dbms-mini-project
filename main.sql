DROP DATABASE IF EXISTS lostfound;
CREATE DATABASE lostfound;
USE lostfound;


-- TABLE 1: USERS
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  phone VARCHAR(15),
  role ENUM('student','staff','admin') DEFAULT 'student'
);

-- TABLE 2: LOCATIONS  (Separate table for normalization)
CREATE TABLE locations (
  location_id INT AUTO_INCREMENT PRIMARY KEY,
  location_name VARCHAR(100) NOT NULL,
  building VARCHAR(50),
  floor_no INT
);

-- TABLE 3: ITEMS
CREATE TABLE items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  item_name VARCHAR(100) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  status ENUM('lost','found','claimed') DEFAULT 'lost',
  report_date DATE DEFAULT (CURRENT_DATE),
  reported_by INT,
  location_id INT,
  FOREIGN KEY (reported_by) REFERENCES users(user_id),
  FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- TABLE 4: CLAIMS
CREATE TABLE claims (
  claim_id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT,
  claimer_id INT,
  claim_date DATE DEFAULT (CURRENT_DATE),
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  remarks VARCHAR(255),
  FOREIGN KEY (item_id) REFERENCES items(item_id),
  FOREIGN KEY (claimer_id) REFERENCES users(user_id)
);

-- FUNCTION: Count how many items a user has reported
DELIMITER //
CREATE FUNCTION count_items_by_user(p_user_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE total INT;
  SELECT COUNT(*) INTO total FROM items WHERE reported_by = p_user_id;
  RETURN total;
END //
DELIMITER ;

-- PROCEDURE 1: Add a Lost or Found Item
DELIMITER //
CREATE PROCEDURE add_item(
  IN p_name VARCHAR(100),
  IN p_desc TEXT,
  IN p_cat VARCHAR(50),
  IN p_status ENUM('lost','found'),
  IN p_user INT,
  IN p_loc INT
)
BEGIN
  INSERT INTO items(item_name, description, category, status, reported_by, location_id)
  VALUES (p_name, p_desc, p_cat, p_status, p_user, p_loc);
END //
DELIMITER ;

-- PROCEDURE 2: Approve or Reject a Claim
DELIMITER //
CREATE PROCEDURE update_claim_status(
  IN p_claim_id INT,
  IN p_status ENUM('approved','rejected'),
  IN p_remark VARCHAR(255)
)
BEGIN
  UPDATE claims
  SET status = p_status,
      remarks = p_remark
  WHERE claim_id = p_claim_id;
END //
DELIMITER ;

-- TRIGGER 1: Auto-append timestamp info when a new item is inserted
DELIMITER //
CREATE TRIGGER trg_item_insert
BEFORE INSERT ON items
FOR EACH ROW
BEGIN
  -- Automatically append timestamp info to description
  SET NEW.description = CONCAT(
      COALESCE(NEW.description, ''),
      ' [Added on: ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), ']'
  );
END //
DELIMITER ;

-- TRIGGER 2: Auto-update item status when claim is approved
DELIMITER //
CREATE TRIGGER trg_claim_approve
AFTER UPDATE ON claims
FOR EACH ROW
BEGIN
  IF NEW.status = 'approved' THEN
    UPDATE items 
    SET status='claimed',
        description = CONCAT(
            COALESCE(description,''), 
            ' [Claim approved on ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'), ']'
        )
    WHERE item_id=NEW.item_id;
  END IF;
END //
DELIMITER ;


-- SAMPLE DATA POPULATION (DML)

-- Users
INSERT INTO users (name, email, phone, role) VALUES
('Shivam Anand', 'shivam@example.com', '9999999999', 'student'),
('Priya Verma', 'priya@example.com', '8888888888', 'staff'),
('Ravi Adram', 'ravi.admin@example.com', '7777777777', 'admin');

-- Locations
INSERT INTO locations (location_name, building, floor_no) VALUES
('Library', 'Block A', 1),
('Cafeteria', 'Block B', 0),
('Main Ground', 'Block C', 0);

-- Items (Lost + Found)
INSERT INTO items (item_name, description, category, status, reported_by, location_id)
VALUES
('Black Wallet', 'Leather wallet with ID card', 'Accessories', 'lost', 1, 1),
('Water Bottle', 'Blue Milton bottle', 'Daily Use', 'found', 2, 2),
('Laptop Charger', 'HP charger 65W', 'Electronics', 'lost', 1, 3);

-- Claims
INSERT INTO claims (item_id, claimer_id, status, remarks)
VALUES
(2, 1, 'pending', 'Looks like my bottle'),
(1, 2, 'approved', 'Owner confirmed');

-- APPLICATION QUERIES

-- Nested Query: Users who reported more than average number of items
SELECT name, user_id
FROM users
WHERE user_id IN (
    SELECT reported_by
    FROM items
    GROUP BY reported_by
    HAVING COUNT(item_id) > (
        SELECT AVG(item_count)
        FROM (
            SELECT COUNT(item_id) AS item_count
            FROM items
            GROUP BY reported_by
        ) AS sub
    )
);

-- Join Query: Show all claims with related item and user info
SELECT 
    c.claim_id,
    i.item_name,
    u.name AS claimer_name,
    c.status AS claim_status,
    i.status AS item_status
FROM claims c
JOIN items i ON c.item_id = i.item_id
JOIN users u ON c.claimer_id = u.user_id;

-- Aggregate Query: Count of items by category
SELECT 
    category,
    COUNT(item_id) AS total_items
FROM items
GROUP BY category
ORDER BY total_items DESC;

-- Correlated Query: Items reported by users who have claimed items
SELECT 
    u.user_id,
    u.name
FROM users u
WHERE EXISTS (
    SELECT 1
    FROM items i
    WHERE i.reported_by = u.user_id   
);


-- DEMO CALLS
-- Example: Add item using procedure
-- CALL add_item('Red Umbrella','Lost during rain','Accessories','lost',1,3);

-- Example: Approve claim
-- CALL update_claim_status(1,'approved','Verified');

-- Example: Check how many items user 1 reported
-- SELECT count_items_by_user(1) AS total_items;



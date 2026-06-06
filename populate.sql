-- populates query tables with data
INSERT INTO users (login, password, phonenumber, address, role) VALUES ('alice', 'password123', '123-456-7890', '123 Main St', 'Seller');
INSERT INTO users (login, password, phonenumber, address, role) VALUES ('bob', 'password456', '234-567-8901', '456 Oak Ave', 'Buyer');
INSERT INTO users (login, password, phonenumber, address, role) VALUES ('charlie', 'password789', '345-678-9012', '789 Pine Rd', 'Admin');

INSERT INTO item (item_id, item_name, category, starting_price, image_url, item_condition, description, seller_login, seller_role) VALUES (1, 'Vintage Clock', 'Antiques', 50.00, 'http://example.com/clock.jpg', 'Used', 'A beautiful vintage clock in working condition.', 'alice', 'Seller');
INSERT INTO item (item_id, item_name, category, starting_price, image_url, item_condition, description, seller_login, seller_role) VALUES (2, 'Gaming Console', 'Electronics', 200.00, 'http://example.com/console.jpg', 'New', 'A brand new gaming console with all accessories.', 'alice', 'Seller');

INSERT INTO auction (auction_id, item_id, seller_login, seller_role) VALUES (1, 1, 'alice', 'Seller');
INSERT INTO auction (auction_id, item_id, seller_login, seller_role) VALUES (2, 2, 'alice', 'Seller');

INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) VALUES (1, 1, 'bob', 'Buyer', 55.00);
INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) VALUES (2, 2, 'bob', 'Buyer', 250.00);

INSERT INTO payment (payment_id, auction_id, buyer_login, buyer_role, amount, payment_status) VALUES (1, 1, 'bob', 'Buyer', 55.00, 'Completed');

INSERT INTO shipment (shipment_id, auction_id, buyer_login, buyer_role, shipping_address, shipping_status) VALUES (1, 1, 'bob', 'Buyer', '456 Oak Ave', 'Shipped');
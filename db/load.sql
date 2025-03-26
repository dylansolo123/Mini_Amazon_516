-- Load Users
\copy Users(email, full_name, address, password, balance, is_seller) FROM 'users.csv' WITH CSV HEADER;
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM Users));

-- Load Product Categories
\copy Product_Categories(category_name, description) FROM 'product_categories.csv' WITH CSV HEADER;
SELECT setval('product_categories_category_id_seq', (SELECT MAX(category_id) FROM Product_Categories));

-- Load Products
\copy Products(category_id, name, description, image_url, created_by) FROM 'products.csv' WITH CSV HEADER;
SELECT setval('products_product_id_seq', (SELECT MAX(product_id) FROM Products));

-- Load Seller Inventory
\copy Seller_Inventory(seller_id, product_id, price, quantity) FROM 'seller_inventory.csv' WITH CSV HEADER;
SELECT setval('seller_inventory_inventory_id_seq', (SELECT MAX(inventory_id) FROM Seller_Inventory));

-- Load Carts
\copy Carts(user_id) FROM 'carts.csv' WITH CSV HEADER;
SELECT setval('carts_cart_id_seq', (SELECT MAX(cart_id) FROM Carts));

-- Load Cart Items
\copy Cart_Items(cart_id, seller_id, product_id, quantity, unit_price) FROM 'cart_items.csv' WITH CSV HEADER;
SELECT setval('cart_items_cart_item_id_seq', (SELECT MAX(cart_item_id) FROM Cart_Items));

-- Load Orders
\copy Orders(buyer_id, total_amount, fulfillment_status) FROM 'orders.csv' WITH CSV HEADER;
SELECT setval('orders_order_id_seq', (SELECT MAX(order_id) FROM Orders));

-- Load Order Items
\copy Order_Items(order_id, seller_id, product_id, quantity, unit_price, fulfillment_status) FROM 'order_items.csv' WITH CSV HEADER;
SELECT setval('order_items_order_item_id_seq', (SELECT MAX(order_item_id) FROM Order_Items));

-- Load Product Reviews
\copy Product_Reviews(product_id, user_id, rating, review_text) FROM 'product_reviews.csv' WITH CSV HEADER;
SELECT setval('product_reviews_review_id_seq', (SELECT MAX(review_id) FROM Product_Reviews));

-- Load Seller Reviews
\copy Seller_Reviews(seller_id, user_id, rating, review_text) FROM 'seller_reviews.csv' WITH CSV HEADER;
SELECT setval('seller_reviews_review_id_seq', (SELECT MAX(review_id) FROM Seller_Reviews));
-- Load Message Threads
\copy Message_Threads(buyer_id, seller_id, order_id) FROM 'message_threads.csv' WITH CSV HEADER;
SELECT setval('message_threads_thread_id_seq', (SELECT MAX(thread_id) FROM Message_Threads));

-- Load Messages
\copy Messages(thread_id, sender_id, message_text) FROM 'messages.csv' WITH CSV HEADER;
SELECT setval('messages_message_id_seq', (SELECT MAX(message_id) FROM Messages));


-- Table: Users
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    address TEXT,
    password VARCHAR(255) NOT NULL,
    balance DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    is_seller BOOLEAN NOT NULL DEFAULT FALSE
);

-- Table: Product_Categories
CREATE TABLE Product_Categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    description TEXT
);

-- Table: Products
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(512),
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category FOREIGN KEY (category_id)
        REFERENCES Product_Categories(category_id),
    CONSTRAINT fk_products_created_by FOREIGN KEY (created_by)
        REFERENCES Users(user_id)
);

-- Table: Seller_Inventory
CREATE TABLE Seller_Inventory (
    inventory_id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_seller_inventory_seller FOREIGN KEY (seller_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_seller_inventory_product FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

-- Table: Carts
CREATE TABLE Carts (
    cart_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,  -- one cart per user
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_carts_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
);

-- Table: Cart_Items
CREATE TABLE Cart_Items (
    cart_item_id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_items_cart FOREIGN KEY (cart_id)
        REFERENCES Carts(cart_id),
    CONSTRAINT fk_cart_items_seller FOREIGN KEY (seller_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_cart_items_product FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

-- Table: Orders
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    CONSTRAINT fk_orders_buyer FOREIGN KEY (buyer_id)
        REFERENCES Users(user_id)
);

-- Table: Order_Items
CREATE TABLE Order_Items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    fulfillment_status VARCHAR(50) NOT NULL DEFAULT 'Pending',
    fulfillment_date TIMESTAMP,
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id)
        REFERENCES Orders(order_id),
    CONSTRAINT fk_order_items_seller FOREIGN KEY (seller_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
);

-- Table: Product_Reviews
CREATE TABLE Product_Reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_reviews_product FOREIGN KEY (product_id)
        REFERENCES Products(product_id),
    CONSTRAINT fk_product_reviews_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
);

-- Table: Seller_Reviews
CREATE TABLE Seller_Reviews (
    review_id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    review_text TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_seller_reviews_seller FOREIGN KEY (seller_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_seller_reviews_user FOREIGN KEY (user_id)
        REFERENCES Users(user_id)
);

-- Table: Message_Threads
CREATE TABLE Message_Threads (
    thread_id SERIAL PRIMARY KEY,
    buyer_id INTEGER NOT NULL,
    seller_id INTEGER NOT NULL,
    order_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_threads_buyer FOREIGN KEY (buyer_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_message_threads_seller FOREIGN KEY (seller_id)
        REFERENCES Users(user_id),
    CONSTRAINT fk_message_threads_order FOREIGN KEY (order_id)
        REFERENCES Orders(order_id)
);

-- Table: Messages
CREATE TABLE Messages (
    message_id SERIAL PRIMARY KEY,
    thread_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_thread FOREIGN KEY (thread_id)
        REFERENCES Message_Threads(thread_id),
    CONSTRAINT fk_messages_sender FOREIGN KEY (sender_id)
        REFERENCES Users(user_id)
);

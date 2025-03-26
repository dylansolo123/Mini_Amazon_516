from werkzeug.security import generate_password_hash
import csv
from faker import Faker
import random
import os
from collections import defaultdict

# Create generated directory
os.makedirs('generated', exist_ok=True)

# Constants for data generation
num_users = 100
num_categories = 9  # Must match the actual categories list
num_products = 100  # Reduced to ensure consistency
num_seller_inventory = 200
num_carts = 50
num_cart_items = 100
num_orders = 150
num_order_items = 200
num_product_reviews = 100
num_seller_reviews = 50
num_message_threads = 50
num_messages = 100

# Track valid IDs
valid_products = set()
valid_sellers = set()
valid_carts = set()
valid_orders = set()
valid_threads = set()
valid_inventory = []

Faker.seed(0)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    with open('generated/users.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        # Add header row to match load.sql
        writer.writerow(['email', 'full_name', 'address', 'password', 'balance', 'is_seller'])
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            full_name = fake.name()
            address = fake.address().replace('\n', ' ')
            balance = f'{str(fake.random_int(max=1000))}.{fake.random_int(max=99):02}'
            is_seller = 'true' if random.random() < 0.3 else 'false'
            if is_seller == 'true':
                valid_sellers.add(uid + 1)
            writer.writerow([email, full_name, address, password, balance, is_seller])
        print(f'{num_users} generated')

def gen_product_categories(num_categories):
    categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports', 
                 'Toys', 'Food', 'Beauty', 'Garden']
    with open('generated/product_categories.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        # Add header row to match load.sql
        writer.writerow(['category_name', 'description'])
        print('Product Categories...', end=' ', flush=True)
        for i in range(len(categories)):
            if i % 2 == 0:
                print(f'{i}', end=' ', flush=True)
            category_name = categories[i]
            description = fake.text(max_nb_chars=200).replace('\n', ' ')
            writer.writerow([category_name, description])
        print(f'{len(categories)} generated')

def gen_products(num_products):
    # Define valid category IDs (1 through 9)
    valid_categories = list(range(1, 10))  # Creates list [1,2,3,4,5,6,7,8,9]
    
    with open('generated/products.csv', 'w', newline='') as f:
        writer = get_csv_writer(f)
        writer.writerow(['category_id', 'name', 'description', 'image_url', 'created_by'])
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 50 == 0:
                print(f'{pid}', end=' ', flush=True)
            # Use random.choice instead of randint to ensure we only get valid categories
            category_id = random.choice(valid_categories)
            name = fake.catch_phrase()
            description = fake.text(max_nb_chars=200).replace('\n', ' ')
            image_url = f'http://example.com/images/product{pid}.jpg'
            created_by = random.choice(list(valid_sellers)) if valid_sellers else 1
            valid_products.add(pid + 1)
            writer.writerow([category_id, name, description, image_url, created_by])
        print(f'{num_products} generated')

def gen_seller_inventory(num_seller_inventory):
    with open('generated/seller_inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['seller_id', 'product_id', 'price', 'quantity'])
        print('Seller Inventory...', end=' ', flush=True)
        for i in range(num_seller_inventory):
            if i % 50 == 0:
                print(f'{i}', end=' ', flush=True)
            seller_id = random.choice(list(valid_sellers))
            product_id = random.choice(list(valid_products))
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            quantity = fake.random_int(min=1, max=100)
            valid_inventory.append((seller_id, product_id, price))
            writer.writerow([seller_id, product_id, price, quantity])
        print(f'{num_seller_inventory} generated')

def gen_carts(num_carts):
    used_users = set()
    with open('generated/carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['user_id'])
        print('Carts...', end=' ', flush=True)
        cart_id = 1
        while len(used_users) < num_carts:
            user_id = random.randint(1, num_users)
            if user_id not in used_users:
                used_users.add(user_id)
                valid_carts.add(cart_id)
                writer.writerow([user_id])
                cart_id += 1
        print(f'{num_carts} generated')

def gen_cart_items(num_cart_items):
    with open('generated/cart_items.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['cart_id', 'seller_id', 'product_id', 'quantity', 'unit_price'])
        print('Cart Items...', end=' ', flush=True)
        for i in range(num_cart_items):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            cart_id = random.choice(list(valid_carts))
            if valid_inventory:
                seller_id, product_id, unit_price = random.choice(valid_inventory)
                quantity = random.randint(1, 10)
                writer.writerow([cart_id, seller_id, product_id, quantity, unit_price])
        print(f'{num_cart_items} generated')

def gen_orders(num_orders):
    with open('generated/orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['buyer_id', 'total_amount', 'status'])
        print('Orders...', end=' ', flush=True)
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
        for i in range(num_orders):
            if i % 30 == 0:
                print(f'{i}', end=' ', flush=True)
            buyer_id = random.randint(1, num_users)
            total_amount = f'{str(fake.random_int(max=2000))}.{fake.random_int(max=99):02}'
            status = random.choice(statuses)
            valid_orders.add(i + 1)
            writer.writerow([buyer_id, total_amount, status])
        print(f'{num_orders} generated')

def gen_order_items(num_order_items):
    with open('generated/order_items.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['order_id', 'seller_id', 'product_id', 'quantity', 'unit_price', 'status'])
        print('Order Items...', end=' ', flush=True)
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
        for i in range(num_order_items):
            if i % 50 == 0:
                print(f'{i}', end=' ', flush=True)
            order_id = random.choice(list(valid_orders))
            if valid_inventory:
                seller_id, product_id, unit_price = random.choice(valid_inventory)
                quantity = random.randint(1, 10)
                status = random.choice(statuses)
                writer.writerow([order_id, seller_id, product_id, quantity, unit_price, status])
        print(f'{num_order_items} generated')

def gen_product_reviews(num_product_reviews):
    with open('generated/product_reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['product_id', 'user_id', 'rating', 'review_text'])
        print('Product Reviews...', end=' ', flush=True)
        for i in range(num_product_reviews):
            if i % 40 == 0:
                print(f'{i}', end=' ', flush=True)
            product_id = random.choice(list(valid_products))
            user_id = random.randint(1, num_users)
            rating = random.randint(1, 5)
            review_text = fake.text(max_nb_chars=200)
            writer.writerow([product_id, user_id, rating, review_text])
        print(f'{num_product_reviews} generated')

def gen_seller_reviews(num_seller_reviews):
    with open('generated/seller_reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['seller_id', 'user_id', 'rating', 'review_text'])
        print('Seller Reviews...', end=' ', flush=True)
        for i in range(num_seller_reviews):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            seller_id = random.choice(list(valid_sellers))
            user_id = random.randint(1, num_users)
            while user_id == seller_id:  # Prevent self-reviews
                user_id = random.randint(1, num_users)
            rating = random.randint(1, 5)
            review_text = fake.text(max_nb_chars=200)
            writer.writerow([seller_id, user_id, rating, review_text])
        print(f'{num_seller_reviews} generated')

def gen_message_threads(num_message_threads):
    with open('generated/message_threads.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['buyer_id', 'seller_id', 'order_id'])
        print('Message Threads...', end=' ', flush=True)
        for i in range(num_message_threads):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            order_id = random.choice(list(valid_orders))
            seller_id = random.choice(list(valid_sellers))
            buyer_id = random.randint(1, num_users)
            while buyer_id == seller_id:  # Ensure buyer and seller are different
                buyer_id = random.randint(1, num_users)
            valid_threads.add(i + 1)
            writer.writerow([buyer_id, seller_id, order_id])
        print(f'{num_message_threads} generated')

def gen_messages(num_messages):
    with open('generated/messages.csv', 'w') as f:
        writer = get_csv_writer(f)
        writer.writerow(['thread_id', 'sender_id', 'message_text'])
        print('Messages...', end=' ', flush=True)
        for i in range(num_messages):
            if i % 40 == 0:
                print(f'{i}', end=' ', flush=True)
            thread_id = random.choice(list(valid_threads))
            sender_id = random.randint(1, num_users)
            message_text = fake.text(max_nb_chars=200)
            writer.writerow([thread_id, sender_id, message_text])
        print(f'{num_messages} generated')

# Generate all data
gen_users(num_users)
gen_product_categories(num_categories)
gen_products(num_products)
gen_seller_inventory(num_seller_inventory)
gen_carts(num_carts)
gen_cart_items(num_cart_items)
gen_orders(num_orders)
gen_order_items(num_order_items)
gen_product_reviews(num_product_reviews)
gen_seller_reviews(num_seller_reviews)
gen_message_threads(num_message_threads)
gen_messages(num_messages)
from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 100
num_categories = 10
num_products = 200
num_seller_inventory = 300
num_carts = 50
num_cart_items = 100
num_orders = 150
num_order_items = 300
num_product_reviews = 200
num_seller_reviews = 100
num_message_threads = 80
num_messages = 200

Faker.seed(0)
fake = Faker()

def get_csv_writer(f):
    return csv.writer(f, dialect='unix')

def gen_users(num_users):
    with open('users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            full_name = fake.name()
            address = fake.address()
            balance = f'{str(fake.random_int(max=1000))}.{fake.random_int(max=99):02}'
            is_seller = fake.random_element(elements=('true', 'false'))
            writer.writerow([email, full_name, address, password, balance, is_seller])
        print(f'{num_users} generated')

def gen_product_categories(num_categories):
    with open('product_categories.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product Categories...', end=' ', flush=True)
        categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Sports', 
                     'Toys', 'Food', 'Beauty', 'Auto', 'Garden']
        for i in range(num_categories):
            if i % 2 == 0:
                print(f'{i}', end=' ', flush=True)
            category_name = categories[i]
            description = fake.text(max_nb_chars=200)
            writer.writerow([category_name, description])
        print(f'{num_categories} generated')

def gen_products(num_products):
    with open('products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 50 == 0:
                print(f'{pid}', end=' ', flush=True)
            category_id = fake.random_int(min=1, max=num_categories)
            name = fake.catch_phrase()
            description = fake.text(max_nb_chars=200)
            image_url = f'http://example.com/images/product{pid}.jpg'
            created_by = fake.random_int(min=1, max=num_users)
            writer.writerow([category_id, name, description, image_url, created_by])
        print(f'{num_products} generated')

def gen_seller_inventory(num_seller_inventory):
    with open('seller_inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Inventory...', end=' ', flush=True)
        for i in range(num_seller_inventory):
            if i % 50 == 0:
                print(f'{i}', end=' ', flush=True)
            seller_id = fake.random_int(min=1, max=num_users)
            product_id = fake.random_int(min=1, max=num_products)
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            quantity = fake.random_int(min=1, max=100)
            writer.writerow([seller_id, product_id, price, quantity])
        print(f'{num_seller_inventory} generated')

def gen_carts(num_carts):
    with open('carts.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Carts...', end=' ', flush=True)
        for i in range(num_carts):
            if i % 10 == 0:
                print(f'{i}', end=' ', flush=True)
            user_id = fake.random_int(min=1, max=num_users)
            writer.writerow([user_id])
        print(f'{num_carts} generated')

def gen_cart_items(num_cart_items):
    with open('cart_items.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Cart Items...', end=' ', flush=True)
        for i in range(num_cart_items):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            cart_id = fake.random_int(min=1, max=num_carts)
            seller_id = fake.random_int(min=1, max=num_users)
            product_id = fake.random_int(min=1, max=num_products)
            quantity = fake.random_int(min=1, max=10)
            unit_price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            writer.writerow([cart_id, seller_id, product_id, quantity, unit_price])
        print(f'{num_cart_items} generated')

def gen_orders(num_orders):
    with open('orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
        for i in range(num_orders):
            if i % 30 == 0:
                print(f'{i}', end=' ', flush=True)
            buyer_id = fake.random_int(min=1, max=num_users)
            total_amount = f'{str(fake.random_int(max=2000))}.{fake.random_int(max=99):02}'
            status = fake.random_element(elements=statuses)
            writer.writerow([buyer_id, total_amount, status])
        print(f'{num_orders} generated')

def gen_order_items(num_order_items):
    with open('order_items.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Order Items...', end=' ', flush=True)
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered']
        for i in range(num_order_items):
            if i % 50 == 0:
                print(f'{i}', end=' ', flush=True)
            order_id = fake.random_int(min=1, max=num_orders)
            seller_id = fake.random_int(min=1, max=num_users)
            product_id = fake.random_int(min=1, max=num_products)
            quantity = fake.random_int(min=1, max=10)
            unit_price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            status = fake.random_element(elements=statuses)
            writer.writerow([order_id, seller_id, product_id, quantity, unit_price, status])
        print(f'{num_order_items} generated')

def gen_product_reviews(num_product_reviews):
    with open('product_reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Product Reviews...', end=' ', flush=True)
        for i in range(num_product_reviews):
            if i % 40 == 0:
                print(f'{i}', end=' ', flush=True)
            product_id = fake.random_int(min=1, max=num_products)
            user_id = fake.random_int(min=1, max=num_users)
            rating = fake.random_int(min=1, max=5)
            review_text = fake.text(max_nb_chars=200)
            writer.writerow([product_id, user_id, rating, review_text])
        print(f'{num_product_reviews} generated')

def gen_seller_reviews(num_seller_reviews):
    with open('seller_reviews.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Seller Reviews...', end=' ', flush=True)
        for i in range(num_seller_reviews):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            seller_id = fake.random_int(min=1, max=num_users)
            user_id = fake.random_int(min=1, max=num_users)
            rating = fake.random_int(min=1, max=5)
            review_text = fake.text(max_nb_chars=200)
            writer.writerow([seller_id, user_id, rating, review_text])
        print(f'{num_seller_reviews} generated')

def gen_message_threads(num_message_threads):
    with open('message_threads.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Message Threads...', end=' ', flush=True)
        for i in range(num_message_threads):
            if i % 20 == 0:
                print(f'{i}', end=' ', flush=True)
            buyer_id = fake.random_int(min=1, max=num_users)
            seller_id = fake.random_int(min=1, max=num_users)
            order_id = fake.random_int(min=1, max=num_orders)
            writer.writerow([buyer_id, seller_id, order_id])
        print(f'{num_message_threads} generated')

def gen_messages(num_messages):
    with open('messages.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Messages...', end=' ', flush=True)
        for i in range(num_messages):
            if i % 40 == 0:
                print(f'{i}', end=' ', flush=True)
            thread_id = fake.random_int(min=1, max=num_message_threads)
            sender_id = fake.random_int(min=1, max=num_users)
            message_text = fake.text(max_nb_chars=200)
            writer.writerow([thread_id, sender_id, message_text])
        print(f'{num_messages} generated')

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
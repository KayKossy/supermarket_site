from flask import Flask, render_template, request, redirect, url_for, session
import urllib.request
import json
import random
import string
import sqlite3
from datetime import datetime


app = Flask(__name__)

app.secret_key = 'supermarket_secret_key_123'


# ==================================================
# PAYSTACK TEST KEYS
# ==================================================

# Replace these with your real Paystack TEST keys later.

PAYSTACK_SECRET_KEY = "12345"
PAYSTACK_PUBLIC_KEY = "12345"


# ==================================================
# SQLITE DATABASE
# ==================================================

DATABASE = "inventory.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==================================================
# CREATE INVENTORY DATABASE
# ==================================================

def initialize_database():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (

            product_id INTEGER PRIMARY KEY,

            stock INTEGER NOT NULL DEFAULT 20

        )
    """)

    connection.commit()

    connection.close()


# ==================================================
# PRODUCT DATABASE
# ==================================================

PRODUCTS = {

    1: {
        "name": "Fresh Bananas (Bunch)",
        "price": 2000.99,
        "category": "Produce",
        "image": "banana.png"
    },

    2: {
        "name": "Whole Milk (1L)",
        "price": 1500.99,
        "category": "Dairy",
        "image": "milk.png"
    },

    3: {
        "name": "Sliced Bread",
        "price": 3000.99,
        "category": "Bakery",
        "image": "bread.png"
    },

    4: {
        "name": "Crunchy Peanut Butter",
        "price": 4210.99,
        "category": "Pantry",
        "image": "peanut.png"
    },

    5: {
        "name": "Organic Eggs (Dozen)",
        "price": 3200.10,
        "category": "Dairy",
        "image": "eggs.png"
    },

    6: {
        "name": "Dark Chocolate Bar",
        "price": 2000.00,
        "category": "Pantry",
        "image": "chocolate.png"
    },

    7: {
        "name": "Apples (pack of 4)",
        "price": 2200.00,
        "category": "Produce",
        "image": "apples.png"
    },

    8: {
        "name": "Oranges (pack of 6)",
        "price": 1000.00,
        "category": "Produce",
        "image": "oranges.png"
    },

    9: {
        "name": "Watermelon",
        "price": 1500.00,
        "category": "Produce",
        "image": "watermelon.png"
    },

    10: {
        "name": "Tomatoes (per kg)",
        "price": 1250.00,
        "category": "Produce",
        "image": "tomatoes.png"
    },

    11: {
        "name": "Potatoes (per kg)",
        "price": 3700.00,
        "category": "Produce",
        "image": "potatoes.png"
    },

    12: {
        "name": "Onions",
        "price": 1000.00,
        "category": "Produce",
        "image": "onions.png"
    },

    13: {
        "name": "Carrots",
        "price": 1500.00,
        "category": "Produce",
        "image": "carrots.png"
    },

    14: {
        "name": "Pepper",
        "price": 800.00,
        "category": "Produce",
        "image": "pepper.png"
    },

    15: {
        "name": "Cabbage",
        "price": 1200.00,
        "category": "Produce",
        "image": "cabbage.png"
    },

    16: {
        "name": "Grapes",
        "price": 1500.00,
        "category": "Produce",
        "image": "grapes.png"
    },

    17: {
        "name": "Powdered Milk",
        "price": 1500.00,
        "category": "Dairy & Eggs",
        "image": "powdered-milk.png"
    },

    18: {
        "name": "Yoghurt",
        "price": 1200.00,
        "category": "Dairy & Eggs",
        "image": "yoghurt.png"
    },

    19: {
        "name": "Cheese",
        "price": 2500.00,
        "category": "Dairy & Eggs",
        "image": "cheese.png"
    },

    20: {
        "name": "Butter",
        "price": 1800.00,
        "category": "Dairy & Eggs",
        "image": "butter.png"
    },

    21: {
        "name": "Cake",
        "price": 4500.00,
        "category": "Bakery",
        "image": "cake.png"
    },

    22: {
        "name": "Doughnuts",
        "price": 2500.00,
        "category": "Bakery",
        "image": "doughnuts.png"
    },

    23: {
        "name": "Biscuits",
        "price": 1800.00,
        "category": "Bakery",
        "image": "biscuits.png"
    },

    24: {
        "name": "Meat Pie",
        "price": 1500.00,
        "category": "Bakery",
        "image": "meatpie.png"
    },

    25: {
        "name": "White Rice",
        "price": 4500.00,
        "category": "Pantry",
        "image": "rice.png"
    },

    26: {
        "name": "Spaghetti",
        "price": 1800.00,
        "category": "Pantry",
        "image": "spagetti.png"
    },

    27: {
        "name": "Cooking Oil",
        "price": 6500.00,
        "category": "Pantry",
        "image": "oil.png"
    },

    28: {
        "name": "Tomato Paste",
        "price": 1200.00,
        "category": "Pantry",
        "image": "paste.png"
    },

    29: {
        "name": "Sugar",
        "price": 2000.00,
        "category": "Pantry",
        "image": "sugar.png"
    },

    30: {
        "name": "Salt",
        "price": 800.00,
        "category": "Pantry",
        "image": "salt.png"
    }
}


# ==================================================
# ADD PRODUCTS TO INVENTORY DATABASE
# ==================================================

def populate_inventory():

    connection = get_db_connection()

    cursor = connection.cursor()

    for product_id in PRODUCTS:

        cursor.execute(
            """
            INSERT OR IGNORE INTO inventory
            (product_id, stock)
            VALUES (?, ?)
            """,
            (product_id, 20)
        )

    connection.commit()

    connection.close()


# ==================================================
# GET STOCK FOR ONE PRODUCT
# ==================================================

def get_stock(product_id):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT stock
        FROM inventory
        WHERE product_id = ?
        """,
        (product_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:

        return 0

    return row["stock"]


# ==================================================
# GET ALL PRODUCTS WITH CURRENT STOCK
# ==================================================

def get_products_with_stock():

    products = {}

    for product_id, product in PRODUCTS.items():

        products[product_id] = product.copy()

        products[product_id]["stock"] = get_stock(
            product_id
        )

    return products


# ==================================================
# UPDATE STOCK
# ==================================================

def update_stock(product_id, new_stock):

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE inventory

        SET stock = ?

        WHERE product_id = ?
        """,
        (new_stock, product_id)
    )

    connection.commit()

    connection.close()


# ==================================================
# REDUCE STOCK
# ==================================================

def reduce_stock():

    cart = get_cart()

    connection = get_db_connection()

    cursor = connection.cursor()

    try:

        for product_id, quantity in cart.items():

            product_id = int(product_id)

            cursor.execute(
                """
                UPDATE inventory

                SET stock = stock - ?

                WHERE product_id = ?

                AND stock >= ?
                """,
                (
                    quantity,
                    product_id,
                    quantity
                )
            )

            if cursor.rowcount == 0:

                raise ValueError(
                    "Not enough stock."
                )

        connection.commit()

        return True

    except Exception:

        connection.rollback()

        return False

    finally:

        connection.close()


# ==================================================
# GENERATE ORDER ID
# ==================================================

def generate_order_id():

    date_part = datetime.now().strftime(
        "%Y%m%d"
    )

    random_part = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=5
        )
    )

    return f"ADM-{date_part}-{random_part}"


# ==================================================
# CART HELPER
# ==================================================

def get_cart():

    if 'cart' not in session:

        session['cart'] = {}


    # Convert old list-style carts
    # into quantity dictionaries.

    if isinstance(session['cart'], list):

        old_cart = session['cart']

        new_cart = {}

        for product_id in old_cart:

            product_id = str(product_id)

            if product_id in new_cart:

                new_cart[product_id] += 1

            else:

                new_cart[product_id] = 1

        session['cart'] = new_cart

        session.modified = True


    return session['cart']


# ==================================================
# CHECK STOCK
# ==================================================

def cart_has_enough_stock():

    cart = get_cart()

    for product_id, quantity in cart.items():

        product_id = int(product_id)

        if product_id not in PRODUCTS:

            return False

        current_stock = get_stock(
            product_id
        )

        if quantity > current_stock:

            return False

    return True


# ==================================================
# LANDING PAGE
# ==================================================

@app.route("/")
def landing():

    return render_template(
        "landing.html"
    )


# ==================================================
# SHOP
# ==================================================

@app.route("/shop")
def homepage():

    cart = get_cart()

    selected_category = request.args.get(
        'category'
    )

    search_query = request.args.get(
        'search',
        ''
    ).strip().lower()

    products_with_stock = (
        get_products_with_stock()
    )

    filtered_products = products_with_stock


    # CATEGORY FILTER

    if selected_category:

        filtered_products = {

            product_id: product

            for product_id, product
            in products_with_stock.items()

            if product['category']
            == selected_category

        }


    # SEARCH FILTER

    if search_query:

        filtered_products = {

            product_id: product

            for product_id, product
            in filtered_products.items()

            if search_query
            in product['name'].lower()

            or search_query
            in product['category'].lower()

        }


    # BUILD CART ITEMS

    cart_items = []

    for product_id, quantity in cart.items():

        product_id = int(product_id)

        if product_id in products_with_stock:

            product = products_with_stock[
                product_id
            ]

            cart_items.append({

                "id": product_id,

                "name": product["name"],

                "price": product["price"],

                "category": product["category"],

                "image": product["image"],

                "quantity": quantity,

                "stock": product["stock"],

                "subtotal":
                    product["price"]
                    * quantity

            })


    cart_count = sum(
        cart.values()
    )

    total_cost = sum(

        item["subtotal"]

        for item in cart_items

    )


    return render_template(

        'index.html',

        products=filtered_products,

        cart_items=cart_items,

        cart_count=cart_count,

        total_cost=total_cost,

        cart=cart

    )


# ==================================================
# ADD TO CART
# ==================================================

@app.route(
    '/add_to_cart/<int:product_id>',
    methods=['POST']
)
def add_to_cart(product_id):

    cart = get_cart()

    if product_id not in PRODUCTS:

        return redirect(
            url_for('homepage')
        )


    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0
    )

    available_stock = get_stock(
        int(product_id)
    )


    # Do not allow adding an item
    # when stock is zero.

    if available_stock <= 0:

        return redirect(
            url_for('homepage')
        )


    # Do not allow more than
    # available stock.

    if current_quantity < available_stock:

        cart[product_id] = (
            current_quantity + 1
        )


    session['cart'] = cart

    session.modified = True

    return redirect(
        url_for('homepage')
    )


# ==================================================
# INCREASE QUANTITY
# ==================================================

@app.route(
    '/increase_quantity/<int:product_id>',
    methods=['POST']
)
def increase_quantity(product_id):

    cart = get_cart()

    if product_id not in PRODUCTS:

        return redirect(
            url_for('homepage')
        )


    product_id = str(product_id)

    current_quantity = cart.get(
        product_id,
        0
    )

    available_stock = get_stock(
        int(product_id)
    )


    if current_quantity < available_stock:

        cart[product_id] = (
            current_quantity + 1
        )


    session['cart'] = cart

    session.modified = True

    return redirect(
        url_for('homepage')
    )


# ==================================================
# DECREASE QUANTITY
# ==================================================

@app.route(
    '/decrease_quantity/<int:product_id>',
    methods=['POST']
)
def decrease_quantity(product_id):

    cart = get_cart()

    product_id = str(product_id)

    if product_id in cart:

        cart[product_id] -= 1

        if cart[product_id] <= 0:

            del cart[product_id]


    session['cart'] = cart

    session.modified = True

    return redirect(
        url_for('homepage')
    )


# ==================================================
# CLEAR CART
# ==================================================

@app.route('/clear_cart')
def clear_cart():

    session['cart'] = {}

    session.modified = True

    return redirect(
        url_for('homepage')
    )


# ==================================================
# BUILD CART ITEMS
# ==================================================

def build_cart_items():

    cart = get_cart()

    products_with_stock = (
        get_products_with_stock()
    )

    cart_items = []

    for product_id, quantity in cart.items():

        product_id = int(product_id)

        if product_id in products_with_stock:

            product = products_with_stock[
                product_id
            ]

            cart_items.append({

                "id": product_id,

                "name": product["name"],

                "price": product["price"],

                "category": product["category"],

                "image": product["image"],

                "quantity": quantity,

                "stock": product["stock"],

                "subtotal":
                    product["price"]
                    * quantity

            })

    return cart_items


# ==================================================
# CHECKOUT
# ==================================================

@app.route('/checkout')
def checkout():

    cart = get_cart()

    if not cart:

        return redirect(
            url_for('homepage')
        )


    if not cart_has_enough_stock():

        return redirect(
            url_for('homepage')
        )


    cart_items = build_cart_items()

    total_cost = sum(

        item["subtotal"]

        for item in cart_items

    )


    return render_template(

        'checkout.html',

        cart_items=cart_items,

        total_cost=total_cost,

        paystack_public_key=
            PAYSTACK_PUBLIC_KEY

    )


# ==================================================
# CASH ON DELIVERY
# ==================================================

@app.route(
    '/place_order',
    methods=['POST']
)
def place_order():

    cart = get_cart()

    if not cart:

        return redirect(
            url_for('homepage')
        )


    # Check stock before accepting
    # the order.

    if not cart_has_enough_stock():

        return redirect(
            url_for('homepage')
        )


    cart_items = build_cart_items()

    total_cost = sum(

        item["subtotal"]

        for item in cart_items

    )


    customer_name = request.form.get(
        'customer_name'
    )

    phone = request.form.get(
        'phone'
    )

    email = request.form.get(
        'email'
    )

    address = request.form.get(
        'address'
    )


    payment_method = "Cash on Delivery"

    order_id = generate_order_id()


    # Reduce stock in SQLite.

    if not reduce_stock():

        return redirect(
            url_for('homepage')
        )


    # Clear cart.

    session['cart'] = {}

    session.modified = True


    return render_template(

        'order_success.html',

        order_id=order_id,

        customer_name=customer_name,

        phone=phone,

        email=email,

        address=address,

        payment_method=payment_method,

        cart_items=cart_items,

        total_cost=total_cost

    )


# ==================================================
# PAYSTACK PAYMENT INITIALIZATION
# ==================================================

@app.route(
    '/initialize_payment',
    methods=['POST']
)
def initialize_payment():

    cart = get_cart()

    if not cart:

        return redirect(
            url_for('homepage')
        )


    if not cart_has_enough_stock():

        return redirect(
            url_for('homepage')
        )


    cart_items = build_cart_items()

    total_cost = sum(

        item["subtotal"]

        for item in cart_items

    )


    customer_name = request.form.get(
        'customer_name'
    )

    phone = request.form.get(
        'phone'
    )

    email = request.form.get(
        'email'
    )

    address = request.form.get(
        'address'
    )


    # Save customer information temporarily.

    session['customer_name'] = (
        customer_name
    )

    session['phone'] = phone

    session['email'] = email

    session['address'] = address


    # Generate Order ID.

    order_id = generate_order_id()

    session['order_id'] = order_id


    # Paystack uses kobo.

    amount = int(
        round(total_cost * 100)
    )


    data = {

        "email": email,

        "amount": amount,

        "callback_url": url_for(
            'payment_callback',
            _external=True
        )

    }


    encoded_data = json.dumps(
        data
    ).encode("utf-8")


    req = urllib.request.Request(

        "https://api.paystack.co/"
        "transaction/initialize",

        data=encoded_data,

        headers={

            "Authorization":
                f"Bearer {PAYSTACK_SECRET_KEY}",

            "Content-Type":
                "application/json"

        },

        method="POST"

    )


    try:

        with urllib.request.urlopen(
            req
        ) as response:

            result = json.loads(

                response.read()
                .decode("utf-8")

            )


        if result.get("status"):

            authorization_url = (
                result["data"]
                ["authorization_url"]
            )

            return redirect(
                authorization_url
            )


        return (
            "Payment initialization failed."
        )


    except Exception as error:

        print(
            "PAYSTACK ERROR:",
            error
        )

        return (
            "Unable to connect to Paystack. "
            "Check your test keys."
        )


# ==================================================
# PAYSTACK CALLBACK
# ==================================================

@app.route('/payment_callback')
def payment_callback():

    reference = request.args.get(
        'reference'
    )

    if not reference:

        return (
            "Payment reference was not provided."
        )


    # Verify payment with Paystack.

    req = urllib.request.Request(

        f"https://api.paystack.co/"
        f"transaction/verify/{reference}",

        headers={

            "Authorization":
                f"Bearer {PAYSTACK_SECRET_KEY}"

        },

        method="GET"

    )


    try:

        with urllib.request.urlopen(
            req
        ) as response:

            result = json.loads(

                response.read()
                .decode("utf-8")

            )


        if (

            result.get("status")

            and

            result.get(
                "data",
                {}
            ).get("status")
            == "success"

        ):

            cart = get_cart()


            if not cart:

                return (
                    "This order has already "
                    "been processed."
                )


            if not cart_has_enough_stock():

                return (
                    "Payment was successful, "
                    "but the requested items "
                    "are no longer available."
                )


            cart_items = build_cart_items()

            total_cost = sum(

                item["subtotal"]

                for item in cart_items

            )


            customer_name = session.get(
                'customer_name'
            )

            phone = session.get(
                'phone'
            )

            email = session.get(
                'email'
            )

            address = session.get(
                'address'
            )


            payment_method = "Paystack"


            order_id = session.get(
                'order_id'
            )


            if not order_id:

                order_id = generate_order_id()


            # Reduce stock in SQLite.

            if not reduce_stock():

                return (
                    "Payment was successful, "
                    "but there was a stock "
                    "processing problem. "
                    "Please contact the store."
                )


            # Clear cart.

            session['cart'] = {}

            session.modified = True


            return render_template(

                'order_success.html',

                order_id=order_id,

                customer_name=customer_name,

                phone=phone,

                email=email,

                address=address,

                payment_method=payment_method,

                cart_items=cart_items,

                total_cost=total_cost,

                reference=reference

            )


        return (
            "Payment was not successful."
        )


    except Exception as error:

        print(
            "PAYMENT VERIFICATION ERROR:",
            error
        )

        return (
            "Unable to verify payment."
        )


# ==================================================
# INVENTORY PAGE
# ==================================================

@app.route('/inventory')
@app.route('/admin/inventory')
def inventory():

    products = (
        get_products_with_stock()
    )

    return render_template(

        'inventory.html',

        products=products

    )


# ==================================================
# UPDATE INVENTORY
# ==================================================

@app.route(
    '/admin/update_stock/<int:product_id>',
    methods=['POST']
)
def admin_update_stock(product_id):

    if product_id not in PRODUCTS:

        return redirect(
            url_for('inventory')
        )


    stock_value = request.form.get(
        'stock'
    )


    try:

        new_stock = int(stock_value)


        if new_stock < 0:

            new_stock = 0


    except (
        ValueError,
        TypeError
    ):

        return redirect(
            url_for('inventory')
        )


    update_stock(
        product_id,
        new_stock
    )


    return redirect(
        url_for('inventory')
    )


# ==================================================
# START FLASK
# ==================================================

initialize_database()

populate_inventory()


if __name__ == '__main__':

    app.run(

        debug=True,

        host='0.0.0.0',

        port=8000

    )
    
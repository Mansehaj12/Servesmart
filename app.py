from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"

# -------------------- DB Connection --------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@waheguru65#",
        database="servesmart"
    )

# -------------------- HOME --------------------
@app.route('/')
def home():
    username = session.get('username')
    return render_template('index.html', username=username)

# -------------------- LOGIN --------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = user['username']
            session['user_id'] = user['user_id']
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password.'

    return render_template('login.html', error=error)

# -------------------- SIGNUP --------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Username already exists!'
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()

            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            new_user = cursor.fetchone()
            session['username'] = new_user['username']
            session['user_id'] = new_user['user_id']
            flash('Account created successfully.', 'success')

        cursor.close()
        conn.close()
        if not error:
            return redirect(url_for('home'))

    return render_template('signup.html', error=error)

# -------------------- DASHBOARD --------------------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

# -------------------- LOGOUT --------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# -------------------- MENU --------------------
@app.route('/menu')
def menu():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, price, category, image_url FROM menu")
    menu_items = cursor.fetchall()
    cursor.close()
    conn.close()

    cart = session.get("cart", [])
    cart_count = len(cart)

    return render_template("menu.html", menu_items=menu_items, cart_count=cart_count)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        category = request.form['category']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (name, description, price, image_url, category) VALUES (%s, %s, %s, %s, %s)",
                       (name, description, price, image_url, category))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('menu'))

    return render_template('add_item.html')

# -------------------- CART --------------------
@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(float(item['price']) for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, price, image_url FROM menu WHERE id = %s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()

    if item:
        cart_item = {
            'id': item['id'],
            'name': item['name'],
            'price': float(item['price']),
            'image_url': item['image_url']
        }
        cart = session.get('cart', [])
        cart.append(cart_item)
        session['cart'] = cart
        session.modified = True

    return redirect(url_for('menu'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
        session.modified = True
    return redirect(url_for('cart'))

# -------------------- BILL & HISTORY --------------------
@app.route("/bill")
def bill():
    cart_items = session.get('cart', [])
    total = sum(float(item['price']) for item in cart_items)
    return render_template("bill.html", cart_items=cart_items, total=total)

@app.route("/orders")
def orders():
    # Dummy data for now — in future this should come from DB
    sample_orders = [
        {"item": "Veggie Burger", "quantity": 2, "total_price": 300},
        {"item": "Cold Coffee", "quantity": 1, "total_price": 120}
    ]
    return render_template('orders.html', orders=sample_orders)

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/admin")
def admin():
    return render_template("admin_dashboard.html")

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(debug=True)

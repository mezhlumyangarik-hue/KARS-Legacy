from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# ==========================================
# 🔒 ՀԱՍՏԱՏՈՒՆ ՊԱՀՊԱՆՄԱՆ ԿԱՐԳԱՎՈՐՈՒՄ (PERSISTENT STORAGE)
# ==========================================
# Եթե աշխատում է Render-ի վրա, օգտագործում է /var/data, հակառակ դեպքում՝ պրոյեկտի հիմնական պապկան
if os.environ.get('RENDER'):
    PERSISTENT_STORAGE = '/var/data'
else:
    PERSISTENT_STORAGE = os.path.dirname(os.path.abspath(__file__))

# Բազայի և նկարների ճիշտ ճանապարհները
DB_NAME = os.path.join(PERSISTENT_STORAGE, 'doors_database.db')
UPLOAD_FOLDER = os.path.join(PERSISTENT_STORAGE, 'static', 'uploads')

DB_NAME = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'doors_database.db')
#os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 🛠️ ԲԱԶԱՅԻ ՍՏԵՂԾՈՒՄ
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Ապրանքներ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            metal TEXT,
            wood TEXT,
            filler TEXT,
            category TEXT,
            is_new INTEGER,
            desc TEXT,
            main_image TEXT,
            gallery_images TEXT
        )
    ''')
    
    # 2. Զամբյուղի Պատվերներ (Քարտով գնումներ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone_number TEXT,
            products TEXT,
            total_amount REAL,
            mode TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Չափագրումներ (Անհատական պատվերներ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone_number TEXT,
            address TEXT,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def get_all_products_from_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, price, metal, wood, filler, category, is_new, desc, main_image, gallery_images FROM products ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        products = []
        for r in rows:
            products.append({
                'id': r[0], 
                'title': r[1], 
                'price': r[2], 
                'metal': r[3], 
                'wood': r[4], 
                'filler': r[5],
                'category': r[6], 
                'is_new': bool(r[7]), 
                'desc': r[8], 
                'main_image': r[9] if r[9] else '',
                'gallery_images': r[10].split(',') if r[10] else []
            })
        return products
    except Exception as e:
        print(f"Բազայից կարդալու սխալ: {e}")
        return []

@app.context_processor
def inject_cart_count():
    cart = session.get('cart', {})
    total_count = 0
    if isinstance(cart, dict):
        for item in cart.values():
            if isinstance(item, dict):
                total_count += item.get('quantity', 0)
    
    site_mode = session.get('site_mode', 'Test Mode')
    return dict(cart_count=total_count, site_mode=site_mode)

# ==========================================
# 🌟 ՆԿԱՐՆԵՐԻ ՎԵՐԲԵՌՆՄԱՆ ԵՐԹՈՒՂԻ (UPLOAD ROUTE)
# ==========================================
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Ֆայլը չի գտնվել'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Ֆայլ ընտրված չէ'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Քանի որ նկարները պահվում են արտաքին /var/data պապկայում, 
        # Render-ում դրանք կարդալու համար վերադարձնում ենք /static/uploads/filename URL-ը
        return jsonify({'location': f'/static/uploads/{filename}'})

# ==========================================
# ԷՋԵՐԻ ԵՐԹՈՒՂԻՆԵՐ (ROUTES)
# ==========================================

@app.route('/')
def home():
    all_doors = get_all_products_from_db()
    new_doors = [door for door in all_doors if door['is_new']]
    return render_template('index.html', products=new_doors)

@app.route('/shop')
def shop_page():
    selected_category = request.args.get('category')
    all_doors = get_all_products_from_db()
    
    if selected_category:
        products = [door for door in all_doors if door['category'] == selected_category]
    else:
        products = all_doors
        
    return render_template('shop.html', products=products, selected_category=selected_category)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        return redirect(url_for('shop_page'))
        
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, price, metal, wood, filler, category, is_new, desc, main_image, gallery_images FROM products WHERE title LIKE ? OR desc LIKE ? ORDER BY id DESC", (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for r in rows:
            products.append({
                'id': r[0], 'title': r[1], 'price': r[2], 'metal': r[3], 'wood': r[4], 'filler': r[5],
                'category': r[6], 'is_new': bool(r[7]), 'desc': r[8], 'main_image': r[9] if r[9] else '',
                'gallery_images': r[10].split(',') if r[10] else []
            })
    except Exception as e:
        print(f"Որոնման սխալ: {e}")
        products = []
        
    return render_template('shop.html', products=products, search_query=query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    all_doors = get_all_products_from_db()
    product = next((item for item in all_doors if item['id'] == product_id), None)
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product)

@app.route('/cart')
def cart_page():
    cart = session.get('cart', {})
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart_items=cart.values(), total_price=total_price)

@app.route('/checkout')
def checkout_page():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('shop_page'))
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('checkout.html', total_price=total_price)

@app.route('/orders')
def orders_page():
    return render_template('orders.html')

# ==========================================
# ԶԱՄԲՅՈՒՂԻ ՖՈՒՆԿՑԻԱՆԵՐ
# ==========================================

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    all_doors = get_all_products_from_db()
    product = next((item for item in all_doors if item['id'] == product_id), None)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']
    prod_id_str = str(product_id)
    if prod_id_str in cart:
        cart[prod_id_str]['quantity'] += 1
    else:
        cart[prod_id_str] = {
            'id': product['id'], 
            'title': product['title'], 
            'price': product['price'],
            'main_image': product['main_image'], 
            'quantity': 1
        }
    session.modified = True
    return redirect(request.referrer or url_for('shop_page'))

@app.route('/update-cart-quantity/<string:product_id>/<string:action>', methods=['POST'])
def update_cart_quantity(product_id, action):
    cart = session.get('cart', {})
    if product_id in cart:
        if action in ['plus', 'increase']:
            cart[product_id]['quantity'] += 1
        elif action in ['minus', 'decrease']:
            cart[product_id]['quantity'] -= 1
            if cart[product_id]['quantity'] <= 0:
                cart.pop(product_id)
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart_page'))

@app.route('/remove-from-cart/<string:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        cart.pop(product_id)
        session['cart'] = cart
        session.modified = True
    return redirect(url_for('cart_page'))

@app.route('/clear-cart', methods=['POST', 'GET'])
def clear_cart():
    session.pop('cart', None)
    session.modified = True
    return redirect(url_for('cart_page'))

# ==========================================
# ՀԱՅՏԵՐԻ ԳՐԱՆՑՈՒՄ
# ==========================================

@app.route('/submit-order', methods=['POST'])
def submit_order():
    name = request.form.get('name') or 'Անոնիմ'
    phone = request.form.get('phone') or 'Նշված չէ'
    city = request.form.get('city', 'Գորիս')
    door_type = request.form.get('door_type', 'Նշված չէ')
    size = request.form.get('size', 'Չափսը նշված չէ')
    notes = request.form.get('notes', '')
    
    full_address = f"📍 Բնակավայր՝ {city} | 🚪 Տեսակ՝ {door_type} | 📐 Չափս՝ {size} | 📝 Նշումներ՝ {notes}"
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO measurements (customer_name, phone_number, address) VALUES (?, ?, ?)', (name, phone, full_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Չափագրման բազայի սխալ. {e}")
        
    return render_template('success.html', title="📩 Հայտն Ընդունված Է", text="Ձեր չափագրման հայտը հաջողությամբ գրանցվել է։")

@app.route('/submit-cart-checkout', methods=['POST'])
def submit_cart_checkout():
    name = request.form.get('name') or request.form.get('customer_name') or 'Անոնիմ'
    phone = request.form.get('phone') or request.form.get('phone_number') or 'Նշված չէ'
    city = request.form.get('city', 'Գորիս')
    notes = request.form.get('notes', '')

    cart = session.get('cart', {})
    cart_summary = []
    total_price = 0
    
    for item in cart.values():
        try:
            price = int(str(item['price']).replace(',', '').replace(' ', ''))
            qty = int(item.get('quantity', 1))
            total_price += price * qty
            cart_summary.append(f"{item['title']} ({qty} հատ)")
        except:
            pass

    products_text = ", ".join(cart_summary) if cart_summary else "Դատարկ զամբյուղ"
    full_details = f"📦 Ապրանքներ: {products_text} | 📍 Բնակավայր: {city} | 📝 Նշումներ: {notes}"
    current_mode = session.get('site_mode', 'Test Mode')

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (customer_name, phone_number, products, total_amount, mode) VALUES (?, ?, ?, ?, ?)",
            (name, phone, full_details, total_price, current_mode)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Բազայի սխալ պատվերի ժամանակ. {e}")

    session.pop('cart', None)
    return render_template('success.html', title="📩 Պատվերը Գրանցվեց", text="Շնորհակալություն! Ձեր պատվերը հաջողությամբ ընդունվել է։")

# ==========================================
# ԱԴՄԻՆ ՊԱՆԵԼ
# ==========================================

@app.route('/admin')
def admin_panel():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, customer_name, phone_number, address, date_created FROM measurements ORDER BY id DESC")
    measurements = cursor.fetchall()
    
    cursor.execute("SELECT id, customer_name, phone_number, products, total_amount, mode, date FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()
    conn.close()
    
    products = get_all_products_from_db()
    return render_template('admin.html', measurements=measurements, orders=orders, products=products, doors_count=len(products))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    title = request.form.get('title')
    price = request.form.get('price')
    category = request.form.get('category')
    metal = request.form.get('metal', '')
    wood = request.form.get('wood', '')
    filler = request.form.get('filler', '')
    desc = request.form.get('desc', '')
    main_image = request.form.get('main_image', '')
    gallery_images = request.form.get('gallery_images', '')
    
    is_new = 1
        
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO products (title, price, metal, wood, filler, category, is_new, desc, main_image, gallery_images) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, price, metal, wood, filler, category, is_new, desc, main_image, gallery_images)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ապրանք ավելացնելու սխալ: {e}")
            
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-product/<int:product_id>', methods=['POST', 'GET'])
def delete_product(product_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ապրանք ջնջելու սխալ: {e}")
    return redirect(url_for('admin_panel'))

@app.route('/toggle-mode')
def toggle_mode():
    current = session.get('site_mode', 'Test Mode')
    if current == 'Test Mode':
        session['site_mode'] = 'Live Mode'
    else:
        session['site_mode'] = 'Test Mode'
    session.modified = True
    return redirect(request.referrer or url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

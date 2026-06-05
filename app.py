from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import DictCursor
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# ==========================================
# 📂 ՃԻՇՏ ՃԱՆԱՊԱՐՀՆԵՐ (RENDER-Ի ՀԱՄԱՐ)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ==========================================
# 🔗 ՄԻԱՑՈՒՄ SUPABASE POSTGRESQL ԲԱԶԱՅԻՆ
# ==========================================
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    # Կապվում է Render-ի Environment-ի հղումով Supabase բազային
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# 🛠️ ԲԱԶԱՅԻ ԱՂՅՈՒՍԱԿՆԵՐԻ ՍՏԵՂԾՈՒՄ (PostgreSQL ՍԻՆՏԱՔՍՈՎ)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Ապրանքներ (desc-ի փոխարեն օգտագործում ենք desc_text)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            metal TEXT,
            wood TEXT,
            filler TEXT,
            category TEXT,
            is_new INTEGER,
            desc_text TEXT,
            main_image TEXT,
            gallery_images TEXT
        );
    ''')
    
    # 2. Զամբյուղի Պատվերներ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name TEXT,
            phone_number TEXT,
            products TEXT,
            total_amount REAL,
            mode TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # 3. Չափագրումներ
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id SERIAL PRIMARY KEY,
            customer_name TEXT,
            phone_number TEXT,
            address TEXT,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Ավտոմատ կանչում ենք աղյուսակների ստեղծումը Supabase-ում
init_db()

def get_all_products_from_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("SELECT id, title, price, metal, wood, filler, category, is_new, desc_text, main_image, gallery_images FROM products ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = []
        for r in rows:
            products.append({
                'id': r['id'], 
                'title': r['title'], 
                'price': r['price'], 
                'metal': r['metal'], 
                'wood': r['wood'], 
                'filler': r['filler'],
                'category': r['category'], 
                'is_new': bool(r['is_new']), 
                'desc': r['desc_text'],  # Պահում ենք 'desc' անունը HTML-ների համար
                'main_image': r['main_image'] if r['main_image'] else '',
                'gallery_images': r['gallery_images'].split(',') if r['gallery_images'] else []
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
# 🌟 ՆԿԱՐՆԵՐԻ ՎԵՐԲԵՌՆՄԱՆ ԵՐԹՈՒՂԻ
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
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        # PostgreSQL-ում LIKE-ի փոխարեն ILIKE ենք անում, որ մեծատառ/փոքրատառ կապ չունենա
        cursor.execute("""
            SELECT id, title, price, metal, wood, filler, category, is_new, desc_text, main_image, gallery_images 
            FROM products 
            WHERE title ILIKE %s OR desc_text ILIKE %s 
            ORDER BY id DESC
        """, (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        products = []
        for r in rows:
            products.append({
                'id': r['id'], 'title': r['title'], 'price': r['price'], 'metal': r['metal'], 'wood': r['wood'], 'filler': r['filler'],
                'category': r['category'], 'is_new': bool(r['is_new']), 'desc': r['desc_text'], 'main_image': r['main_image'] if r['main_image'] else '',
                'gallery_images': r['gallery_images'].split(',') if r['gallery_images'] else []
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO measurements (customer_name, phone_number, address) VALUES (%s, %s, %s)', (name, phone, full_address))
        conn.commit()
        cursor.close()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orders (customer_name, phone_number, products, total_amount, mode) VALUES (%s, %s, %s, %s, %s)",
            (name, phone, full_details, total_price, current_mode)
        )
        conn.commit()
        cursor.close()
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, customer_name, phone_number, address, date_created FROM measurements ORDER BY id DESC")
    measurements = cursor.fetchall()
    
    cursor.execute("SELECT id, customer_name, phone_number, products, total_amount, mode, date FROM orders ORDER BY id DESC")
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    
    products = get_all_products_from_db()
    return render_template('admin.html', measurements=measurements, orders=orders, products=products, doors_count=len(products))

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    title = request.form.get('title')
    price = int(request.form.get('price'))
    category = request.form.get('category')
    metal = request.form.get('metal', '')
    wood = request.form.get('wood', '')
    filler = request.form.get('filler', '')
    desc = request.form.get('desc', '')
    main_image = request.form.get('main_image', '')
    gallery_images = request.form.get('gallery_images', '')
    
    is_new = 1
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO products (title, price, metal, wood, filler, category, is_new, desc_text, main_image, gallery_images) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (title, price, metal, wood, filler, category, is_new, desc, main_image, gallery_images)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ապրանք ավելացնելու սխալ: {e}")
            
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete-product/<int:product_id>', methods=['POST', 'GET'])
def delete_product(product_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        cursor.close()
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

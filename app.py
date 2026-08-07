from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import DictCursor
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# ==========================================
# 📂 VERCEL PATHS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('/tmp' if os.environ.get('VERCEL') else BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ==========================================
# 🔗 SUPABASE POSTGRESQL CONNECT
# ==========================================
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# ==========================================
# 💎 ՄՇՏԱԿԱՆ (ԱՆԽԱՓԱՆ) ՄՈՒՏՔԻ ԴՌՆԵՐԻ ՆԿԱՐՆԵՐ
# ==========================================
# Այս SVG նկարները չեն կախված արտաքին սերվերներից և 100% աշխատելու են Vercel-ում
DOOR_1_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 700' width='100%' height='100%'><rect width='400' height='700' fill='%231e242b'/><rect x='20' y='20' width='360' height='660' fill='%232a323d' stroke='%23d4af37' stroke-width='4'/><rect x='40' y='40' width='180' height='620' fill='%23222831'/><line x1='60' y1='60' x2='60' y2='640' stroke='%23393e46' stroke-width='6'/><line x1='90' y1='60' x2='90' y2='640' stroke='%23393e46' stroke-width='6'/><line x1='120' y1='60' x2='120' y2='640' stroke='%23393e46' stroke-width='6'/><line x1='150' y1='60' x2='150' y2='640' stroke='%23393e46' stroke-width='6'/><line x1='180' y1='60' x2='180' y2='640' stroke='%23393e46' stroke-width='6'/><rect x='250' y='60' width='110' height='500' fill='%235c6e82' opacity='0.7'/><rect x='250' y='570' width='110' height='90' fill='%235c6e82' opacity='0.7'/><rect x='48' y='320' width='14' height='120' rx='4' fill='%23d4af37'/><circle cx='55' cy='460' r='6' fill='%23d4af37'/></svg>"

DOOR_2_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 700' width='100%' height='100%'><rect width='400' height='700' fill='%23191919'/><rect x='20' y='20' width='360' height='660' fill='%23222222' stroke='%23444' stroke-width='3'/><rect x='40' y='40' width='320' height='100' fill='%232c2c2c'/><rect x='50' y='50' width='60' height='80' fill='%233a4f63' opacity='0.8'/><rect x='290' y='50' width='60' height='80' fill='%233a4f63' opacity='0.8'/><rect x='50' y='160' width='60' height='500' fill='%233a4f63' opacity='0.8'/><rect x='290' y='160' width='60' height='500' fill='%233a4f63' opacity='0.8'/><rect x='130' y='160' width='140' height='500' fill='%232c2c2c'/><line x1='150' y1='170' x2='150' y2='650' stroke='%23111' stroke-width='5'/><line x1='170' y1='170' x2='170' y2='650' stroke='%23111' stroke-width='5'/><line x1='190' y1='170' x2='190' y2='650' stroke='%23111' stroke-width='5'/><line x1='210' y1='170' x2='210' y2='650' stroke='%23111' stroke-width='5'/><line x1='230' y1='170' x2='230' y2='650' stroke='%23111' stroke-width='5'/><line x1='250' y1='170' x2='250' y2='650' stroke='%23111' stroke-width='5'/><rect x='122' y='320' width='12' height='140' fill='%23cccccc'/></svg>"

DOOR_3_SVG = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 700' width='100%' height='100%'><rect width='400' height='700' fill='%232b2622'/><rect x='20' y='20' width='360' height='660' fill='%2338312b' stroke='%23c5a059' stroke-width='3'/><rect x='40' y='40' width='320' height='620' fill='%232b2622'/><rect x='60' y='60' width='280' height='580' fill='%23423932'/><line x1='80' y1='60' x2='80' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='110' y1='60' x2='110' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='140' y1='60' x2='140' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='170' y1='60' x2='170' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='200' y1='60' x2='200' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='230' y1='60' x2='230' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='260' y1='60' x2='260' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='290' y1='60' x2='290' y2='640' stroke='%232b2622' stroke-width='8'/><line x1='320' y1='60' x2='320' y2='640' stroke='%232b2622' stroke-width='8'/><rect x='48' y='330' width='10' height='100' fill='%23c5a059'/></svg>"

PERMANENT_PRODUCTS = [
    {
        'id': 1001,
        'title': 'KARS Modern Slate Glass Door',
        'price': 280000,
        'metal': '3մմ Բարձրամուր Պողպատ',
        'wood': 'MDF Փայտյա Երեսպատում',
        'filler': 'Բազալտե Ջերմամեկուսիչ Բամբակ',
        'category': 'Արտաքին Մետաղական',
        'is_new': True,
        'desc': 'Մոդեռն դիզայնով արտաքին մուտքի դուռ՝ ապակե ներդիրով, երկար բռնակով և բարձր անվտանգության փականներով։',
        'main_image': DOOR_1_SVG,
        'gallery_images': [DOOR_1_SVG]
    },
    {
        'id': 1002,
        'title': 'KARS Grand Lattice Gate Door',
        'price': 320000,
        'metal': 'Ամրացված Մետաղական Կարկաս 3մմ',
        'wood': 'Պրեմիում MDF Էմալ Պատվածք',
        'filler': 'Ձայնամեկուսիչ Բազալտե Սալ',
        'category': 'Էքսկլյուզիվ Մուտքի Դուռ',
        'is_new': True,
        'desc': 'Շքեղ երկաթյա դուռ՝ երկկողմանի ապակե հատվածներով և դեկորատիվ մետաղական նախշերով։',
        'main_image': DOOR_2_SVG,
        'gallery_images': [DOOR_2_SVG]
    },
    {
        'id': 1003,
        'title': 'KARS Vertical Slat Entrance Door',
        'price': 240000,
        'metal': '2.5մմ Պողպատյա Պրոֆիլ',
        'wood': 'Բնական MDF Vertical Panel',
        'filler': 'Ջերմա-ձայնամեկուսիչ Սալ',
        'category': 'MDF Մուտքի Դուռ',
        'is_new': True,
        'desc': 'Ուղղահայաց գծերով ժամանակակից մուտքի դուռ՝ առանձնատների և բնակարանների համար։',
        'main_image': DOOR_3_SVG,
        'gallery_images': [DOOR_3_SVG]
    }
]

def get_all_products_from_db():
    products = list(PERMANENT_PRODUCTS)
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(cursor_factory=DictCursor)
            cursor.execute("SELECT id, title, price, metal, wood, filler, category, is_new, desc_text, main_image, gallery_images FROM products ORDER BY id DESC")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
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
                    'desc': r['desc_text'],  
                    'main_image': r['main_image'] if r['main_image'] else '',
                    'gallery_images': r['gallery_images'].split(',') if r['gallery_images'] else []
                })
        except Exception as e:
            print(f"DB read error: {e}")
            
    return products

@app.route('/init-database-secure-999')
def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            return "DATABASE_URL missing"
        cursor = conn.cursor()
        
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
        return "Database initialized successfully"
    except Exception as e:
        return f"Database init error: {e}"

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'File not found'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return jsonify({'location': f'/static/uploads/{filename}'})
        except Exception as e:
            return jsonify({'error': f'Save error: {e}'}), 500

@app.route('/')
def home():
    all_doors = get_all_products_from_db()
    new_doors = [door for door in all_doors if door['is_new']]
    display_products = new_doors if new_doors else all_doors
    return render_template('index.html', products=display_products)

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
    query = request.args.get('query', '').strip().lower()
    if not query:
        return redirect(url_for('shop_page'))
        
    all_doors = get_all_products_from_db()
    products = [d for d in all_doors if query in d['title'].lower() or query in d['desc'].lower()]
        
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

@app.route('/submit-order', methods=['POST'])
def submit_order():
    name = request.form.get('name') or 'Անոնիմ'
    phone = request.form.get('phone') or 'Նշված չէ'
    city = request.form.get('city', 'Գորիս')
    door_type = request.form.get('door_type', 'Նշված չէ')
    size = request.form.get('size', 'Չափսը նշված չէ')
    notes = request.form.get('notes', '')
    
    full_address = f"📍 Բնակավայր՝ {city} | 🚪 Տեսակ՝ {door_type} | 📐 Չափս՝ {size} | 📝 Նշումներ՝ {notes}"
    
    conn = get_db_connection()
    if conn:
        try:
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

    conn = get_db_connection()
    if conn:
        try:
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

@app.route('/admin')
def admin_panel():
    measurements, orders = [], []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, customer_name, phone_number, address, date_created FROM measurements ORDER BY id DESC")
            measurements = cursor.fetchall()
            cursor.execute("SELECT id, customer_name, phone_number, products, total_amount, mode, date FROM orders ORDER BY id DESC")
            orders = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Ադմին բազայի սխալ: {e}")
        
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
        
    conn = get_db_connection()
    if conn:
        try:
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
    conn = get_db_connection()
    if conn:
        try:
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

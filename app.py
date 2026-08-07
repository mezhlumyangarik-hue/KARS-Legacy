from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import psycopg2
from psycopg2.extras import DictCursor
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# ==========================================
# 📂 ՃԻՇՏ ՃԱՆԱՊԱՐՀՆԵՐ (VERCEL-Ի ՀԱՄԱՐ)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('/tmp' if os.environ.get('VERCEL') else BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ==========================================
# 🔗 ՄԻԱՑՈՒՄ SUPABASE POSTGRESQL ԲԱԶԱՅԻՆ
# ==========================================
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        return conn
    except Exception as e:
        print(f"Բազային միանալու սխալ: {e}")
        return None

# ==========================================
# 💎 ՖԻՔՍՎԱԾ (ԱՆՋՆՋԵԼԻ) KARS LEGACY ԱՊՐԱՆՔՆԵՐ՝ ՄՇՏԱԿԱՆ ՆԿԱՐՆԵՐՈՎ
# ==========================================
PERMANENT_PRODUCTS = [
    {
        'id': 1001,
        'title': 'KARS Armored Metal Grand 01',
        'price': 280000,
        'metal': '3մմ Բարձրամուր Պողպատ',
        'wood': 'MDF Փայտյա Երեսպատում (Ընկույզ)',
        'filler': 'Բազալտե Ջերմամեկուսիչ Բամբակ',
        'category': 'Արտաքին Մետաղական',
        'is_new': True,
        'desc': 'Բարձրամուր արտաքին երկաթյա դուռ՝ նախատեսված առանձնատների համար։ Ապահովված է բարձր որակի փականներով և ձայնամեկուսացմամբ։',
        'main_image': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
        'gallery_images': [
            'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1481277542470-605612bd2d61?auto=format&fit=crop&w=800&q=80'
        ]
    },
    {
        'id': 1002,
        'title': 'KARS Classic MDF Elegance',
        'price': 145000,
        'metal': 'Ամրացված Մետաղական Կարկաս',
        'wood': 'Պրեմիում MDF Էմալ Պատվածք',
        'filler': 'Բնական Փայտ / Ձայնամեկուսիչ Սալ',
        'category': 'Միջսենյակային',
        'is_new': True,
        'desc': 'Ժամանակակից, էլեգանտ դիզայնով միջսենյակային դուռ՝ բնակարանների և գրասենյակների համար։',
        'main_image': 'https://images.unsplash.com/photo-1481277542470-605612bd2d61?auto=format&fit=crop&w=800&q=80',
        'gallery_images': [
            'https://images.unsplash.com/photo-1481277542470-605612bd2d61?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80'
        ]
    },
    {
        'id': 1003,
        'title': 'KARS Modern Gold Edition',
        'price': 195000,
        'metal': '2.5մմ Պողպատյա Պրոֆիլ',
        'wood': 'Բնական Փայտ / MDF',
        'filler': 'Ջերմա-ձայնամեկուսիչ Սալ',
        'category': 'Էքսկլյուզիվ',
        'is_new': True,
        'desc': 'Էքսկլյուզիվ ոսկեգույն էլեմենտներով պրեմիում դասի դուռ, որը կապահովի Ձեր տան շքեղ տեսքն ու անվտանգությունը։',
        'main_image': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80',
        'gallery_images': [
            'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=800&q=80',
            'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80'
        ]
    }
]

def get_all_products_from_db():
    products = list(PERMANENT_PRODUCTS) # Միշտ ներառում է ֆիքսված ապրանքները
    
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
            print(f"Բազայից կարդալու սխալ: {e}")
            
    return products

# 🛠️ ԲԱԶԱՅԻ ԱՂՅՈՒՍԱԿՆԵՐԻ ՍՏԵՂԾՈՒՄ
@app.route('/init-database-secure-999')
def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            return "DATABASE_URL-ը բացակայում է կամ սխալ է:"
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

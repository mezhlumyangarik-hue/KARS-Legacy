from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# 3 ՀՍՏԱԿ ՄՈՒՏՔԻ ԴՌՆԵՐԻ ՆԿԱՐՆԵՐ
PERMANENT_PRODUCTS = [
    {
        'id': 1001,
        'title': 'KARS Grand Armored Metal 01',
        'price': 280000,
        'metal': '3մմ Բարձրամուր Պողպատ',
        'wood': 'MDF Փայտյա Երեսպատում',
        'filler': 'Բազալտե Ջերմամեկուսիչ Բամբակ',
        'category': 'double-iron',  # Երկկողմանի Երկաթ
        'is_new': True,
        'desc': 'Բարձր որակի արտաքին մուտքի մետաղական դուռ՝ ապակե հատվածով, երկար մոդեռն բռնակով և բարձր պաշտպանվածությամբ։',
        'main_image': 'https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1002,
        'title': 'KARS Premium MDF Entry Door',
        'price': 195000,
        'metal': '2.5մմ Մետաղական Կարկաս',
        'wood': 'Պրեմիում MDF Էմալ Պատվածք',
        'filler': 'Ձայնամեկուսիչ Սալ',
        'category': 'double-wood',  # Երկկողմանի Փայտ / MDF
        'is_new': True,
        'desc': 'Շքեղ մուտքի դուռ՝ երկկողմանի ապակե ներդիրներով և դեկորատիվ մետաղական նախշերով։',
        'main_image': 'https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1003,
        'title': 'KARS Modern Steel & MDF Elite',
        'price': 240000,
        'metal': '3մմ Պողպատյա Պրոֆիլ',
        'wood': 'Մոդեռն MDF Vertical Panel',
        'filler': 'Բազալտե Ջերմամեկուսիչ Սալ',
        'category': 'single-wood',  # Մեկ կողմը Փայտ
        'is_new': True,
        'desc': 'Ժամանակակից ուղղահայաց գծերով դիզայնով մուտքի դուռ՝ նախատեսված առանձնատների և բնակարանների համար։',
        'main_image': 'https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?auto=format&fit=crop&w=1200&q=80']
    }
]

@app.route('/')
def home():
    return render_template('index.html', products=PERMANENT_PRODUCTS)

@app.route('/shop')
def shop_page():
    # Կարդում ենք կատեգորիան URL-ից (օրինակ՝ /shop?category=double-iron)
    selected_category = request.args.get('category', '')
    
    if selected_category:
        filtered_products = [p for p in PERMANENT_PRODUCTS if p.get('category') == selected_category]
    else:
        filtered_products = PERMANENT_PRODUCTS

    return render_template(
        'shop.html', 
        products=filtered_products, 
        selected_category=selected_category
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((item for item in PERMANENT_PRODUCTS if item['id'] == product_id), None)
    if product is None:
        abort(404)
    return render_template('product_detail.html', product=product)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'cart' not in session:
        session['cart'] = []
    
    # Ավելացնում ենք ապրանքը զամբյուղում
    session['cart'].append(product_id)
    session.modified = True
    
    return redirect(url_for('shop_page'))

if __name__ == '__main__':
    app.run(debug=True)

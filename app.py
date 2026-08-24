from flask import Flask, render_template, request, abort, session, redirect, url_for, jsonify
import os

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# 9 ՄՇՏԱԿԱՆ ԴՌՆԵՐ (ԱՄԵՆ ԿԱՏԵԳՈՐԻԱՅԻՑ 3-ԱԿԱՆ ՀԱՏ)
PERMANENT_PRODUCTS = [
    # 1. Երկկողմանի Երկաթ (double-iron) - 3 հատ
    {
        'id': 1001,
        'title': 'KARS Grand Armored Metal 01',
        'price': 280000,
        'metal': '3մմ Բարձրամուր Պողպատ',
        'wood': 'MDF Փայտյա Երեսպատում',
        'filler': 'Բազալտե Ջերմամեկուսիչ Բամբակ',
        'category': 'double-iron',
        'is_new': True,
        'desc': 'Բարձր որակի արտաքին մուտքի մետաղական դուռ՝ ապակե հատվածով, երկար մոդեռն բռնակով և բարձր պաշտպանվածությամբ։',
        'main_image': 'https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1004,
        'title': 'KARS Titan Steel Shield',
        'price': 320000,
        'metal': '3.5մմ Զրահապատ Պողպատ',
        'wood': 'Պրեպրեգ Մետաղական Ծածկույթ',
        'filler': 'Ձայնամեկուսիչ Բազալտ',
        'category': 'double-iron',
        'is_new': False,
        'desc': 'Երկկողմանի ամրացված մետաղական դուռ՝ նախատեսված հատուկ անվտանգություն պահանջող առանձնատների համար։',
        'main_image': 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1005,
        'title': 'KARS Iron Heavy Duty',
        'price': 295000,
        'metal': '3մմ Պողպատ',
        'wood': 'Փոշեներկված Մետաղ',
        'filler': 'Մեկուսիչ Փրփուր',
        'category': 'double-iron',
        'is_new': True,
        'desc': 'Երկաթյա ամուր դուռ՝ հակահրդեհային և հակահարվածային համակարգերով։',
        'main_image': 'https://images.unsplash.com/photo-1481277542470-605612bd2d61?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1481277542470-605612bd2d61?auto=format&fit=crop&w=1200&q=80']
    },

    # 2. Երկկողմանի Փայտ / MDF (double-wood) - 3 հատ
    {
        'id': 1002,
        'title': 'KARS Premium MDF Entry Door',
        'price': 195000,
        'metal': '2.5մմ Մետաղական Կարկաս',
        'wood': 'Պրեմիում MDF Էմալ Պատվածք',
        'filler': 'Ձայնամեկուսիչ Սալ',
        'category': 'double-wood',
        'is_new': True,
        'desc': 'Շքեղ մուտքի դուռ՝ երկկողմանի ապակե ներդիրներով և դեկորատիվ մետաղական նախշերով։',
        'main_image': 'https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1534430480872-3498386e7856?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1006,
        'title': 'KARS Classic Oak Double Panel',
        'price': 230000,
        'metal': '2մմ Կարկաս',
        'wood': 'Բնական Կաղնու Ֆաներա',
        'filler': 'Մեկուսիչ Բամբակ',
        'category': 'double-wood',
        'is_new': False,
        'desc': 'Դասական դիզայնով երկկողմանի MDF/փայտյա դուռ՝ բնական կաղնու տեքստուրայով։',
        'main_image': 'https://images.unsplash.com/photo-1517646287270-a5a9ca602e5c?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1517646287270-a5a9ca602e5c?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1007,
        'title': 'KARS Elegant White Enamel',
        'price': 210000,
        'metal': '2մմ Պողպատ',
        'wood': 'Սպիտակ Էմալապատ MDF',
        'filler': 'Ձայնամեկուսիչ Փրփուր',
        'category': 'double-wood',
        'is_new': True,
        'desc': 'Նրբագեղ սպիտակ փայտյա երեսպատմամբ դուռ՝ մոդեռն ինտերիերի համար։',
        'main_image': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?auto=format&fit=crop&w=1200&q=80']
    },

    # 3. Մեկ կողմը Փայտ (single-wood) - 3 հատ
    {
        'id': 1003,
        'title': 'KARS Modern Steel & MDF Elite',
        'price': 240000,
        'metal': '3մմ Պողպատյա Պրոֆիլ',
        'wood': 'Մոդեռն MDF Vertical Panel',
        'filler': 'Բազալտե Ջերմամեկուսիչ Սալ',
        'category': 'single-wood',
        'is_new': True,
        'desc': 'Ժամանակակից ուղղահայաց գծերով դիզայնով մուտքի դուռ՝ նախատեսված առանձնատների և բնակարանների համար։',
        'main_image': 'https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1008,
        'title': 'KARS Eco Walnut Single Wood',
        'price': 185000,
        'metal': '2մմ Պողպատ',
        'wood': 'Ընկույզի Փայտյա Վանել',
        'filler': 'Ջերմամեկուսիչ Սալ',
        'category': 'single-wood',
        'is_new': False,
        'desc': 'Մեկ կողմից բնական ընկույզի փայտով երեսպատված մուտքի բարձրորակ դուռ։',
        'main_image': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1586023492125-27b2c045efd7?auto=format&fit=crop&w=1200&q=80']
    },
    {
        'id': 1009,
        'title': 'KARS Dark Loft Single Panel',
        'price': 225000,
        'metal': '2.5մմ Պողպատ',
        'wood': 'Մութ MDF Տեքստուրա',
        'filler': 'Բազալտե Բամբակ',
        'category': 'single-wood',
        'is_new': True,
        'desc': 'Լոֆթ Սթայլ մեկ կողմից փայտյա դեկորատիվ վահանակով արտաքին դուռ։',
        'main_image': 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': ['https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80']
    }
]

@app.route('/')
def home():
    return render_template('index.html', products=PERMANENT_PRODUCTS)

@app.route('/shop')
def shop_page():
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
    
    session['cart'].append(product_id)
    session.modified = True
    
    return redirect(url_for('shop_page'))

if __name__ == '__main__':
    app.run(debug=True)

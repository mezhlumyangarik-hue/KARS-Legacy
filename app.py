from flask import Flask, render_template, abort

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

PERMANENT_PRODUCTS = [
    {
        'id': 1001,
        'title': 'KARS Grand Armored Metal 01',
        'price': 280000,
        'metal': '3մմ Բարձրամուր Պողպատ',
        'wood': 'MDF Փայտյա երեսպատում',
        'filler': 'Բազալտե Ջերմաձայնակլանիչ Բամբակ',
        'category': 'double-iron',
        'is_new': True,
        'desc': 'Բարձր որակի արտաքին մուտքի մետաղական դուռ՝ ապակե հատվածով, երկշերտ բռնակով և բարձր պաշտպանությամբ:',
        'main_image': 'https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': [
            'https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80'
        ]
    },
    {
        'id': 1004,
        'title': 'KARS Titan Steel Shield',
        'price': 320000,
        'metal': '3.5մմ Զրահապատ Պողպատ',
        'wood': 'Պոլիմերդ Մետաղական Ծածկույթ',
        'filler': 'Ձայնամեկուսիչ Բազալտ',
        'category': 'double-iron',
        'is_new': False,
        'desc': 'Երկկողմանի ամրացված մետաղական դուռ՝ նախատեսված հատուկ անվտանգություն պահանջող առանձնատների համար:',
        'main_image': 'https://images.unsplash.com/photo-1513694203232-719a280e22f?auto=format&fit=crop&w=1200&q=80',
        'gallery_images': [
            'https://images.unsplash.com/photo-1513694203232-719a280e22f?auto=format&fit=crop&w=1200&q=80'
        ]
    }
]

@app.route('/')
def index():
    return render_template('index.html', products=PERMANENT_PRODUCTS)

# Քո index.html-ը կանչում է product_detail endpoint-ը
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in PERMANENT_PRODUCTS if p['id'] == product_id), None)
    if not product:
        abort(404)

    # Քո project-ում որ template-ն առկա է, դա կօգտագործվի
    try:
        return render_template('product_detail.html', product=product, door=product)
    except Exception:
        return render_template('door_detail.html', door=product, product=product)

# Հին /door/ հղումները նույնպես պահում ենք
@app.route('/door/<int:door_id>')
def door_detail(door_id):
    door = next((p for p in PERMANENT_PRODUCTS if p['id'] == door_id), None)
    if not door:
        abort(404)

    try:
        return render_template('door_detail.html', door=door, product=door)
    except Exception:
        return render_template('product_detail.html', product=door, door=door)

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/shop')
def shop():
    return render_template('shop.html', products=PERMANENT_PRODUCTS)

if __name__ == '__main__':
    app.run(debug=True)

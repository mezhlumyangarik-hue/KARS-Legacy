from flask import Flask, render_template, request, abort

app = Flask(__name__)
app.secret_key = 'mezhlumyan_doors_ultra_secret_key_999'

# Մուտքի դռներ (նախնական ապրանքներ՝ կոդի մեջ)
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
        'gallery_images': ['https://images.unsplash.com/photo-1558036117-15d82a90b9b1?auto=format&fit=crop&w=1200&q=80']
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
        'gallery_images': ['https://images.unsplash.com/photo-1513694203232-719a280e22f?auto=format&fit=crop&w=1200&q=80']
    }
]

@app.route('/')
def index():
    # Վերադարձնում է դռների ցանկը հիմնական էջում
    return render_template('index.html', products=PERMANENT_PRODUCTS)

@app.route('/door/<int:door_id>')
def door_detail(door_id):
    # Որոնում ենք կոնկրետ դուռն ըստ ID-ի
    door = next((p for p in PERMANENT_PRODUCTS if p['id'] == door_id), None)
    if not door:
        abort(404)
    return render_template('door_detail.html', door=door)

if __name__ == '__main__':
    app.run(debug=True)

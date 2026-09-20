from flask import Flask, render_template, request, abort, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "mezhlumyan_doors_ultra_secret_key_999"


# =========================================================
# KARS LEGACY — ՄՇՏԱԿԱՆ ԱՊՐԱՆՔՆԵՐ
# Ապրանքները պահվում են հենց կոդի մեջ։
# Նկարները վերցվում են static/image/ պանակից։
# =========================================================

PERMANENT_PRODUCTS = [
    {
        "id": 1001,
        "title": "KARS Grand Armored Metal 01",
        "price": 280000,
        "metal": "3մմ Բարձրամուր Պողպատ",
        "wood": "MDF Փայտյա երեսպատում",
        "filler": "Բազալտե Ջերմաձայնակլանիչ Բամբակ",
        "category": "double-iron",
        "is_new": True,
        "desc": "Բարձր որակի արտաքին մուտքի մետաղական դուռ՝ ապակե հատվածով, երկշերտ բռնակով և բարձր պաշտպանությամբ:",
        "main_image": "KARS_Legacy_1.jpg",
        "gallery_images": [
            "KARS_Legacy_1.jpg",
            "Kars_Legacy_2.jpg",
            "KARS_Legacy_3.jpg"
        ]
    },
    {
        "id": 1004,
        "title": "KARS Titan Steel Shield",
        "price": 320000,
        "metal": "3.5մմ Զրահապատ Պողպատ",
        "wood": "Պոլիմերդ Մետաղական Ծածկույթ",
        "filler": "Ձայնամեկուսիչ Բազալտ",
        "category": "double-iron",
        "is_new": False,
        "desc": "Երկկողմանի ամրացված մետաղական դուռ՝ նախատեսված հատուկ անվտանգություն պահանջող առանձնատների համար:",
        "main_image": "Kars_Legacy_2.jpg",
        "gallery_images": [
            "Kars_Legacy_2.jpg",
            "KARS_Legacy_1.jpg",
            "KARS_Legacy_3.jpg"
        ]
    }
]


# =========================================================
# ՕԳՆԱԿԱՆ ՖՈՒՆԿՑԻԱՆԵՐ
# =========================================================

def get_product(product_id):
    return next(
        (product for product in PERMANENT_PRODUCTS if product["id"] == product_id),
        None
    )


def get_cart():
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return cart


def cart_items():
    items = []
    total = 0
    cart = get_cart()

    for product in PERMANENT_PRODUCTS:
        key = str(product["id"])
        quantity = int(cart.get(key, 0))

        if quantity > 0:
            item = dict(product)
            item["quantity"] = quantity
            item["subtotal"] = product["price"] * quantity
            items.append(item)
            total += item["subtotal"]

    return items, total


@app.context_processor
def inject_global_data():
    items, total = cart_items()
    return {
        "cart_count": sum(item["quantity"] for item in items),
        "cart_items": items,
        "cart_total": total,
        "permanent_products": PERMANENT_PRODUCTS
    }


# =========================================================
# ԳԼԽԱՎՈՐ
# =========================================================

@app.route("/")
def index():
    return render_template(
        "index.html",
        products=PERMANENT_PRODUCTS,
        search_query=""
    )


# layout.html-ում օգտագործվող home անունը
@app.route("/home")
def home():
    return redirect(url_for("index"))


# =========================================================
# ՏԵՍԱԿԱՆԻ
# =========================================================

@app.route("/shop")
def shop():
    return render_template(
        "shop.html",
        products=PERMANENT_PRODUCTS,
        search_query=""
    )


# layout.html-ի shop_page հղման համար
@app.route("/shop-page")
def shop_page():
    return redirect(url_for("shop"))


# =========================================================
# ՈՐՈՆՈՒՄ
# =========================================================

@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        products = PERMANENT_PRODUCTS
    else:
        q = query.lower()
        products = [
            product for product in PERMANENT_PRODUCTS
            if q in product["title"].lower()
            or q in product["desc"].lower()
            or q in product["category"].lower()
            or q in product["metal"].lower()
            or q in product["wood"].lower()
        ]

    return render_template(
        "shop.html",
        products=products,
        search_query=query
    )


# =========================================================
# ԱՊՐԱՆՔԻ ԷՋ
# =========================================================

@app.route("/door/<int:door_id>")
@app.route("/product/<int:door_id>")
def door_detail(door_id):
    product = get_product(door_id)

    if not product:
        abort(404)

    # Տալիս ենք և՛ door, և՛ product,
    # որպեսզի երկու տեսակի template-երի հետ աշխատի։
    return render_template(
        "product_detail.html",
        product=product,
        door=product
    )


# =========================================================
# ԶԱՄԲՅՈՒՂ
# =========================================================

@app.route("/cart")
def cart():
    items, total = cart_items()

    return render_template(
        "cart.html",
        items=items,
        products=items,
        total=total,
        cart_total=total
    )


@app.route("/cart-page")
def cart_page():
    return redirect(url_for("cart"))


@app.route("/add-to-cart/<int:product_id>", methods=["GET", "POST"])
@app.route("/cart/add/<int:product_id>", methods=["GET", "POST"])
def add_to_cart(product_id):
    product = get_product(product_id)

    if not product:
        abort(404)

    cart = get_cart()
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + 1

    session["cart"] = cart
    session.modified = True

    return redirect(request.referrer or url_for("index"))


@app.route("/remove-from-cart/<int:product_id>", methods=["GET", "POST"])
@app.route("/cart/remove/<int:product_id>", methods=["GET", "POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    key = str(product_id)

    if key in cart:
        cart[key] = int(cart[key]) - 1
        if cart[key] <= 0:
            del cart[key]

    session["cart"] = cart
    session.modified = True

    return redirect(request.referrer or url_for("cart"))


@app.route("/cart/clear", methods=["GET", "POST"])
@app.route("/clear-cart", methods=["GET", "POST"])
def clear_cart():
    session["cart"] = {}
    session.modified = True
    return redirect(url_for("cart"))


# =========================================================
# ՉԱՓԱԳՐՈՒՄ / ՊԱՏՎԵՐ
# =========================================================

@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/orders-page")
def orders_page():
    return redirect(url_for("orders"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = cart_items()

    if request.method == "POST":
        # Այստեղ տվյալները կարող են հետագայում ուղարկվել
        # WhatsApp / Telegram / email / database։
        session["cart"] = {}
        session.modified = True
        return render_template(
            "success.html",
            total=total,
            items=items
        )

    return render_template(
        "checkout.html",
        items=items,
        total=total,
        cart_total=total
    )


@app.route("/success")
def success():
    return render_template("success.html")


# =========================================================
# APP START
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)

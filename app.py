from flask import Flask, render_template, request, redirect, url_for, session, abort

app = Flask(__name__)
app.secret_key = "mezhlumyan_doors_ultra_secret_key_999"

# =========================================================
# KARS LEGACY — PRODUCTS
# Images are stored locally in: static/image/
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
            "KARS_Legacy_3.jpg",
        ],
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
        "main_image": "KARS_Legacy_3.jpg",
        "gallery_images": [
            "KARS_Legacy_3.jpg",
            "Kars_Legacy_2.jpg",
            "KARS_Legacy_1.jpg",
        ],
    },
]


# =========================================================
# HELPERS
# =========================================================

def get_product(product_id):
    return next(
        (product for product in PERMANENT_PRODUCTS if product["id"] == product_id),
        None,
    )


def get_cart():
    return session.get("cart", {})


def get_cart_items():
    cart = get_cart()
    items = []

    for product_id, quantity in cart.items():
        product = get_product(int(product_id))
        if product:
            quantity = int(quantity)
            item = dict(product)
            item["quantity"] = quantity
            item["subtotal"] = product["price"] * quantity
            items.append(item)

    return items


def get_cart_count():
    return sum(int(qty) for qty in get_cart().values())


def get_cart_total():
    return sum(item["subtotal"] for item in get_cart_items())


# Makes cart_count available in EVERY template.
@app.context_processor
def inject_global_values():
    return {
        "cart_count": get_cart_count(),
        "cart_items": get_cart_items(),
        "cart_total": get_cart_total(),
    }


# =========================================================
# MAIN PAGES
# =========================================================

@app.route("/")
def home():
    return render_template(
        "index.html",
        products=PERMANENT_PRODUCTS,
        search_query="",
    )


# Backward-compatible endpoint if any old template uses index.
@app.route("/index")
def index():
    return redirect(url_for("home"))


@app.route("/shop")
def shop_page():
    query = request.args.get("query", "").strip()

    if query:
        query_lower = query.lower()
        products = [
            product
            for product in PERMANENT_PRODUCTS
            if query_lower in product["title"].lower()
            or query_lower in product["desc"].lower()
            or query_lower in product["category"].lower()
        ]
    else:
        products = PERMANENT_PRODUCTS

    return render_template(
        "shop.html",
        products=products,
        search_query=query,
    )


# Old endpoint name kept working.
@app.route("/shop-page")
def shop():
    return redirect(url_for("shop_page"))


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return redirect(url_for("shop_page"))

    return redirect(url_for("shop_page", query=query))


@app.route("/orders")
def orders_page():
    return render_template("orders.html")


# =========================================================
# PRODUCT
# =========================================================

@app.route("/door/<int:door_id>")
def door_detail(door_id):
    product = get_product(door_id)

    if product is None:
        abort(404)

    # Supports templates that use either "door" or "product".
    return render_template(
        "product_detail.html",
        product=product,
        door=product,
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    return render_template(
        "product_detail.html",
        product=product,
        door=product,
    )


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart_page():
    return render_template(
        "cart.html",
        items=get_cart_items(),
        total=get_cart_total(),
    )


# Old endpoint name kept working.
@app.route("/cart-page")
def cart():
    return redirect(url_for("cart_page"))


@app.route("/cart/add/<int:product_id>", methods=["POST", "GET"])
def add_to_cart(product_id):
    product = get_product(product_id)

    if product is None:
        abort(404)

    cart = dict(get_cart())
    key = str(product_id)
    cart[key] = int(cart.get(key, 0)) + 1

    session["cart"] = cart
    session.modified = True

    return redirect(request.referrer or url_for("shop_page"))


@app.route("/cart/remove/<int:product_id>", methods=["POST", "GET"])
def remove_from_cart(product_id):
    cart = dict(get_cart())
    key = str(product_id)

    if key in cart:
        cart.pop(key)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("cart_page"))


@app.route("/cart/clear", methods=["POST", "GET"])
def clear_cart():
    session["cart"] = {}
    session.modified = True
    return redirect(url_for("cart_page"))


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = get_cart_items()
    total = get_cart_total()

    if request.method == "POST":
        # The existing checkout template can receive the order data.
        # A real database/order system can be connected later.
        return render_template(
            "success.html",
            items=items,
            total=total,
            customer_name=request.form.get("name", ""),
            customer_phone=request.form.get("phone", ""),
        )

    return render_template(
        "checkout.html",
        items=items,
        total=total,
    )


@app.route("/success")
def success():
    return render_template(
        "success.html",
        items=[],
        total=0,
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)

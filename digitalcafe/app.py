from flask import Flask, redirect
from flask import render_template
from flask import request
from flask import session
import database as db
import authentication
import logging
import ordermanagement as om

app = Flask(__name__)

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/addtocart', methods=['POST', ])
def addtocart():
    code = request.form.get('code')
    quantity = int(request.form.get('quantity'))
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a
    # quantity of 1 for now

    item["qty"] = quantity
    item["code"] = code
    item["name"] = product["name"]
    item["subtotal"] = product["price"]*item["qty"]

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')


@app.route('/updatecart', methods=['POST', ])
def updatecart():
    request_type = request.form.get('submit')
    code = request.form.get('code')
    product = db.get_product(int(code))
    cart = session["cart"]

    # Update quantity of item in cart
    if request_type == "Update":
        quantity = int(request.form.get("quantity"))
        cart[code]["qty"] = quantity
        cart[code]["subtotal"] = quantity * product["price"]

    # Remove item from cart
    elif request_type == 'Remove':
        del cart[code]

    session["cart"] = cart

    return redirect('/cart')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("cart", None)
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if (is_successful):
        session["user"] = user
        return redirect('/')
    else:
        return redirect('/loginerror')


@app.route('/')
def index():
    return render_template('index.html', page="Index")


@app.route('/loginerror')
def loginerror():
    return render_template('loginerror.html', page="Loginerror")


@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products",
                           product_list=product_list)

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    return render_template('productdetails.html', code=code,
                           product=product)

@app.route('/branches')
def branches():
    code = request.args.get('code', '')
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(int(code))
    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/formsubmission', methods = ['POST'])
def form_submission():
    qty = request.form.getlist("qty")
    return render_template('formsubmission.html',qty=qty)

@app.route('/order_complete')
def ordercomplete():
    return render_template('order_complete.html')

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect("/order_complete")

@app.route('/past_orders')
def orderhistory():
    user_=session["user"]
    username=user_["username"]
    confirmed_order=om.check_user(username)

    if confirmed_order == True:
        past_orders=db.get_orders(username)

        return render_template('orders.html', past_orders=past_orders)

    else:
        return render_template("noorders.html")

@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html')

@app.route('/pass_change', methods=['GET', 'POST'])
def change_pass():
    user_ = session["user"]
    username = user_["username"]
    old_p = db.get_password(username)
    old_p_form = request.form.get('old_p')
    new_p = request.form.get('new_p')
    new_p_c = request.form.get('new_p_c')

    if old_p_form == old_p and new_p == new_p_c:
        change_pass = db.change_db(username, new_p)
        change_error = "Password changed successfully."
        return render_template("changepassword.html")

    elif new_p != new_p_c:
        change_error = "New passwords don't match. Please try again."
        return render_template("changepassword.html")

    else old_p_form != old_p:
        change_error = "Previous password entered incorrectly. Please try again."
        return render_template("changepassword.html")

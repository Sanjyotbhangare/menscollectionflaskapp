from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import or_
import datetime

# Creating Flask App
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://qgeplhiqaiqjkc:5441b15685a420e804ee7f5a8e867256403ff2a9a976400ca4a54466dce7c144@ec2-44-195-100-240.compute-1.amazonaws.com:5432/d28ku781comne6"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 300
app.config['UPLOAD_FOLDER'] = "static/images/"
# Creating SQLAlchemy ORM model
db = SQLAlchemy(app)
# postgresql://postgres:root@127.0.0.1:5432/menscollection


db.session.cart_items = {}
db.session.cart_size = 0
db.session.search = ''
db.session.mobile_no = ''
db.session.admin = ''


class customException(Exception):
    def __int__(self, msg):
        super().__init__(msg)
        self.msg = msg


# All Tables in database
class Product(db.Model):
    product_id = db.Column(db.Integer(), primary_key=True)
    brand = db.Column(db.String(20), unique=False, nullable=False)
    category = db.Column(db.String(20), unique=False, nullable=False)
    clothe_type = db.Column(db.String(20), unique=False, nullable=False)
    pattern = db.Column(db.String(20), unique=False, nullable=False)
    fitting = db.Column(db.String(20), unique=False, nullable=False)
    color = db.Column(db.String(20), unique=False, nullable=False)
    size = db.Column(db.Integer(), unique=False, nullable=False)
    rate = db.Column(db.Integer(), unique=False, nullable=False)
    image = db.Column(db.String(20), unique=False, nullable=False)


class Customer(db.Model):
    mobile_number = db.Column(db.Integer(), primary_key=True)
    password = db.Column(db.String(20), unique=False, nullable=False)
    cust_name = db.Column(db.String(20), unique=False, nullable=False)


class OrderProduct(db.Model):
    order_id = db.Column(db.Integer(), primary_key=True)
    order_date = db.Column(db.DateTime, unique=False, nullable=False)
    mobile_number = db.Column(db.Integer(), unique=False, nullable=False)
    address = db.Column(db.String(100), unique=False, nullable=False)
    total_amount = db.Column(db.Integer(), unique=False, nullable=False)


class OrderDetails(db.Model):
    order_id = db.Column(db.Integer(), primary_key=True)
    product_id = db.Column(db.Integer(), primary_key=True)
    quantity = db.Column(db.Integer(), unique=False, nullable=False)
    rate = db.Column(db.Integer(), unique=False, nullable=False)
    amount = db.Column(db.Integer(), unique=False, nullable=False)


class Admin(db.Model):
    admin_id = db.Column(db.Integer(), primary_key=True)
    password = db.Column(db.String(20), unique=False, nullable=False)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/SignIn", methods=['GET', 'POST'])
def signIn():
    # Check user is already logged in or not
    try:
        if db.session.mobile_no != '':
            raise customException("Already Logged In ..!")
    except customException as e:
        allproduct = Product.query.all()
        return render_template("products.html", products=allproduct, cart=db.session.cart_size, msg=e)

    if request.method == "POST":
        # validating mobile number and password
        mobile = request.form.get('mobileno')
        password = request.form.get('password')
        try:
            if mobile == '':
                raise customException("Please Enter Mobile Number")
            elif len(mobile) != 10:
                raise customException("Please Enter Valid Mobile Number")
            elif not mobile.isdigit():
                raise customException("Mobile Number Should Contain Digits Only")
            elif mobile[0] not in ('6', '7', '8', '9'):
                raise customException("Please Enter Valid Mobile Number Series")
            elif password == '':
                raise customException("Please Enter Password")
            elif len(password) < 8 or len(password) > 15:
                raise customException("Length of Password Must be Between 8 to 15")
            elif not password.isalnum():
                raise customException("Password Should Contain Digits or Alphabets Only")
            else:
                # checking customer is present or not
                find_customer = Customer.query.filter_by(mobile_number=int(mobile), password=password).all()
                if len(find_customer) == 0:
                    raise customException("Invalid Mobile Number or Password .!!!")
                else:
                    db.session.mobile_no = mobile
                    allproduct = Product.query.all()
                    return render_template("products.html", products=allproduct, cart=db.session.cart_size)

        except customException as e:
            return render_template("signIn.html", msg=e)

    return render_template("signIn.html")


@app.route("/ForgetPassword", methods=['GET', 'POST'])
def forgetPassword():
    if request.method == "POST":
        # validating mobile number and password
        mobile = request.form.get('mobileno')
        password = request.form.get('password')
        try:
            if mobile == '':
                raise customException("Please Enter Mobile Number")
            elif len(mobile) != 10:
                raise customException("Please Enter Valid Mobile Number")
            elif not mobile.isdigit():
                raise customException("Mobile Number Should Contain Digits Only")
            elif mobile[0] not in ('6', '7', '8', '9'):
                raise customException("Please Enter Valid Mobile Number Series")
            elif password == '':
                raise customException("Please Enter Password")
            elif len(password) < 8 or len(password) > 15:
                raise customException("Length of Password Must be Between 8 to 15")
            elif not password.isalnum():
                raise customException("Password Should Contain Digits or Alphabets Only")
            else:
                # checking customer is present or not
                find_customer = Customer.query.filter_by(mobile_number=int(mobile)).all()
                if len(find_customer) == 0:
                    raise customException("Mobile Number Not Found .!!!")
                else:
                    # Updating the password
                    Customer.query.filter_by(mobile_number=int(mobile)).update(dict({'password': password}))
                    db.session.commit()
                    return render_template("signIn.html", msg="Password Changed")

        except customException as e:
            return render_template("ForgetPassword.html", msg=e)

    return render_template("forgetPassword.html")


@app.route("/SignUp", methods=['GET', 'POST'])
def signUp():
    # validating mobile number and password
    if request.method == "POST":
        mobile = request.form.get('mobileno')
        name = request.form.get('cust_name').strip()
        password = request.form.get('password')

        try:
            if mobile == '':
                raise customException("Please Enter Mobile Number")
            elif len(mobile) != 10:
                raise customException("Please Enter Valid Mobile Number")
            elif not mobile.isdigit():
                raise customException("Mobile Number Should Contain Digits Only")
            elif mobile[0] not in ('6', '7', '8', '9'):
                raise customException("Please Enter Valid Mobile Number Series")
            elif name == '':
                raise customException("Please Enter Name")
            elif len(name) > 30:
                raise customException("Length of Name is too long")
            elif not all(char.isalpha() or char.isspace() for char in name):
                raise customException("Name should Not Contain Digits or Special Characters")
            elif password == '':
                raise customException("Please Enter Password")
            elif len(password) < 8 or len(password) > 15:
                raise customException("Length of Password Must be Between 8 to 15")
            elif not password.isalnum():
                raise customException("Password Should Contain Digits or Alphabets Only")
            else:
                # checking customer is present or not
                find_customer = Customer.query.filter_by(mobile_number=int(mobile)).all()
                if len(find_customer) == 1:
                    raise customException("Mobile Number Already Present .!!!")
                else:
                    # Inserting customer Data to database
                    result = Customer(mobile_number=mobile, password=password, cust_name=name)
                    db.session.add(result)
                    db.session.commit()
                    return render_template("signIn.html", success='Successfully Registered Please Login')

        except customException as e:
            return render_template("signUp.html", msg=e)

    return render_template("signUp.html")


@app.route("/Products")
def products():
    allproduct = Product.query.all()
    return render_template("products.html", products=allproduct, cart=db.session.cart_size)


@app.route("/Search", methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        db.session.search = request.form.get('search')
        try:
            # searching in database
            allproduct = Product.query.filter(
                or_(Product.brand.like('%' + db.session.search + '%'),
                    Product.category.like('%' + db.session.search + '%'),
                    Product.clothe_type.like('%' + db.session.search + '%'),
                    Product.pattern.like('%' + db.session.search + '%'),
                    Product.fitting.like('%' + db.session.search + '%'),
                    Product.color.like('%' + db.session.search + '%'),
                    Product.rate.like('%' + db.session.search + '%'))).all()

            if len(allproduct) == 0:
                raise customException("No Product Found .!!!")
        except customException as e:
            return render_template("products.html", msg=e)

        return render_template("products.html", products=allproduct, cart=db.session.cart_size)


@app.route("/AddToCart", methods=['GET', 'POST'])
def addToCart():
    # Check user is already logged in or not
    try:
        if db.session.mobile_no == '':
            raise customException("Need to login .!!!")

        # Adding product to cart item
        if request.method == "POST":
            db.session.cart_items.update({request.form.get('pid'): 1})
            db.session.cart_size = len(db.session.cart_items)

        if db.session.search == '':
            allproduct = Product.query.all()
        else:
            allproduct = Product.query.filter(
                or_(Product.brand.like('%' + db.session.search + '%'),
                    Product.category.like('%' + db.session.search + '%'),
                    Product.clothe_type.like('%' + db.session.search + '%'),
                    Product.pattern.like('%' + db.session.search + '%'),
                    Product.fitting.like('%' + db.session.search + '%'),
                    Product.color.like('%' + db.session.search + '%'),
                    Product.rate.like('%' + db.session.search + '%'))).all()

        return render_template("products.html", products=allproduct, cart=db.session.cart_size)

    except customException as e:
        return render_template("signIn.html", msg=e)


@app.route("/Cart")
def cart():
    # Check user is already logged in or not
    try:
        if db.session.mobile_no == '':
            raise customException("Need to login .!!!")
        cart_products = []
        # getting product information from database
        for prod_id in db.session.cart_items:
            product_info = Product.query.filter_by(product_id=int(prod_id)).all()
            for i in product_info:
                cart_products.append(i)

        return render_template("cart.html", packed=zip(cart_products, db.session.cart_items.values()))

    except customException as e:
        return render_template("signIn.html", msg=e)


@app.route("/Remove", methods=['GET', 'POST'])
def remove():
    # Removing product from cart item
    if request.method == "POST":
        db.session.cart_items.pop(request.form.get('pid'))

    return cart()


@app.route("/ChangeQuantity", methods=['GET', 'POST'])
def changeQuantity():
    # Updating quantity by updating
    if request.method == "POST":
        qty = request.form.get('mod_quantity')
        db.session.cart_items.update({request.form.get('pid'): int(qty)})

    cart_products = []
    # getting product information from database
    for prod_id in db.session.cart_items:
        product_info = Product.query.filter_by(product_id=int(prod_id)).all()
        for i in product_info:
            cart_products.append(i)

    return render_template("cart.html", packed=zip(cart_products, db.session.cart_items.values()))


@app.route("/Purchase", methods=['GET', 'POST'])
def purchase():
    try:
        if len(db.session.cart_items) == 0:
            raise customException('Add Some Item to the Cart  .!!!')

        address = request.form.get('address').strip()
        total_amount = request.form.get('grand_total')
        # Inserting Order in order_product table
        entry = OrderProduct(order_date=datetime.date.today(), mobile_number=int(db.session.mobile_no), address=address,
                             total_amount=int(total_amount))
        db.session.add(entry)
        db.session.commit()

        for item, qty in db.session.cart_items.items():
            price = 0
            price_info = Product.query.filter_by(product_id=item).all()
            for i in price_info:
                price = i.rate
            # Inserting Order details in order_details table
            product_info = OrderDetails(order_id=entry.order_id, product_id=item, quantity=qty, rate=price,
                                        amount=qty * price)
            db.session.add(product_info)
            db.session.commit()

        db.session.cart_items = {}
        db.session.cart_size = 0
        allproduct = Product.query.all()
        return render_template("products.html", products=allproduct,
                               cart=db.session.cart_size, success="Order Placed Successfully")

    except customException as e:
        allproduct = Product.query.all()
        return render_template("products.html", products=allproduct, msg=e)


@app.route("/PreviousOrder")
def previousOrder():
    # Check user is already logged in or not
    try:
        if db.session.mobile_no == '':
            raise customException("Need To Login ..!")
    except customException as e:
        return render_template("signIn.html", msg=e)

    # Getting information of previous order of user from database
    query = "select * from order_details join order_product using(order_id) join product using(product_id)" \
            " where mobile_number = " + db.session.mobile_no + " order by order_date desc"
    print(query)
    result = db.session.execute(query)
    return render_template("previousOrder.html", result=result)


@app.route("/Logout")
def logout():
    # Check user is already logged in or not
    try:
        if db.session.mobile_no == '':
            raise customException("Need to login .!!!")

        # Removing values from all session variables
        db.session.cart_items = {}
        db.session.cart_size = 0
        db.session.search = ''
        db.session.mobile_no = ''
        return render_template("index.html")

    except customException as e:
        return render_template("signIn.html", msg=e)


@app.route("/AdminLogin", methods=['GET', 'POST'])
def adminLogin():
    # Checking admin already login or not
    try:
        if db.session.admin != '':
            raise customException("Already Logged In ..!")
    except customException as e:
        query = "select * from order_product join order_details using(order_id) order by order_date desc"
        result = db.session.execute(query)
        return render_template("admin.html", result=result, msg=e)

    if request.method == "POST":
        idNumber = request.form.get('id')
        password = request.form.get('password')
        # validating inputs
        try:
            if idNumber == '':
                raise customException("Please Enter Mobile Number")
            elif password == '':
                raise customException("Please Enter Password")
            elif len(password) < 8 or len(password) > 15:
                raise customException("Length of Password Must be Between 8 to 15")
            elif not password.isalnum():
                raise customException("Password Should Contain Digits or Alphabets Only")
            else:
                # Checking id is present or not
                find_admin = Admin.query.filter_by(admin_id=idNumber, password=password).all()
                if len(find_admin) == 0:
                    raise customException("Invalid Id or Password .!!!")
                else:
                    db.session.admin = idNumber
                    query = "select * from order_product join order_details using(order_id) order by order_date desc"
                    result = db.session.execute(query)
                    return render_template("admin.html", result=result)

        except customException as e:
            return render_template("adminLogin.html", msg=e)

    return render_template("adminLogin.html")


@app.route("/Admin")
def administrator():
    # Checking admin already login or not
    try:
        if db.session.admin == '':
            raise customException("Need To Login ..!")
    except customException as e:
        return render_template("adminLogin.html", msg=e)

    # Details of all order
    query = "select * from order_product join order_details using(order_id) order by order_date desc"
    result = db.session.execute(query)
    return render_template("admin.html", result=result)


@app.route("/AdminProducts")
def adminProducts():
    # Checking admin already login or not
    try:
        if db.session.admin == '':
            raise customException("Need To Login ..!")
    except customException as e:
        return render_template("adminLogin.html", msg=e)

    # Details of all product
    allproduct = Product.query.all()
    return render_template("adminproducts.html", result=allproduct)


@app.route("/AddProduct", methods=['GET', 'POST'])
def addProduct():
    # Checking admin already login or not
    try:
        if db.session.admin == '':
            raise customException("Need To Login ..!")
    except customException as e:
        return render_template("adminLogin.html", msg=e)

    if request.method == "POST":
        try:
            brand = request.form.get('brand').strip()
            category = request.form.get('category').strip()
            clothe_type = request.form.get('clothe_type').strip()
            pattern = request.form.get('pattern').strip()
            fitting = request.form.get('fitting').strip()
            size = request.form.get('size').strip()
            color = request.form.get('color').strip()
            rate = request.form.get('rate').strip()
            image = request.files['image']

            # Validating product information
            if not brand.isalpha():
                raise customException("Brand Name Should Contains Only Alphabets")
            if not category.isalpha():
                raise customException("Category Name Should Contains Only Alphabets")
            if not clothe_type.isalpha():
                raise customException("Clothe Type Should Contains Only Alphabets")
            if not pattern.isalpha():
                raise customException("Pattern Name Should Contains Only Alphabets")
            if not fitting.isalpha():
                raise customException("Fitting Should Contains Only Alphabets")
            if not color.isalpha():
                raise customException("Color Name Should Contains Only Alphabets")
            if not size.isdigit():
                raise customException("Size Should Contains Only Digits")
            if not rate.isdigit():
                raise customException("Rate Should Contains Only Digits")

            if image.filename.split('.')[1] not in ('jpg', 'jpeg', 'png'):
                raise customException("Invalid Extension Of Image")

            # Saving image in folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
            # Inserting into Database
            result = Product(brand=brand, category=category, clothe_type=clothe_type, pattern=pattern, fitting=fitting,
                             color=color, size=size, rate=rate, image=image.filename)
            db.session.add(result)
            db.session.commit()
            return render_template("addproduct.html", msg='Product Successfully Added')

        except customException as e:
            return render_template("addproduct.html", msg=e)

    return render_template("addproduct.html")


@app.route("/DeleteProduct", methods=['GET', 'POST'])
def deleteProduct():
    # Checking admin already login or not
    try:
        if db.session.admin == '':
            raise customException("Need To Login ..!")
    except customException as e:
        return render_template("adminLogin.html", msg=e)

    # removing product from database
    if request.method == "POST":
        product_id = request.form.get('pid')
        Product.query.filter_by(product_id=product_id).delete()
        db.session.commit()

    allproduct = Product.query.all()
    return render_template("adminproducts.html", result=allproduct)


@app.route("/AdminLogout")
def adminLogout():
    # Checking admin already login or not
    try:
        if db.session.admin == '':
            raise customException("Need to login .!!!")

        # removing allocated session variable
        db.session.admin = ''
        return render_template("index.html")

    except customException as e:
        return render_template("adminLogin.html", msg=e)


if __name__ == "__main__":
    app.run(debug=False)

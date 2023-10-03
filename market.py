from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



app.app_context().push()
app.config['SECRET_KEY'] = 'a97b6165fc6e1d159a97a9b8'


class User_product(db.Model):

    __tablename__ = "user_product"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    
    password = db.Column(db.String(8))
    email = db.Column(db.String(50), unique=True)
    products = db.relationship('Product', secondary="user_product",
                               cascade="all,delete", backref="users")

    # products = db.relationship('Product', secondary=user_product, lazy='subquery',
    #                            backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'{self.id}'


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    price = db.Column(db.Float)
    expdate = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    ms = db.Column(db.String, nullable=False)
    desc=db.Column(db.String(100))
    
    

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):
        return f'{self.name}'


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    c_item = db.relationship('Product', lazy=True,
                             backref='section')

    def __repr__(self):
        return f'{self.name}'



adc=[]


def showproducts():
    products = Product.query.all()
    return products



def showcategory():
    c = db.session.query(Category).all()
    return c


def addcart(a):
    if adc == []:
        adc.append(a)
        return 0
    elif adc != []:
        for i in adc:
            print(i.name)
            print(a.name)
            if i.name == a.name:
                return 1

    adc.append(a)

def clearcart():
    global adc
    adc = []


def checkcart(a):
    if adc == []:
        return 0
    elif adc != []:
        for i in adc:

            if i.name == a.name:
                return 1


def showcart():
    return (adc)




@app.route("/")
def home():
    if 'username' in session:
        username = session['username']
        # return render_template('home.html')
        products = showproducts()
        
        categories = showcategory()

        return render_template('home.html', products=products, categories=categories)
    return render_template('welcome.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    message = ""

    if request.method=="GET":
        return render_template("/signup.html")

    if request.method == 'POST':
        if request.form["username"] == "admin":
            msg = "Username reserved for store manager"
            return render_template("/signup.html", message=msg, category="danger")

        cust = User(
            username=request.form["username"],  password=request.form["password"], email=request.form["email"])

        username = request.form["username"]
        email = request.form["email"]

        account = db.session.query(User).filter(
            User.username == username).first()
        mail = db.session.query(User).filter(User.email == email).first()
        print(account)

        if account != None:

            message = "Username already exists"
            return render_template("/signup.html", message=message, category='danger')

        elif mail != None:
            message = "Email already used! Please use any other email address"
            return render_template("/signup.html", message=message, category='danger')
        else:

            db.session.add(cust)
            db.session.commit()
            message = "Account created successfully! Login to continue"
            return render_template("login.html", message=message, category="success")
            


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        message = ""
        return render_template("/login.html")

    if request.method == 'POST':

        name = request.form['username']
    
        password = request.form['password']
        
        account = User.query.filter(User.username == name).first()
        

        if account == None:
            message = "Username "+name+" does not exist. Register to continue"
            return render_template("login.html", message=message, category="danger")

        elif account.username == request.form['username'] and account.password == request.form['password']:

            session['loggedin'] = True
            session['username'] = account.username
            

            return redirect(url_for('home'))

        else:

            msg = 'Incorrect username / password !'
            return render_template("login.html", message=msg, category="danger")


@app.route("/adminlogin", methods=["POST", "GET"])
def adminlogin():
    if request.method == 'GET':
        return render_template("/adminlogin.html")
    msg = ""
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username != "admin" or password != "admin":
            msg = "Not an Admin"
            return render_template('/adminlogin.html', message=msg, category="danger")
        msg = "Sucessfully logged in as admin"
        return redirect(url_for('.inventory'))
    


@app.route("/inventory")
def inventory():
    return render_template("/inventory.html")


@app.route('/logout')
def logout():
    clearcart()
    session.pop('loggedin', None)

    session.pop('username', None)
    
    
    return redirect(url_for('login'))

# Controllers for Inventory Management


@app.route("/addsection", methods=["POST", "GET"])
def addsection():
    if request.method == "GET":

        return render_template("/addsection.html")

    if request.method == "POST":
        sectionname = request.form['section']
        info = db.session.query(Category).filter(
            Category.name == sectionname).first()
        if info != None:
            return render_template("/addsection.html", message="Category already exists", category="danger")
        section = Category(name=sectionname)
        db.session.add(section)
        db.session.commit()
        return render_template("/inventory.html", message="Category added successfully", category="success")


@app.route("/addproduct", methods=["POST", "GET"])
def addproduct():
    inf =showcategory()
    ms = ["Kg", "L", "Dozen", "Unit"]
    if request.method == "GET":

        return render_template("/addproduct.html", inf=inf, ms=ms)
    if request.method == "POST":

        category = db.session.query(Category).filter(
            Category.name == request.form.get("category")).first()
        cat_id = category.id
        item = Product(name=request.form['name'], price=request.form['price'], expdate=request.form['expdate'],
                       quantity=request.form['quantity'], ms=request.form.get("ms"), category_id=cat_id,desc=request.form['desc'])
        db.session.add(item)
        db.session.commit()
        return render_template("/inventory.html", message=(request.form['name'])+" added successfully", category="success")



@app.route("/removesection", methods=["POST", "GET"])
def removesection():

    if request.method == "GET":
        inf = db.session.query(Category).all()

        return render_template("/removesection.html", inf=inf)
    if request.method == "POST":
        sel = request.form.get("remove")
        

        cat = Category.query.filter_by(name=sel).first()
        for product in cat.c_item:
            db.session.delete(product)
        
        db.session.delete(cat)
        db.session.commit()
        inf = Category.query.all()
        cat = ""
        return render_template("/inventory.html", message="Category removed sucessfully", category="success")


@app.route("/removeproduct", methods=["POST", "GET"])
def removeproduct():
    if request.method == "GET":
        products = showproducts()

        return render_template("/removeproduct.html", products=products)


@app.route('/<int:id>/delete/', methods=['GET'])
def delete(id):

    stud = Product.query.filter_by(id=id).first()
    stud.section.c_item.remove(stud)
    stud.users=[]
    db.session.delete(stud)
    db.session.commit()
    return redirect("/removeproduct")


@app.route('/<int:id>/update', methods=['GET', 'POST'])
def update(id):
    item = Product.query.filter_by(id=id).first()
    if request.method == "GET":

        return render_template('update.html', item=item)
    if request.method == "POST":
        item.price = request.form['price']
        item.quantity = request.form['quantity']
        db.session.commit()
        return redirect("/removeproduct")


@app.route('/<int:id>/addtocart', methods=["GET"])
def addtocart(id):
    if request.method == "GET":
        a = Product.query.filter(Product.id == id).first()
        addcart(a)
        return redirect("/")



@app.route('/<int:id>/buyproduct', methods=['GET', 'POST'])
def buyproduct(id):

    if request.method == "GET":
        a = Product.query.filter(Product.id == id).first()
        return render_template("/buyproduct.html", item=a)
    if request.method == "POST":

        u = db.session.query(User).filter(
            User.username == session['username']).first()

        q = int(request.form['quantity'])

        a = db.session.query(Product).filter(Product.id == id).first()
        if(a.quantity==0):
             return render_template("/buyproduct.html", item=a,message=""+ a.name +"Sorry for Inconvenience Out Of Stock",category="danger")

        if((a.quantity-q)<0):
            return render_template("/buyproduct.html", item=a,message="Sorry for Inconvenience PLease select less no of products",category="danger")
        a.quantity -= q
    
        l = User_product(user_id=u.id, product_id=id)

        db.session.add(l)
        db.session.commit()

        return redirect("/showcart")


@app.route("/showcart", methods=["GET"])
def cart():
    if request.method == "GET":
        h = showcart()

        return render_template("/cart.html", products=h)



@app.route("/search")
def search():
    query = request.args.get('search')
    q = "%"+query+"%"
    products = Product.query.filter(
        or_(Product.name.like(q), Product.price.like(q))).all()
    print(products)
    categories = showcategory()
    return render_template("search.html", products=products, categories=categories)



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)

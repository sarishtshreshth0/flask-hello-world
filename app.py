from flask import Flask, render_template, request ,session , redirect , url_for
from flask_mail import Mail, Message
import random
from datetime import date
today = date.today().strftime("%Y-%m-%d")
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as bs
import random
import time
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
uri = "mongodb+srv://sarishtshreshth:openforall@cluster0.sf3lhpf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
app = Flask(__name__)
app.secret_key = "securemore"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'saristhshreshth12@gmail.com'
app.config['MAIL_PASSWORD'] = "emyx zmzd afjf keqh"
app.config['MAIL_DEFAULT_SENDER'] = 'saristhshreshth12@gmail.com'
mail = Mail(app)

db = client['ecommerce']
db_user = db['user']
db_otp = db['otp']
db_contact = db['contact']
db_product = db['product']
db_cart = db['cart']
db_wishlist = db['wishlist']
@app.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method == "POST" :
        email = request.form['email']
        password = request.form['password']
        if email and password:
            check = db_user.find_one({"email":email, "password":password})
            if check:
                session['username'] = email
                return redirect("/")
            else:
                return redirect("/login")
        else:
            return redirect("/login")
    else:
        return render_template("login.html")
@app.route('/signup',methods = ['GET', 'POST'])
def signup():
    if request.method == "POST" :
        first = request.form['first']
        session['name'] = first
        last = request.form['last']
        m_number = request.form['m_number']
        email = request.form['email']
        session['email'] = email
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if email and password and first and last and confirm_password:
            db_user.insert_one({"first": first, "last": last, "m_number" :m_number , "email":email, "password":password, "confirm_password":confirm_password})
            return redirect("/verify")
        else:
            return redirect("/signup")
    else:
        return render_template("signup.html")


@app.route('/logout',methods = ['GET', 'POST'])
def logout():
    session.pop("username", None)
    return redirect("/login")

def send_otp():
    random_number = random.randint(1000, 9999)
    session['otp'] = str(random_number)
    db_otp.insert_one({"otp": str(random_number)})
    send_mail(random_number)
    return random_number

def send_mail(stored_otp):
    msg = Message(
        subject="Ecommerce Project",
        recipients=[session['email']],
        body= "your otp is " + str(stored_otp)
    )
    mail.send(msg)
    return "Mail sent!"

@app.route("/verify", methods=['GET', 'POST'])
def verify():
    if request.method == "POST":
        v1 = request.form.get('v1', '')
        v2 = request.form.get('v2', '')
        v3 = request.form.get('v3', '')
        v4 = request.form.get('v4', '')

        entered_otp = int(v1 + v2 + v3 + v4)
        stored_otp = int(session.get('otp', 0))

        print("Stored OTP:", stored_otp)
        print("Entered OTP:", entered_otp)
        if entered_otp == stored_otp:
            return redirect("/login")
        else:
            return redirect("/signup")

    result = send_otp()
    print("Generated OTP:", result)
    return render_template("verify_otp.html")

@app.route("/reset-password", methods=['GET', 'POST'])
def reset_password():
    return render_template("reset_password.html")

@app.route("/",methods = ['GET', 'POST'])
def home():
    name = db_user.find_one({"email":session.get('username')})
    if name:
        name = name["first"].title()
    else:
        name = "Login"
    session['name'] = name
    return render_template("index.html",name = name)

@app.route("/contact",methods = ['GET', 'POST'])
def contact():
    if request.method == "POST":
        message = request.form['message']
        msg = Message(
            subject="Ecommerce Project",
            recipients=[session['username']],
            body= message
        )
        mail.send(msg)
        db_contact.insert_one({"Id": session['username'],"issue": message ,"status": 'Pending', "raiseBy":session.get('name') , 'date' : today})
        return redirect("/ticketraise")
    name = session.get('name', 'Login')
    email = session.get('username', "Login")
    return render_template("contact_us.html",name = name , email = email)

@app.route("/ticketraise",methods = ['GET', 'POST'])
def ticket():
    Id = db_contact.count_documents({})
    return render_template("ticket_raised.html" , Id = Id)

@app.route("/raisedlist",methods = ['GET', 'POST'])
def listraised():
    list_raised = [i for i in db_contact.find({"Id":session.get('username')})]
    return render_template("show_raised.html" , raised = list_raised)

@app.route("/address",methods = ['GET', 'POST'])
def address():
    return render_template("manage_address.html")

@app.route("/setting", methods=['GET', 'POST'])
def setting():
    if session.get('username') is None:
        return redirect("/login")

    email = session.get('username')
    data = db_user.find_one({"email": email})

    if request.method == "POST" and "edit_mode" in request.form:
        return render_template(
            "Profile_setting.html",
            first=data["first"].title(),
            last=data["last"].title(),
            gender=data.get("gender", ""),
            email=email,
            m_number=data["m_number"],
            edit_mode=True
        )


    if request.method == "POST" and "save_mode" in request.form:
        new_first = request.form['first_name'].strip().title()
        new_last = request.form['last_name'].strip().title()
        new_m_number = request.form['m_number'].strip()
        new_gender = request.form.get('gender', '')
        # Update database
        db_user.update_one(
            {"email": email},
            {"$set": {
                "first": new_first,
                "last": new_last,
                "m_number": new_m_number,
                "gender": new_gender
            }}
        )

        return redirect("/setting")

    return render_template(
        "Profile_setting.html",
        first=data["first"].title(),
        last=data["last"].title(),
        gender=data.get("gender", ""),
        email=email,
        m_number=data["m_number"],
        edit_mode=False
    )

@app.route("/order",methods = ['GET', 'POST'])
def order():

    return render_template("orderpage.html")

@app.route("/mobile",methods = ['GET', 'POST'])
def product_list():
    product = [i for i in db_product.find()]
    return render_template("product_list_phone.html", products = product)




@app.route("/searched", methods=['GET', 'POST'])
def searched():
    search = request.args.get('query')
    pages = 2
    product = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for page in range(1, pages):
        url = f"https://www.flipkart.com/search?q={search}&page={page}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            continue

        html_box = bs(response.text, 'html.parser')
        classes = ['gqcSqV YGE0gZ', "_4WELSP WH5SS-", "_4WELSP"]
        follow = None

        for class_name in classes:
            follow = html_box.find_all('div', {'class': class_name})
            if follow:
                break

        for item in follow:
            try:
                product.append({'image': item.img['src'], 'desc': item.img['alt']})
            except AttributeError:
                continue

    return render_template("searched.html", products=product)
@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    if 'username' not in session:
        return redirect(url_for("login"))
    username = session['username']
    product_id = request.form.get("product_id")
    product_name = request.form.get("product_name")
    product_price = request.form.get("product_price")
    product_image = request.form.get("product_image")
    existing_item = db_cart.find_one({"username": username, "product_id": product_id})
    if existing_item:
        db_cart.update_one({"username": username, "product_id": product_id}, {"$inc": {"quantity": 1}})
    else:
        db_cart.insert_one({
            "username": username,
            "product_id": product_id,
            "name": product_name,
            "price": product_price,
            "image_url": product_image,
            "quantity": 1
        })
    return redirect(url_for("product_list"))

@app.route("/cart", methods=['GET', 'POST'])
def cart():
    if 'username' not in session:
        return redirect("/login")
    username = session['username']
    if request.method == "POST":
        action = request.form.get("action")
        product_id = request.form.get("product_id")
        if action == "remove":
            db_cart.delete_one({"username": username, "product_id": product_id})
        elif action == "increase":
            db_cart.update_one({"username": username, "product_id": product_id}, {"$inc": {"quantity": 1}})
        elif action == "decrease":
            cart_item = db_cart.find_one({"username": username, "product_id": product_id})
            if cart_item and cart_item["quantity"] > 1:
                db_cart.update_one({"username": username, "product_id": product_id}, {"$inc": {"quantity": -1}})
            else:
                db_cart.delete_one({"username": username, "product_id": product_id})
        return redirect(url_for("cart"))
    cart_items = list(db_cart.find({"username": username}))
    return render_template("cart.html", cart_items=cart_items)

@app.route("/add_to_wishlist", methods=['POST'])
def add_to_wishlist():
    if 'username' not in session:
        return redirect(url_for("login"))
    username = session['username']
    product_id = request.form.get("product_id")
    product_name = request.form.get("product_name")
    product_price = request.form.get("product_price")
    product_image = request.form.get("product_image")
    existing_item = db_wishlist.find_one({"username": username, "product_id": product_id})
    if existing_item:
        db_wishlist.update_one({"username": username, "product_id": product_id})
    else:
        db_wishlist.insert_one({
            "username": username,
            "product_id": product_id,
            "name": product_name,
            "price": product_price,
            "image_url": product_image
        })
    return redirect(url_for("product_list"))


@app.route("/wishlist", methods=['GET', 'POST'])
def wishlist():
    if 'username' not in session:
        return redirect("/login")
    username = session['username']
    if request.method == "POST":
        action = request.form.get("action")
        product_id = request.form.get("product_id")
        if action == "remove":
            db_wishlist.delete_one({"username": username, "product_id": product_id})
        return redirect(url_for("wishlist"))
    db_wishlist_items = list(db_wishlist.find({"username": username}))
    return render_template("wishlist.html", wishlist_items=db_wishlist_items)


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request,redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
from database import get_db_connection
app=Flask(__name__)
app.secret_key="dev_secret_key"
@app.route("/")
def home():
    return "Secure Login Project is Running"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)
        totp_secret = pyotp.random_base32()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password, totp_secret) VALUES (%s, %s, %s)",
                (email, hashed_password, totp_secret)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return "Registration successful"

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        conn=get_db_connection()
        cursor=conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user=cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"],password):
            session["temp_user_id"]=user["id"]
            return "password verified. Proceed to OTP."
        
        return "Invalid email or password"
    
    return render_template("login.html")

if __name__=="__main__":
    app.run(debug=True)
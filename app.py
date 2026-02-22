from flask import Flask, render_template, request,redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import random
from datetime import datetime, timedelta
from email_utils import send_otp_email
from database import get_db_connection
app=Flask(__name__)
app.secret_key="dev_secret_key"
@app.route("/")
def home():
    return "Secure Login Project is Running"


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not password or not confirm_password:
            return "All fields are required"

        if password != confirm_password:
            return "Passwords do not match"

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (email, hashed_password)
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return f"Registration error: {e}"

        conn.close()
        return "Registration successful"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return "Email and password required"

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return "User not found"

        # 🔍 DEBUG LINE (IMPORTANT)
        print("DEBUG → Entered password:", password)
        print("DEBUG → Stored hash:", user["password"])

        if not check_password_hash(user["password"], password):
            return "Invalid email or password"

        # ---- OTP GENERATION ----
        otp = str(random.randint(100000, 999999))
        expiry=datetime.now()+timedelta(minutes=5)
        conn=get_db_connection()
        cursor=conn.cursor()
        cursor.execute(
            "UPDATE users SET email_otp=%s, otp_expiry=%s WHERE id=%s",
            (otp,expiry,user["id"])
        )
        conn.commit()
        conn.close()

        send_otp_email(user["email"], otp)

        session["temp_user_id"]=user["id"]  
        
        return redirect(url_for("otp"))

    return render_template("login.html")

@app.route("/otp", methods=["GET", "POST"])
def otp():
    if "temp_user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        otp_input = request.form.get("otp")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT email_otp, otp_expiry FROM users WHERE id=%s",
            (session["temp_user_id"],)
        )
        user = cursor.fetchone()
        conn.close()

        if not user or not user["email_otp"] or not user["otp_expiry"]:
            return "OTP expired. Please login again."

        if user["otp_expiry"] < datetime.now():
            return "OTP expired. Please login again."

        if otp_input != user["email_otp"]:
            return "Invalid OTP"

        # ✅ SUCCESS
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET email_otp=NULL, otp_expiry=NULL WHERE id=%s",
            (session["temp_user_id"],)
        )
        conn.commit()
        conn.close()

        session.pop("temp_user_id")
        session["user_logged_in"] = True
        return redirect(url_for("dashboard"))

    return render_template("otp.html")

if __name__=="__main__":
    app.run(debug=True)
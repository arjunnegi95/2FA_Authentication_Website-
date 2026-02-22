from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash
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
if __name__=="__main__":
    app.run(debug=True)
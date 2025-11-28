from flask import Flask, request, render_template, redirect, make_response

app = Flask(__name__)

USERS = {
    "admin": "admin123"
}

PRODUCT = {
    "name": "Super Gadget",
    "price": 199
}

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    user = request.form.get("username")
    password = request.form.get("password")

    if USERS.get(user) == password:
        resp = make_response(redirect("/admin"))
        # VULNERABLE: session management by insecure cookie
        resp.set_cookie("session_user", user)
        return resp

    return "Invalid credentials"

@app.route("/admin")
def admin():
    session_user = request.cookies.get("session_user")

    if session_user != "admin":
        return "Unauthorized"

    return render_template("admin.html", product=PRODUCT)

@app.route("/update_price", methods=["POST"])
def update_price():
    # VULNERABLE:
    #  - No CSRF token
    #  - Accepts any POST from any origin
    #  - No SameSite cookie protection

    session_user = request.cookies.get("session_user")
    if session_user != "admin":
        return "Unauthorized"

    new_price = request.form.get("price")
    if not new_price:
        return "Missing price"

    PRODUCT["price"] = int(new_price)

    return render_template("success.html", product=PRODUCT)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=False)

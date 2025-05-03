import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
import datetime

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    init_total = 10000
    transactions_db = db.execute("SELECT symbol, SUM(shares) as shares, price, SUM(shares * price) as TOTAL FROM transactions where user_id = ? GROUP BY symbol", user_id)
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]

    return render_template("index.html", database=transactions_db, cash=cash, total = init_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")

        if not symbol:
            return apology("Must give symbol!")

        stock = lookup(symbol)

        if stock == None:
            return apology("Symbol does not exist.")

        if not request.form.get("shares"):
            return apology("Must give share(s)!")

        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("shares must be a postive integer", 400)

        if shares <= 0:
            return apology("Shares must be a positive integer.", 400)

        transaction_value = shares * stock["price"]

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        if user_cash < transaction_value:
            return apology("Not Enough Money")
        uptd_cash = user_cash - transaction_value

        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        date = datetime.datetime.now()

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], shares, stock["price"], date)

        flash(f"Bought {shares} of {symbol} for {usd(transaction_value)}, Updated cash: {usd(uptd_cash)}")

        # redirect user to the homepage
        return redirect("/")
    else:
        return render_template("buy.html")
    # return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    transaction_db = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    return render_template("history.html", transactions = transaction_db)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        Symbol = request.form.get("symbol")

        if not Symbol:
            return apology("Must give symbol")

        stock = lookup(Symbol)

        if stock == None:
            return apology("Symbol does not exist")
        return render_template("quoted.html", price = stock["price"], symbol = stock["symbol"])

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        name = request.form.get("username")
        if not name:
            return apology("must provide username", 400)
        # Ensure username was unique
        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", name
        )

        # Render apology when username already existed
        if len(rows) == 1:
            return apology("This username was already taken", 400)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)
        # Render apology when the passwords don't match
        if password != request.form.get("confirmation"):
            return apology("Passwords do not match", 400)

        hashed_pwd = generate_password_hash(password)
        db.execute("INSERT INTO users(username, hash) VALUES (?, ?)", name, hashed_pwd)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("registration.html")
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        user_id = session["user_id"]
        symbols_user = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("sell.html", symbols=[row["symbol"] for row in symbols_user])
    else:
        symbol = request.form.get("symbol")
        try:
            shares = int(request.form.get("shares"))
        except ValueError:
            return apology("Must be a positive integer!", 400)

        if shares <= 0:
            return apology("Shares must be a positive integer", 400)

        if not symbol:
            return apology("Must give symbol!")

        stock = lookup(symbol)

        if stock == None:
            return apology("Symbol does not exist!")


        transaction_value = shares * stock["price"]

        user_id = session["user_id"]
        user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        user_cash = user_cash_db[0]["cash"]

        user_shares = db.execute("SELECT SUM(shares) as shares FROM transactions WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)
        user_shares_real = user_shares[0]["shares"]

        if shares > user_shares_real:
            return apology("You do not have this amount of shares")

        uptd_cash = user_cash + transaction_value

        db.execute("UPDATE users SET cash = ? WHERE id = ?", uptd_cash, user_id)

        date = datetime.datetime.now()

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], (-1)*shares, stock["price"], date)

        flash(f"Sell {shares} of {symbol} for {usd(transaction_value)}, Updated cash: {usd(uptd_cash)}")

        return redirect("/")

# personal touch
@app.route("/changePassword", methods = ["GET", "POST"])
@login_required
def changePassword():
    """Allow users to change their password"""
    if request.method == "POST":
        curr_passwd = request.form.get("current_password")
        new_passwd = request.form.get("new_password")
        confirm_new_passwd = request.form.get("confirm_new_password")

        if not curr_passwd:
            return apology("Must input your current password!")

        old_passwd = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        # Ensure the query returns exactly one result
        # Check whether the current password is correct or not
        if len(old_passwd) != 1 or not check_password_hash(old_passwd[0]["hash"], curr_passwd):
            return apology("Invalid user and/or password", 403)

        if not new_passwd:
            return apology("Must input your new password")
        if not confirm_new_passwd:
            return apology("Must confirm your new password")
        if new_passwd != confirm_new_passwd:
            return apology("Password does not match!")

        # Update the new password
        hashed_new_passwd = generate_password_hash(new_passwd)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hashed_new_passwd, session["user_id"])

        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    else:
        return render_template("changePassword.html")

@app.route("/addCash", methods=["POST", "GET"])
@login_required
def addCash():
    user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    user_cash = user_cash_db[0]["cash"]

    if request.method == "GET":
        return render_template("addCash.html", user_cash = user_cash)
    try:
        cash = int(request.form.get("cash"))
    except ValueError:
        return apology("If you don't want more money go away then!")

    if (cash <= 0):
        return apology("Are you sure?", 400)
    total_cash = cash + user_cash


    if total_cash > 10000:
        return apology("Don't be greedy! Your maximum money is 10000")
    else:
        db.execute("UPDATE users SET cash = ? WHERE id = ?", total_cash, session["user_id"])
        flash("Moolah Molahhhh MOREEEEE Moolahhh")
    return render_template("addCash.html", user_cash = total_cash)


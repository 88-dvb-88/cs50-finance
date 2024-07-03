import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

import datetime
import pytz

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


    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        #Ensure symbole is not blank
        if not symbol or not shares:
            return apology("Please, fill in the blanks", 400)

        stock = lookup(symbol)

        if not stock:
            return apology("Must provide valid stock symbol", 400)

        try:
            int_shares = int(shares)
            if int_shares <= 0:
                return apology("A positive integer must be inserted for the shares")
        except:
                    return apology("Insert a valid number for the shares")

        total_amount = float(stock["price"]) * int_shares

        # Get user ID and available cash from session
        user_id = session.get("user_id")
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        cash = float(user[0]["cash"])
        if cash < total_amount:
            return apology("Insufficient funds")

        # Check when the purchase has been done
        purchase_date = datetime.datetime.now(pytz.timezone("US/Eastern"))

        # Insert transaction record
        db.execute("CREATE TABLE transactions(user_id TEXT, symbol TEXT, shares INTERGER, total_shares INTERGER, price FLOAT, purchase_date DATE)")
        db.execute("INSERT INTO transactions(user_id,symbol,shares,price,purchase_date) VALUES (?,?,?,?,?)",
                   user_id, stock["symbol"], shares, total_amount, purchase_date,
                       )

         # Check if the stock is already in the portfolio
        db.execute("CREATE TABLE portfolio (user_id TEXT, symbol TEXT, price FLOAT, total_shares INTERGER)")
        db.execute("SELECT symbol FROM portfolio WHERE user_id = ? AND symbol = ?",
                        user_id,
                        symbol,
                    )

        #UPDATE or INSERT portfolio record
        if len(row) != 1:
            db.execute("INSERT INTO portfolio(user_id,symbol,total_shares VALUES (?,?,?,?)",
                            user_id,
                            symbol,

                            shares,
                        )

        else:
            row = db.execute(
                "SELECT total_shares FROM portfolio WHERE user_id = ? AND symbol = ?",
                            user_id,
                            symbol,
                        )
        old_shares = row[0]["total_shares"]
        new_shares = old_shares + int(shares)
        db.execute(
             "UPDATE portfolio SET total_shares = ? WHERE user_id = ? AND symbol = ?",
                            new_shares,
                            user_id,
                            symbol,
                            )

        #UPDATE user's cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                            cash,
                            user_id
                        )
                        # Flash success message and redirect to homepage
        flash(f"Bought {shares} shares of {symbol} for {usd(total_amount)}!")
        return redirect("/")


    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

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

     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        # Ensure symbol is not blank
        if symbol == "":
            return apology("Please enter a symbol", 400)

        stock_quote = lookup(symbol)

        if not stock_quote:
            return apology("INVALID SYMBOL", 400)
        else:
            return render_template("quoted.html", symbol=stock_quote)

    # User reached route via GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Validate submission
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Query database for newly inserted user
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure password confirmation
        if not (password == confirmation):
            return apology("the passwords do not match", 400)

        # Ensure password not blank
        if password == "" or confirmation == "" or username == "":
            return apology("This field is required", 400)

        # Ensure username does not exists already
        if len(rows) == 1:
            return apology("username already exist", 400)
        else:
            hashcode = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hashcode)

        # Redirect user to home page
        return redirect("/")
        # User reached route via GET (likely for displaying the registration form)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")

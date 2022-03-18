
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///classroom.db")


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


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
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # selecting all roles from database
        roles = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])

        # Redirect student user to student page
        if roles[0]["role"] == "student":
             return render_template("student.html")
        # Redirect teacher user to teacher page
        elif roles[0]["role"] == "teacher":
            return render_template("teacher.html")
        # Otherwise, redirect to login page
        else: 
            return render_template("login.html")
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        print("Submitted")
        # Ensure username was submitted
        if not request.form.get("username"):
           return apology("must provide username", 400)
        
        #Selecting all usernames into rowws
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        
        # Ensure username does not already exist
        if len(rows) == 1:
            return apology("Username already exists", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        choice = request.form.get("choice")
        classroomcode = request.form.get("classroomcode")

        # Ensure passwords match
        if password != confirmation:
            return apology("Passwords do not match", 400)
        
        # Ensure classroom code is inputted correctly
        if classroomcode != '3GR25Y' and choice == "student":
            return apology("Classroom code not found")
        try:
            db.execute("INSERT INTO users(username, hash, role) VALUES(?, ?, ?)", username, generate_password_hash(password), choice)
        finally: 
            return redirect("/login")
    else:
        return render_template("register.html")


@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/student", methods=["GET", "POST"])
def student():
    # If the "Submit a Link!" button is clicked:
    if request.method == "POST":
        # Get and store the inputted URL link 
        urllink = request.form.get("url").lower().strip()
        current_urls = [x["uploads"] for x in db.execute("SELECT uploads FROM uploads")]
        # If the inputted url link exists and is unique, store it in the uploads table
        if urllink and urllink not in current_urls:
            db.execute("INSERT INTO uploads(uploads) VALUES(?)", urllink)
        # Load the student page with all existing teacher concepts and student uploads displayed on the page
        concepts = db.execute("SELECT concept FROM concepts")
        uploads = db.execute("SELECT uploads FROM uploads")
        return render_template("student.html", concepts=concepts, uploads=uploads)
    # Automatically load the student page with any existing teacher concepts displayed on the page
    else:
        concepts = db.execute("SELECT concept FROM concepts")
        return render_template("student.html", concepts=concepts)
    

@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    # If the "Add" button is clicked:
    if request.method == "POST":
        # Get and store the inputted concept
        conceptvalue = request.form.get("concept").lower().strip()
        current_concepts = [x["concept"] for x in db.execute("SELECT concept FROM concepts")]
        # If the inputted concept exists and is unique, store it in the concepts table
        if conceptvalue and conceptvalue not in current_concepts:
            db.execute("INSERT INTO concepts(concept) VALUES(?)", conceptvalue)
        # Load the teacher page with all existing teacher concepts and student uploads displayed on the page
        concepts = db.execute("SELECT concept FROM concepts")
        uploads = db.execute("SELECT uploads FROM uploads")
        return render_template("teacher.html", uploads=uploads, concepts=concepts)
     # Automatically load the teacher page with any existing student uploads displayed on the page
    else:
        uploads = db.execute("SELECT uploads FROM uploads")
        return render_template("teacher.html", uploads=uploads)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

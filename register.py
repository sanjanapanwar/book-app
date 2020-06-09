import os
from sqlalchemy import create_engine
from flask import Flask, render_template, request, url_for, session
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__, static_url_path='/static')
engine = create_engine("postgresql:///cs50project1")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if(username == "" and password == ""):
        return render_template("login.html")
    db.execute("""INSERT INTO bookuser(username,password) 
                    VALUES(:username,:password)""",
               {
                   "username": username,
                   "password": password
               })
    db.commit()

    return render_template("search.html")


@app.route("/login", methods=["POST"])
def login():

    username = str(request.form.get("username"))
    password = str(request.form.get("password"))
    username1 = db.execute("""SELECT username FROM bookuser
                                    WHERE password=:password""",
                           {
                               "password": password
                           }).fetchone()

    password1 = db.execute("""SELECT password FROM bookuser
                                WHERE username=:username""",
                           {
                               "username": username
                           }).fetchone()

    if(username == "" or password == ""):
        return render_template("error.html", message="""Username or password can't be empty!
                                                            Please enter a valid username or password""")
    elif(username1 == (username,) and password1 == (password,)):
        return render_template("search.html")
    elif(username1 != (username,) or password1 != (password,)):
        return render_template("error.html", message="Your username or password is incorrect")
    else:
        return render_template("error.html",
                               message="""You are not logged in! 
                                            Please create a new account!""",
                               username1=username1,
                               password1=password1,
                               username=username,
                               password=password)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("book")
    if query == "":
        return render_template("error.html",
                               message="""Please enter title,author or isbn ,
                                            then only you are able to search""")

    query = "%"+request.form.get("book")+"%"
    query = query.title()
    book = db.execute("""SELECT * FROM book WHERE title LIKE :query or
                isbn LIKE :query or author LIKE :query""",
                      {
                          "query": query
                      }).fetchall()

    return render_template("Book.html", book=book)


@app.route('/book/<isbn>', methods=["GET", "POST"])
def book(isbn):
    book = db.execute("SELECT * from book WHERE  isbn=:isbn",
                      {"isbn": isbn}).fetchall()
    if book.rowcount == 0:
        return render_template("error.html",
                               message="SORRY! No such book in description")

    return render_template("details.html", book=book)


@app.route("/logout", methods=["POST"])
def logout():
    return render_template("register2.html")

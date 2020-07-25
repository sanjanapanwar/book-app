import os
import psycopg2
from sqlalchemy import create_engine
from flask_session import Session
from flask import Flask, render_template, request, url_for, session,redirect,flash
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__, static_url_path='/static')

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine("postgresql:///cs50project1")
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/register1")
def register1():
    return render_template("register2.html")
@app.route("/login1")
def login1():
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
   
    session["user_name"]=str(username)
    if(username == "" and password == ""):
        return render_template("login.html")
    db.execute("""INSERT INTO bookuser(username,password) 
                    VALUES(:username,:password)""",
               {
                   "username": username,
                   "password": password
               })
    db.commit()

    return render_template("search.html",username=username)


@app.route("/login", methods=["GET","POST"])
def login():
    
    session.clear()

    username = str(request.form.get("username"))
    password = str(request.form.get("password"))
    
    username1 = db.execute("""SELECT username FROM bookuser
                                    WHERE username=:username""",
                           {
                               "username":username
                           }).fetchone()

    password1 = db.execute("""SELECT password FROM bookuser
                                WHERE username=:username""",
                           {
                               "username":username
                           }).fetchone()
     
    session["user_name"]=str(username)

  

    if(username == "" or password == ""):
        return render_template("error.html", message="""Username or password can't be empty!
                                                            Please enter a valid username or password""")
    
    elif(username1 == (username,) and password1 == (password,)):
        return render_template("search.html",username=username)
    elif(username1 != (username,) or password1 != (password,)):
        return render_template("error.html", message="Your username or password is incorrect")
    elif(username!=username1):
        return render_template("error.html",message="you are not logged in,please signup first!")
    else:
        return render_template("error.html",
                               message="""You are not logged in! 
                                            Please create a new account!""")


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
                      })
    if book.rowcount==0:
        return render_template("error.html",message="No such book in description",book=book)

    return render_template("Book.html", book=book)


@app.route('/book/<isbn>', methods=["GET", "POST"])
def book(isbn):
    
    if request.method=="POST":
        username=session["user_name"]
        ratings=request.form.get("ratings")
        comments=request.form.get("comments")

    
        book_id=db.execute("select * from book where isbn=:isbn",{"isbn":isbn}).fetchone()
        book_id=int(book_id[0])

        review1=db.execute("select * from reviews where bookuser_id=:bookuser_id and book_id=:book_id",{"bookuser_id":username,"book_id":book_id})

        


        if review1.rowcount==1:
            flash("you have already submitted your review",'warning')
            return redirect("/book/"+isbn)
         
        ratings=int(ratings)

        
        db.execute("INSERT INTO reviews (book_id,bookuser_id,comments,ratings) VALUES(:book_id,:bookuser_id,:comments,:ratings)",{"book_id":book_id,"bookuser_id":username,"comments":comments,"ratings":ratings})
        db.commit()
      

        
        return redirect("/book/"+isbn)
    
    else:
        
        book_id=db.execute("select * from book where isbn=:isbn",{"isbn":isbn}).fetchone()
        book_id=int(book_id[0])
        book=db.execute("select * from book where isbn=:isbn",{"isbn":isbn}).fetchall()
        review=db.execute("select * from reviews where book_id=:book_id",{"book_id":book_id}).fetchall()

        return render_template("details.html",book=book,review=review)

       
    

       
@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return render_template("home.html")

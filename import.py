import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql:///cs50project1")
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("/home/sanjana/Downloads/project1/books.csv", "r")
    reader = csv.reader(f)
    next(reader)
    for isbn, title, author, year in reader:
        db.execute("""INSERT INTO book (isbn,title,author,year) 
                        VALUES (:isbn,:title,:author,:year)""",
                   {
                       "isbn": isbn,
                       "title": title,
                       "author": author,
                       "year": year
                   })
        db.commit()
        print(
            f"Added book with ISBN:{isbn} Title:{title} Author:{author} Year:{year}")


if __name__ == "__main__":
    main()

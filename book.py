# using flask to build CRUD application with flask and SQLAlchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)  # initialize flask app

# root: is the password
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:8889/book'
# this retrieves the variable dbURL from the curr environment
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # initialize a connection to datatbase
# Cross-Origin Resource Sharing (CORS)
CORS(app)

# new class book, inherit from a basic database model provided by SQLAlchemy
# this also make SQLAlchemy create a table called book if run the db.create_all() function


class Book(db.Model):
    __tablename__ = 'book'

    # specify attributes of books
    isbn13 = db.Column(db.String(13), primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    availability = db.Column(db.Integer)

    # initialize attributes
    def __init__(self, isbn13, title, price, availability):
        self.isbn13 = isbn13
        self.title = title
        self.price = price
        self.availability = availability

    # specify how to represent our book obj as a JSON string
    def json(self):
        return {"isbn13": self.isbn13, "title": self.title, "price": self.price, "availability": self.availability}


# https://127.0.0.1:5000/book


# use flask's app.route decorator to map the URL route /book to function get_all
# by default without specifying = GET method
@app.route("/book")
def get_all():
    booklist = Book.query.all()  # this is a query attribute of SQLAlchemy, returns a list

    if len(booklist):  # if not empty
        return jsonify(  # iteration and create JSON rep of using book.json()
            {
                "code": 200,
                "data": {
                    "books": [book.json() for book in booklist]  # iteration
                }
            }
        )
    return jsonify(  # instead of returning 404 NOT FOUND, this message will show
        {
            "code": 404,
            "message": "There are no books"
        }
    ), 404

# finding a specific book


@app.route("/book/<string:isbn13>")
def find_by_isbn13(isbn13):
    # retrieve only book with isbn13, as it returns a list of 1 book,
    # first() return one book or none if no matching book
    book = Book.query.filter_by(isbn13=isbn13).first()
    if book:
        return jsonify(
            {
                "code": 200,
                "data": book.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Book not found."
        }
    ), 404


@app.route("/book/<string:isbn13>", methods=['POST'])
def create_book(isbn13):
    if (Book.query.filter_by(isbn13=isbn13).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "isbn13": isbn13
                },
                "message": "Book already exists."
            }
        ), 400

    data = request.get_json()
    book = Book(isbn13, **data)

    try:
        db.session.add(book)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "isbn13": isbn13
                },
                "message": "An error occurred creating the book."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": book.json()
        }
    ), 201


# this ensures that we dont start up the web server if we import this script in another one
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


# export dbURL=mysql+mysqlconnector://root:root@localhost:3306/book

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy   
from flask_marshmallow import Marshmallow
from flask_cors import CORS    
from flask_heroku import Heroku
from flask_bcrypt import Bcrypt  

import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]='postgres://ghzjwktpsdrtmt:068b66b7d6c673626d92d090c4ecb7fc1ee73c28f7e49f5774b2589ef1ce4018@ec2-52-21-247-176.compute-1.amazonaws.com:5432/dcl0tk6vat7cuc'

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)


Heroku(app)
CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields=("id", "email", "password")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)

class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    people = db.Column(db.String, nullable=True)
    title = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=False, unique=True)
    date = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=True)

    def __init__(self, people, title, description, date, location):
        self.people = people
        self.title = title
        self.description = description
        self.date = date
        self.location = location

class JournalSchema(ma.Schema):
    class Meta: 
        feilds = ("id", "people", "title", "description", "date", "location")

journal_schema = JournalSchema()
multiple_journal_schema = JournalSchema(many=True)      

@app.route("/user/add", methods=["POST"])
def create_user():
    if request.content_type != "application/json":
        return "JSON is needed"

    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password")

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    record = User(email, password_hash)
    db.session.add(record)
    db.session.commit()

    return jsonify("User added successfully")

@app.route("/journal/add", methods=["POST"])
def create_journal():
    if request.content_type !="application/json":
        return "JSON required"

    post_data = request.get_json()
    people = post_data.get("people")
    title = post_data.get("title")
    description = post_data.get("description")
    date = post_data.get("date")
    location = post_data.get("location")

    record = Journal(people, title, description, date, location)
    db.session.add(record)
    db.session.commit()

    return jsonify("Data added successfully")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User.email, User.password).all()
    return jsonify(multiple_user_schema.dump(all_users))


@app.route("/user/get/<email>", methods=["GET"])
def get_one_user(email):
    one_user = db.session.query(User).filter(User.email == email).first()
    return jsonify(user_schema.dump(one_user))

@app.route("/user/journal/<email>/<journal_title>", methods=["GET"])
def get_one_users_journal(email, journal_title):
    user = db.session.query(User).filter(User.email == user_email).first()
    journal = db.session.query(Journal).filter(Journal.title == journal_title).first()
    result = [user_schema.dump(user), journal_schema.dump(journal)]
    return jsonify(result)

@app.route("/user/delete/<user>", methods=["DELETE"])
def delete_user_journal_by_id(id):
    record = db.session.query(User).filter(User.email == email).first()
    if record is None:
        return jsonify("User does not exist")

@app.route("/journal/get", methods=["GET"])
def get_all_journals():
    all_books = db.session.query(Journal.id, Journal.people, Journal.title, Journal.description, Journal.date, Journal.location).all()
    return jsonify(all_books)

@app.route("/journal/delete/<id>", methods=["DELETE"])
def delete_journal(id):
    one_journal = db.session.query(Journal).filter(Journal.id == id).first()
    db.session.delete(one_journal)
    db.session.commit()
    return jsonify(f"Journal was deleted")


@app.route("/user/authentication", methods=["POST"])
def user_authentication():
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."

    post_data = request.get_json()
    email = post_data.get("email")
    password = post_data.get("password")

    user = db.session.query(User).filter(User.email == email).first()

    if email is None:
        return jsonify("Invalid Credentials")

    if bcrypt.check_password_hash(user.password, password) != True:
        return jsonify("Invalid Credentials")

    return {
        "status": "logged_in"
    }


if __name__ == "__main__":
    app.run(debug=True)

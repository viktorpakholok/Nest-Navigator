"""HOuses"""
from flask import Flask, request, render_template, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy

import json
import os

# with open("js.json", "r") as file:
#     data_json = json.load(file)
#     data_json = data_json['mainEntity']['itemListElement'][0]['offers']['offers']

# with open('result.json', 'r') as file:
#     data_json_olx = json.load(file)

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'houses4_db.db')
app.config['SECRET_KEY'] = 'BohdanBohdanBohdan'

db = SQLAlchemy(app)

class Apartament(db.Model):
    '''
    How the table will be looking to the perspective 
    of every element
    '''
    ### Create a table
    __tablename__ = 'Apartaments'
    images = db.Column(db.String)
    url = db.Column(db.String, primary_key = True)
    name = db.Column(db.String)
    area = db.Column(db.REAL)
    price = db.Column(db.REAL)
    currency = db.Column(db.String)
    rooms = db.Column(db.Integer)
    district = db.Column(db.String)
    city = db.Column(db.String)

    def __init__(self, images, url, name, area, price, currency, rooms, district, city) -> None:
        self.images = images
        self.url = url
        self.name = name
        self.area = area
        self.currency = currency
        self.price = price
        self.rooms = rooms
        self.district = district
        self.city = city

    def __repr__(self) -> str:
        return f"{self.name} {self.price} {self.currency}"

@app.route("/")
def main():
    return render_template('main_page.html')


# def index():
#     apartaments = Apartament.query.filter().all()
#     # print('************************')
#     # print(apartaments)
#     # print('************************')
#     return render_template('index.html', apartaments = apartaments)


@app.route("/our_team")
def team():
    return render_template('team_page.html')

@app.route("/search")
def search():
    return render_template('search_page.html')

if __name__ == "__main__":
#    with app.app_context():         # <--- without these two lines,
        # db.create_all()             # <--- we get the OperationalError in the title
    app.run(debug=True)

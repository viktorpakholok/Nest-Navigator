"""HOuses"""
from flask import Flask, request, render_template, Blueprint, url_for
from flask_sqlalchemy import SQLAlchemy
# import json
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

@app.route('/', methods = ["POST", "GET"], defaults = {'page': 5})
@app.route('/<int:page>', methods = ["GET", "POST"])
def index(page):
    pages = 5
    apartaments = Apartament.query.paginate(page, pages, error_out = False)
    if request.method == 'POST':
        query = Apartament.query
        if "city_tag" in request.form and request.form["city_tag"]:
            query = query.filter(Apartament.city.like(request.form["city_tag"]))
        if "district_tag" in request.form and request.form["district_tag"]:
            query = query.filter(Apartament.district.like(request.form["district_tag"]))
        if "min_area_tag" in request.form and request.form["min_area_tag"]:
            query = query.filter(Apartament.area >= float(request.form["min_area_tag"]))
        if "max_area_tag" in request.form and request.form["max_area_tag"]:
            query = query.filter(Apartament.area <= float(request.form["max_area_tag"]))
        if "min_price_tag" in request.form and request.form["min_price_tag"]:
            query = query.filter(Apartament.area >= float(request.form["min_price_tag"]))
        if "max_price_tag" in request.form and request.form["max_price_tag"]:
            query = query.filter(Apartament.area <= float(request.form["max_price_tag"]))
        if "min_rooms_tag" in request.form and request.form["min_rooms_tag"]:
            query = query.filter(Apartament.area >= float(request.form["min_rooms_tag"]))
        if "max_rooms_tag" in request.form and request.form["max_rooms_tag"]:
            query = query.filter(Apartament.area <= float(request.form["max_rooms_tag"]))
        apartaments = query.paginate(per_page = pages, error_out = False)
    return render_template('index.html', apartaments=apartaments)


if __name__ == "__main__":
    app.run(debug=True)

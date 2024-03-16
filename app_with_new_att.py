"""HOuses"""
import os
from flask import Flask, request, render_template, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'houses_test_test_db.db')
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
    price_per_meter = db.Column(db.REAL)

@app.route('/', methods = ["POST", "GET"], defaults = {'page': 1, 'sort': 'none'})
@app.route('/<int:page>/<string:sort>', methods = ["GET", "POST"])
def index(page, sort):
    pages = 5
    if request.method == 'POST':
        session['filters'] = {
            'city': request.form.get('city_tag'),
            'district': request.form.get('district_tag'),
            'min_area': request.form.get('min_area_tag'),
            'max_area': request.form.get('max_area_tag'),
            'min_price': request.form.get('min_price_tag'),
            'max_price': request.form.get('max_price_tag'),
            'min_rooms': request.form.get('min_rooms_tag'),
            'max_rooms': request.form.get('max_rooms_tag'),
        }
        return redirect(url_for('index', page=page, sort=sort))

    filters = session.get('filters', {})

    query = Apartament.query
    if filters.get('city'):
        query = query.filter(Apartament.city.like(filters['city']))
    if filters.get('district'):
        query = query.filter(Apartament.district.like(filters['district']))
    if filters.get('min_area'):
        query = query.filter(Apartament.area >= float(filters['min_area']))
    if filters.get('max_area'):
        query = query.filter(Apartament.area <= float(filters['max_area']))
    if filters.get('min_price'):
        query = query.filter(Apartament.price >= float(filters['min_price']))
    if filters.get('max_price'):
        query = query.filter(Apartament.price <= float(filters['max_price']))
    if filters.get('min_rooms'):
        query = query.filter(Apartament.rooms >= int(filters['min_rooms']))
    if filters.get('max_rooms'):
        query = query.filter(Apartament.rooms <= int(filters['max_rooms']))

    print(sort)

    if sort == 'price_low':
        query = query.order_by(Apartament.price)
    elif sort == 'price_high':
        query = query.order_by(Apartament.price.desc())
    elif sort == 'price_sqm_low':
        query = query.order_by((Apartament.price_per_meter))
    elif sort == 'price_sqm_high':
        query = query.order_by(Apartament.price_per_meter.desc())

    apartaments = query.paginate(page, pages, error_out = False)
    return render_template('index.html', apartaments=apartaments)

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)

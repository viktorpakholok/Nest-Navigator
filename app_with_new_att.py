"""
The main file which runs the web application

"""


from flask import Flask, request, session, redirect, url_for, render_template, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BohdanBohdanBohdan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Housesdb_owner:MOGU0lh5ByIg@ep-aged-pine-a29r8a5c.eu-central-1.aws.neon.tech/Housesdb'
db = SQLAlchemy(app)

class Apartment(db.Model):
    """
    
    """
    __tablename__ = 'Apartments'
    images = db.Column(db.String)
    url = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    area = db.Column(db.Float)
    price = db.Column(db.Float)
    currency = db.Column(db.String)
    rooms = db.Column(db.Integer)
    district = db.Column(db.String)
    city = db.Column(db.String)
    price_per_meter = db.Column(db.Float)

def filter_query(filters):
    query = Apartment.query
    if filters.get('city'):
        query = query.filter(Apartment.city.like('%' + filters['city'] + '%'))
    if filters.get('district'):
        query = query.filter(Apartment.district.like('%' + filters['district'] + '%'))
    if filters.get('min_area'):
        query = query.filter(Apartment.area >= float(filters['min_area']))
    if filters.get('max_area'):
        query = query.filter(Apartment.area <= float(filters['max_area']))
    if filters.get('min_price'):
        query = query.filter(Apartment.price >= float(filters['min_price']))
    if filters.get('max_price'):
        query = query.filter(Apartment.price <= float(filters['max_price']))
    if filters.get('min_rooms'):
        query = query.filter(Apartment.rooms >= int(filters['min_rooms']))
    if filters.get('max_rooms'):
        query = query.filter(Apartment.rooms <= int(filters['max_rooms']))
    return query

def sort_query(query, filters):
    if filters.get('sort_max_price'):
        query = query.order_by(desc(Apartment.price))
    if filters.get('sort_min_price'):
        query = query.order_by(asc(Apartment.price))
    if filters.get('sort_max_price/area'):
        query = query.order_by(desc(Apartment.price_per_meter))
    if filters.get('sort_min_price/area'):
        query = query.order_by(asc(Apartment.price_per_meter))
    return query

@app.route('/reset', methods=['POST'])
def reset():
    session.pop('filters', None)  # Remove the filters from the session
    return redirect(url_for('index'))  # Redirect the user to the index page

@app.route('/', methods = ["POST", "GET"], defaults = {'page': 1})
@app.route('/<int:page>', methods = ["GET", "POST"])
def index(page):
    pages = 5
    if request.method == 'POST':
        session_filters = session.get('filters', {})
        session_filters.update({
            'city': request.form.get('city_tag'),
            'district': request.form.get('district_tag'),
            'min_area': request.form.get('min_area_tag'),
            'max_area': request.form.get('max_area_tag'),
            'min_price': request.form.get('min_price_tag'),
            'max_price': request.form.get('max_price_tag'),
            'min_rooms': request.form.get('min_rooms_tag'),
            'max_rooms': request.form.get('max_rooms_tag'),
            'sort_max_price':request.form.get('sort_max_price_tag'),
            'sort_min_price':request.form.get('sort_min_price_tag'),
            'sort_max_price/area':request.form.get('sort_max_pricearea_tag'),
            'sort_min_price/area':request.form.get('sort_min_pricearea_tag')
        })
        session_filters = {k: v for k, v in session_filters.items() if v is not None}
        session['filters'] = session_filters
        return redirect(url_for('index', page=page))
    filters = session.get('filters', {})
    query = filter_query(filters)
    query = sort_query(query, filters)
    apartaments = query.paginate(page=page, per_page=pages, error_out=False)
    # print(apartaments)
    return render_template('index.html', apartaments=apartaments, filters=filters)

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)

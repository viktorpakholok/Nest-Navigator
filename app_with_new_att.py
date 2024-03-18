"""HOuses"""
import os
from flask import Flask, request, render_template, url_for, session, redirect, g
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

def filter_query(filters):
    g.query = Apartament.query
    if filters.get('city'):
        g.query = g.query.filter(Apartament.city.like(filters['city']))
    if filters.get('district'):
        g.query = g.query.filter(Apartament.district.like(filters['district']))
    if filters.get('min_area'):
        g.query = g.query.filter(Apartament.area >= float(filters['min_area']))
    if filters.get('max_area'):
        g.query = g.query.filter(Apartament.area <= float(filters['max_area']))
    if filters.get('min_price'):
        g.query = g.query.filter(Apartament.price >= float(filters['min_price']))
    if filters.get('max_price'):
        g.query = g.query.filter(Apartament.price <= float(filters['max_price']))
    if filters.get('min_rooms'):
        g.query = g.query.filter(Apartament.rooms >= int(filters['min_rooms']))
    if filters.get('max_rooms'):
        g.query = g.query.filter(Apartament.rooms <= int(filters['max_rooms']))
    # if filters.get('sort_max_price'):
    #     g.query = g.query.order_by(Apartament.price.desc())
    return g.query

def sort_query(query, filters):
    if filters.get('sort_max_price'):
        query = query.order_by(Apartament.price.desc())
    if filters.get('sort_min_price'):
        query = query.order_by(Apartament.price)
    if filters.get('sort_max_price/area'):
        query = query.order_by(Apartament.price_per_meter.desc())
    if filters.get('sort_min_price/area'):
        query = query.order_by(Apartament.price_per_meter)
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
    g.query = filter_query(filters)
    query = sort_query(g.query, filters)
    apartaments = query.paginate(page, pages, error_out = False)
    return render_template('index.html', apartaments=apartaments, filters=filters)
if __name__ == "__main__":
    app.run(debug=True, use_reloader = False)

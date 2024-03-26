"""
The main file which runs the web application
"""

from flask import Flask, request, session, redirect, url_for, render_template, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
import os
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Housesdb_owner:\
MOGU0lh5ByIg@ep-aged-pine-a29r8a5c.eu-central-1.aws.neon.tech/Housesdb'
app.config['SECRET_KEY'] = 'BohdanBohdanBohdan'

db = SQLAlchemy(app)

class Apartment(db.Model):
    '''
    How the table will be looking to the perspective 
    of every element
    '''
    ### Create a table
    __tablename__ = 'Apartments'
    images = db.Column(db.String)
    url = db.Column(db.String, primary_key = True)
    name = db.Column(db.String)
    area = db.Column(db.Float)
    price = db.Column(db.Float)
    currency = db.Column(db.String)
    rooms = db.Column(db.Integer)
    district = db.Column(db.String)
    city = db.Column(db.String)
    price_per_meter = db.Column(db.Float)

def get_all_districts_and_cities(data_base) -> dict:
    """
    Return all districts in a form of a dictinary

    {city : set of all districts}
    
    """
    alp = 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ'
    query2 = Apartment.query.filter(Apartment.district!='')
    output_dictinary = {}
    for row in query2:
        output_dictinary.setdefault(row.city, set()).add(row.district)
    return {key: sorted(list(val)) for key, val in sorted(output_dictinary.items(), key=lambda x: alp.index(x[0][0].upper()))}
        # output_dictinary.setdefault()

def filter_query(filters):
    g.query = Apartment.query
    if filters.get('city'):
        g.query = g.query.filter(Apartment.city.like('%' + filters['city'] + '%'))
    if filters.get('district'):
        g.query = g.query.filter(Apartment.district.like('%' + filters['district'] + '%'))
    if filters.get('min_area'):
        g.query = g.query.filter(Apartment.area >= float(filters['min_area']))
    if filters.get('max_area'):
        g.query = g.query.filter(Apartment.area <= float(filters['max_area']))
    if filters.get('min_price'):
        g.query = g.query.filter(Apartment.price >= float(filters['min_price']))
    if filters.get('max_price'):
        g.query = g.query.filter(Apartment.price <= float(filters['max_price']))
    if filters.get('min_rooms'):
        g.query = g.query.filter(Apartment.rooms >= int(filters['min_rooms']))
    if filters.get('max_rooms'):
        g.query = g.query.filter(Apartment.rooms <= int(filters['max_rooms']))
    # if filters.get('sort_max_price'):
    #     g.query = g.query.order_by(Apartment.price.desc())
    return g.query

def sort_query(query, filters):
    if filters.get('dropdown') == 'sort_max_price_tag':
        query = query.order_by(desc(Apartment.price))
    if filters.get('dropdown') == 'sort_min_price_tag':
        query = query.order_by(asc(Apartment.price))
    if filters.get('dropdown') == 'sort_max_pricearea_tag':
        query = query.order_by(desc(Apartment.price_per_meter))
    if filters.get('dropdown') == 'sort_min_pricearea_tag':
        query = query.order_by(asc(Apartment.price_per_meter))
    return query

@app.route('/reset', methods=['POST'])
def reset():
    session.pop('filters', None)  # Remove the filters from the session
    return redirect(url_for('search'))  # Redirect the user to the index page

@app.route('/')
def main():

    return render_template('main_page.html')

@app.route("/our_team")
def team():

    return render_template('team_page.html')

@app.route('/search/', methods = ["POST", "GET"], defaults = {'page': 1})
@app.route('/search/<int:page>', methods = ["GET", "POST"])
def search(page):
    pages = 15
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
            # 'sort_max_price':request.form.get('sort_max_price_tag'),
            # 'sort_min_price':request.form.get('sort_min_price_tag'),
            # 'sort_max_price/area':request.form.get('sort_max_pricearea_tag'),
            # 'sort_min_price/area':request.form.get('sort_min_pricearea_tag')
            'dropdown': request.form.get('dropdown')
        })
        session_filters = {k: v for k, v in session_filters.items() if v is not None}
        session['filters'] = session_filters
        return redirect(url_for('search', page=page))

    filters = session.get('filters', {})
    g.query = filter_query(filters)
    query = sort_query(g.query, filters)

    apartaments = query.paginate(page=page, per_page=pages, error_out = False)
    t_s = time.time()
    city_dis_dict = get_all_districts_and_cities(db)
    print(time.time() - t_s)

    return render_template('search_page.html', apartaments=apartaments, filters=filters, city_dis_dict = get_all_districts_and_cities(db))

if __name__ == "__main__":
    app.run(debug=True, use_reloader = False, threaded=True)
    # deded = get_all_districts_and_cities(db)
    # print(deded)

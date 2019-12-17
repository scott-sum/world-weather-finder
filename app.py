import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# instantiation of flask app
app = Flask(__name__)

# turn debug mode ON
app.config['DEBUG'] = True

# location of database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

# turn off sqlalchemy warnings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret'

# instantiating database
db = SQLAlchemy(app)

# A city is made up an id and a name
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # nullable means it cannot be an empty field

# goes to the openweathermap api, gets the data, and returns it in json format
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=55c46c522e046a327371d4c804957faf'
    r = requests.get(url).json()
    return r

# homepage route
@app.route('/')
def index_get():
    
    cities = City.query.all() # get all cities
    
    weather_data = []

    for city in cities:        
        # getting the city weather information which is currently in json
        r = get_weather_data(city.name)
        print(r)

        # create weather object to append to array
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        # append it to the array to post
        weather_data.append(weather)

    #second parameter passes to html file
    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city') # getting the city from the form
    if new_city: # checks if city is entered in form
        existing_city = City.query.filter_by(name=new_city).first() #checks if new city already exists in database
       
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            
            # cod comes from json object and 200 means it is successful
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                # add the city to the database and commit changes
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = "City does not exist in the world!"
        else:
            err_msg = 'City already exists in the database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!')

    return redirect(url_for('index_get'))



@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()

    # delete the city from the database and commit changes
    db.session.delete(city)
    db.session.commit()

    # flash messages
    flash(f'Successfully deleted {city.name}', 'success)')
    return redirect(url_for('index_get'))
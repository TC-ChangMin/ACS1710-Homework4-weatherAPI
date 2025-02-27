import os
import requests

from pprint import PrettyPrinter
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_file
from geopy.geocoders import Nominatim


################################################################################
## SETUP
################################################################################

app = Flask(__name__)

# Get the API key from the '.env' file
load_dotenv()

pp = PrettyPrinter(indent=4)

API_KEY = os.getenv('API_KEY')
API_URL = 'http://api.openweathermap.org/data/2.5/weather'


################################################################################
## ROUTES
################################################################################

@app.route('/')
def home():
    """Displays the homepage with forms for current or historical data."""
    context = {
        'min_date': (datetime.now() - timedelta(days=5)),
        'max_date': datetime.now()
    }
    return render_template('home.html', **context)

def get_letter_for_units(units):
    """Returns a shorthand letter for the given units."""
    return 'F' if units == 'imperial' else 'C' if units == 'metric' else 'K'

@app.route('/results')
def results():
    """Displays results for current weather conditions."""
    # TODO: Use 'request.args' to retrieve the city & units from the query
    # parameters.
    city = request.args.get('city')
    units = request.args.get('units')

    params = {
        # TODO: Enter query parameters here for the 'appid' (your api key),
        # the city, and the units (metric or imperial).
        # See the documentation here: https://openweathermap.org/current

        'appid': API_KEY,
        'q': city,
        'units': units

    }
    
    result_json = requests.get(API_URL, params=params).json()

    # Uncomment the line below to see the results of the API call!
    print(f"="*100)
    print(f"="*100)
    pp.pprint(result_json)

    # TODO: Replace the empty variables below with their appropriate values.
    # You'll need to retrieve these from the result_json object above.

    # For the sunrise & sunset variables, I would recommend to turn them into
    # datetime objects. You can do so using the `datetime.fromtimestamp()` 
    # function.
    context = {
        'date': datetime.now(),
        'city': result_json['name'],
        'description': result_json['weather'][0]['description'],
        'temp': result_json['main']['temp'],
        'humidity': result_json['main']['humidity'],
        'wind_speed': result_json['wind']['speed'],
        'sunrise': result_json['sys']['sunrise'],
        'sunset': result_json['sys']['sunset'],
        'units_letter': get_letter_for_units(units)
    }

    return render_template('results.html', **context)


@app.route('/comparison_results')
def comparison_results():
    """Displays the relative weather for 2 different cities."""
    # TODO: Use 'request.args' to retrieve the cities & units from the query
    # parameters.
    city1 = request.args.get('city1')
    city2 = request.args.get('city2')
    units = request.args.get('units')

    # TODO: Make 2 API calls, one for each city. HINT: You may want to write a 
    # helper function for this!

    def get_hours_from_timestamp(unix_timestamp):
        # Convert Unix timestamp to datetime and get the hour as an integer
        local_time = datetime.fromtimestamp(unix_timestamp)
        return local_time.hour

    def make_api_call(city, units):
        params = {
            'appid': API_KEY,
            'q': city,
            'units': units
        }
        return requests.get(API_URL, params=params).json()
    
    city1_info = make_api_call(city1, units)
    city2_info = make_api_call(city2, units) 
    
    # TODO: Pass the information for both cities in the context. Make sure to
    # pass info for the temperature, humidity, wind speed, and sunset time!
    # HINT: It may be useful to create 2 new dictionaries, `city1_info` and 
    # `city2_info`, to organize the data.
    context = {
        'city1': city1,
        'city2': city2,
        'date': datetime.now(),

        'city1_info': {
            'temp': city1_info['main']['temp'],
            'humidity': city1_info['main']['humidity'],
            'wind_speed': city1_info['wind']['speed'],
            'sunset': get_hours_from_timestamp(city1_info['sys']['sunset'])
        },
        'city2_info': {
            'temp': city2_info['main']['temp'],
            'humidity': city2_info['main']['humidity'],
            'wind_speed': city2_info['wind']['speed'],
            'sunset': get_hours_from_timestamp(city2_info['sys']['sunset'])
        },
        'units': get_letter_for_units(units)
    }

    return render_template('comparison_results.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True, port=5001)

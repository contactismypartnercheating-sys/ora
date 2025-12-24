"""
Orastria API - Personalized Astrology Book Generator
Deploy on Railway.app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import tempfile
import boto3
from botocore.config import Config
from datetime import datetime
import uuid

from book_generator import OrastriaBookGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ============== CONFIGURATION ==============
PROKERALA_CLIENT_ID = os.environ.get('PROKERALA_CLIENT_ID')
PROKERALA_CLIENT_SECRET = os.environ.get('PROKERALA_CLIENT_SECRET')

B2_KEY_ID = os.environ.get('B2_KEY_ID')
B2_APP_KEY = os.environ.get('B2_APP_KEY')
B2_BUCKET_NAME = os.environ.get('B2_BUCKET_NAME', 'orastria-books')
B2_ENDPOINT = os.environ.get('B2_ENDPOINT', 'https://s3.us-west-004.backblazeb2.com')

# ============== PROKERALA API ==============
def get_prokerala_token():
    """Get OAuth token from Prokerala"""
    url = "https://api.prokerala.com/token"
    data = {
        'grant_type': 'client_credentials',
        'client_id': PROKERALA_CLIENT_ID,
        'client_secret': PROKERALA_CLIENT_SECRET
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()['access_token']


def get_birth_chart(birth_date, birth_time, latitude, longitude, timezone):
    """
    Get birth chart from Prokerala API
    
    birth_date: "1998-09-06"
    birth_time: "18:30"
    latitude: 34.3989
    longitude: 35.8972
    timezone: "Asia/Beirut"
    """
    token = get_prokerala_token()
    
    # Combine date and time
    datetime_str = f"{birth_date}T{birth_time}:00{get_tz_offset(timezone)}"
    
    url = "https://api.prokerala.com/v2/astrology/planet-position"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "ayanamsa": 1,  # Lahiri
        "coordinates": f"{latitude},{longitude}",
        "datetime": datetime_str
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    data = response.json()['data']
    
    # Also get the ascendant/rising sign
    asc_url = "https://api.prokerala.com/v2/astrology/kundli"
    asc_response = requests.get(asc_url, headers=headers, params=params)
    asc_data = asc_response.json()['data'] if asc_response.ok else None
    
    return parse_chart_data(data, asc_data)


def get_tz_offset(timezone):
    """Get timezone offset string like +03:00"""
    # Common timezone offsets - expand as needed
    offsets = {
        'Asia/Beirut': '+02:00',
        'America/New_York': '-05:00',
        'America/Chicago': '-06:00',
        'America/Los_Angeles': '-08:00',
        'Europe/London': '+00:00',
        'Europe/Paris': '+01:00',
        'Asia/Dubai': '+04:00',
        'Asia/Kolkata': '+05:30',
        'Australia/Sydney': '+11:00',
        'UTC': '+00:00'
    }
    return offsets.get(timezone, '+00:00')


def parse_chart_data(planet_data, kundli_data):
    """Parse Prokerala response into our format"""
    
    zodiac_signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    
    def get_sign(planet_info):
        """Extract sign from planet data"""
        # Prokerala returns sign id (0-11) or sign name
        if 'sign' in planet_info:
            sign = planet_info['sign']
            if isinstance(sign, dict):
                return sign.get('name', zodiac_signs[sign.get('id', 0)])
            elif isinstance(sign, int):
                return zodiac_signs[sign]
            return sign
        return 'Unknown'
    
    planets = planet_data.get('planet_positions', planet_data.get('planets', []))
    
    chart = {
        'sun_sign': 'Unknown',
        'moon_sign': 'Unknown',
        'rising_sign': 'Unknown',
        'mercury': 'Unknown',
        'venus': 'Unknown',
        'mars': 'Unknown',
        'jupiter': 'Unknown',
        'saturn': 'Unknown'
    }
    
    # Map planet names to our keys
    planet_map = {
        'Sun': 'sun_sign',
        'Moon': 'moon_sign',
        'Mercury': 'mercury',
        'Venus': 'venus',
        'Mars': 'mars',
        'Jupiter': 'jupiter',
        'Saturn': 'saturn'
    }
    
    for planet in planets:
        name = planet.get('name', planet.get('planet', ''))
        if name in planet_map:
            chart[planet_map[name]] = get_sign(planet)
    
    # Get rising sign from kundli data
    if kundli_data:
        ascendant = kundli_data.get('ascendant', {})
        if ascendant:
            chart['rising_sign'] = get_sign(ascendant)
    
    return chart


# ============== BACKBLAZE UPLOAD ==============
def upload_to_b2(file_path, file_name):
    """Upload PDF to Backblaze B2 and return public URL"""
    
    s3 = boto3.client(
        's3',
        endpoint_url=B2_ENDPOINT,
        aws_access_key_id=B2_KEY_ID,
        aws_secret_access_key=B2_APP_KEY,
        config=Config(signature_version='s3v4')
    )
    
    # Upload file
    s3.upload_file(
        file_path,
        B2_BUCKET_NAME,
        file_name,
        ExtraArgs={'ContentType': 'application/pdf'}
    )
    
    # Generate public URL
    # Adjust this based on your B2 bucket settings
    public_url = f"{B2_ENDPOINT}/{B2_BUCKET_NAME}/{file_name}"
    
    return public_url


# ============== GEOCODING ==============
def geocode_location(place_name):
    """
    Get latitude, longitude, and timezone for a place
    Using a free geocoding service
    """
    # Using Nominatim (free, no API key needed)
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': place_name,
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'OrastriaApp/1.0'}
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    results = response.json()
    if not results:
        raise ValueError(f"Could not find location: {place_name}")
    
    lat = float(results[0]['lat'])
    lon = float(results[0]['lon'])
    
    # Get timezone using another free API
    tz_url = f"https://timeapi.io/api/TimeZone/coordinate?latitude={lat}&longitude={lon}"
    tz_response = requests.get(tz_url)
    
    if tz_response.ok:
        timezone = tz_response.json().get('timeZone', 'UTC')
    else:
        timezone = 'UTC'
    
    return lat, lon, timezone


# ============== API ENDPOINTS ==============
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'orastria-api'})


@app.route('/generate', methods=['POST'])
def generate_book():
    """
    Generate a personalized astrology book
    
    Expected JSON body:
    {
        "name": "Jennifer Dahab",
        "email": "jennifer@example.com",
        "birth_date": "1998-09-06",
        "birth_time": "18:30",
        "birth_place": "Zgharta, Lebanon",
        "book_type": "sample"  // or "full"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'birth_date', 'birth_time', 'birth_place']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Parse inputs
        name = data['name']
        birth_date = data['birth_date']  # "1998-09-06"
        birth_time = data['birth_time']  # "18:30"
        birth_place = data['birth_place']
        book_type = data.get('book_type', 'sample')
        email = data.get('email', '')
        
        # Step 1: Geocode the birth place
        latitude, longitude, timezone = geocode_location(birth_place)
        
        # Step 2: Get birth chart from Prokerala
        chart = get_birth_chart(birth_date, birth_time, latitude, longitude, timezone)
        
        # Step 3: Format birth date for display
        date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
        
        # Format birth time for display
        time_obj = datetime.strptime(birth_time, "%H:%M")
        formatted_time = time_obj.strftime("%I:%M %p")
        
        # Step 4: Build person data
        person_data = {
            'name': name,
            'birth_date': formatted_date,
            'birth_time': formatted_time,
            'birth_place': birth_place,
            'sun_sign': chart['sun_sign'],
            'moon_sign': chart['moon_sign'],
            'rising_sign': chart['rising_sign'],
            'venus': chart['venus'],
            'mars': chart['mars'],
            'mercury': chart['mercury'],
        }
        
        # Step 5: Generate PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
        
        generator = OrastriaBookGenerator(tmp_path, person_data, book_type=book_type)
        generator.build()
        
        # Step 6: Upload to Backblaze
        file_id = str(uuid.uuid4())[:8]
        safe_name = name.lower().replace(' ', '_')
        file_name = f"books/{safe_name}_{file_id}.pdf"
        
        download_url = upload_to_b2(tmp_path, file_name)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Return success response
        return jsonify({
            'success': True,
            'download_url': download_url,
            'person': {
                'name': name,
                'sun_sign': chart['sun_sign'],
                'moon_sign': chart['moon_sign'],
                'rising_sign': chart['rising_sign']
            },
            'book_type': book_type
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': f'API error: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/chart', methods=['POST'])
def get_chart_only():
    """
    Get just the birth chart without generating a book
    Useful for previewing or debugging
    """
    try:
        data = request.json
        
        birth_date = data['birth_date']
        birth_time = data['birth_time']
        birth_place = data['birth_place']
        
        latitude, longitude, timezone = geocode_location(birth_place)
        chart = get_birth_chart(birth_date, birth_time, latitude, longitude, timezone)
        
        return jsonify({
            'success': True,
            'location': {
                'place': birth_place,
                'latitude': latitude,
                'longitude': longitude,
                'timezone': timezone
            },
            'chart': chart
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

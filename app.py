import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get API key from environment variable
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
OMDB_API_URL = 'http://www.omdbapi.com/'

@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_movies():
    """Search for movies using OMDB API"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    
    if not query:
        return jsonify({'error': 'Please enter a search term'}), 400
    
    if not OMDB_API_KEY:
        return jsonify({'error': 'OMDB API key not configured'}), 500
    
    try:
        # Make request to OMDB API
        params = {
            'apikey': OMDB_API_KEY,
            's': query,
            'page': page,
            'type': 'movie'
        }
        
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Response') == 'False':
            return jsonify({'error': data.get('Error', 'No movies found')}), 404
        
        # Format the response
        movies = []
        for movie in data.get('Search', []):
            movies.append({
                'title': movie.get('Title', 'N/A'),
                'year': movie.get('Year', 'N/A'),
                'imdb_id': movie.get('imdbID', 'N/A'),
                'poster': movie.get('Poster', ''),
                'type': movie.get('Type', 'movie')
            })
        
        return jsonify({
            'movies': movies,
            'total_results': int(data.get('totalResults', 0)),
            'current_page': page,
            'total_pages': (int(data.get('totalResults', 0)) + 9) // 10  # 10 results per page
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except ValueError as e:
        return jsonify({'error': f'Data parsing error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/movie/<imdb_id>')
def get_movie_details(imdb_id):
    """Get detailed information about a specific movie"""
    if not OMDB_API_KEY:
        return jsonify({'error': 'OMDB API key not configured'}), 500
    
    try:
        params = {
            'apikey': OMDB_API_KEY,
            'i': imdb_id,
            'plot': 'full'
        }
        
        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('Response') == 'False':
            return jsonify({'error': data.get('Error', 'Movie not found')}), 404
        
        # Format detailed movie information
        movie_details = {
            'title': data.get('Title', 'N/A'),
            'year': data.get('Year', 'N/A'),
            'rated': data.get('Rated', 'N/A'),
            'released': data.get('Released', 'N/A'),
            'runtime': data.get('Runtime', 'N/A'),
            'genre': data.get('Genre', 'N/A'),
            'director': data.get('Director', 'N/A'),
            'writer': data.get('Writer', 'N/A'),
            'actors': data.get('Actors', 'N/A'),
            'plot': data.get('Plot', 'N/A'),
            'language': data.get('Language', 'N/A'),
            'country': data.get('Country', 'N/A'),
            'awards': data.get('Awards', 'N/A'),
            'poster': data.get('Poster', ''),
            'ratings': data.get('Ratings', []),
            'metascore': data.get('Metascore', 'N/A'),
            'imdb_rating': data.get('imdbRating', 'N/A'),
            'imdb_votes': data.get('imdbVotes', 'N/A'),
            'imdb_id': data.get('imdbID', 'N/A'),
            'type': data.get('Type', 'movie'),
            'dvd': data.get('DVD', 'N/A'),
            'box_office': data.get('BoxOffice', 'N/A'),
            'production': data.get('Production', 'N/A'),
            'website': data.get('Website', 'N/A')
        }
        
        return jsonify(movie_details)
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

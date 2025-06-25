from flask import Flask, jsonify, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from urllib.parse import urlencode
from spotify import spotify  # This imports the blueprint
from nlp_processor import MusicNLPProcessor
import os
import time
import requests
import random

# Initialize NLP processor
nlp_processor = MusicNLPProcessor()

# Load environment variables
load_dotenv()


app = Flask(__name__)

# CORRECT ORDER
CORS(
    app,
    origins=[
        "https://music-recommender-app.vercel.app",
        "http://localhost:5173",
        "http://192.168.29.8:5173/",
    ],
    supports_credentials=True,
)

# THEN register blueprints
app.register_blueprint(spotify)


# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Soptify Configuration
# Spotify Token Gen SEC
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# API KEY
app.secret_key = os.getenv("FLASK_SECRET_KEY")
# Add just below app.secret_key
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)


# Initialize Database
db = SQLAlchemy(app)


# Define Music Table Model
class Music(db.Model):
    __tablename__ = "music_recommendations"
    __table_args__ = {'schema': 'public'} 

    id = db.Column(db.Integer, primary_key=True)
    sad_music = db.Column(db.String(100))
    romantic_music = db.Column(db.String(100))
    party_music = db.Column(db.String(100))
    happy_music = db.Column(db.String(100))
    melancholy_music = db.Column(db.String(100))
    focus_music = db.Column(db.String(100))
    instrumental_music = db.Column(db.String(100))
    k_pop_music = db.Column(db.String(100))
    electronic_music = db.Column(db.String(100))
    rnb_music = db.Column(db.String(100))
    blues_music = db.Column(db.String(100))
    personal_fav = db.Column(db.String(100))
    native_music = db.Column(db.String(100))
    classical_music = db.Column(db.String(100))
    workout_music = db.Column(db.String(100))
    rock_music = db.Column(db.String(100))
    rap_music = db.Column(db.String(100))
    pop_music = db.Column(db.String(100))
    jazz_music = db.Column(db.String(100))
    motivational_music = db.Column(db.String(100))
    trending_music = db.Column(db.String(100))
    latest_music = db.Column(db.String(100))
    top_music = db.Column(db.String(100))
    hidden_gems_music = db.Column(db.String(100))
    developers_choice_music = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "sad_music": self.sad_music,
            "romantic_music": self.romantic_music,
            "party_music": self.party_music,
            "happy_music": self.happy_music,
            "melancholy_music": self.melancholy_music,
            "focus_music": self.focus_music,
            "instrumental_music": self.instrumental_music,
            "k_pop_music": self.k_pop_music,
            "electronic_music": self.electronic_music,
            "rnb_music": self.rnb_music,
            "blues_music": self.blues_music,
            "personal_fav": self.personal_fav,
            "native_music": self.native_music,
            "classical_music": self.classical_music,
            "workout_music": self.workout_music,
            "rock_music": self.rock_music,
            "rap_music": self.rap_music,
            "pop_music": self.pop_music,
            "jazz_music": self.jazz_music,
            "motivational_music": self.motivational_music,
            "trending_music": self.trending_music,
            "latest_music": self.latest_music,
            "top_music": self.top_music,
            "hidden_gems_music": self.hidden_gems_music,
            "developers_choice_music": self.developers_choice_music,
        }


# Route to fetch all songs
@app.route("/songs", methods=["GET"])
def get_songs():
    songs = Music.query.all()
    return jsonify([song.to_dict() for song in songs])


# Route to fetch songs by genre
from flask import request, url_for


@app.route("/songs/<genre>", methods=["GET"])
def get_songs_by_genre(genre):
    allowed_genres = [
        "sad_music",
        "romantic_music",
        "party_music",
        "happy_music",
        "melancholy_music",
        "focus_music",
        "instrumental_music",
        "k_pop_music",
        "electronic_music",
        "rnb_music",
        "blues_music",
        "personal_fav",
        "native_music",
        "classical_music",
        "workout_music",
        "rock_music",
        "rap_music",
        "pop_music",
        "jazz_music",
        "motivational_music",
        "trending_music",
        "latest_music",
        "top_music",
        "hidden_gems_music",
        "developers_choice_music",
    ]

    if genre not in allowed_genres:
        return jsonify({"error": "Invalid genre"}), 400

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 10))

    genre_column = getattr(Music, genre)
    total_items = Music.query.filter(genre_column.isnot(None)).count()

    songs = (
        Music.query.with_entities(genre_column)
        .filter(genre_column.isnot(None))
        .offset(offset)
        .limit(limit)
        .all()
    )

    results = [song[0] for song in songs]

    next_offset = offset + limit
    prev_offset = max(0, offset - limit)

    # Create full URLs for next and previous
    base_url = request.base_url
    next_url = (
        f"{base_url}?offset={next_offset}&limit={limit}"
        if next_offset < total_items
        else None
    )
    prev_url = f"{base_url}?offset={prev_offset}&limit={limit}" if offset > 0 else None

    return jsonify(
        {
            "results": results,
            "next_offset": next_offset,
            "total_items": total_items,
            "has_more": next_offset < total_items,
            "length": len(results),
            "next": next_url,
            "prev": prev_url,
        }
    )

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """NLP-powered music recommendation chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process user message with NLP
        analysis = nlp_processor.process_user_message(user_message)
        
        # Generate conversational response
        response = nlp_processor.generate_response(analysis, user_message)
        
        # Get actual songs from database based on recommended genres
        recommended_songs = []
        for genre in response['genres']:
            # Query your database for songs in this genre
            genre_column = getattr(Music, genre, None)
            if genre_column:
                songs = Music.query.with_entities(genre_column).filter(
                    genre_column.isnot(None)
                ).limit(5).all()
                
                genre_songs = [song[0] for song in songs if song[0]]
                recommended_songs.extend(genre_songs)
        
        # Remove duplicates and limit results
        unique_songs = list(set(recommended_songs))
        
        return jsonify({
            'bot_message': response['message'],
            'recommended_songs': unique_songs[:10],  # Top 10 recommendations
            'genres': response['genres'],
            'follow_up': response.get('follow_up', ''),
            'analysis': {
                'emotions': analysis['emotions'],
                'activities': analysis['activities'],
                'confidence': analysis['confidence']
            }
        })
    
    except Exception as e:
        return jsonify({'error': f'Chat processing failed: {str(e)}'}), 500


# Alternative endpoint for getting songs by emotion/mood
@app.route("/songs/by-mood", methods=["POST"])
def get_songs_by_mood():
    """Get songs based on mood/emotion analysis"""
    try:
        data = request.get_json()
        mood_text = data.get('mood', '')
        limit = data.get('limit', 10)
        
        if not mood_text:
            return jsonify({'error': 'Mood text is required'}), 400
        
        # Process mood with NLP
        analysis = nlp_processor.process_user_message(mood_text)
        genres = analysis['recommended_genres']
        
        # Get songs from recommended genres
        all_songs = []
        for genre in genres:
            genre_column = getattr(Music, genre, None)
            if genre_column:
                songs = Music.query.with_entities(genre_column).filter(
                    genre_column.isnot(None)
                ).limit(limit // len(genres) + 2).all()
                
                genre_songs = [song[0] for song in songs if song[0]]
                all_songs.extend(genre_songs)
        
        # Remove duplicates and shuffle
        unique_songs = list(set(all_songs))
        random.shuffle(unique_songs)
        
        return jsonify({
            'songs': unique_songs[:limit],
            'detected_emotions': analysis['emotions'],
            'confidence': analysis['confidence'],
            'recommended_genres': genres
        })
    
    except Exception as e:
        return jsonify({'error': f'Mood analysis failed: {str(e)}'}), 500

# Run the Flask app
if __name__ == "__main__":
    print("Flask app is starting...")
    app.run(debug=True)

@app.route("/test-db")
def test_db():
    try:
        count = Music.query.count()
        return f"✅ Database connected! Found {count} records in music_recommendations table."
    except Exception as e:
        return f"❌ Database error: {str(e)}"

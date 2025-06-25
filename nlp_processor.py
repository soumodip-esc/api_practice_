import re
import json
from textblob import TextBlob
from collections import Counter
import random

class MusicNLPProcessor:
    def __init__(self):
        # Emotion mapping to your database genres
        self.emotion_genre_mapping = {
            'sad': ['sad_music', 'blues_music', 'melancholy_music'],
            'happy': ['happy_music', 'pop_music', 'party_music'],
            'romantic': ['romantic_music', 'rnb_music', 'jazz_music'],
            'energetic': ['workout_music', 'electronic_music', 'rock_music'],
            'relaxed': ['focus_music', 'instrumental_music', 'classical_music'],
            'nostalgic': ['blues_music', 'jazz_music', 'classical_music'],
            'motivated': ['motivational_music', 'workout_music', 'rap_music'],
            'party': ['party_music', 'electronic_music', 'pop_music'],
            'melancholy': ['melancholy_music', 'sad_music', 'blues_music'],
            'focus': ['focus_music', 'instrumental_music', 'classical_music']
        }
        
        # Keyword patterns for different emotions and contexts
        self.emotion_keywords = {
            'sad': ['sad', 'depressed', 'down', 'blue', 'crying', 'heartbroken', 'lonely', 'upset', 'hurt'],
            'happy': ['happy', 'joyful', 'excited', 'cheerful', 'glad', 'upbeat', 'positive', 'elated'],
            'romantic': ['love', 'romantic', 'date', 'crush', 'valentine', 'intimate', 'romantic'],
            'energetic': ['energetic', 'pumped', 'hyped', 'active', 'workout', 'gym', 'running', 'dance'],
            'relaxed': ['chill', 'relax', 'calm', 'peaceful', 'studying', 'meditation', 'zen', 'quiet'],
            'nostalgic': ['nostalgic', 'memories', 'past', 'old times', 'remember', 'childhood'],
            'motivated': ['motivated', 'inspired', 'determined', 'confident', 'strong', 'powerful'],
            'party': ['party', 'club', 'dancing', 'celebration', 'fun', 'wild', 'night out'],
            'melancholy': ['melancholy', 'bittersweet', 'wistful', 'pensive', 'thoughtful'],
            'focus': ['study', 'work', 'concentrate', 'focus', 'productivity', 'background']
        }
        
        # Activity context mapping
        self.activity_mapping = {
            'workout': ['workout_music', 'electronic_music', 'motivational_music'],
            'study': ['focus_music', 'instrumental_music', 'classical_music'],
            'party': ['party_music', 'electronic_music', 'pop_music'],
            'driving': ['rock_music', 'pop_music', 'rap_music'],
            'cooking': ['jazz_music', 'rnb_music', 'pop_music'],
            'cleaning': ['pop_music', 'electronic_music', 'motivational_music'],
            'sleeping': ['instrumental_music', 'classical_music', 'focus_music']
        }

    def preprocess_text(self, text):
        """Clean and normalize input text"""
        text = text.lower().strip()
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def extract_emotions(self, text):
        """Extract emotions from text using keyword matching and sentiment analysis"""
        processed_text = self.preprocess_text(text)
        detected_emotions = []
        
        # Keyword-based emotion detection
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in processed_text:
                    detected_emotions.append(emotion)
        
        # Sentiment analysis fallback
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        if not detected_emotions:
            if sentiment.polarity > 0.3:
                detected_emotions.append('happy')
            elif sentiment.polarity < -0.3:
                detected_emotions.append('sad')
            else:
                detected_emotions.append('relaxed')
        
        return list(set(detected_emotions))  # Remove duplicates

    def extract_activities(self, text):
        """Extract activity context from text"""
        processed_text = self.preprocess_text(text)
        activities = []
        
        for activity, _ in self.activity_mapping.items():
            if activity in processed_text:
                activities.append(activity)
        
        return activities

    def get_genre_recommendations(self, emotions, activities=None):
        """Map emotions and activities to music genres from your database"""
        recommended_genres = []
        
        # Primary recommendations based on emotions
        for emotion in emotions:
            if emotion in self.emotion_genre_mapping:
                recommended_genres.extend(self.emotion_genre_mapping[emotion])
        
        # Secondary recommendations based on activities
        if activities:
            for activity in activities:
                if activity in self.activity_mapping:
                    recommended_genres.extend(self.activity_mapping[activity])
        
        # Remove duplicates and return top 3-5 genres
        genre_counts = Counter(recommended_genres)
        return [genre for genre, _ in genre_counts.most_common(5)]

    def process_user_message(self, message):
        """Main processing function"""
        emotions = self.extract_emotions(message)
        activities = self.extract_activities(message)
        genres = self.get_genre_recommendations(emotions, activities)
        
        return {
            'emotions': emotions,
            'activities': activities,
            'recommended_genres': genres,
            'confidence': self.calculate_confidence(emotions, activities)
        }

    def calculate_confidence(self, emotions, activities):
        """Calculate confidence score for recommendations"""
        base_score = 0.5
        if emotions:
            base_score += 0.3
        if activities:
            base_score += 0.2
        
        return min(base_score, 1.0)

    def generate_response(self, analysis_result, user_message):
        """Generate conversational response"""
        emotions = analysis_result['emotions']
        genres = analysis_result['recommended_genres']
        
        if not emotions:
            return {
                'message': "I'd love to help you find the perfect music! Could you tell me more about how you're feeling or what you're doing?",
                'genres': ['trending_music', 'top_music', 'developers_choice_music']
            }
        
        # Create personalized response
        emotion_text = self.format_emotions(emotions)
        response_templates = [
            f"I can sense you're feeling {emotion_text}. Here are some songs that might resonate with your mood:",
            f"Based on your {emotion_text} vibe, I've found some perfect matches:",
            f"Feeling {emotion_text}? These songs should hit the right note:",
        ]
        
        response = random.choice(response_templates)
        
        return {
            'message': response,
            'genres': genres[:3],  # Top 3 genre recommendations
            'follow_up': self.generate_follow_up(emotions)
        }

    def format_emotions(self, emotions):
        """Format emotions for natural language response"""
        if len(emotions) == 1:
            return emotions[0]
        elif len(emotions) == 2:
            return f"{emotions[0]} and {emotions[1]}"
        else:
            return f"{', '.join(emotions[:-1])}, and {emotions[-1]}"

    def generate_follow_up(self, emotions):
        """Generate follow-up questions or suggestions"""
        follow_ups = {
            'sad': "Would you like something to help you process these feelings, or perhaps something to lift your spirits?",
            'happy': "Should I find more upbeat tracks to keep this energy going?",
            'romantic': "Are you looking for something for a special someone or just feeling the love?",
            'energetic': "Need something for a workout or just want to keep the energy high?",
            'relaxed': "Perfect for unwinding! Want something for background or active listening?"
        }
        
        primary_emotion = emotions[0] if emotions else 'relaxed'
        return follow_ups.get(primary_emotion, "How do these recommendations sound? I can adjust based on your feedback!")

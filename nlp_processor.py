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
        
        
        # Fixed: Removed duplicate 'romantic' key and improved keyword patterns
        self.emotion_keywords = {
            'sad': ['sad', 'depressed', 'down', 'blue', 'crying', 'heartbroken', 'lonely', 'upset', 'hurt','low', 'awful', 'terrible', 'bad', 'miserable', 'gloomy', 'devastated', 'broken',
        'disappointed', 'hopeless', 'grief', 'sorrow', 'despair', 'melancholic' ],
    
        'happy': ['happy', 'joyful', 'excited', 'cheerful', 'glad', 'upbeat', 'positive', 'elated','thrilled', 'ecstatic', 'fantastic', 'wonderful', 'amazing', 'great', 'awesome',
        'excellent', 'delighted', 'overjoyed', 'euphoric', 'blissful'],
    
        'energetic': ['energetic', 'pumped', 'hyped', 'active', 'workout', 'gym', 'running', 'dance','exercise', 'fitness', 'cardio', 'training', 'intense', 'powerful', 'strong',
        'adrenaline', 'boost', 'motivation', 'energy', 'pump', 'beast mode', 'sweat',
        'lift', 'weights', 'crossfit', 'hiit', 'run', 'jog', 'sprint'],
    
        'romantic': ['love', 'romantic', 'date', 'crush', 'valentine', 'intimate','romance', 'affection', 'passion', 'relationship', 'boyfriend', 'girlfriend',
        'husband', 'wife', 'partner', 'soulmate', 'sweetheart', 'darling', 'beloved',
        'dinner', 'anniversary', 'proposal', 'wedding', 'honeymoon'],
    
        'relaxed': ['chill', 'relax', 'calm', 'peaceful', 'studying', 'meditation', 'zen', 'quiet','tranquil', 'serene', 'mellow', 'soothing', 'unwind', 'decompress', 'breathe',
        'mindful', 'spa', 'massage', 'ambient', 'soft', 'gentle', 'laid back'],
    
        'party': ['party', 'club', 'dancing', 'celebration', 'fun', 'wild', 'night out','dance', 'nightclub', 'disco', 'rave', 'festival', 'concert', 'dj',
        'bass', 'beat', 'groove', 'vibe', 'turn up', 'lit', 'banging', 'banger'],
    
        'focus': ['study', 'work', 'concentrate', 'focus', 'productivity', 'background','studying', 'working', 'office', 'homework', 'exam', 'concentration',
        'reading', 'writing', 'coding', 'programming', 'task', 'project', 'deep work', 'workout']
        }
        
        # Activity context mapping
        self.activity_mapping = {
            'workout': ['workout_music', 'electronic_music', 'motivational_music'],
            'study': ['focus_music', 'instrumental_music', 'classical_music'],
            'studying': ['focus_music', 'instrumental_music', 'classical_music'],  # Added variant
            'party': ['party_music', 'electronic_music', 'pop_music'],
            'driving': ['rock_music', 'pop_music', 'rap_music'],
            'cooking': ['jazz_music', 'rnb_music', 'pop_music'],
            'cleaning': ['pop_music', 'electronic_music', 'motivational_music'],
            'sleeping': ['instrumental_music', 'classical_music', 'focus_music'],
            'working': ['focus_music', 'instrumental_music', 'classical_music'],  # Added variant
            'exercise': ['workout_music', 'electronic_music', 'motivational_music'],  # Added variant
            'running': ['workout_music', 'electronic_music', 'motivational_music'],  # Added variant
            'gym': ['workout_music', 'electronic_music', 'motivational_music'],  # Added variant
        }

    def preprocess_text(self, text):
        """Clean and normalize input text"""
        if not isinstance(text, str):
            return ""
        
        text = text.lower().strip()
        # Remove special characters but keep spaces and handle contractions better
        text = re.sub(r"[^\w\s']", ' ', text)
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        return text.strip()

    def extract_emotions(self, text):
        """Extract emotions from text using keyword matching and sentiment analysis"""
        if not text:
            return []
            
        processed_text = self.preprocess_text(text)
        detected_emotions = []
        
        # Improved keyword-based emotion detection with word boundaries
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, processed_text):
                    detected_emotions.append(emotion)
                    break  # Only add emotion once per category
        
        # Sentiment analysis fallback with better thresholds
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            if not detected_emotions:
                if sentiment.polarity > 0.2:
                    detected_emotions.append('happy')
                elif sentiment.polarity < -0.2:
                    detected_emotions.append('sad')
                else:
                    detected_emotions.append('relaxed')
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            if not detected_emotions:
                detected_emotions.append('relaxed')
        
        return list(set(detected_emotions))  # Remove duplicates

    def extract_activities(self, text):
        """Extract activity context from text"""
        if not text:
            return []
            
        processed_text = self.preprocess_text(text)
        activities = []
        
        for activity in self.activity_mapping.keys():
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(activity) + r'\b'
            if re.search(pattern, processed_text):
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
        if recommended_genres:
            genre_counts = Counter(recommended_genres)
            return [genre for genre, _ in genre_counts.most_common(5)]
        else:
            # Fallback genres if no specific matches
            return ['trending_music', 'top_music', 'developers_choice_music']

    def process_user_message(self, message):
        """Main processing function with error handling"""
        try:
            if not message or not isinstance(message, str):
                return {
                    'emotions': [],
                    'activities': [],
                    'recommended_genres': ['trending_music', 'top_music', 'developers_choice_music'],
                    'confidence': 0.1
                }
            
            emotions = self.extract_emotions(message)
            activities = self.extract_activities(message)
            genres = self.get_genre_recommendations(emotions, activities)
            
            return {
                'emotions': emotions,
                'activities': activities,
                'recommended_genres': genres,
                'confidence': self.calculate_confidence(emotions, activities)
            }
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                'emotions': [],
                'activities': [],
                'recommended_genres': ['trending_music', 'top_music', 'developers_choice_music'],
                'confidence': 0.1
            }

    def calculate_confidence(self, emotions, activities):
        """Calculate confidence score for recommendations"""
        base_score = 0.3  # Lowered base score for more realistic confidence
        
        if emotions:
            base_score += len(emotions) * 0.2  # Higher confidence with more emotions detected
        if activities:
            base_score += len(activities) * 0.15  # Bonus for activity context
        
        return min(base_score, 1.0)

    def generate_response(self, analysis_result, user_message=""):
        """Generate conversational response with better error handling"""
        try:
            emotions = analysis_result.get('emotions', [])
            genres = analysis_result.get('recommended_genres', [])
            
            if not emotions:
                return {
                    'message': "I'd love to help you find the perfect music! Could you tell me more about how you're feeling or what you're doing?",
                    'genres': genres[:3] if genres else ['trending_music', 'top_music', 'developers_choice_music'],
                    'follow_up': "What's your mood like today?"
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
                'genres': genres[:3] if len(genres) >= 3 else genres,  # Top 3 or all available
                'follow_up': self.generate_follow_up(emotions)
            }
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'message': "I'm here to help you find great music! What are you in the mood for?",
                'genres': ['trending_music', 'top_music', 'developers_choice_music'],
                'follow_up': "Tell me about your current mood or what you're doing."
            }

    def format_emotions(self, emotions):
        """Format emotions for natural language response"""
        if not emotions:
            return "neutral"
        elif len(emotions) == 1:
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
            'relaxed': "Perfect for unwinding! Want something for background or active listening?",
            'motivated': "Looking for something to keep you driven and focused?",
            'party': "Ready to get the party started? Want some dance-worthy tracks?",
            'nostalgic': "Want to take a trip down memory lane with some classic vibes?",
            'melancholy': "Sometimes introspective music hits just right. Want something thoughtful?",
            'focus': "Need some background music that won't distract from your tasks?"
        }
        
        if not emotions:
            return "How do these recommendations sound? I can adjust based on your feedback!"
            
        primary_emotion = emotions[0]
        return follow_ups.get(primary_emotion, "How do these recommendations sound? I can adjust based on your feedback!")

# Example usage and testing
if __name__ == "__main__":
    processor = MusicNLPProcessor()
    
    # Test cases
    test_messages = [
        "I'm feeling really sad today",
        "Need some workout music for the gym",
        "Want something romantic for date night",
        "I'm studying and need focus music",
        "",  # Empty message test
        None,  # None test
        123,  # Non-string test
    ]
    
    for msg in test_messages:
        print(f"\nTesting: {msg}")
        try:
            result = processor.process_user_message(msg)
            response = processor.generate_response(result, str(msg) if msg else "")
            print(f"Emotions: {result['emotions']}")
            print(f"Genres: {result['recommended_genres']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Response: {response['message']}")
        except Exception as e:
            print(f"Error: {e}")
import random
import speech_recognition as sr
from flask import Flask, request, jsonify, render_template
from deep_translator import GoogleTranslator
from textblob import TextBlob

app = Flask(__name__)

# Emoji Mapping for Emotions
EMOTION_MAP = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "neutral": "😐"
}

# SABS-Specific Responses
RESPONSES = {
    "greeting": [
        "Hello! I'm Luna, the SABS assistant. How can I help you today?",
        "Hi there! Need info about admissions, courses, or events at SABS?",
        "Welcome to SABS! Luna here to guide you around our campus online. 😊"
    ],

    "admission": [
        "For admission details, visit https://www.sabs.ac.in/admission or contact admissions@sabs.ac.in"
    ],

     "apply": [    
        "You can apply online and check eligibility at https://www.sabs.ac.in/apply-online",
        "Admissions are open! Explore your future at SABS here: https://www.sabs.ac.in/apply-online"
     ],
     "courses": [
        "We offer UG Courses like Bcom , BBA , BCA. Browse at  https://www.sabs.ac.in/programs-overview",
        "From Computer Science to Commerce — check all programs here: https://www.sabs.ac.in/programs-overview",
        "Looking for course info? Everything is listed at https://www.sabs.ac.in/programs-overview"
    ],
   
  "courselist": {
    "bca": [
      "About BCA details : https://sabs.ac.in/courses-bca"
    ],
    "bcom": [
      "About BCom details : https://sabs.ac.in/courses-bcom"
    ],
    "bba": [
      "About BBA details : https://sabs.ac.in/courses-bba"
    ]
  },
    "events": [
        "Our latest events and announcements are at https://www.sabs.ac.in/events",
        "Exciting things always happening at SABS! Check the event calendar: https://www.sabs.ac.in/video"
    ],
    "gallery": [
        "SABS hosts fests, seminars, and more. Stay updated here: https://www.sabs.ac.in/events",
        "SABS media [ Press Clipping] . Check here: https://www.sabs.ac.in/press-clipping"
    ],
    "contact": [
        "You can contact us at https://www.sabs.ac.in/contact-us or call the main office on  +91-80-28488676.",
        "Need help? Our support team is available. Reach out via Email : info@sabs.ac.in",
        "Contact us on WHATSAPP : +91 80 2848 8676"
    ],
    "facilities": [
        "Explore our state-of-the-art library, computer labs, seminar halls, sports facilities and more : https://www.sabs.ac.in/facilities",
        "We provide top-notch learning and recreational facilities. Know more: https://www.sabs.ac.in/facilities",
        "From labs to lounges – view our campus infrastructure here: https://www.sabs.ac.in/facilities"
    ],
    "Benefitsforstudents": [
        "SABS students benefit from mentorship programs, clubs, and excellent academic support. Learn more: https://www.sabs.ac.in/counseling-mentoring",
        "Life at SABS is vibrant and inspiring. Discover what our students enjoy: https://www.sabs.ac.in/statuatory-cells",
        "Students at SABS thrive with hands-on experience and community engagement. Read more: https://www.sabs.ac.in/remedial-classes",
        "Previous Year question papers are also available : https://sabs.ac.in/question-papers"
    ],
    "placements": [
        "SABS has an excellent placement record. Visit https://www.sabs.ac.in/placements",
        "Get placed with leading companies! Learn about our placement process: https://www.sabs.ac.in/placements"
    ],
    "recruiters":[
         "Our placement cell partners with top companies for campus recruitment. Details here: https://www.sabs.ac.in/placements"
    ], 

    "about": [
        "SABS is committed to academic excellence and holistic development. Learn more about us: https://www.sabs.ac.in/about-us",
        "Want to know about SABS's legacy, vision, and mission? Visit: https://www.sabs.ac.in/about-us",
        "Explore who we are and what we stand for here: https://www.sabs.ac.in/about-us",
        "Explore our instituions all over the karnataka : https://sabs.ac.in/institutions"
    ],
    "website": [
        "Visit our website for more information : https://sabs.ac.in/"
    ],
    "how_are_you": [
        "I’m just a bunch of code, but thanks for asking! How about you?",
        "I’m Luna, and I’m always here to chat with you! How’s your day going?",
        "I’m great! Ready to assist you anytime."
    ],
    "help": [
        "Of course! Luna is here to help. What do you need?",
        "I’m Luna, your virtual assistant. Let me know how I can assist!",
        "Sure! Tell me what’s troubling you, and I’ll do my best to help."
    ],
    "joke": [
        "Why did the chatbot break up with the user? Too many unresolved issues! 😆",
        "I asked my server for a joke… but it crashed. 😂",
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐞"
    ],
    "motivation": [
        "You got this! Luna believes in you!",
        "Keep going! Success is just around the corner. - Luna",
        "Stay strong and keep pushing forward! You’re amazing. - Luna"
    ],

    "Thanks": [
        "I am very glad to help you",
        "Anytime ☺️",
        "Your Welcome! Anything else I can do for you?"
        ],

    "default": [
        "I'm not sure I understood. You can ask me about admissions, courses, events, or contact info.",
        "Oops! Luna's still learning. Can you rephrase that?",
        "Try asking about SABS programs, how to apply, or upcoming events!",
        "Hmm... I don't have an answer for that yet. Try asking something else!",
        "I’m still learning, but Luna is here to chat! Can you ask in a different way?"

    ]
    
    }

# Language Translation
def translate_text(text, src_lang, target_lang="en"):
    return GoogleTranslator(source=src_lang, target=target_lang).translate(text)

# Sentiment Analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "happy"
    elif polarity > 0.1:
        return "neutral"
    elif polarity < -0.2:
        return "angry"
    elif polarity < -0.1:
        return "sad"
    else:
        return "neutral"

# Voice Recognition
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        try:
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except:
            return "Sorry, I couldn't understand your speech. Please try again."

# Chatbot Logic
def chatbot_response(user_message):
    message = user_message.lower()
    if any(greet in message for greet in ["hi", "hello", "hey"]):
        return random.choice(RESPONSES["greeting"])
    elif "admission" in message :
        return random.choice(RESPONSES["admission"])
    elif "apply" in message:
        return random.choice(RESPONSES["apply"])
    elif "course" in message or "program" in message:
        return random.choice(RESPONSES["courses"])
    elif "bca" in message:
        return random.choice(RESPONSES["courselist"]["bca"])
    elif "bcom" in message:
        return random.choice(RESPONSES["courselist"]["bcom"])
    elif "bba" in message:
        return random.choice(RESPONSES["courselist"]["bba"])
    elif "event" in message:
        return random.choice(RESPONSES["events"])
    elif "gallery" in message:
        return random.choice(RESPONSES["gallery"])
    elif "contact" in message or "phone" in message or "call" in message:
        return random.choice(RESPONSES["contact"])
    elif "facility" in message or "facilities" in message:
        return random.choice(RESPONSES["facilities"])
    elif "benefits for student" in message or "students" in message:
        return random.choice(RESPONSES["Benefitsforstudents"])
    elif "placement" in message or "job" in message:
        return random.choice(RESPONSES["placements"])
    elif "recruiters" in message :
        return random.choice(RESPONSES["recruiters"])
    elif "about" in message:
        return random.choice(RESPONSES["about"])
    elif "website" in message:
        return random.choice(RESPONSES["website"])
    elif "how are you" in message:
        return random.choice(RESPONSES["how_are_you"])
    elif "help" in message:
        return random.choice(RESPONSES["help"])
    elif "Thank you" in message or "Thanks" in message:
        return random.choice(RESPONSES["Thanks"])
    elif "tell me a joke" in message or "make me laugh" in message:
        return random.choice(RESPONSES["joke"])
    elif "motivate me" in message or "inspire me" in message or "motivate" in message:
        return random.choice(RESPONSES["motivation"])
    else:
        return random.choice(RESPONSES["default"])

# Routes
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/voice', methods=['GET'])
def voice_chat():
    speech_text = recognize_speech()
    return jsonify({"voice_text": speech_text})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_language = data.get("language", "en")

    translated = translate_text(user_message, user_language)
    response = chatbot_response(translated)
    emotion = analyze_sentiment(translated)

    return jsonify({
        "avatar": EMOTION_MAP.get(emotion, "🤖"),
        "response": response,
        "emotion": emotion.capitalize()
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

import random
import speech_recognition as sr
from flask import Flask, request, jsonify, render_template
from deep_translator import GoogleTranslator
from textblob import TextBlob

app = Flask(__name__)

# Emojis representing sentiment
EMOTION_MAP = {
    "happy": "😊",
    "sad": "😢",
    "angry": "😡",
    "neutral": "😐"
}

# SABS Responses
RESPONSES = {
    "greeting": [
        "Hello! I'm Luna, the SABS assistant. How can I help you today?",
        "Hi there! Need info about admissions, courses, or events at SABS?",
        "Welcome to SABS! Luna here to guide you around our campus online. 😊"
    ],
    "admission": [
        "For admission details, visit <a href='https://www.sabs.ac.in/admission' target='_blank'>sabs.ac.in/admission</a> or email admissions@sabs.ac.in",
        "You can apply online and check eligibility at <a href='https://www.sabs.ac.in/apply-online' target='_blank'>Apply Now</a>",
        "Explore your future at SABS! Admissions info: <a href='https://www.sabs.ac.in/apply-online' target='_blank'>Apply Here</a>"
    ],
    "courses": [
        "We offer UG Courses like BCom, BBA, BCA. Browse at <a href='https://www.sabs.ac.in/programs-overview' target='_blank'>Programs</a>",
        "Explore all our academic programs: <a href='https://www.sabs.ac.in/programs-overview' target='_blank'>Programs Overview</a>"
    ],
    "events": [
        "Stay updated on events: <a href='https://www.sabs.ac.in/events' target='_blank'>Event Page</a>",
        "Fests, seminars, and more: <a href='https://www.sabs.ac.in/video' target='_blank'>Gallery</a>",
        "Media Coverage: <a href='https://www.sabs.ac.in/press-clipping' target='_blank'>Press Clipping</a>"
    ],
    "contact": [
        "Email: contact@sabs.ac.in | Call: +91-80-28488676",
        "WhatsApp: +91 80 2848 8676 | Visit: <a href='https://sabs.ac.in/contact' target='_blank'>Contact Page</a>"
    ],
    "facilities": [
        "Explore our library, labs, seminar halls, and more: <a href='https://www.sabs.ac.in/facilities' target='_blank'>Facilities</a>"
    ],
    "Benefitsforstudents": [
        "Mentorship, clubs, support, and more: <a href='https://www.sabs.ac.in/counseling-mentoring' target='_blank'>Student Benefits</a>",
        "Community and growth: <a href='https://www.sabs.ac.in/statuatory-cells' target='_blank'>Statutory Cells</a>",
        "Remedial Classes: <a href='https://www.sabs.ac.in/remedial-classes' target='_blank'>Support System</a>",
        "Previous year question papers: <a href='https://sabs.ac.in/question-papers' target='_blank'>Question Papers</a>"
    ],
    "placements": [
        "Top recruiters, great records! <a href='https://www.sabs.ac.in/placements' target='_blank'>Placement Cell</a>"
    ],
    "about": [
        "SABS is committed to excellence. Learn more: <a href='https://www.sabs.ac.in/about-us' target='_blank'>About Us</a>",
        "Institutions across Karnataka: <a href='https://sabs.ac.in/institutions' target='_blank'>Institutions</a>"
    ],
    "how_are_you": [
        "I'm Luna, your cheerful assistant 😊 How’s your day going?",
        "Just a few lines of code, but always ready to help!"
    ],
    "help": [
        "I can help you with admissions, courses, placements, and more! Ask me anything.",
        "Type or speak your question and Luna will assist!"
    ],
    "joke": [
        "Why did the chatbot break up with the user? Too many unresolved issues! 😂",
        "I asked my server for a joke... but it crashed 😅"
    ],
    "motivation": [
        "You got this! Luna believes in you! 🌟",
        "Push forward — you're doing amazing! 💪"
    ],
    "default": [
        "Hmm... I’m not sure I understood that. Try asking about admissions, courses, or events!",
        "Luna is still learning. Could you rephrase that?"
    ]
}


def translate_text(text, src_lang, target_lang="en"):
    return GoogleTranslator(source=src_lang, target=target_lang).translate(text)


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


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=5)
            return recognizer.recognize_google(audio)
        except:
            return "Sorry, I couldn't understand your speech. Please try again."


def chatbot_response(message):
    message = message.lower()

    mappings = {
        "greeting": ["hi", "hello", "hey"],
        "admission": ["admission", "apply"],
        "courses": ["course", "program"],
        "events": ["event", "fest", "seminar"],
        "contact": ["contact", "reach"],
        "facilities": ["facility", "facilities"],
        "Benefitsforstudents": ["benefit", "students", "counseling", "clubs"],
        "placements": ["placement", "job"],
        "about": ["about", "institution"],
        "how_are_you": ["how are you"],
        "help": ["help"],
        "joke": ["joke", "laugh"],
        "motivation": ["motivate", "inspire"]
    }

    for key, keywords in mappings.items():
        if any(kw in message for kw in keywords):
            return random.choice(RESPONSES[key])

    return random.choice(RESPONSES["default"])


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/voice', methods=['GET'])
def voice_route():
    text = recognize_speech()
    return jsonify({"voice_text": text})


@app.route('/chat', methods=['POST'])
def chat_route():
    data = request.get_json()
    user_msg = data.get("message", "")
    lang = data.get("language", "en")

    translated_msg = translate_text(user_msg, lang)
    reply = chatbot_response(translated_msg)
    emotion = analyze_sentiment(translated_msg)
    emoji = EMOTION_MAP.get(emotion, "🤖")

    return jsonify({
        "response": reply,
        "emotion": emotion.capitalize(),
        "avatar": emoji
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

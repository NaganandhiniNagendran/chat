from flask import Flask, render_template, request, jsonify
import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import speech_recognition as sr
import openai
import os

app = Flask(__name__)

# Set up OpenAI API key (Replace with your actual key or use an environment variable)
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Sample Diseases and Treatments in Tamil & English
disease_data = {
    "fever": "Drink plenty of fluids, rest, and take paracetamol if necessary.",
    "காய்ச்சல்": "பலமாக சாப்பிடவும், ஓய்வெடுக்கவும், மற்றும் பராசிட்டமால் மாத்திரை எடுத்துக்கொள்ளவும்.",
    "cold": "Stay hydrated, use steam inhalation, and take antihistamines if needed.",
    "சளி": "நீரை அதிகமாக குடிக்கவும், நீராவி உட்கொள்ளவும், மற்றும் தேவைப்பட்டால் மாத்திரைகள் எடுத்துக்கொள்ளவும்.",
    "flu": "Get plenty of rest, drink warm fluids, and take ibuprofen if needed.",
    "காய்ச்சல் (இணைந்த)": "நன்றாக ஓய்வெடுக்கவும், சூடான நீரை குடிக்கவும், மற்றும் தேவைப்பட்டால் ஐபுபுரோபென் எடுத்துக்கொள்ளவும்.",
    "headache": "Stay hydrated, get enough rest, and take a pain reliever like ibuprofen.",
    "தலைவலி": "நீரை அதிகமாக குடிக்கவும், ஓய்வெடுக்கவும், மற்றும் தேவைப்பட்டால் ஐபுபுரோபென் மாத்திரை எடுத்துக்கொள்ளவும்.",
    "diabetes": "Maintain a healthy diet, exercise regularly, and monitor blood sugar levels.",
    "நீரிழிவு": "ஆரோக்கியமான உணவு உண்ணவும், ஒழுங்காக உடற்பயிற்சி செய்யவும், மற்றும் இரத்த சர்க்கரை அளவை கண்காணிக்கவும்.",
    "hypertension": "Reduce salt intake, exercise, and follow your doctor's advice on medications.",
    "உயர் இரத்த அழுத்தம்": "உப்பு உட்கொள்வதை குறைக்கவும், உடற்பயிற்சி செய்யவும், மற்றும் மருத்துவரின் ஆலோசனையை பின்பற்றவும்.",
    "asthma": "Use inhalers as prescribed, avoid allergens, and practice breathing exercises.",
    "ஆஸ்துமா": "மருத்துவர் பரிந்துரைத்த இன்ஹேலர்களை பயன்படுத்தவும், அலர்ஜியை தவிர்க்கவும், மற்றும் மூச்சு பயிற்சிகள் செய்யவும்.",
    "covid-19": "Isolate, rest, stay hydrated, and consult a doctor if symptoms worsen.",
    "கோவிட்-19": "தனிமைப்படுத்திக்கொள்ளவும், ஓய்வெடுக்கவும், நீரை அதிகமாக குடிக்கவும், மற்றும் மருத்துவரை அணுகவும்.",
    "arthritis": "Take pain relievers, perform gentle exercises, and apply warm or cold compresses.",
    "முதுகுவலி": "வலி நீக்கி மாத்திரைகள் எடுத்துக்கொள்ளவும், மெதுவான உடற்பயிற்சிகள் செய்யவும், மற்றும் சூடான அல்லது குளிர்ந்த கட்டங்களை பயன்படுத்தவும்.",
    "stomach ulcer": "Avoid spicy foods, take antacids, and follow a bland diet.",
    "அழுகிய வயிறு": "சுவையான உணவுகளை தவிர்க்கவும், ஆக்சிட் மாத்திரைகள் எடுத்துக்கொள்ளவும், மற்றும் சோம்பலான உணவு உண்ணவும்.",
    "allergy": "Avoid allergens, use antihistamines, and apply creams for itching.",
    "அலர்ஜி": "அலர்ஜிகளையும் தவிர்க்கவும், ஆன்டிஹிஸ்டாமின்கள் பயன்படுத்தவும், மற்றும் கசப்புக்கு க்ரீம் பயன்படுத்தவும்.",
    "chronic kidney disease": "Monitor kidney function, reduce salt intake, and follow your doctor's treatment plan.",
    "நிரந்தர சிறுநீரக நோய்": "சிறுநீரக செயல்பாடுகளை கண்காணிக்கவும், உப்பை குறைக்கவும், மற்றும் மருத்துவரின் மருத்துவ திட்டத்தை பின்பற்றவும்.",
    "gastroenteritis": "Stay hydrated, avoid dairy, and eat bland foods like toast and rice.",
    "முதுகொடுத்தகை": "நீரை அதிகமாக குடிக்கவும், பாலூட்டும் உணவுகளுக்கு தவிர்க்கவும், மற்றும் ரொட்டி மற்றும் அரிசி போன்ற சோம்பலான உணவுகளை உண்ணவும்.",
    "pneumonia": "Take antibiotics as prescribed, stay hydrated, and rest.",
    "நரம்புத்தொற்று": "மருத்துவர் பரிந்துரைத்த இந்தி மாத்திரைகளை எடுத்துக்கொள்ளவும், நீரை அதிகமாக குடிக்கவும், மற்றும் ஓய்வெடுக்கவும்.",
    "anemia": "Take iron supplements, eat iron-rich foods, and follow your doctor's advice.",
    "சுற்றுச்சூழல் குறைபாடு": "இரும்பு மாத்திரைகள் எடுத்துக்கொள்ளவும், இரும்பு நிறைந்த உணவுகளை உண்ணவும், மற்றும் மருத்துவரின் ஆலோசனையை பின்பற்றவும்.",
    "skin rash": "Use moisturizing creams, avoid scratching, and apply hydrocortisone cream for inflammation.",
    "தாடி பருகும்": "தூய்மை க்ரீம்கள் பயன்படுத்தவும், கசக்காதிருப்பதற்காக தவிர்க்கவும், மற்றும் இடுக்குமாற்றம் க்ரீம் பயன்படுத்தவும்.",
    "migraine": "Rest in a dark, quiet room, stay hydrated, and take migraine medication as prescribed.",
    "மிகிரேன்": "ஒரு கருப்பு, அமைதியான அறையில் ஓய்வெடுக்கவும், நீரை அதிகமாக குடிக்கவும், மற்றும் மிகிரேன் மருத்துவம் எடுத்துக்கொள்ளவும்.",
    "epilepsy": "Take antiepileptic drugs as prescribed and avoid triggers.",
    "உறுப்பு குருட்டு நோய்": "மருத்துவர் பரிந்துரைத்த உடற்பயிற்சி மருந்துகளை எடுத்துக்கொள்ளவும், ஊக்குவிப்புகளை தவிர்க்கவும்.",
    "back pain": "Apply heat or cold compresses, rest, and take pain relievers if needed.",
    "பின் வலி": "சூடான அல்லது குளிர்ந்த கட்டங்களை பயன்படுத்தவும், ஓய்வெடுக்கவும், மற்றும் தேவையானால் வலி நீக்கிகள் எடுத்துக்கொள்ளவும்.",
    "insomnia": "Follow a regular sleep routine, limit caffeine intake, and practice relaxation techniques.",
    "அறிந்துவிடாதவை": "ஒரு பரிபாலனமான தூக்க அட்டவணையை பின்பற்றவும், காபி குறைக்கவும், மற்றும் ஆறுதல் பயிற்சிகளை செய்யவும்.",
    "hepatitis": "Avoid alcohol, follow your doctor's treatment plan, and take antiviral medication if prescribed.",
    "கல்லீரல் நோய்": "ஆல்கஹால் தவிர்க்கவும், மருத்துவரின் மருத்துவ திட்டத்தை பின்பற்றவும், மற்றும் பரிந்துரைத்துவிட்டால் வைரஸ் எதிர்ப்பு மருந்து எடுத்துக்கொள்ளவும்.",
    "cancer": "Consult your doctor for treatment options like chemotherapy, radiation, or surgery.",
    "புற்றுநோய்": "மருத்துவரை அணுகி, கொம்பிப்பை, கதிரவினை அல்லது அறுவை சிகிச்சை போன்ற மருத்துவத் தேர்வுகளை பரிந்துரைக்கவும்.",
    "gout": "Take medications like colchicine, avoid purine-rich foods, and rest the affected joint.",
    "குட்டி": "கொல்சிசின் மாத்திரைகள் போன்ற மருந்துகளை எடுத்துக்கொள்ளவும், புரினை நிறைந்த உணவுகளை தவிர்க்கவும், மற்றும் பாதிக்கப்பட்ட குழாயில் ஓய்வெடுக்கவும்."
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input'].strip().lower()
        if not user_input:
            return jsonify({'response': 'Please enter a message.'})

        response = disease_data.get(user_input, "I'm not sure about that. Please consult a doctor.")
        return jsonify({'response': response})
    return render_template('index.html')

@app.route('/speech', methods=['POST'])
def speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            try:
                user_input = recognizer.recognize_google(audio, language="en-US")
            except sr.UnknownValueError:
                user_input = recognizer.recognize_google(audio, language="ta-IN")
            response = disease_data.get(user_input.lower(), "I'm not sure about that. Please consult a doctor.")
            return jsonify({'user_input': user_input, 'response': response})
        except sr.UnknownValueError:
            return jsonify({'response': "Sorry, I couldn't understand. Try again."})
        except sr.RequestError:
            return jsonify({'response': "Error connecting to speech service."})

if __name__ == '__main__':
    app.run(debug=True)
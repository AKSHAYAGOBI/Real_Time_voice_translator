from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from gtts import gTTS
import os
from playsound import playsound
from googletrans import Translator

app = Flask(__name__)

translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak something...")
        audio = recognizer.listen(source)  # Listen for the first phrase
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"error": "Sorry, I could not understand the audio."})
        except sr.RequestError as e:
            return jsonify({"error": "Could not request results from Google Speech Recognition service; {0}".format(e)})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data['text']
    target_language = data['language']
    
    translated = translator.translate(text, dest=target_language)
    return jsonify({"translated_text": translated.text})

@app.route('/speak', methods=['POST'])
def speak():
    text = request.json['text']
    language = 'en'  # Set your desired output language for speech
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save('output.mp3')
    playsound('output.mp3')  # Play the converted file
    os.remove('output.mp3')  # Remove the file after playing
    return jsonify({"message": "Speech output completed."})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from gtts import gTTS
import os
import pygame
import time
pygame.mixer.init()
from deep_translator import GoogleTranslator

app = Flask(__name__)

translator = GoogleTranslator(source='auto')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    data = request.json or {}
    source_lang = data.get('source_lang', 'en')
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Please speak something...")
        audio = recognizer.listen(source, timeout=5)
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio, language=source_lang)
            print("You said: " + text)
            return jsonify({"text": text})
        except sr.WaitTimeoutError:
            return jsonify({"error": "No speech detected within 5 seconds. Try again."})
        except sr.UnknownValueError:
            return jsonify({"error": "Sorry, I could not understand the audio."})
        except sr.RequestError as e:
            return jsonify({"error": "Could not request results from Google Speech Recognition service; {0}".format(e)})

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data['text']
    source_lang = data.get('source_lang', 'auto')
    target_language = data['language']

    translated = translator.translate(text, source=source_lang, target_language=target_language)
    return jsonify({"translated_text": translated})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data['text']
    language = data.get('language', 'en')
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save('output.mp3')
    pygame.mixer.music.load('output.mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    try:
        os.remove('output.mp3')
    except OSError:
        pass  # File already deleted or not found
    return jsonify({"message": "Speech output completed."})

if __name__ == '__main__':
    app.run(debug=True)

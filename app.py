import os
from flask import Flask, request, jsonify
from translate import Translator
from config import *

app = Flask(__name__)
translator = Translator(MODEL_PATH)

app.config["DEBUG"] = False

def return_success(data):
    return jsonify({
        "data": data
    })

def return_error(err_code, err_msg):
    return jsonify({
        "error": {
            "code": err_code,
            "message": err_msg,
        }
    })

@app.route('/', methods=["GET"])
def health_check():
    return return_success("Service is up and running")

@app.route('/lang_routes', methods = ["GET"])
def get_lang_route():
    lang = request.args['lang']

    all_langs = translator.get_supported_langs()
    lang_routes = [l for l in all_langs if l[0] == lang]

    return return_success(lang_routes)

@app.route('/supported_languages', methods=["GET"])
def get_supported_languages():
    langs = translator.get_supported_langs()

    return return_success(langs)

@app.route('/translate', methods=["POST"])
def get_prediction():
    source = request.json['source']
    target = request.json['target']
    text = request.json['text']
    chunk_num = request.json['chunk_num']

    translation = translator.translate(source, target, text)

    return return_success({
        "text": translation,
        "chunk_num": chunk_num,
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

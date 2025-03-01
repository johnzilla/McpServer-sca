"""
Sample code file for testing the analyzer
Contains multiple imports and potential vulnerabilities
"""
import requests
from flask import Flask, request, jsonify
import jwt
import pandas as pd
import numpy as np
from cryptography.fernet import Fernet
import yaml
from PIL import Image

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    # Potential security issue: uses unsafe yaml load
    config = yaml.load(request.data)
    
    # Makes external HTTP request
    response = requests.get(config['api_url'])
    
    # Uses older JWT methods
    token = jwt.encode({'data': response.json()}, 'secret', algorithm='HS256')
    
    return jsonify({'token': token})

def process_image(path):
    # Image processing with PIL
    img = Image.open(path)
    img = img.resize((100, 100))
    return img

if __name__ == '__main__':
    app.run(debug=True)

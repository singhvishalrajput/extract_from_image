from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import os
from PIL import Image
import io
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize EasyOCR reader once for the entire application
reader = easyocr.Reader(['en'])

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Only PNG and JPEG files are supported'}), 400
    
    try:
        # Read the image file
        image_bytes = file.read()
        
        # Check file size
        if len(image_bytes) > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File size exceeds 4MB limit'}), 400
        
        # Convert bytes to image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL Image to numpy array
        image_np = np.array(image)
        
        # Perform OCR on numpy array
        result = reader.readtext(image_np)
        
        # Extract text from results
        extracted_text = '\n'.join([text[1] for text in result])
        
        if not extracted_text:
            return jsonify({
                'success': False,
                'error': 'No text was detected in the image'
            }), 400
        
        return jsonify({
            'success': True,
            'text': extracted_text,
            'fileType': file.filename.rsplit('.', 1)[1].lower()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Error processing image: {str(e)}"
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
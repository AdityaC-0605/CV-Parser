from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from parser import ResumeParser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse-resume', methods=['POST'])
def parse_resume():
    try:
        # Check if file is present in request
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        
        # If user doesn't select file
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only PDF and DOCX files are allowed'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure upload directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        # Save the file
        try:
            file.save(filepath)
        except Exception as e:
            return jsonify({'error': f'Error saving file: {str(e)}'}), 500
        
        try:
            # Parse the resume
            parser = ResumeParser()
            result = parser.parse_resume(filepath)
            
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            
            if not result:
                return jsonify({'error': 'Failed to parse resume'}), 500
            
            # Return the parsed results
            return jsonify(result)
            
        except Exception as e:
            # Clean up the file in case of error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error parsing resume: {str(e)}'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
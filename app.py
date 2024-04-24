import os
import re
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import pandas as pd

app = Flask(__name__)

def extract_info_from_pdf(uploaded_file):
    # Save the uploaded file to a temporary location
    filename = secure_filename(uploaded_file.filename)
    temp_filepath = os.path.join("uploads", filename)
    uploaded_file.save(temp_filepath)
    
    text = ""
    email = ""
    contact = ""
    with open(temp_filepath, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
    
    email_match = re.search(email_pattern, text)
    if email_match:
        email = email_match.group(0)
    
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact = phone_match.group(0)
    
    # Delete the temporary file after extracting information
    os.remove(temp_filepath)
    
    return {'Text': text, 'Email': email, 'Contact': contact}

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            cv_data = extract_info_from_pdf(uploaded_file)
            df = pd.DataFrame([cv_data])
            df.to_excel("cv_info.xlsx", index=False, engine='openpyxl')  # Specify the engine as 'openpyxl' and change the file extension to '.xlsx'
            return send_file("cv_info.xlsx", as_attachment=True)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')

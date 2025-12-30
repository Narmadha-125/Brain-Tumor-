from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
import joblib
from PIL import Image
import os
import random
from fpdf import FPDF
import datetime
import base64
import io
from io import BytesIO
import base64
from flask import request, jsonify
from deep_translator import GoogleTranslator

translated_text = GoogleTranslator(source='auto', target='ta').translate("Hello")

app = Flask(__name__)
model = joblib.load('model.pkl')

# Healthy quotes
quotes = [
    "A healthy outside starts from the inside.",
    "Your body hears everything your mind says — stay positive.",
    "Eat well, move more, feel strong.",
    "Healing begins with awareness.",
    "Health is the crown on the well person’s head.",
    "Health is wealth. Protect your mind.",
    "Early detection saves lives.",
    "A healthy outside starts from the inside.",
    "Wellness begins with awareness."
]

# Doctor suggestions
doctors = [
    {"name": "Dr. Aarthi Ramesh", "hospital": "Apollo Hospitals, Chennai"},
    {"name": "Dr. Vikram Shetty", "hospital": "Manipal Hospitals, Bangalore"},
    {"name": "Dr. Rajesh Iyer", "hospital": "AIIMS, Delhi"},
    {"name": "Anita Raj", "hospital": "Apollo Hospitals", "location": "Chennai"},
    {"name": "Ravi Kumar", "hospital": "AIIMS", "location": "New Delhi"},
    {"name": "Sahana N", "hospital": "CMC", "location": "Vellore"},
    {"name": "Dev Sharma", "hospital": "Fortis", "location": "Mumbai"}
]

# Route for index.html
@app.route('/')
def index():
    quote = random.choice(quotes)
    return render_template('index.html', quote=quote)

# Predict Route
@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return "No image uploaded", 400

    file = request.files['image']
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Limit to 2MB

    # Process image
    img = Image.open(file).convert('L').resize((100, 100))
    img_array = np.array(img).flatten().reshape(1, -1)
    pred = model.predict(img_array)[0]

    img.seek(0)
    scan_bytes = file.read()
    scan_base64 = "data:image/jpeg;base64," + base64.b64encode(scan_bytes).decode('utf-8')

    if pred == 1:
        result = "Tumor Detected"
        suggestions = {
            "do": ["Eat leafy greens", "Exercise regularly", "Drink plenty of water"],
            "dont": ["Avoid processed meats", "Limit sugar", "Do not smoke or drink"],
            "eat": ["Fruits", "Omega-3 rich foods", "Turmeric"],
            "avoid": ["Red meat", "Sugary drinks", "Fried foods"]
        }
        doctor = random.choice(doctors)
    else:
        result = "No Tumor Detected"
        suggestions = {
            "do": ["Maintain healthy lifestyle"],
            "dont": ["Avoid skipping meals"],
            "eat": ["Balanced diet"],
            "avoid": ["Overeating"]
        }
        doctor = None
        img_io = BytesIO()
        img.save(img_io, 'PNG')  # or 'JPEG' based on your upload
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()

# Pass to HTML


    return render_template(
        'result.html',
        result=result,
        suggestions=suggestions,
        doctor=doctor,
        quote=random.choice(quotes),
        scan_image=scan_base64,
        current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
        current_time=datetime.datetime.now().strftime("%H:%M:%S")
    )


@app.route('/ask_chatbot', methods=['POST'])
def ask_chatbot():
    data = request.get_json()
    question = data.get('question', '')

    # Simple rule-based answers (you can use NLP/ML later)
    responses = {
        "what is brain tumor": "A brain tumor is an abnormal growth of cells in the brain.",
        "symptoms": "Symptoms include headaches, nausea, vision problems, and seizures.",
        "treatment": "Treatments include surgery, radiation therapy, and chemotherapy.",
        "do's": "Follow your doctor's instructions, eat healthy, stay hydrated.",
        "don'ts": "Avoid stress, unhealthy food, and self-medication.",
        "what to eat": "Fresh fruits, vegetables, lean protein, whole grains.",
        "what to avoid": "Processed foods, sugar, alcohol, tobacco.",
        "symptoms": "Symptoms include headaches, nausea, vision problems, and seizures.",
        "treatment": "Treatments include surgery, radiation therapy, and chemotherapy.",
        "do's": "Follow your doctor's instructions, eat healthy, stay hydrated.",
        "don'ts": "Avoid stress, unhealthy food, and self-medication.",
        "what to eat": "Fresh fruits, vegetables, lean protein, whole grains.",
        "what to avoid": "Processed foods, sugar, alcohol, tobacco.",
       
    "is brain tumor cancer": "Some brain tumors are cancerous (malignant), others are noncancerous (benign).",
    "can brain tumor cause memory loss": "Yes, depending on its location, a brain tumor can affect memory and thinking.",
    "how is brain tumor diagnosed": "Brain tumors are diagnosed through MRI, CT scans, and biopsy.",
    "is brain tumor curable": "Some brain tumors can be cured with early detection and proper treatment.",
    "how long can you live with a brain tumor": "Life expectancy depends on the tumor type, location, and treatment.",
    "can stress cause brain tumor": "No, stress does not directly cause brain tumors.",
    "types of brain tumor": "There are over 120 types including gliomas, meningiomas, and pituitary tumors.",
    "is brain tumor painful": "It can cause headaches and pressure in the head.",
    "can brain tumor be hereditary": "Some types may be linked to genetic conditions.",
    "how does chemotherapy help": "It kills or stops the growth of cancerous cells.",
    "can brain tumor affect vision": "Yes, tumors near the optic nerve can cause vision problems.",
    "best hospital for brain tumor treatment": "Top hospitals include CMC, AIIMS, and Apollo in India.",
    "can kids get brain tumors": "Yes, though it's rarer than in adults.",
    "early signs of brain tumor": "Frequent headaches, nausea, blurred vision, and confusion.",
    "can mobile radiation cause brain tumor": "There\u2019s no strong scientific evidence to support this.",
    "how to prevent brain tumor": "Avoiding radiation exposure and leading a healthy life may help.",
    "brain tumor surgery risks": "Includes infection, bleeding, and neurological issues.",
    "how long does brain tumor surgery take": "Usually 3 to 6 hours depending on the case.",
    "recovery time after brain surgery": "It may take weeks to months.",
    "can brain tumor reoccur": "Yes, some tumors can come back.",
    "who is narmadha":"narmadha is joel's wife."

        
    }

    lower_q = question.lower()
    answer = "Sorry, I don't know that. Please ask something else."

    for key in responses:
        if key in lower_q:
            answer = responses[key]
            break

    # Detect and auto-translate to Tamil if input is in Tamil
    if any(ord(char) > 3000 for char in question):  # Tamil Unicode range
        translator = Translator()
        answer = translator.translate(answer, dest='ta').text

    return jsonify({'answer': answer})

# Generate downloadable PDF report
@app.route('/download_report', methods=['POST'])
@app.route('/download_report', methods=['POST'])
def download_report():
    result = request.form.get('result')
    doctor = request.form.get('doctor')
    scan_image = request.form.get('scan_image')
    date = request.form.get('date')
    time = request.form.get('time')
    dos = request.form.get('dos', '').replace("\\n", "\n")
    donts = request.form.get('donts', '').replace("\\n", "\n")
    eat = request.form.get('eat', '').replace("\\n", "\n")
    avoid = request.form.get('avoid', '').replace("\\n", "\n")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(200, 10, txt="Brain Tumor Detection Report", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {date} | Time: {time}", ln=True)
    pdf.cell(200, 10, txt=f"Result: {result}", ln=True)

    if doctor:
        pdf.cell(200, 10, txt=f"Recommended Doctor: {doctor}", ln=True)

        image_data = request.form.get('image_data', '')
    if image_data:
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image.save(f"{report_path}/scan_image.png")
        pdf.image(f"{report_path}/scan_image.png", x=10, y=pdf.get_y(), w=100)


    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Do's:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, dos)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="Don'ts:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, donts)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="What to Eat:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, eat)

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, txt="What to Avoid:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, avoid)

    # ✅ Convert to BytesIO for Flask
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_stream = io.BytesIO(pdf_bytes)
    return send_file(pdf_stream, as_attachment=True, download_name="Brain_Tumor_Report.pdf")



# Template filter for line breaks
@app.template_filter('nl2br')
def nl2br(value):
    return value.replace("\n", "<br>")

# Flask server start
if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)

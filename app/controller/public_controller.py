import requests
from flask import Blueprint, request, jsonify
from app.models import Contact
from app import db

# Flask Blueprint
pubcontroller = Blueprint('public_controller', __name__, template_folder='templates/public')

RECAPTCHA_SECRET_KEY = "6LcwwHEsAAAAALc-XNpZSfECBEwUhgQcRMVIhW1N"
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

@pubcontroller.route('/new-contact', methods=['POST'])
def new_contact():
    # 1. Kunin ang data (suportado ang Form Data at JSON)
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    recaptcha_token = request.form.get('g-recaptcha-response') 

    # 2. Simple validation
    if not all([name, email, subject, message, recaptcha_token]):
        return jsonify({"error": "All fields, including reCAPTCHA, are required"}), 400
    
    # 3. VERIFY RECAPTCHA
    try:
        payload = {
            'secret': RECAPTCHA_SECRET_KEY,
            'response': recaptcha_token,
            'remoteip': request.remote_addr
        }
        response = requests.post(VERIFY_URL, data=payload, timeout=10)
        result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"reCAPTCHA Connection Error: {e}")
        return jsonify({"error": "Internal server error during verification"}), 500

    if not result.get("success") or result.get("score", 0) < 0.5:
        return jsonify({
            "error": "reCAPTCHA verification failed. Too many bot-like signals.",
            "details": result.get("error-codes", [])
        }), 400
    try:
        contact_entry = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        db.session.add(contact_entry)
        db.session.commit()
        
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"DATABASE ERROR: {e}")
        return jsonify({"error": "Failed to save message to database"}), 500
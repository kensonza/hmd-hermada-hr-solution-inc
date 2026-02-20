from flask import Blueprint, request, jsonify
from app.models import Contact
from app import db
#from app import db, socketio

# Flask Blueprint (Public Controller)
pubcontroller = Blueprint('public_controller', __name__, template_folder='templates/public')

### API Endpoint for Contact Form Submission ###
@pubcontroller.route('/new-contact', methods=['POST'])
def new_contact():

    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    recaptcha_token = request.form.get('g-recaptcha-response') 

    # Simple validation
    if not (name and email and subject and message):
        return jsonify({"error": "All fields are required"}), 400
    
    # ---- VERIFY RECAPTCHA ----
    secret_key = "6LcwwHEsAAAAALc-XNpZSfECBEwUhgQcRMVIhW1N"  # g-recaptcha secret key
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': secret_key,
        'response': recaptcha_token
    }
    response = request.post(verify_url, data=payload)
    result = response.json()

    if not result.get("success") or result.get("score", 0) < 0.5:
        return jsonify({"error": "reCAPTCHA verification failed. Please try again."}), 400

    try:
        new_contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        # Save to database
        db.session.add(new_contact)
        db.session.commit()
        
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500
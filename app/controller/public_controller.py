from flask import Blueprint, request, jsonify
from app.models import Contact
from app import db, socketio

# Flask Blueprint (Public Controller)
pubcontroller = Blueprint('public_controller', __name__, template_folder='templates/public')

### API Endpoint for Contact Form Submission ###
@pubcontroller.route('/new-contact', methods=['POST'])
def new_contact():

    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Simple validation
    if not (name and email and subject and message):
        return jsonify({"error": "All fields are required"}), 400
    try:
        # Create new Contact instance
        new_contact = Contact(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        # Save to database
        db.session.add(new_contact)
        db.session.commit()

        # Emit a socket event for real-time updates
        socketio.emit('new_contact', {
            "token_id": new_contact.token_id,
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "date_created": new_contact.date_created.strftime("%Y-%m-%d %H:%M:%S")
        }, namespace='/')
        
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        db.session.rollback()  # IMPORTANT: to prevent the session from getting stuck
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500  # temporarily show real error
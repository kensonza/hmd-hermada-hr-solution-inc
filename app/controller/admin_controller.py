import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from app.models import Contact
from app.models import Users
from app.models import Newsletter
from app.models import NewsletterSubscribers
from app import db
#from app import db, socketio
from app.routes.admin_routes import admin_contact_inquiries
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

admcontroller = Blueprint('admin_controller', __name__, template_folder='templates/admin')

# Let's Talk / Contact (Contact Inquiries).
@admcontroller.route('/api/contact/inquiries')
def get_inquiries():
    
    inquiries = db.session.execute(db.select(Contact).order_by(Contact.date_created.desc())).scalars().all()

    data = [{
        "token_id": i.token_id,
        "name": i.name,
        "email": i.email,
        "subject": i.subject,
        "message": i.message,
        "date_created": i.date_created.strftime("%Y-%m-%d %H:%M:%S")
    } for i in inquiries]

    return jsonify(data)


# Our Newsletter (Newsletter Subscribers).
@admcontroller.route('/api/newsletter-subscribers')
def get_newsletter_subscriber():
    
    newsletter_subscriber = db.session.execute(db.select(NewsletterSubscribers).order_by(NewsletterSubscribers.date_created.desc())).scalars().all()

    data = [{
        "ns_token_id": i.ns_token_id,
        "ns_email": i.ns_email,
        "ns_status": i.ns_status,
        "date_created": i.date_created.strftime("%Y-%m-%d %H:%M:%S")
    } for i in newsletter_subscriber]

    return jsonify(data)

# Our Newsletter (HMD Newsletter).
@admcontroller.route('/api/newsletters')
def get_newsletters():
    newsletters = db.session.execute(db.select(Newsletter).order_by(Newsletter.date_created.desc())).scalars().all()

    data = [{
        "nl_token_id": n.nl_token_id,
        "nl_title": n.nl_title,
        "nl_subject": n.nl_subject,
        "nl_description": n.nl_description,
        "nl_status": n.nl_status,
        "date_created": n.date_created.strftime("%Y-%m-%d %H:%M:%S")
    } for n in newsletters]

    return jsonify(data)

@admcontroller.route('/admin/add-newsletter', methods=['POST'])
def add_newsletter():
    try:
        nl_title = request.form.get('nl_title')
        nl_subject = request.form.get('nl_subject')
        nl_description = request.form.get('nl_description')

        if not nl_title or not nl_subject or not nl_description:
            return jsonify({"error": "All fields are required."}), 400

        # I-save sa Database (Tugma sa model mo)
        new_newsletter = Newsletter(
            nl_title=nl_title,
            nl_subject=nl_subject,
            nl_description=nl_description,
            nl_status="Active"
        )

        db.session.add(new_newsletter)
        db.session.commit()

        return jsonify({"message": "Newsletter created successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admcontroller.route('/admin/update-newsletter/<nl_token_id>', methods=['PUT'])
def update_newsletter(nl_token_id):
    try:
        data = request.get_json()
        
        newsletter = Newsletter.query.filter_by(nl_token_id=nl_token_id).first()
        
        if not newsletter:
            return jsonify({"error": "Newsletter not found."}), 404

        # Update ang fields
        newsletter.nl_title = data.get('nl_title')
        newsletter.nl_subject = data.get('nl_subject')
        newsletter.nl_description = data.get('nl_description')
        newsletter.nl_status = data.get('nl_status', 'Active')

        db.session.commit()

        return jsonify({"message": "Newsletter updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admcontroller.route('/admin/delete-newsletter/<nl_token_id>', methods=['DELETE'])
def delete_newsletter(nl_token_id):
    try:
        newsletter = Newsletter.query.filter_by(nl_token_id=nl_token_id).first()
        
        if not newsletter:
            return jsonify({"error": "Newsletter not found."}), 404

        db.session.delete(newsletter)
        db.session.commit()

        return jsonify({"message": "Newsletter deleted successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

# User Accounts (Users).
@admcontroller.route('/api/user/accounts')
def get_user_accounts():
    
    user_accounts = db.session.execute(db.select(Users).order_by(Users.date_created.desc())).scalars().all()

    data = [{
        "user_token_id": i.user_token_id,
        "first_name": i.first_name,
        "last_name": i.last_name,
        "nickname": i.nickname,
        "email": i.email,
        "department": i.department,
        "role": i.role,
        "status": i.status,
        "date_created": i.date_created.strftime("%Y-%m-%d %H:%M:%S")
    } for i in user_accounts]
    
    return jsonify(data)

@admcontroller.route('/admin/new-user', methods=['POST'])
def new_user():

    first_name = request.form.get('txtFName')
    last_name = request.form.get('txtLName')
    nickname = request.form.get('txtNickName')
    email = request.form.get('txtEmail')
    password = request.form.get('txtPassword')
    department = request.form.get('txtDepartment')
    role = request.form.get('txtRole')
    status = request.form.get('txtStatus')

    if not (first_name and last_name and nickname and email and password and department and role and status):
        return jsonify({"error": "All fields are required"}), 400
    
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": f"The email '{email}' is already in use!"}), 400

    try:
        new_user = Users(
            first_name=first_name,
            last_name=last_name,
            nickname=nickname,
            email=email,
            password=password,
            department=department,
            role=role,
            status=status
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User created successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500

@admcontroller.route('/admin/edit-user', methods=['POST'])
def edit_user():
    user_id = request.form.get('user_id')
    first_name = request.form.get('txtFName')
    last_name = request.form.get('txtLName')
    nickname = request.form.get('txtNickName')
    email = request.form.get('txtEmail')
    department = request.form.get('txtDepartment')
    role = request.form.get('txtRole')
    status = request.form.get('txtStatus')

    try:
        user = Users.query.filter_by(user_token_id=user_id).first()
        if not user:
            return jsonify({"error": "User not found"})

        user.first_name = first_name
        user.last_name = last_name
        user.nickname = nickname
        user.email = email
        user.department = department
        user.role = role
        user.status = status

        db.session.commit()

        return jsonify({"message": "User updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})

@admcontroller.route('/admin/change-password', methods=['POST'])
def change_password_user():
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not user_id or not new_password:
        return jsonify({"error": "Missing required fields"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    try:
        user = Users.query.filter_by(user_token_id=user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.password = hashed_password 
        
        db.session.commit()

        return jsonify({"message": "Password updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@admcontroller.route("/admin/delete-user/<user_token_id>", methods=["POST"])
def delete_user(user_token_id):
    try:
        user = Users.query.filter_by(user_token_id=user_token_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        user_fullname = f"{user.first_name} {user.last_name}"
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": f"Successfully deleted {user_fullname}"}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
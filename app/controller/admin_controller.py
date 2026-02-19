from flask import Blueprint, request, jsonify
from app.models import Contact
from app.models import Users
from app import db
#from app import db, socketio
from app.routes.admin_routes import admin_contact_inquiries
from werkzeug.security import generate_password_hash

# Flask Blueprint (Admin Controller)
admcontroller = Blueprint('admin_controller', __name__, template_folder='templates/admin')

### API endpoint to get contact inquiries for admin dashboard ###
@admcontroller.route('/api/contact/inquiries')
def get_inquiries():
    
    # Get all contact inquiries ordered by date created (newest first)
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

### API endpoint to get user accounts for admin dashboard ###
@admcontroller.route('/api/user/accounts')
def get_user_accounts():
    
    # Get all user accounts ordered by date created (newest first)
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

### API Endpoint for User Accounts Form Submission ###
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

    # Simple validation
    if not (first_name and last_name and nickname and email and password and department and role and status):
        return jsonify({"error": "All fields are required"}), 400
    
    # Check if email already exists
    existing_user = Users.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": f"The email '{email}' is already in use!"}), 400

    try:
        # Create new Contact instance
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
        # Save to database
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User created successfully!"}), 200
    except Exception as e:
        db.session.rollback()  # IMPORTANT: to prevent the session from getting stuck
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500  # temporarily show real error


### API Endpoint for Edit User Form Submission ###
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


### API Endpoint for Change Password Form Submission ###
@admcontroller.route('/admin/change-password', methods=['POST'])
def change_password_user():
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # 1. Basic Validation (Backend side)
    if not user_id or not new_password:
        return jsonify({"error": "Missing required fields"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Passwords do not match!"}), 400

    try:
        user = Users.query.filter_by(user_token_id=user_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        user.password = hashed_password  # Siguraduhin na 'password' ang column name mo
        
        db.session.commit()

        return jsonify({"message": "Password updated successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


### API Endpoint for Delete User ###
@admcontroller.route("/admin/delete-user/<user_token_id>", methods=["POST"])
def delete_user(user_token_id):
    try:
        user = Users.query.filter_by(user_token_id=user_token_id).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404

        # I-save ang pangalan bago i-delete
        user_fullname = f"{user.first_name} {user.last_name}"
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": f"Successfully deleted {user_fullname}"}), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}") # Lalabas ito sa terminal mo
        return jsonify({"error": str(e)}), 500
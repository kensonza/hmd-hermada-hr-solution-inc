from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from app.models import Users

# Define Blueprint
auth = Blueprint('auth', __name__)

# Login
@auth.route('/hidden/admin-panel/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = Users.query.filter_by(email = request.form['txtEmail']).first()
        
        if user is not None:
            # Verify password using Werkzeug
            if check_password_hash(user.password, request.form['txtPassword']):
                if user.status == 'Inactive':
                    flash('Your account is locked. Please call your administrator.', 'error')
                else:
                    session['loggedin'] = True
                    session['token_id'] = user.user_token_id
                    session['nickname'] = user.nickname
                    session['email'] = user.email
                    session['role'] = user.role

                    # Redirect to HOME page
                    return redirect(url_for('admin_route.admin_index'))

            else:
                flash('Incorrect Username or Password.', 'error')
        else:
            flash('Incorrect Username or Password.', 'error')
    
    # Back to login page if the user credential does not match
    return render_template('admin/login.html')

# Logout
@auth.route('/hidden/admin-panel/logout')
def logout():
    # Destroy all session
    session.pop('loggedin', None)
    session.pop('user_token_id', None)
    session.pop('nickname', None)
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('auth.login'))
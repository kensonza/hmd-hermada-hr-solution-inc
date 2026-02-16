from flask import Blueprint, render_template, session
from app.controller.login_required import login_required
from app.extension import db
from app.models.contact import Contact

# Flask Blueprint (Admin Route) 
admroute = Blueprint('admin_route', __name__, template_folder='templates/admin') 

# Index (Dashboard)
@admroute.route('/hidden/admin-panel/dashboard')
@login_required
def admin_index():

    # Get member session
    user_session = session['nickname']

    return render_template('admin/index.html', adnav_active='index', user_session = user_session)


# Lets Talk / Contact Page
@admroute.route('/hidden/admin-panel/contact-inquiries')
@login_required
def admin_contact_inquiries():

    # Get member session
    user_session = session['nickname']


    return render_template('admin/contact-inquiries.html', parentnav_active='sites', adnav_active='contact-inquiries', user_session = user_session)


#### Settings ####

# User Accounts
@admroute.route('/hidden/admin-panel/user-accounts')
@login_required
def admin_user_accounts():

    # Get member session
    user_session = session['nickname']


    return render_template('admin/user-accounts.html', adnav_active='user-accounts', user_session = user_session)
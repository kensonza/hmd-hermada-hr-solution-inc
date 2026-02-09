from flask import Blueprint, render_template, request, session
from app.views.login_required import login_required
from app.extension import db

from app.views import admroute

# Admin Index (Home Page)
@admroute.route('/hidden/admin-panel/dashboard')
@login_required
def admin_index():

    # Get member session
    user_session = session['full_name']

    return render_template('admin/index.html', user_session = user_session)
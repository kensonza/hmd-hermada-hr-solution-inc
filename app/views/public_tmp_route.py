# This module is for templates linked routes.
from flask import Blueprint, render_template
 
from app.views import tmproute

# Services Page Linked Route
@tmproute.route('/services/details')
def services_details():
    return render_template('public/services-details.html', nav_active='services')

# Careers Page Linked Route
@tmproute.route('/careers/job')
def careers_job():
    return render_template('public/careers-job.html', nav_active='careers')

import os
import requests
import re
import logging
import uuid
from os import name
from app.controller.invalidate_cache import invalidate_cache
from flask import Blueprint, request, jsonify, current_app, url_for
from wtforms.validators import email
from app.models import Contact, Newsletter, NewsletterSubscribers
from app import db
from flask_mail import Message
from datetime import datetime
from zoneinfo import ZoneInfo

pubcontroller = Blueprint('public_controller', __name__, template_folder='templates/public')

VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

# --- REUSABLE BREVO SEND FUNCTION ---
def send_via_brevo(subject, html_content, to_email, to_name=None, reply_to=None):
    api_key = os.getenv('BREVO_API_KEY')
    if not api_key:
        logging.error("BREVO_API_KEY not found in environment variables.")
        return False

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json"
    }

    payload = {
        "sender": {"name": "HMD Hermada", "email": "ask@hmdhermada.com"},
        "to": [{"email": to_email, "name": to_name or to_email}],
        "subject": subject,
        "htmlContent": html_content
    }

    if reply_to:
        payload["replyTo"] = {"email": reply_to}

    try:
        response = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201, 202]:
            return True
        logging.error(f"Brevo API Error: {response.text}")
        return False
    except Exception as e:
        logging.error(f"Network Error during Brevo send: {e}")
        return False

# Let's Talk / Contact (Contact Form Submission).
# Manager or Concerned Personnel Email Template.
def generate_contact_html(name, email, subject, message_content):
    # I-process ang message para gumana ang line breaks sa HTML
    formatted_message = message_content.replace('\n', '<br>')
    
    template = """
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>New Website Inquiry</title>
        <style>
          body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
          table {{ border-collapse: collapse !important; }}
          body {{ margin: 0; padding: 0; width: 100%; font-family: Arial, sans-serif; background-color: #f9f9f9; }}
          .email-container {{ max-width: 600px; margin: auto; background: #ffffff; border: 1px solid #e0e0e0; }}
          .header {{ background: #dec55d; color: #ffffff !important; text-align: center; padding: 30px 20px; font-size: 26px; font-weight: bold; }}
          .body-content {{ padding: 30px 25px; line-height: 1.6; color: #333333; }}
          .info-table {{ width: 100%; margin-bottom: 20px; border-collapse: collapse; }}
          .info-table td {{ padding: 10px 5px; border-bottom: 1px solid #eeeeee; }}
          .label {{ font-weight: bold; width: 100px; color: #555; }}
          .message-box {{ background: #fcfcfc; border-left: 4px solid #dec55d; padding: 15px; margin-top: 10px; font-style: italic; }}
          .footer {{ background: #f4f4f4; text-align: center; padding: 20px; font-size: 12px; color: #777777; }}
          @media screen and (max-width: 600px) {{ .email-container {{ width: 100% !important; }} .header {{ font-size: 22px !important; }} }}
        </style>
      </head>
      <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td align="center" style="padding: 20px 0;">
              <table class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">
                <tr><td class="header">New Contact Inquiry</td></tr>
                <tr>
                  <td class="body-content">
                    <p>Hi Admin, you have received a new message from the contact form:</p>
                    <table class="info-table">
                      <tr><td class="label">Name:</td><td>{name}</td></tr>
                      <tr><td class="label">Email:</td><td><a href="mailto:{email}" style="color: #dec55d; text-decoration: none;">{email}</a></td></tr>
                      <tr><td class="label">Subject:</td><td>{subject}</td></tr>
                    </table>
                    <p><strong>Message:</strong></p>
                    <div class="message-box">{message}</div>
                    <div style="text-align: center; margin-top: 30px;">
                      <a href="https://www.hmdhermada.com/hidden/admin-panel/contact-inquiries" style="background: #333; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; display: inline-block; font-weight: bold;">Go to Admin Panel</a>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="footer">
                    &copy; 2026 HMD Hermada HR Solutions Corporation. All Rights Reserved.
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
      </html>
    """
    return template.format(name=name, email=email, subject=subject, message=formatted_message)

# Client Reply Email Template.
def generate_client_reply_html(name, subject):
    template = """
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You - HMD Hermada</title>
        <style>
          body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
          table {{ border-collapse: collapse !important; }}
          body {{ margin: 0; padding: 0; width: 100%; font-family: Arial, sans-serif; background-color: #f9f9f9; }}
          .email-container {{ max-width: 600px; margin: auto; background: #ffffff; border: 1px solid #e0e0e0; }}
          .header {{ background: #dec55d; color: #ffffff !important; text-align: center; padding: 30px 20px; font-size: 26px; font-weight: bold; }}
          .body-content {{ padding: 30px 25px; line-height: 1.6; color: #333333; }}
          .footer {{ background: #f4f4f4; text-align: center; padding: 20px; font-size: 12px; color: #777777; }}
          .gold-text {{ color: #dec55d; font-weight: bold; }}
          @media screen and (max-width: 600px) {{ .email-container {{ width: 100% !important; }} .header {{ font-size: 22px !important; }} }}
        </style>
      </head>
      <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td align="center" style="padding: 20px 0;">
              <table class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">
                <tr><td class="header">HMD Hermada HR Solutions Corporation</td></tr>
                <tr>
                  <td class="body-content">
                    <h2 style="color: #dec55d; margin-top: 0;">Hi {name},</h2>
                    <p>Thank you for reaching out to us! This is to confirm that we have received your inquiry regarding <span class="gold-text">"{subject}"</span>.</p>
                    <p>Our team is currently reviewing your message and we will get back to you as soon as possible, usually within 24-48 business hours.</p>
                    <p>In the meantime, feel free to visit our website to learn more about <span class="gold-text">#TheGoldStandard</span> in people solutions.</p>
                    <div style="text-align: center; margin-top: 30px;">
                      <a href="https://www.hmdhermada.com/" style="background: #dec55d; color: #ffffff; text-decoration: none; padding: 12px 25px; border-radius: 5px; display: inline-block; font-weight: bold;">Visit Our Website</a>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td class="footer">
                    <div style="text-align: center; margin-bottom: 20px;">
                      <a href="https://www.facebook.com/hmdhermada/" target="_blank" style="text-decoration: none; margin: 0 5px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" title="Facebook | HMD Hermada" alt="Facebook | HMD Hermada" width="22" height="22" style="display: inline-block; vertical-align: middle;">
                      </a>
                      <a href="https://www.linkedin.com/company/hmd-hermada" target="_blank" style="text-decoration: none; margin: 0 5px;">
                        <img src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png" title="LinkedIn | HMD Hermada" alt="LinkedIn | HMD Hermada" width="22" height="22" style="display: inline-block; vertical-align: middle;">
                      </a>
                    </div>

                    &copy; 2026 HMD Hermada HR Solutions Corporation. All Rights Reserved.<br>
                    <span style="display: block; margin-top: 5px;">
                      Unit 2C 4th Floor Regus One E-com Bldg Ocean Drive Mall Of Asia Complex, Barangay 76 1300 Pasay City NCR, Fourth District Philippines
                      <br>
                      (02) 8 737 9323 | +63 917 960 6290 | +63 917 103 0298
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
      </html>
    """
    return template.format(name=name, subject=subject)

@pubcontroller.route('/new-contact', methods=['POST'])
@invalidate_cache(pattern="cache:*api/contact/inquiries*")
def new_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    recaptcha_token = request.form.get('g-recaptcha-response')

    if not all([name, email, subject, message, recaptcha_token]):
        return jsonify({"error": "All fields, including reCAPTCHA, are required"}), 400
    
    # reCAPTCHA Verification
    try:
        payload = {
            'secret': current_app.config.get('RECAPTCHA_SECRET_KEY'),
            'response': recaptcha_token,
            'remoteip': request.remote_addr
        }
        response = requests.post(VERIFY_URL, data=payload, timeout=10)
        result = response.json()
    except Exception as e:
        return jsonify({"error": "reCAPTCHA connection error"}), 500

    if not result.get("success") or result.get("score", 0) < 0.5:
        return jsonify({"error": "Bot-like activity detected."}), 400

    try:
        # Save to Database
        contact_entry = Contact(name=name, email=email, subject=subject, message=message)
        db.session.add(contact_entry)
        db.session.commit()

        # Send Emails Via BREVO
        manager_email = "ask@hmdhermada.com"
        
        # Email to Manager
        html_manager = generate_contact_html(name, email, subject, message)
        send_via_brevo(f"New Inquiry: {subject}", html_manager, manager_email, "HMD Admin", reply_to=email)
        
        # Auto-reply to Client
        html_client = generate_client_reply_html(name, subject)
        send_via_brevo("Thank you for reaching out to HMD Hermada", html_client, email, name)

        return jsonify({"message": "Message sent successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f"ERROR: {str(e)}")
        return jsonify({"error": "Failed to process your request"}), 500
    
# Our Newsletter (Newsletter Subscription Form Submission).
EMAIL_REGEX = r'^[^@]+@[^@]+\.[^@]+$'
logging.basicConfig(level=logging.DEBUG)

def generate_newsletter_html(unsubscribe_link, content):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HMD Hermada Newsletter</title>
  <style>
    body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
    table {{ border-collapse: collapse !important; }}
    body {{ margin: 0; padding: 0; width: 100%; font-family: Arial, sans-serif; background-color: #f9f9f9; }}
    .email-container {{
      max-width: 600px;
      margin: auto;
      background: #ffffff;
      border: 1px solid #e0e0e0;
    }}
    .header {{
      background: #dec55d;
      color: #ffffff !important;
      text-align: center;
      padding: 30px 20px;
      font-size: 26px;
      font-weight: bold;
    }}
    .body-content {{
      padding: 30px 25px;
      line-height: 1.6;
      color: #333333;
    }}
    .body-content h2 {{
      color: #dec55d;
      margin-top: 0;
    }}
    .cta-button {{
      background: #dec55d;
      color: #ffffff !important;
      text-decoration: none;
      padding: 14px 25px;
      border-radius: 5px;
      display: inline-block;
      margin: 20px 0;
      font-weight: bold;
    }}
    .footer {{
      background: #f4f4f4;
      text-align: center;
      padding: 20px;
      font-size: 12px;
      color: #777777;
    }}
    .gold-text {{ color: #dec55d; font-weight: bold; }}
    
    /* Para sa Mobile */
    @media screen and (max-width: 600px) {{
      .email-container {{ width: 100% !important; }}
      .header {{ font-size: 22px !important; }}
    }}
  </style>
</head>
<body>
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td align="center" style="padding: 20px 0;">
        <table class="email-container" width="600" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td class="header">
              HMD Hermada Newsletter
            </td>
          </tr>

          <tr>
            <td class="body-content">

              {content}

              <div style="text-align: center;">
                <a href="https://www.hmdhermada.com/" class="cta-button">Visit Our Website</a>
              </div>
          </tr>

          <tr>
            <td class="footer">
              <div style="text-align: center; margin-bottom: 20px;">
                <a href="https://www.facebook.com/hmdhermada/" target="_blank" style="text-decoration: none; margin: 0 5px;">
                  <img src="https://cdn-icons-png.flaticon.com/512/733/733547.png" title="Facebook | HMD Hermada" alt="Facebook | HMD Hermada" width="22" height="22" style="display: inline-block; vertical-align: middle;">
                </a>
                <a href="https://www.linkedin.com/company/hmd-hermada" target="_blank" style="text-decoration: none; margin: 0 5px;">
                  <img src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png" title="LinkedIn | HMD Hermada" alt="LinkedIn | HMD Hermada" width="22" height="22" style="display: inline-block; vertical-align: middle;">
                </a>
              </div>

              &copy; 2026 HMD Hermada HR Solutions Corporation. All Rights Reserved.<br>
              <span style="display: block; margin-top: 5px;">
                Unit 2C 4th Floor Regus One E-com Bldg Ocean Drive Mall Of Asia Complex, Barangay 76 1300 Pasay City NCR, Fourth District Philippines
                <br>
                (02) 8 737 9323 | +63 917 960 6290 | +63 917 103 0298
              </span>
              <a href="{unsubscribe_link}" style="color:#007bff; text-decoration:underline;">Unsubscribe</a> | <a href="#" style="color: #777;">Update Preferences</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

@pubcontroller.route('/send-newsletter', methods=['POST'])
@invalidate_cache(pattern="cache:*api/newsletters*")
def send_newsletter():
    recipient = request.get_json().get('email') if request.is_json else request.form.get('email')
    logging.debug(f"Recipient detected: {recipient}")

    if not recipient or not re.match(r'^[^@]+@[^@]+\.[^@]+$', recipient):
        return jsonify({'status': 'error', 'message': 'Valid email is required.'}), 400

    try:
        latest_nl = Newsletter.query.filter_by(nl_status="Active").order_by(Newsletter.date_created.desc()).first()
        newsletter_html_content = latest_nl.nl_description if latest_nl else "<p>Welcome to our newsletter!</p>"
        email_subject = latest_nl.nl_subject if latest_nl else "Welcome to HMD Hermada Newsletter"

        existing_sub = NewsletterSubscribers.query.filter_by(ns_email=recipient).first()
        new_subscription = None

        if not existing_sub:
            new_subscription = NewsletterSubscribers(
                ns_email=recipient,
                ns_status="Subscribed"
            )
            db.session.add(new_subscription)
            db.session.commit()
            logging.info(f"New subscriber saved: {recipient}")
        else:
            if existing_sub.ns_status == "Unsubscribed":
                existing_sub.ns_token_id = str(uuid.uuid4())
                existing_sub.ns_status = "Subscribed"
                existing_sub.date_created = datetime.now(ZoneInfo("Asia/Manila"))
                db.session.commit()
                logging.info(f"Subscriber {recipient} re-subscribed.")
                new_subscription = existing_sub 
            else:
                logging.info(f"Email {recipient} already subscribed.")
                return jsonify({'status': 'error', 'message': f'{recipient} is already subscribed.'}), 400

        # token-based unsubscribe link
        unsubscribe_link = url_for('public_controller.unsubscribe', token=new_subscription.ns_token_id, _external=True)
        
        email_content = generate_newsletter_html(unsubscribe_link, content=newsletter_html_content)

        is_sent = send_via_brevo(
            subject=email_subject, 
            html_content=email_content, 
            to_email=recipient
        )

        if is_sent:
            return jsonify({
                'status': 'success',
                'message': f'Thank you! Your subscription has been saved and a welcome email was sent to {recipient}.'
            })
        else:
            return jsonify({
                'status': 'error', 
                'message': 'Subscription saved but failed to send welcome email.'
            }), 500

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error during subscription: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Something went wrong. Please try again later.'}), 500

@pubcontroller.route('/unsubscribe/<token>')
@invalidate_cache(pattern="cache:*api/newsletter-subscribers*")
def unsubscribe(token):
    sub = NewsletterSubscribers.query.filter_by(ns_token_id=token).first()
    
    if not sub:
        return "Invalid unsubscribe link", 404

    if sub.ns_status == "Unsubscribed":
        return "This unsubscribe link is no longer valid or you have already unsubscribed.", 410

    try:
        sub.ns_status = "Unsubscribed"
        sub.date_created = datetime.now(ZoneInfo("Asia/Manila"))
        db.session.commit()
        return "You have successfully unsubscribed from our newsletter.", 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Unsubscribe error: {str(e)}")
        return "An error occurred. Please try again later.", 500
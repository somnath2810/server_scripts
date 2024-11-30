import os
import smtplib
import base64
import imaplib
import email
import json
from email.message import EmailMessage
from email.header import decode_header
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import atexit

# SMTP configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

# IMAP configuration
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Email credentials
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"

# Directory to save images
SAVE_DIR = "generated_images"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# ========================
# Email Sending Function
# ========================
def send_email(subject, body, to_email, from_email, password, image_path=None):
    """Send an email with optional image attachment."""
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)

    if image_path:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img_name = os.path.basename(image_path)
            msg.add_attachment(img_data, maintype='image', subtype='jpg', filename=img_name)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
    print("Email sent successfully.")


# ========================
# Email Receiving Functions
# ========================
def check_email_for_description():
    """Check for the latest unseen email with a text description."""
    description = None
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        messages = messages[0].split(b' ')

        for mail_id in messages:
            if mail_id:
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    description = part.get_payload(decode=True).decode()
                        else:
                            if msg.get_content_type() == "text/plain":
                                description = msg.get_payload(decode=True).decode()

                mail.store(mail_id, '+FLAGS', '\\Seen')
                break

    return description


def check_email_for_attachment():
    """Check for the latest unseen email with an image attachment."""
    image_path = None
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, 'UNSEEN')
        messages = messages[0].split(b' ')

        for mail_id in messages:
            if mail_id:
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        if msg.is_multipart():
                            for part in msg.walk():
                                if "attachment" in str(part.get("Content-Disposition")):
                                    filename = part.get_filename()
                                    if filename:
                                        image_path = os.path.join(SAVE_DIR, filename)
                                        with open(image_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))

                mail.store(mail_id, '+FLAGS', '\\Seen')
                break

    return image_path


# ========================
# Flask Routes
# ========================

@app.route('/')
def home():
    """Home route for health checks."""
    return jsonify({"message": "Server is running!"})


@app.route('/send-email', methods=['POST'])
def handle_send_email():
    """Handle requests to send an email with optional image."""
    data = request.json
    if 'image' in data:
        image_data = data['image'].split(",")[1]  # Remove base64 header
        image_path = os.path.join(SAVE_DIR, "uploaded_image.jpg")
        with open(image_path, "wb") as fh:
            fh.write(base64.b64decode(image_data))

        subject = data.get('phrase', "Image")
        body = data.get('phrase', "Image Only")

        send_email(
            subject=subject,
            body=body,
            to_email="sender2receiver24@gmail.com",
            from_email=EMAIL,
            password=PASSWORD,
            image_path=image_path
        )
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "No image data received"}), 400


@app.route('/get-description', methods=['GET'])
def get_description():
    """Get the latest email text description."""
    description = check_email_for_description()
    return jsonify({"description": description or ""})


@app.route('/get-image', methods=['GET'])
def get_image():
    """Get the latest image attachment from email."""
    image_path = check_email_for_attachment()
    if image_path and os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')
    else:
        return jsonify({"message": "No new images found"}), 404


# ========================
# Cleanup Function
# ========================
def cleanup_images():
    """Clean up old image files."""
    try:
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")


# ========================
# Main Entry Point
# ========================
if __name__ == "__main__":
    atexit.register(cleanup_images)
    import os
    PORT = int(os.getenv('PORT', 5000))
    # app.run(port=5000)
    app.run(host="0.0.0.0", port=port)

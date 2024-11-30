from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import smtplib
import os
from email.message import EmailMessage
import imaplib
import email
from email.header import decode_header
import json
import base64
import atexit

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"
SAVE_DIR = "generated_images"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Utility function to send email
def send_email(subject, body, to_email, from_email, password, image_path=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)

    if image_path:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img_name = os.path.basename(image_path)
            msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
    print("Email sent successfully.")
    # try:
    #     print("Preparing email...")
    #     msg = EmailMessage()
    #     msg['Subject'] = subject
    #     msg['From'] = from_email
    #     msg['To'] = to_email
    #     msg.set_content(body)

    #     if image_path:
    #         print(f"Attaching file: {image_path}")
    #         with open(image_path, 'rb') as img_file:
    #             img_data = img_file.read()
    #             img_name = os.path.basename(image_path)
    #             msg.add_attachment(img_data, maintype='image', subtype='jpeg', filename=img_name)

    #     print(f"Connecting to SMTP server: {SMTP_SERVER}:{SMTP_PORT}")
    #     with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
    #         smtp.login(from_email, password)
    #         print("Logged in to SMTP server.")
    #         smtp.send_message(msg)
    #         print("Email sent successfully.")
    # except Exception as e:
    #     print(f"Error sending email: {e}")

# Handle receiving data and sending emails
@app.route('/send-email', methods=['POST'])
def send_email_route():
    try:
        data = request.json
        print("Received data:", data)

        if 'image' in data:
            image_data = data['image'].split(",")[1]  # Remove base64 header
            image_path = os.path.join(SAVE_DIR, "received_image.jpg")
            with open(image_path, "wb") as fh:
                fh.write(base64.b64decode(image_data))

            mail_body = data.get('phrase', "Image Only")
            subject = "Sketch" if 'phrase' in data else "Image"

            # Send the image via email
            send_email(
                subject=subject,
                body=mail_body,
                to_email="sender2receiver24@gmail.com",
                from_email=EMAIL,
                password=PASSWORD,
                image_path=image_path
            )
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "error", "message": "No image data received"}), 400

    except Exception as e:
        print(f"Error in /send-email: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Utility function to check email for descriptions
def check_email_for_description():
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
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding)
                        from_ = msg.get("From")
                        
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/plain":
                                    description = part.get_payload(decode=True).decode()

                        else:
                            if msg.get_content_type() == "text/plain":
                                description = msg.get_payload(decode=True).decode()

                mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                break  # Process only the first unseen email

    return description

@app.route('/get-description', methods=['GET'])
def get_description():
    description = check_email_for_description()
    if description:
        return jsonify({"description": description})
    else:
        return jsonify({"description": ""})

# Utility function to check email for image attachments
def check_email_for_attachment():
    image_path = None
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')  # Get unseen emails
        messages = messages[0].split(b' ')

        for mail_id in messages:
            if mail_id:
                status, msg_data = mail.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if "attachment" in content_disposition and "image" in content_type:
                                    filename = part.get_filename()
                                    if filename:
                                        image_path = os.path.join(SAVE_DIR, filename)
                                        with open(image_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                break  # Process only the first unseen email

    return image_path

@app.route('/get-image', methods=['GET'])
def get_image():
    image_path = check_email_for_attachment()  # Get image from email
    if image_path and os.path.exists(image_path):
        return send_file(image_path, mimetype='image/jpeg')  # Serve image
    else:
        return jsonify({"message": "No new images found"}), 404

# Cleanup saved images on exit
def cleanup_images():
    try:
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed image: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Health check
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Server is running!"})

# Start the Flask server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use Render.com assigned port
    atexit.register(cleanup_images)
    app.run(host="0.0.0.0", port=port)

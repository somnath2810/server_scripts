import os
import imaplib
import email
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# IMAP configuration (use environment variables for deployment)
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = os.getenv("EMAIL")  # Email address
PASSWORD = os.getenv("PASSWORD")  # Email password

# Directory to save images (on the Render server)
SAVE_DIR = "/tmp/generated_image"  # Use /tmp for ephemeral storage on Render
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Global variable to cache the last image path
LAST_IMAGE_PATH = None

def delete_old_images():
    """Delete all old images in the directory."""
    try:
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg')):
                os.remove(file_path)
                print(f"Removed old image: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def check_email_for_attachment():
    """Check for new emails and save attachments."""
    global LAST_IMAGE_PATH
    image_path = None

    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')  # Get unseen emails
        messages = messages[0].split(b' ')

        if not messages or messages == [b'']:
            print("No new emails.")
            return None

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
                                        delete_old_images()  # Delete old images

                                        image_path = os.path.join(SAVE_DIR, filename)
                                        with open(image_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                                        LAST_IMAGE_PATH = image_path

                        else:
                            content_type = msg.get_content_type()
                            if "image" in content_type:
                                filename = "generated_image.jpg"
                                image_path = os.path.join(SAVE_DIR, filename)

                                delete_old_images()  # Delete old images

                                with open(image_path, "wb") as f:
                                    f.write(msg.get_payload(decode=True))
                                LAST_IMAGE_PATH = image_path

                mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                break  # Process only the first unseen email

    print("Image saved at:", image_path)
    return image_path
    

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Flask app is running"}), 200


@app.route('/get-image', methods=['GET', 'HEAD'])
def get_image():
    """Endpoint to serve the latest image."""
    global LAST_IMAGE_PATH

    # Ensure a new email check
    check_email_for_attachment()

    # Serve the last cached image
    if LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
        if request.method == 'HEAD':
            # For HEAD requests, only return 200 OK with no body
            return '', 200
        return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
    else:
        return jsonify({"message": "No new images found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

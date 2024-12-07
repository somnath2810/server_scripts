import os
import imaplib
import email
from email.header import decode_header
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Email credentials and settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"

# Directory to save images
SAVE_DIR = "/tmp/generated_image"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Globals to cache the latest data
LAST_IMAGE_PATH = None
LAST_DESCRIPTION = None


def process_unseen_emails():
    """
    Fetch the description and attachment (image) from the latest unseen email.
    Returns:
        description (str): The email description text.
        image_path (str): The path to the saved image, if any.
    """
    global LAST_IMAGE_PATH, LAST_DESCRIPTION
    description = None
    image_path = None

    try:
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

                            # Extract description and attachment
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    if content_type == "text/plain" and not description:
                                        description = part.get_payload(decode=True).decode()
                                    elif "attachment" in content_disposition and "image" in content_type:
                                        filename = part.get_filename()
                                        if filename:
                                            image_path = os.path.join(SAVE_DIR, filename)
                                            with open(image_path, "wb") as f:
                                                f.write(part.get_payload(decode=True))
                            else:
                                if msg.get_content_type() == "text/plain" and not description:
                                    description = msg.get_payload(decode=True).decode()

                    mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark email as read
                    break  # Process only the first unseen email

    except Exception as e:
        print(f"Error processing emails: {e}")

    # Update cached data
    if description:
        LAST_DESCRIPTION = description
    if image_path and os.path.exists(image_path):
        LAST_IMAGE_PATH = image_path

    return description, image_path


@app.route('/', methods=['GET'])
def home():
    """Root endpoint to check if the server is running."""
    return jsonify({"message": "Flask app is running"}), 200


@app.route('/get-description', methods=['GET'])
def get_description():
    """
    Endpoint to get the latest email description.
    Returns:
        - A JSON response containing the description text.
        - Cached description if no new email is found.
    """
    global LAST_DESCRIPTION
    description, _ = process_unseen_emails()  # Fetch description and image together

    if description:
        return jsonify({"description": description})
    elif LAST_DESCRIPTION:
        return jsonify({"description": LAST_DESCRIPTION})
    else:
        return jsonify({"message": "No description available"}), 404


@app.route('/get-image', methods=['GET', 'HEAD'])
def get_image():
    """
    Endpoint to get the latest image attachment.
    Returns:
        - The latest image file or a cached image if no new one is found.
    """
    global LAST_IMAGE_PATH
    _, image_path = process_unseen_emails()  # Fetch description and image together

    if image_path and os.path.exists(image_path):
        if request.method == 'HEAD':
            return '', 200
        return send_file(image_path, mimetype='image/jpeg')

    if LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
        if request.method == 'HEAD':
            return '', 200
        return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')

    return jsonify({"message": "No images available"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

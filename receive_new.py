# import os
# import imaplib
# import email
# from flask import Flask, jsonify, send_file, request
# from flask_cors import CORS

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)

# # IMAP configuration (use environment variables for deployment)
# IMAP_SERVER = 'imap.gmail.com'
# IMAP_PORT = 993
# EMAIL = os.getenv("EMAIL")  # Email address
# PASSWORD = os.getenv("PASSWORD")  # Email password

# # Directory to save images (on the Render server)
# SAVE_DIR = "/tmp/generated_image"  # Use /tmp for ephemeral storage on Render
# if not os.path.exists(SAVE_DIR):
#     os.makedirs(SAVE_DIR)

# # Global variable to cache the last image path
# LAST_IMAGE_PATH = None

# def delete_old_images():
#     """Delete all old images in the directory."""
#     try:
#         for filename in os.listdir(SAVE_DIR):
#             file_path = os.path.join(SAVE_DIR, filename)
#             if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg')):
#                 os.remove(file_path)
#                 print(f"Removed old image: {file_path}")
#     except Exception as e:
#         print(f"Error during cleanup: {e}")

# def check_email_for_attachment():
#     """Check for new emails and save attachments."""
#     global LAST_IMAGE_PATH
#     image_path = None

#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")

#         status, messages = mail.search(None, 'UNSEEN')  # Get unseen emails
#         messages = messages[0].split(b' ')

#         if not messages or messages == [b'']:
#             print("No new emails.")
#             return None

#         for mail_id in messages:
#             if mail_id:
#                 status, msg_data = mail.fetch(mail_id, "(RFC822)")
#                 for response_part in msg_data:
#                     if isinstance(response_part, tuple):
#                         msg = email.message_from_bytes(response_part[1])

#                         if msg.is_multipart():
#                             for part in msg.walk():
#                                 content_type = part.get_content_type()
#                                 content_disposition = str(part.get("Content-Disposition"))

#                                 if "attachment" in content_disposition and "image" in content_type:
#                                     filename = part.get_filename()
#                                     if filename:
#                                         delete_old_images()  # Delete old images

#                                         image_path = os.path.join(SAVE_DIR, filename)
#                                         with open(image_path, "wb") as f:
#                                             f.write(part.get_payload(decode=True))
#                                         LAST_IMAGE_PATH = image_path

#                         else:
#                             content_type = msg.get_content_type()
#                             if "image" in content_type:
#                                 filename = "generated_image.jpg"
#                                 image_path = os.path.join(SAVE_DIR, filename)

#                                 delete_old_images()  # Delete old images

#                                 with open(image_path, "wb") as f:
#                                     f.write(msg.get_payload(decode=True))
#                                 LAST_IMAGE_PATH = image_path

#                 mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
#                 break  # Process only the first unseen email

#     print("Image saved at:", image_path)
#     return image_path


# def check_email_for_description():
#     description = None
#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")
#         status, messages = mail.search(None, 'UNSEEN')
#         messages = messages[0].split(b' ')

#         for mail_id in messages:
#             if mail_id:
#                 status, msg_data = mail.fetch(mail_id, "(RFC822)")
#                 for response_part in msg_data:
#                     if isinstance(response_part, tuple):
#                         msg = email.message_from_bytes(response_part[1])
#                         subject, encoding = decode_header(msg["Subject"])[0]
#                         if isinstance(subject, bytes):
#                             subject = subject.decode(encoding)
#                         from_ = msg.get("From")

#                         if msg.is_multipart():
#                             for part in msg.walk():
#                                 content_type = part.get_content_type()
#                                 if content_type == "text/plain":
#                                     description = part.get_payload(decode=True).decode()

#                         else:
#                             if msg.get_content_type() == "text/plain":
#                                 description = msg.get_payload(decode=True).decode()

#                 mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
#                 break  # Process only the first unseen email

#     return description


# @app.route('/', methods=['GET'])
# def home():
#     return jsonify({"message": "Flask app is running"}), 200


# @app.route('/get-image', methods=['GET', 'HEAD'])
# def get_image():
#     """Endpoint to serve the latest image."""
#     global LAST_IMAGE_PATH
#     # Ensure a new email check
#     image_path = check_email_for_attachment()

#     # Serve the last cached image
#     # if LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
#     if image_path and os.path.exists(image_path):
#         if request.method == 'HEAD':
#             # For HEAD requests, only return 200 OK with no body
#             return '', 200
#         LAST_IMAGE_PATH = image_path
#         return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
#     else:
#         return jsonify({"message": "No new images found"}), 404


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)


import os
import imaplib
import email
from email.header import decode_header
from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
# EMAIL = os.getenv("EMAIL")  # Email address
# PASSWORD = os.getenv("PASSWORD")  # Email password
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"

SAVE_DIR = "/tmp/generated_image"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

LAST_IMAGE_PATH = None
LAST_DESCRIPTION = None


def check_email_for_description():
    """Fetch description text from the latest unseen email."""
    description = None
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
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding or 'utf-8')
                            print(f"Email Subject: {subject}")

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

    except Exception as e:
        print(f"Error fetching description: {e}")

    return description


def check_email_for_attachment():
    """Fetch the latest attachment from unseen emails."""
    global LAST_IMAGE_PATH
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
                                            LAST_IMAGE_PATH = image_path
                                            print(f"Saved image at: {image_path}")

                    mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                    break  # Process only the first unseen email

    except Exception as e:
        print(f"Error fetching attachment: {e}")

    return image_path


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Flask app is running"}), 200


@app.route('/get-description', methods=['GET'])
def get_description():
    global LAST_DESCRIPTION
    description = check_email_for_description()
    # print("DESC: ", description)
    # if description:
    #     return jsonify({"description": description})
    # else:
    #     return jsonify({"description": ""})
    if description:
        LAST_DESCRIPTION = description
        if request.method == 'HEAD':
            return '', 200
        return jsonify({"description": description})
    elif LAST_DESCRIPTION:
        if request.method == 'HEAD':
            return '', 200
        return jsonify({"description": LAST_DESCRIPTION})
    else:
        return jsonify({"message": "No new images found"}), 404


@app.route('/get-image', methods=['GET', 'HEAD'])
def get_image():
    global LAST_IMAGE_PATH
    image_path = check_email_for_attachment()  # Refresh the latest image

    if image_path and os.path.exists(image_path):
        if request.method == 'HEAD':
            return '', 200
        LAST_IMAGE_PATH = image_path
        return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
    elif LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
    # Serve the last cached image if no new image found
        if request.method == 'HEAD':
            return '', 200
        return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
        # return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
    else:
        return jsonify({"message": "No new images found"}), 404

# def get_image():
#     """Endpoint to serve the latest or cached image."""
#     global LAST_IMAGE_PATH

#     # Try fetching a new image
#     image_path = check_email_for_attachment()

#     if image_path and os.path.exists(image_path):
#         if request.method == 'HEAD':
#             return '', 200  # HEAD request returns 200 OK without a body
#         return send_file(image_path, mimetype='image/jpeg')
#     elif LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
#         # Serve the last cached image if no new image found
#         return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
#     else:
#         return jsonify({"message": "No images available"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
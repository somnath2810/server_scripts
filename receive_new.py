# import os
# import imaplib
# import email
# from email.header import decode_header
# from flask import Flask, jsonify, send_file
# from flask_cors import CORS
# import atexit

# # Initialize Flask app
# app = Flask(__name__)
# CORS(app)

# # IMAP configuration
# IMAP_SERVER = 'imap.gmail.com'
# IMAP_PORT = 993
# EMAIL = "sendermail432@gmail.com"
# PASSWORD = "wlgy xizw duca zphi"
# SAVE_DIR = "generated image"

# if not os.path.exists(SAVE_DIR):
#     os.makedirs(SAVE_DIR)

# # Global variable to cache the last image path
# LAST_IMAGE_PATH = None

# # Function to delete old images from the directory
# def delete_old_images():
#     try:
#         for filename in os.listdir(SAVE_DIR):
#             file_path = os.path.join(SAVE_DIR, filename)
#             if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg')):  # Only delete image files
#                 os.remove(file_path)
#                 print(f"Removed old image: {file_path}")
#     except Exception as e:
#         print(f"Error during cleanup: {e}")

# def check_email_for_attachment():
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
#                                         # Delete old image before saving the new one
#                                         delete_old_images()

#                                         image_path = os.path.join(SAVE_DIR, filename)
#                                         with open(image_path, "wb") as f:
#                                             f.write(part.get_payload(decode=True))

#                         else:
#                             content_type = msg.get_content_type()
#                             if "image" in content_type:
#                                 filename = "generated_image.jpg"
#                                 image_path = os.path.join(SAVE_DIR, filename)

#                                 # Delete old image before saving the new one
#                                 delete_old_images()

#                                 with open(image_path, "wb") as f:
#                                     f.write(msg.get_payload(decode=True))

#                 mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
#                 break  # Process only the first unseen email

#     print("Image saved at:", image_path)
#     return image_path




# if __name__ == "__main__":
#     app.run(port=5000)
#     atexit.register(lambda: delete_old_images())  # Cleanup old images on exit



from flask import Flask, jsonify, send_file
from flask_cors import CORS
import imaplib
import email
from email.header import decode_header
import os
import atexit
import logging

app = Flask(__name__)
CORS(app)

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"
# SAVE_DIR = "received_images"

# Set the directory for saving attachments
if os.getenv("RENDER"):
    # Use /tmp on Render for temporary files
    SAVE_DIR = "/tmp/received_images"
else:
    # Use a local directory for development
    SAVE_DIR = "received_images"

# Ensure the directory exists
os.makedirs(SAVE_DIR, exist_ok=True)
print(f"SAVE_DIR is set to: {SAVE_DIR}")
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

@app.route('/')
def home():
    return "Receiver Service is Running!"

@app.route('/get-description', methods=['GET'])
def get_description():
    description = check_email_for_description()
    if description:
        return jsonify({"description": description})
    else:
        return jsonify({"description": ""})


# def check_email_for_attachment():
#     latest_image_path = None
#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")

#         status, messages = mail.search(None, 'UNSEEN')  # Get unseen emails
#         messages = messages[0].split(b' ')

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
#                                     filename = f"image_{int(time.time())}.jpg"  # Unique filename with timestamp
#                                     latest_image_path = os.path.join(SAVE_DIR, filename)
#                                     with open(latest_image_path, "wb") as f:
#                                         f.write(part.get_payload(decode=True))

#                         else:
#                             content_type = msg.get_content_type()
#                             if "image" in content_type:
#                                 filename = f"image_{int(time.time())}.jpg"
#                                 latest_image_path = os.path.join(SAVE_DIR, filename)
#                                 with open(latest_image_path, "wb") as f:
#                                     f.write(msg.get_payload(decode=True))

#                 mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
#                 break  # Process only the first unseen email

#     return latest_image_path

def delete_old_images():
    try:
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg')):  # Only delete image files
                os.remove(file_path)
                print(f"Removed old image: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")

def check_email_for_attachment():
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
                                        # Delete old image before saving the new one
                                        delete_old_images()

                                        image_path = os.path.join(SAVE_DIR, filename)
                                        with open(image_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))

                        else:
                            content_type = msg.get_content_type()
                            if "image" in content_type:
                                filename = "generated_image.jpg"
                                image_path = os.path.join(SAVE_DIR, filename)

                                # Delete old image before saving the new one
                                delete_old_images()

                                with open(image_path, "wb") as f:
                                    f.write(msg.get_payload(decode=True))

                mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                break  # Process only the first unseen email

    print("Image saved at:", image_path)
    return image_path


@app.route('/get-image', methods=['GET'])
def get_image():
    global LAST_IMAGE_PATH
    image_path = check_email_for_attachment()  # Get image from email

    if image_path and os.path.exists(image_path):
        # Update the cached image path to the new image
        LAST_IMAGE_PATH = image_path
        return send_file(image_path, mimetype='image/jpeg')  # Serve image
    else:
        return jsonify({"message": "No new images found"}), 404


# Update the cached image path when necessary
def get_last_image():
    return LAST_IMAGE_PATH
    
if __name__ == "__main__":
    # atexit.register(cleanup_images)
    app.run(host="0.0.0.0", port=5002)  # Run on a different port for receiving service

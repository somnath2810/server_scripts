# import imaplib
# import email
# from email.header import decode_header
# import os
# import time

# # IMAP configuration
# IMAP_SERVER = 'imap.gmail.com'
# IMAP_PORT = 993

# # Email credentials
# EMAIL = "sendermail432@gmail.com"
# PASSWORD = "wlgy xizw duca zphi"

# # Directory to save attachments
# SAVE_DIR = "descriptions"

# if not os.path.exists(SAVE_DIR):
#     os.makedirs(SAVE_DIR)

# def clean(text):
#     # Clean up text for use as a filename
#     return "".join(c if c.isalnum() else "_" for c in text)

# def check_email():
#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")

#         # Search for unseen messages
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
#                         print("New Email from:", from_)
#                         print("Subject:", subject)

#                         # If the email is multipart (has attachments)
#                         if msg.is_multipart():
#                             for part in msg.walk():
#                                 content_type = part.get_content_type()
#                                 content_disposition = str(part.get("Content-Disposition"))
#                                 if "attachment" in content_disposition:
#                                     filename = part.get_filename()
#                                     if filename:
#                                         filepath = os.path.join(SAVE_DIR, clean(filename))
#                                         with open(filepath, "wb") as f:
#                                             f.write(part.get_payload(decode=True))
#                                         print(f"Attachment saved: {filepath}")
#                         else:
#                             # Handle non-multipart messages
#                             content_type = msg.get_content_type()
#                             if content_type == "text/plain":
#                                 print("Message content:", msg.get_payload(decode=True).decode())

#                 # Mark the email as read
#                 mail.store(mail_id, '+FLAGS', '\\Seen')

# if __name__ == "__main__":
#     while True:
#         print("Checking for new emails...")
#         check_email()
#         time.sleep(1)  # Check every 1 second



from flask import Flask, jsonify, send_file
from flask_cors import CORS
import imaplib
import email
from email.header import decode_header
import os
import atexit

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# IMAP configuration
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"
# SAVE_DIR = "descriptions"
SAVE_DIR = "generated image"
LAST_IMAGE_PATH = None  # Global variable to cache the last image path

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

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
                                content_disposition = str(part.get("Content-Disposition"))
                                if "attachment" in content_disposition:
                                    filename = part.get_filename()
                                    if filename:
                                        filepath = os.path.join(SAVE_DIR, filename)
                                        with open(filepath, "wb") as f:
                                            f.write(part.get_payload(decode=True))
                                elif content_type == "text/plain":
                                    description = part.get_payload(decode=True).decode()

                        else:
                            if msg.get_content_type() == "text/plain":
                                description = msg.get_payload(decode=True).decode()

                mail.store(mail_id, '+FLAGS', '\\Seen')
                break  # Process only the first unseen email

    return description


# except imaplib.IMAP4.error as e:
#         print(f"IMAP error occurred: {e}")
#         return None

@app.route('/get-description', methods=['GET'])
def get_description():
    description = check_email_for_description()
    print("DESC: ", description)
    if description:
        return jsonify({"description": description})
    else:
        return jsonify({"description": ""})

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
                                        image_path = os.path.join(SAVE_DIR, filename)
                                        with open(image_path, "wb") as f:
                                            f.write(part.get_payload(decode=True))

                        else:
                            content_type = msg.get_content_type()
                            if "image" in content_type:
                                filename = "generated_image.jpg"
                                image_path = os.path.join(SAVE_DIR, filename)
                                with open(image_path, "wb") as f:
                                    f.write(msg.get_payload(decode=True))

                mail.store(mail_id, '+FLAGS', '\\Seen')  # Mark as read
                break  # Process only the first unseen email

    print("Image saved at:", image_path)
    return image_path

# def check_email_for_attachment():
#     image_path = None
#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")
#         status, messages = mail.search(None, 'UNSEEN')

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
#                                     filename = f"image_{int(time.time())}.jpg"  # Unique filename
#                                     image_path = os.path.join(SAVE_DIR, filename)
#                                     with open(image_path, "wb") as f:
#                                         f.write(part.get_payload(decode=True))
#                                     print(f"Image saved: {image_path}")
#                         else:
#                             print("No valid attachment found.")
#                 mail.store(mail_id, '+FLAGS', '\\Seen')
#     return image_path



def cleanup_images():
    try:
        for filename in os.listdir(SAVE_DIR):
            file_path = os.path.join(SAVE_DIR, filename)
            if os.path.isfile(file_path) and file_path.endswith(('.png', '.jpg', '.jpeg')):  # Only delete image files
                os.remove(file_path)
                print(f"Removed image: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")


@app.route('/get-image', methods=['GET'])
# def get_image():
#     global LAST_IMAGE_PATH
#     image_path = check_email_for_attachment()  # Get image from email
#     # check_email_for_attachment()
#     # file_name = "generated_image.png"
#     # image_path = os.path.join(SAVE_DIR, file_name)

#     if image_path and os.path.exists(image_path):
#         return send_file(image_path, mimetype='image/jpeg')  # Serve image
#     else:
#         return jsonify({"message": "No new images found"}), 404


@app.route('/get-image', methods=['GET'])
def get_image():
    global LAST_IMAGE_PATH

    try:
        print("Checking for new images...")
        image_path = check_email_for_attachment()

        if image_path and os.path.exists(image_path):
            LAST_IMAGE_PATH = image_path  # Update the cache
            print(f"Serving new image: {image_path}")
            return send_file(image_path, mimetype='image/jpeg')
        elif LAST_IMAGE_PATH and os.path.exists(LAST_IMAGE_PATH):
            print(f"Serving cached image: {LAST_IMAGE_PATH}")
            return send_file(LAST_IMAGE_PATH, mimetype='image/jpeg')
        else:
            print("No images found.")
            return jsonify({"message": "No new images found"}), 404
    except Exception as e:
        print(f"Error in /get-image: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500




if __name__ == "__main__":
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    app.run(port=5000)
    # atexit.register(cleanup_images)
 

# if __name__ == "__main__":
#     app.run(port=5000)

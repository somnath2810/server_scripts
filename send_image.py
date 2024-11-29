# import smtplib
# import os
# from email.message import EmailMessage
# import imaplib
# import email
# from email.header import decode_header
# import time
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from flask_cors import CORS
# import json
# import base64
# from flask import Flask, request, jsonify

# app = Flask(__name__)
# CORS(app)  # This will enable CORS for all routes

# # SMTP configuration for sending emails
# SMTP_SERVER = 'smtp.gmail.com'
# SMTP_PORT = 465

# # IMAP configuration for receiving emails
# IMAP_SERVER = 'imap.gmail.com'
# IMAP_PORT = 993

# # Email credentials
# EMAIL = "sendermail432@gmail.com"
# PASSWORD = "wlgy xizw duca zphi"

# # Send an email
# def send_email(subject, body, to_email, from_email, password, image_path=None):
#     msg = EmailMessage()
#     msg['Subject'] = subject
#     msg['From'] = from_email
#     msg['To'] = to_email
#     msg.set_content(body)

#     if image_path:
#         with open(image_path, 'rb') as img_file:
#             img_data = img_file.read()
#             img_name = os.path.basename(image_path)
#             msg.add_attachment(img_data, maintype='image', subtype='jpg', filename=img_name)

#     with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
#         smtp.login(from_email, password)
#         smtp.send_message(msg)
#     print("Email sent successfully.")

# # Check for new emails
# def check_email():
#     with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as mail:
#         mail.login(EMAIL, PASSWORD)
#         mail.select("inbox")

#         status, messages = mail.search(None, 'UNSEEN')  # Search for unseen messages
#         messages = messages[0].split(b' ')

#         if not messages or messages == [b'']:
#             print("No new emails.")
#             return

#         for mail_id in messages:
#             if mail_id:  # Ensure mail_id is not empty
#                 status, msg_data = mail.fetch(mail_id, "(RFC822)")
#                 for response_part in msg_data:
#                     if isinstance(response_part, tuple):
#                         msg = email.message_from_bytes(response_part[1])
#                         subject, encoding = decode_header(msg["Subject"])[0]
#                         if isinstance(subject, bytes):
#                             subject = subject.decode(encoding)
#                         from_ = msg.get("From")
#                         print("New Email:")
#                         print("Subject:", subject)
#                         print("From:", from_)

#                         if msg.is_multipart():
#                             for part in msg.walk():
#                                 content_type = part.get_content_type()
#                                 content_disposition = str(part.get("Content-Disposition"))
#                                 if "attachment" in content_disposition:
#                                     filename = part.get_filename()
#                                     if filename:
#                                         filepath = os.path.join(os.getcwd(), filename)
#                                         with open(filepath, "wb") as f:
#                                             f.write(part.get_payload(decode=True))
#                                         print(f"Attachment saved: {filepath}")
#                         else:
#                             content_type = msg.get_content_type()
#                             if content_type == "text/plain":
#                                 print("Message content:", msg.get_payload(decode=True).decode())

#                 mail.store(mail_id, '+FLAGS', '\\Seen')

# # if __name__ == "__main__":
#     # i = 0
#     # while True:
#     #     action = input("Type 'send' to send an email, or just press Enter to check for new emails: ")

#     #     if action == 'send':
#     #         i += 1
#     #         image_path = f"image{i}.jpg"  # Update with your actual image path
#     #         send_email(
#     #             subject=f"Generated Content - {time.strftime('%Y-%m-%d %H:%M:%S')}",
#     #             body="Please find the attached image.",
#     #             to_email="sender2receiver24@gmail.com",
#     #             from_email=EMAIL,
#     #             password=PASSWORD,
#     #             image_path=image_path
#     #         )
#     #     else:
#     #         print("Checking for new emails...")
#     #         check_email()
#     #         time.sleep(10)


# class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         content_length = int(self.headers['Content-Length'])
#         post_data = self.rfile.read(content_length)
#         data = json.loads(post_data)
#         # phrase = data['phrase']
#         mailBody = None
#         subject = None
#         print("This is the data: ", data)

#         if 'image' in data:
#             image_data = data['image'].split(",")[1]  # Remove the base64 header
#             image_path = "received_image.jpg"  # Save the image
#             with open(image_path, "wb") as fh:
#                 fh.write(base64.b64decode(image_data))

#             if 'phrase' not in data or not data['phrase']:
#                 mailBody = "Image Only"
#                 subject = "Image"
#             else:
#                 mailBody = data['phrase']
#                 subject = "Sketch"

#             # Send the image via email
#             send_email(
#                 subject=subject,
#                 body=mailBody,
#                 to_email="sender2receiver24@gmail.com",
#                 from_email=EMAIL,
#                 password=PASSWORD,
#                 image_path=image_path
#             )
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(b'{"status":"success"}')

#         else:
#             self.send_response(400)
#             self.end_headers()
#             self.wfile.write(b'{"status":"error", "message":"No image data received"}')

# def run_server():
#     # server_address = ('', 5001)  # Running on localhost:5000
#     # httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
#     # print("Server started at http://localhost:5001")
#     # httpd.serve_forever()
#     PORT = int(os.getenv('PORT', 5000))  # Default to 5000 if PORT is not set
#     server_address = ('', PORT)
#     httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
#     print(f"Server started at http://localhost:{PORT}")
#     httpd.serve_forever()

# if __name__ == "__main__":
#     run_server()




import smtplib
import os
from email.message import EmailMessage
import imaplib
import email
from email.header import decode_header
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64

# SMTP configuration for sending emails
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

# IMAP configuration for receiving emails
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Email credentials
EMAIL = "sendermail432@gmail.com"
PASSWORD = "wlgy xizw duca zphi"

# Send an email
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
            msg.add_attachment(img_data, maintype='image', subtype='jpg', filename=img_name)

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)
    print("Email sent successfully.")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        """Handle HEAD requests."""
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        print("Received data: ", data)

        if 'image' in data:
            image_data = data['image'].split(",")[1]  # Remove the base64 header
            image_path = "received_image.jpg"  # Save the image
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
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'{"status":"success"}')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'{"status":"error", "message":"No image data received"}')

def run_server():
    """Run the HTTP server."""
    import os
    PORT = int(os.getenv('PORT', 5000))  # Default to port 5000 if not set
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server started at http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()

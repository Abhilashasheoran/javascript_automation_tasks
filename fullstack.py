import streamlit as st
import cv2
import pywhatkit
import smtplib
from email.message import EmailMessage
import time
import os
from datetime import datetime
import webbrowser
import imaplib
import email
import requests
from instagrapi import Client

# Email credentials
EMAIL = "email@gmail.com"
EMAIL_PASSWORD = "app_password"

# Instagram credentials
INSTAGRAM_USERNAME = "username"
INSTAGRAM_PASSWORD = "your password "

# Twilio credentials
TWILIO_SID = 'auth_id'
TWILIO_AUTH_TOKEN = 'auth_token'
TWILIO_FROM_NUMBER = '+your_twilio_number'  # Replace with your Twilio number

# 1. Click photo and save
def click_photo():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if ret:
        file = 'photo.jpg'
        cv2.imwrite(file, frame)
        cam.release()
        st.image(file, caption='Photo Captured')
        return file
    st.error("Failed to capture image")

# 2. Send email directly
def send_email(subject, body, attachment=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL
    recipient = st.text_input("Enter recipient email:")
    msg['To'] = recipient
    msg.set_content(body)
    if attachment:
        with open(attachment, 'rb') as f:
            data = f.read()
            msg.add_attachment(data, maintype='image', subtype='jpeg', filename='photo.jpg')
    if st.button("Send Email Now"):
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL, EMAIL_PASSWORD)
                smtp.send_message(msg)
            st.success("Email sent!")
        except Exception as e:
            st.error(f"Email failed: {e}")

# 3. Record video
def record_video(duration=10):
    cam = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    start_time = time.time()
    while int(time.time() - start_time) < duration:
        ret, frame = cam.read()
        if ret:
            out.write(frame)
    cam.release()
    out.release()
    return 'output.avi'

# 4. Send WhatsApp message
def send_whatsapp_message(number, message):
    if st.button("Send WhatsApp Message"):
        try:
            pywhatkit.sendwhatmsg_instantly(number, message)
            st.success("WhatsApp message sent!")
        except Exception as e:
            st.error(f"Failed to send: {e}")

# 5. Send SMS
def send_sms_via_twilio(body, to):
    from twilio.rest import Client
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(body=body, from_=TWILIO_FROM_NUMBER, to=to)
        st.success("SMS sent!")
    except Exception as e:
        st.error(f"SMS failed: {e}")

# 6. Show current GPS location (IP based, no API)
def show_current_location():
    try:
        res = requests.get("https://ipinfo.io").json()
        loc = res.get("loc", "0,0").split(",")
        lat, lon = float(loc[0]), float(loc[1])
        st.write(f"Approximate Location: {res.get('city')}, {res.get('region')}, {res.get('country')}")
        st.map(data={"lat": [lat], "lon": [lon]}, zoom=12)
    except Exception as e:
        st.error(f"Location fetch failed: {e}")

# 7. Show route to destination (Google Maps, no API)
def show_route(destination):
    st.write(f"Opening route to: {destination}")
    webbrowser.open(f"https://www.google.com/maps/dir//{destination.replace(' ', '+')}")

# 8. Search nearby
def search_nearby(query):
    st.write(f"Searching for: {query}")
    webbrowser.open(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")

# 9. Retrieve Gmail messages
def retrieve_gmail_messages():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, EMAIL_PASSWORD)
        mail.select("inbox")
        _, selected_mails = mail.search(None, "ALL")
        messages = selected_mails[0].split()[-10:]
        for num in messages:
            _, msg_data = mail.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            st.write(f"From: {msg['from']}, Subject: {msg['subject']}")
    except Exception as e:
        st.error(f"Failed to retrieve emails: {e}")

# 10. Post to Instagram
def post_to_instagram(photo, caption):
    try:
        cl = Client()
        cl.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        cl.photo_upload(photo, caption)
        st.success("Posted to Instagram!")
    except Exception as e:
        st.error(f"Instagram upload failed: {e}")

# ------------------------------
# Streamlit UI
st.title("📱 Smart Automation Dashboard")

task = st.selectbox("Choose a Task", [
    "Click Photo and Save",
    "Send Email Directly",
    "Click Photo and Email",
    "Record Video and Send to WhatsApp",
    "Send WhatsApp Message",
    "Send SMS Message",
    "Show Current GPS Location",
    "Show Route to Destination",
    "Search Nearby Grocery Stores",
    "Retrieve Last 10 Gmail Messages",
    "Post on Instagram"
])

if task == "Click Photo and Save":
    click_photo()

elif task == "Send Email Directly":
    send_email("Test Email", "This is a test email.")

elif task == "Click Photo and Email":
    photo = click_photo()
    send_email("Photo Email", "Attached is a clicked photo.", attachment=photo)

elif task == "Record Video and Send to WhatsApp":
    video = record_video()
    st.video(video)
    st.write("Now manually send it to WhatsApp via WhatsApp Web or use Twilio API if setup.")

elif task == "Send WhatsApp Message":
    num = st.text_input("Enter phone number with country code:")
    msg = st.text_area("Enter your message:")
    if num and msg:
        send_whatsapp_message(num, msg)

elif task == "Send SMS Message":
    to = st.text_input("To (with country code):")
    body = st.text_input("Message:")
    if to and body:
        send_sms_via_twilio(body, to)

elif task == "Show Current GPS Location":
    show_current_location()

elif task == "Show Route to Destination":
    dest = st.text_input("Enter destination:")
    if dest:
        show_route(dest)

elif task == "Search Nearby Grocery Stores":
    search_nearby("Grocery Stores near me")

elif task == "Retrieve Last 10 Gmail Messages":
    retrieve_gmail_messages()

elif task == "Post on Instagram":
    photo = st.file_uploader("Upload Photo", type=['jpg', 'png'])
    caption = st.text_area("Enter caption")
    if st.button("Post to Instagram") and photo:
        with open("insta_photo.jpg", "wb") as f:
            f.write(photo.read())
        post_to_instagram("insta_photo.jpg", caption)

import smtplib

"""
This file is explicitly for testing smtp connection and to easily not where error
is generating from incase of failed connection.

"""

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Upgrade the connection to secure
    server.login("your_email", "your_app_password")  # wink
    print("✅ Login successful!")
except smtplib.SMTPAuthenticationError as e:
    print("❌ Authentication error:", e)
except smtplib.SMTPException as e:
    print("❌ SMTP error:", e)
finally:
    server.quit()

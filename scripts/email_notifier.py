"""
email_notifier.py
Module for sending email notifications with weather alert information.
Formats weather data into an HTML email and sends it to the configured recipient via Gmail SMTP.
"""

# Importing necessery libraries and module for the script.
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from logger import setup_logger, get_logger
from datetime import datetime

# Initialize load env file
load_dotenv()
# Initialize the logging system for tracking activity and debugging
setup_logger()
logger = get_logger()

# Retrieving secret information from environtment variable
sender = os.getenv("SENDER_EMAIL")
password = os.getenv("APP_PASSWORD")
receiver = os.getenv("RECEIVER_EMAIL")

def send_email(checklisted_data):
    """
    Sends a formatted HTML email with weather alert information to the configured recipient.
    
    Parameters:
        checklisted_data (list): List of dictionaries containing weather records matching alert criteria
                               Each dictionary should contain: location, weather_conditions, description, 
                               temperature, humidity, wind_speed
    
    Returns:
        None - Prints success/error message to log
    """
    # Log the start of the email notification process
    logger.info("Starting email notifier alert to the target email.")
    # Record the start time for performance measurement
    start_time = datetime.now()

    # Validate that weather data is available before attempting to send email
    if not checklisted_data:
        print("No checklisted weather data to send.")
        logger.warning("No checklisted weather data to send, there are error in the program.")
        logger.warning(f"Stopping the program. Time taken: {datetime.now() - start_time}")
        raise SystemExit
        return

    # Initialize string to accumulate HTML table rows for each weather record
    list_items = ""
    # Iterate through each weather record in the checklist
    for data in checklisted_data:
        # Build HTML table row with weather information for this location
        list_items += (
            "<tr>"
            # Display location name in bold
            f"<td><strong>{data['location']}</strong></td>"
            # Display main weather condition and description in italics
            f"<td>{data['weather_conditions']}<br><em>{data['description'].title()}</em></td>"
            # Display temperature in Celsius
            f"<td>{data['temperature']} °C</td>"
            # Display humidity percentage
            f"<td>{data['humidity']}%</td>"
            # Display wind speed in meters per second
            f"<td>{data['wind_speed']} m/s</td>"
            "</tr>"
        )

    # Construct the complete HTML email message with styling and weather information
    msg = f"""
        <html>
            <body style="margin:0;padding:0;font-family:Arial,sans-serif;background:#f4f6fb;color:#333;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;margin:0 auto;padding:24px;">
                    <tr>
                        <td style="background:#ffffff;border-radius:12px;box-shadow:0 4px 18px rgba(0,0,0,0.08);padding:32px;">
                            <h1 style="margin-top:0;color:#1f3c88;">Weather Alert</h1>
                            <p style="font-size:16px;line-height:1.6;margin:0 0 24px;">
                                The following locations are currently matching your weather checklist. Please review the details below and stay prepared.
                            </p>
                            <table role="presentation" width="100%" cellpadding="12" cellspacing="0" style="border-collapse:collapse;">
                                <tr style="background:#eef2fb;color:#1f3c88;text-align:left;">
                                    <th style="padding:12px 16px;border-bottom:2px solid #d8e2f2;">Location</th>
                                    <th style="padding:12px 16px;border-bottom:2px solid #d8e2f2;">Condition</th>
                                    <th style="padding:12px 16px;border-bottom:2px solid #d8e2f2;">Temp</th>
                                    <th style="padding:12px 16px;border-bottom:2px solid #d8e2f2;">Humidity</th>
                                    <th style="padding:12px 16px;border-bottom:2px solid #d8e2f2;">Wind</th>
                                </tr>
                                {list_items}
                            </table>
                            <p style="font-size:14px;color:#555;margin:24px 0 0;">
                                This alert was generated automatically from your checklist rules. Stay safe and keep an eye on changing conditions.
                            </p>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
    """
    # Attempt to send the email using Gmail SMTP server
    try:
        # Establish secure connection to Gmail SMTP server on port 587 (TLS)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            # Upgrade connection to TLS encryption for security
            server.starttls()
            # Authenticate using sender's email and app-specific password
            server.login(sender, password)
            # Create MIME email message with HTML formatting
            email_message = MIMEText(msg, "html")
            # Set email subject line
            email_message["Subject"] = "Weather Alert Notification"
            # Set sender email address
            email_message["From"] = sender
            # Set recipient email address
            email_message["To"] = receiver
            # Send the email message
            server.sendmail(sender, receiver, email_message.as_string())
            # Record the end time for performance measurement
            end_time = datetime.now()
            # Log successed email send
            logger.info("Email notification alert send successfully. Time taken: {}".format(end_time - start_time))
            
    # Catch SMTP-related errors (connection, authentication, sending failures)
    except smtplib.SMTPException as e:
        # Log error message if email sending fails
        logger.error("Failed to send email: {e}")



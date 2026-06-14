import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

sender = os.getenv("SENDER_EMAIL")
password = os.getenv("APP_PASSWORD")
receiver = os.getenv("RECEIVER_EMAIL")

def send_email(checklisted_data):
    if not checklisted_data:
        print("No checklisted weather data to send.")
        return

    list_items = ""
    for data in checklisted_data:
        list_items += (
            "<tr>"
            f"<td><strong>{data['location']}</strong></td>"
            f"<td>{data['weather_conditions']}<br><em>{data['description'].title()}</em></td>"
            f"<td>{data['temperature']} °C</td>"
            f"<td>{data['humidity']}%</td>"
            f"<td>{data['wind_speed']} m/s</td>"
            "</tr>"
        )

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
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            email_message = MIMEText(msg, "html")
            email_message["Subject"] = "Weather Alert Notification"
            email_message["From"] = sender
            email_message["To"] = receiver
            server.sendmail(sender, receiver, email_message.as_string())
            print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")



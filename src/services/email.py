import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.conf.config import config

async def send_email(to_email: str, subject: str, body: str):
    from_email = config.MAIL_USERNAME
    from_password = config.MAIL_PASSWORD
    smtp_server = config.MAIL_SERVER
    smtp_port = config.MAIL_PORT

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
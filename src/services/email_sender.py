import sys
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path)


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from src.conf.config import config

# async def send_email(to_email: str, subject: str, body: str):
#     from_email = config.MAIL_USERNAME
#     from_password = config.MAIL_PASSWORD
#     smtp_server = config.MAIL_SERVER
#     smtp_port = config.MAIL_PORT

#     msg = MIMEMultipart()
#     msg['From'] = from_email
#     msg['To'] = 'hedgy85@ukr.net'
#     msg['Subject'] = 'Parking expenses'

#     msg.attach(MIMEText("Your current parking expenses amount to 1200$, which exceeds the established limit 1000$.", 'plain'))

#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(from_email, from_password)
#         server.sendmail(from_email, to_email, msg.as_string())
#         server.quit()
#         print("Email sent successfully")
#     except Exception as e:
#         print(f"Failed to send email: {e}")


###SEND EMAIL example FASTAPI_MAIL
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email(to_email: str, subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],  # List of recipients
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(send_email())
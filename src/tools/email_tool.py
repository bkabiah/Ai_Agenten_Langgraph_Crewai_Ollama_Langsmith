import os
import smtplib
from email.message import EmailMessage
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool("Send Email to Customer")
def send_email_tool(recipient_email: str, subject: str, body: str) -> str:
    """Sendet eine E-Mail an den Kunden via echtem SMTP."""
    
    # SENIOR FIX: Blockiere leere oder ungültige E-Mails
    if not body or len(body.strip()) < 20:
        return "ABGEBROCHEN: E-Mail-Inhalt ist leer oder zu kurz. Versand verweigert."
    if not subject or len(subject.strip()) < 3:
        return "ABGEBROCHEN: Betreff ist leer. Versand verweigert."

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    sender_email = os.getenv("SENDER_EMAIL", smtp_user)

    if not all([smtp_user, smtp_pass]):
        return "FEHLER: SMTP_USER oder SMTP_PASS fehlt in der .env Datei."

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return f"ERFOLG: E-Mail wurde wirklich an {recipient_email} gesendet!"
    except smtplib.SMTPAuthenticationError:
        return "FEHLER: Falsches Passwort oder kein App-Passwort verwendet."
    except Exception as e:
        return f"FEHLER beim Senden: {str(e)}"

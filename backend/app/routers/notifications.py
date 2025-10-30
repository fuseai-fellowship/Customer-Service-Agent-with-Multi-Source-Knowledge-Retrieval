import smtplib
from email.message import EmailMessage
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.notifications import NotificationRequest
from app.core.config import settings

router = APIRouter(prefix="/notify", tags=["notifications"])

@router.post("")
async def send_notification(payload: NotificationRequest):
    """
    Sends an email notification via SMTP using configured settings.
    """
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.SMTP_SENDER_EMAIL]):
        raise HTTPException(status_code=500, detail="SMTP settings are not fully configured.")

    msg = EmailMessage()
    msg['Subject'] = payload.subject
    msg['From'] = settings.SMTP_SENDER_EMAIL
    msg['To'] = settings.ADMIN_EMAIL
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(payload.body_html, charset='utf-8')

    try:
        server = None
        if settings.SMTP_SSL_TLS:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        
        if settings.SMTP_STARTTLS:
            server.starttls()
        
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"✅ Notification email sent successfully to: {msg['To']}")
        return {"message": "Notification email sent successfully."}

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication Error: Check username/password. Did you use a Google 'App Password'?")
        raise HTTPException(status_code=500, detail="SMTP authentication failed. Check credentials (use App Password for Gmail).")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
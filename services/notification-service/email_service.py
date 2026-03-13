import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, NOTIFICATION_FROM, SERVICE_NAME

logger = logging.getLogger(SERVICE_NAME)


def send_notification(event: dict) -> dict:
    """
    Send order notification. Uses SMTP if credentials are configured,
    otherwise logs the notification (useful for development).
    """
    order_id = event.get("order_id", "UNKNOWN")
    user_id = event.get("user_id", "UNKNOWN")
    inventory_status = event.get("inventory_status", "UNKNOWN")
    product_id = event.get("product_id", "UNKNOWN")
    quantity = event.get("quantity", 0)
    total = event.get("total_amount", 0)
    txn_id = event.get("transaction_id", "N/A")

    subject = f"Order Update: {order_id}"
    body = (
        f"Hello {user_id},\n\n"
        f"Your order {order_id} has been processed.\n\n"
        f"  Product:        {product_id}\n"
        f"  Quantity:        {quantity}\n"
        f"  Total Amount:    ${total}\n"
        f"  Transaction ID:  {txn_id}\n"
        f"  Inventory:       {inventory_status}\n\n"
        f"Thank you for your order!\n"
    )

    if SMTP_USER and SMTP_PASSWORD:
        return _send_email(user_id, subject, body)

    logger.info(f"[NOTIFICATION] To: {user_id} | Subject: {subject}")
    logger.info(f"[NOTIFICATION] Body:\n{body}")
    return {
        "order_id": order_id,
        "user_id": user_id,
        "notification_status": "LOGGED",
        "channel": "console",
    }


def _send_email(to_address: str, subject: str, body: str) -> dict:
    try:
        msg = MIMEMultipart()
        msg["From"] = NOTIFICATION_FROM
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_address} for subject: {subject}")
        return {
            "user_id": to_address,
            "notification_status": "SENT",
            "channel": "email",
        }
    except Exception as e:
        logger.error(f"Failed to send email to {to_address}: {e}")
        return {
            "user_id": to_address,
            "notification_status": "FAILED",
            "channel": "email",
            "error": str(e),
        }

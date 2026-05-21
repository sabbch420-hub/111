from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Optional

from .config import (
    SMTP_ENABLED,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_TLS,
    SMTP_USER,
)


def _smtp_ready() -> bool:
    return bool(SMTP_ENABLED and SMTP_HOST and SMTP_FROM)


def send_email(subject: str, to_email: str, text_body: str, html_body: Optional[str] = None) -> bool:
    if not _smtp_ready():
        print("SMTP non configure. Email ignore.")
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            if SMTP_TLS:
                server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        print(f"Erreur envoi email: {exc}")
        return False


def send_account_approved_email(to_email: str, login_url: str) -> bool:
    subject = "Votre compte IntelliBuild est active"
    text_body = (
        "Bonjour,\n\n"
        "Votre compte a ete active par l'administration.\n"
        f"Vous pouvez vous connecter ici: {login_url}\n\n"
        "Cordialement,\n"
        "Equipe IntelliBuild"
    )
    html_body = (
        "<p>Bonjour,</p>"
        "<p>Votre compte a ete <strong>active</strong> par l'administration.</p>"
        f"<p>Vous pouvez vous connecter ici: <a href=\"{login_url}\">{login_url}</a></p>"
        "<p>Cordialement,<br>Equipe IntelliBuild</p>"
    )
    return send_email(subject, to_email, text_body, html_body)


def send_account_rejected_email(to_email: str, reason: str | None = None) -> bool:
    subject = "Activation de compte IntelliBuild"
    reason_text = f"Motif: {reason}\n\n" if reason else ""
    text_body = (
        "Bonjour,\n\n"
        "Votre demande de creation de compte n'a pas ete acceptee.\n"
        f"{reason_text}"
        "Pour plus d'informations, contactez l'administration.\n\n"
        "Cordialement,\n"
        "Equipe IntelliBuild"
    )
    html_reason = f"<p><strong>Motif:</strong> {reason}</p>" if reason else ""
    html_body = (
        "<p>Bonjour,</p>"
        "<p>Votre demande de creation de compte n'a pas ete acceptee.</p>"
        f"{html_reason}"
        "<p>Pour plus d'informations, contactez l'administration.</p>"
        "<p>Cordialement,<br>Equipe IntelliBuild</p>"
    )
    return send_email(subject, to_email, text_body, html_body)

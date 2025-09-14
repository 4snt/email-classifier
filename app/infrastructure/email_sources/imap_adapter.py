import imaplib, email
from typing import List
from app.domain.entities import Email
from app.domain.ports import EmailSourcePort


class ImapEmailSource(EmailSourcePort):
    def __init__(self, host: str, user: str, password: str, mailbox: str = "INBOX"):
        self.host = host
        self.user = user
        self.password = password
        self.mailbox = mailbox
        self.conn = None

    def _connect(self):
        if not self.conn:
            self.conn = imaplib.IMAP4_SSL(self.host)
            self.conn.login(self.user, self.password)

    def fetch_unread(self) -> List[Email]:
        self._connect()
        self.conn.select(self.mailbox)
        status, ids = self.conn.search(None, "UNSEEN")
        if status != "OK":
            return []

        emails: List[Email] = []
        for num in ids[0].split():
            typ, data = self.conn.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            # Extrai texto simples
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            emails.append(
                Email(
                    subject=msg["subject"],
                    sender=msg["from"],
                    body=body
                )
            )
        return emails

    def mark_as_read(self, ids: List[str]) -> None:
        self._connect()
        for num in ids:
            self.conn.store(num, "+FLAGS", "\\Seen")

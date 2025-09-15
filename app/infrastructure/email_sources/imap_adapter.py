import imaplib, email
from app.domain.entities import Email
from app.domain.ports import EmailSourcePort


class ImapEmailSource(EmailSourcePort):
    def __init__(self, host: str, user: str, password: str, mailbox: str = "INBOX"):
        self.host = host
        self.user = user
        self.password = password
        self.mailbox = mailbox
        self.conn: imaplib.IMAP4_SSL | None = None

    def _connect(self):
        if not self.conn:
            self.conn = imaplib.IMAP4_SSL(self.host)
            self.conn.login(self.user, self.password)

    def fetch_unread(self):
        self._connect()
        self.conn.select(self.mailbox)
        status, ids = self.conn.search(None, "UNSEEN")
        if status != "OK" or not ids or not ids[0]:
            return []

        for num in ids[0].split():
            typ, data = self.conn.fetch(num, "(RFC822)")
            if typ != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            yield num.decode(), Email(
                subject=msg.get("subject"),
                sender=msg.get("from"),
                body=body,
            )

    def mark_as_read(self, ids: list[str]) -> None:
        self._connect()
        for msg_id in ids:
            self.conn.store(msg_id, "+FLAGS", "\\Seen")

    def move_to_folder(self, msg_id: str, folder: str):
        self._connect()
        print(f"[DEBUG] Movendo mensagem {msg_id} para '{folder}'")

        try:
            self.conn.create(folder)
        except:
            pass

        try:
            status, resp = self.conn.store(msg_id, '+X-GM-LABELS', f'({folder})')
            print(f"[DEBUG] Gmail store +X-GM-LABELS -> {status}, {resp}")
        except Exception as e:
            print(f"[WARN] Gmail labels não suportadas, usando fallback: {e}")
            try:
                self.conn.copy(msg_id, folder)
                self.conn.store(msg_id, "+FLAGS", "\\Deleted")
                self.conn.expunge()
                print(f"[DEBUG] Mensagem {msg_id} copiada para {folder} e removida da origem")
            except Exception as e2:
                print(f"[ERROR] Falha ao mover mensagem {msg_id} para {folder}: {e2}")
                return

        try:
            status, resp = self.conn.store(msg_id, "+FLAGS", "\\Seen")
            print(f"[DEBUG] store +FLAGS \\Seen -> {status}, {resp}")
        except Exception as e:
            print(f"[WARN] Não conseguiu marcar como lido: {e}")

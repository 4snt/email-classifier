from app.domain.ports import EmailSourcePort, ClassifierPort, LogRepositoryPort
from app.domain.entities import Category, ClassificationLog


class SyncEmailsUseCase:
    def __init__(
        self,
        email_source: EmailSourcePort,
        classifier: ClassifierPort,
        repo: LogRepositoryPort,
        profile_id: str,
        tokenizer,
    ):
        self.email_source = email_source
        self.classifier = classifier
        self.repo = repo
        self.profile_id = profile_id
        self.tokenizer = tokenizer

    def run(self, stop_event=None):
        print("[DEBUG] Iniciando SyncEmailsUseCase.run()")

        for msg_id, email in self.email_source.fetch_unread():
            if stop_event and stop_event.is_set():
                print("[DEBUG] Interrompendo processamento por stop_event")
                return

            print(f"[DEBUG] Processando email {msg_id} - Assunto: {email.subject}")

            result = self._classify_email(msg_id, email)
            if not result:
                continue

            folder = "Produtivos" if result.category == Category.PRODUCTIVE else "Improdutivos"
            result.extra = {**(result.extra or {}), "profile_id": self.profile_id, "moved_to": folder}

            log = ClassificationLog(
                profile_id=self.profile_id,
                category=result.category,
                reason=result.reason,
                suggested_reply=result.suggested_reply,
                subject=email.subject,
                sender=email.sender,
                body_excerpt=(email.body or "")[:200],
                extra=result.extra,
            )

            self._save_log(msg_id, log)
            self._move_email(msg_id, folder)

        print("[DEBUG] Fim de SyncEmailsUseCase.run()")

    def _classify_email(self, msg_id, email):
        try:
            tokens = self.tokenizer.tokenize(email.body or "")
            result = self.classifier.classify(email, tokens=tokens)
            print(f"[DEBUG] Classificação: {result.category}")
            return result
        except Exception as e:
            print(f"[ERROR] Falha ao classificar {msg_id}: {e}")
            return None

    def _save_log(self, msg_id, log: ClassificationLog):
        try:
            self.repo.save(log)
            print(f"[DEBUG] Log salvo no repositório para {msg_id}")
        except Exception as e:
            print(f"[ERROR] Falha ao salvar log no repositório: {e}")

    def _move_email(self, msg_id, folder: str):
        try:
            self.email_source.move_to_folder(msg_id, folder)
            print(f"[DEBUG] Email {msg_id} movido com sucesso para {folder}")
        except Exception as e:
            print(f"[WARN] Falha ao mover {msg_id} para {folder}: {e}")

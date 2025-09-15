from app.domain.ports import EmailSourcePort, ClassifierPort, LogRepositoryPort
from app.domain.entities import Category, ClassificationLog


class SyncEmailsUseCase:
    def __init__(self, email_source: EmailSourcePort, classifier: ClassifierPort,
                 repo: LogRepositoryPort, profile_id: str, tokenizer):
        self.email_source = email_source
        self.classifier = classifier
        self.repo = repo
        self.profile_id = profile_id
        self.tokenizer = tokenizer

    def run(self):
        print("[DEBUG] Iniciando SyncEmailsUseCase.run()")

        for msg_id, email in self.email_source.fetch_unread():
            print(f"[DEBUG] Processando email {msg_id} - Assunto: {email.subject}")

            # Tokenização + classificação
            try:
                tokens = self.tokenizer.tokenize(email.body or "")
                result = self.classifier.classify(email, tokens=tokens)
                print(f"[DEBUG] Classificação: {result.category}")
            except Exception as e:
                print(f"[ERROR] Falha ao classificar {msg_id}: {e}")
                continue

            # adiciona metadados extras
            result.extra = result.extra or {}
            result.extra["profile_id"] = self.profile_id

            # decide pasta destino
            folder = "Produtivos" if result.category == Category.PRODUCTIVE else "Improdutivos"
            result.extra["moved_to"] = folder
            print(f"[DEBUG] Email {msg_id} será movido para: {folder}")

            # cria log para salvar
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

            try:
                self.repo.save(log)
                print(f"[DEBUG] Log salvo no repositório para {msg_id}")
            except Exception as e:
                print(f"[ERROR] Falha ao salvar log no repositório: {e}")

            # tenta mover
            try:
                self.email_source.move_to_folder(msg_id, folder)
                print(f"[DEBUG] Email {msg_id} movido com sucesso para {folder}")
            except Exception as e:
                print(f"[WARN] Falha ao mover {msg_id} para {folder}: {e}")

        print("[DEBUG] Fim de SyncEmailsUseCase.run()")

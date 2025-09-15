import threading
from app.application.use_cases.sync_emails import SyncEmailsUseCase
from app.infrastructure.nlp.tokenizer_simple import SimpleTokenizer


class ImapService:
    def __init__(self, source, classifier, repo, profile_id, interval=60):
        self.source = source
        self.classifier = classifier
        self.repo = repo
        self.profile_id = profile_id
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.tokenizer = SimpleTokenizer(lang="auto")

    def start(self):
        if not self._thread or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None

    def _worker(self):
        print("[DEBUG] Entrou no worker do ImapService")
        use_case = SyncEmailsUseCase(
            email_source=self.source,
            classifier=self.classifier,
            repo=self.repo,
            profile_id=self.profile_id,
            tokenizer=self.tokenizer,
        )

        while not self._stop_event.is_set():
            try:
                print("[DEBUG] Chamando use_case.run()")
                use_case.run(stop_event=self._stop_event)   # <-- passa o evento
            except Exception:
                import traceback
                print("[ERROR] Falha no use_case.run():")
                traceback.print_exc()
            self._stop_event.wait(self.interval)

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

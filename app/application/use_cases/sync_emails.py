from app.domain.ports import EmailSourcePort, ClassifierPort, RepositoryPort

class SyncEmailsUseCase:
    def __init__(self, email_source: EmailSourcePort, classifier: ClassifierPort, repo: RepositoryPort):
        self.email_source = email_source
        self.classifier = classifier
        self.repo = repo

    def run(self):
        emails = self.email_source.fetch_unread()
        for email in emails:
            result = self.classifier.classify(email, tokens=[])
            self.repo.save(result)

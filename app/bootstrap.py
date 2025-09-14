from app.application.use_cases.classify_email import FileFacade, ClassifyEmailUseCase
from app.infrastructure.extractors.pdf_extractor import PdfExtractor
from app.infrastructure.extractors.txt_extractor import TxtExtractor
from app.infrastructure.nlp.tokenizer_simple import SimpleTokenizer
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier
from app.infrastructure.classifiers.openai_llm import OpenAIClassifier
from app.infrastructure.responders.simple_templates import SimpleResponder
from app.infrastructure.repositories.sql_log_repository import SqlLogRepository
from app.infrastructure.profiles.profile_json import JsonProfileAdapter  
from app.infrastructure.db import init_db, get_session

from app.config import settings


def build_use_case():
    init_db()
    session = next(get_session())
    
    log_repo = SqlLogRepository(session=session)

    facade = FileFacade(pdf_extractor=PdfExtractor(), txt_extractor=TxtExtractor())
    tokenizer = SimpleTokenizer(lang="pt")
    classifier = OpenAIClassifier() if settings.USE_OPENAI else RuleBasedClassifier()
    responder = SimpleResponder()
    profiles = JsonProfileAdapter()  

    return ClassifyEmailUseCase(facade, tokenizer, classifier, responder, profiles, log_repo=log_repo)

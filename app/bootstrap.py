from app.application.use_cases.classify_email import FileFacade, ClassifyEmailUseCase
from app.infrastructure.extractors.pdf_extractor import PdfExtractor
from app.infrastructure.extractors.txt_extractor import TxtExtractor
from app.infrastructure.extractors.eml_extractor import EmlExtractor
from app.infrastructure.nlp.tokenizer_simple import SimpleTokenizer
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier
from app.infrastructure.classifiers.openai_llm import OpenAIClassifier
from app.infrastructure.classifiers.smart_classifier import SmartClassifier
from app.infrastructure.responders.simple_templates import SimpleResponder
from app.infrastructure.repositories.sql_log_repository import SqlLogRepository
from app.infrastructure.profiles.profile_json import JsonProfileAdapter
from app.infrastructure.db import init_db, get_session

from app.config import settings


def build_use_case():
    # DB (SQLite) + session
    init_db()
    session = next(get_session())

    # Repositório de logs
    log_repo = SqlLogRepository(session=session)

    # Extractors de arquivo
    facade = FileFacade(
        pdf_extractor=PdfExtractor(),
        txt_extractor=TxtExtractor(),
        eml_extractor=EmlExtractor(),
    )

    # Tokenizer multilíngue (pt/en/es) com auto-detecção
    tokenizer = SimpleTokenizer(lang="auto")

    # Classificadores: rule-based sempre; LLM opcional com gating
    rule = RuleBasedClassifier()
    if getattr(settings, "USE_OPENAI", False):
        llm = OpenAIClassifier()
        min_conf = getattr(settings, "RB_MIN_CONF", 0.70)  # chama LLM só se RB < 0.70
        classifier = SmartClassifier(rule_based=rule, llm=llm, min_conf=min_conf)
    else:
        classifier = rule

    responder = SimpleResponder()
    profiles = JsonProfileAdapter()

    return ClassifyEmailUseCase(
        file_facade=facade,
        tokenizer=tokenizer,
        classifier=classifier,
        responder=responder,
        profiles=profiles,
        log_repo=log_repo,
    )

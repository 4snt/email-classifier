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
    """Constrói o caso de uso para classificação via API HTTP"""
    init_db()
    session = next(get_session())

    log_repo = SqlLogRepository(session=session)

    facade = FileFacade(
        pdf_extractor=PdfExtractor(),
        txt_extractor=TxtExtractor(),
        eml_extractor=EmlExtractor(),
    )

    tokenizer = SimpleTokenizer(lang="auto")
    classifier = build_classifier()
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


def build_classifier():
    """Retorna o classificador (rule-based + opcional LLM)"""
    rule = RuleBasedClassifier()
    if getattr(settings, "USE_OPENAI", False):
        llm = OpenAIClassifier()
        min_conf = getattr(settings, "RB_MIN_CONF", 0.70)
        return SmartClassifier(rule_based=rule, llm=llm, min_conf=min_conf)
    return rule


def build_imap_deps():
    """Fornece classifier e log_repo para o serviço IMAP"""
    init_db()
    session = next(get_session())
    log_repo = SqlLogRepository(session=session)

    classifier = build_classifier()

    return classifier, log_repo

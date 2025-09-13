from app.application.use_cases.classify_email import FileFacade, ClassifyEmailUseCase
from app.infrastructure.extractors.pdf_extractor import PdfExtractor
from app.infrastructure.extractors.txt_extractor import TxtExtractor
from app.infrastructure.nlp.tokenizer_simple import SimpleTokenizer
from app.infrastructure.classifiers.rule_based import RuleBasedClassifier
from app.infrastructure.classifiers.openai_llm import OpenAIClassifier
from app.infrastructure.responders.simple_templates import SimpleResponder
from app.config import settings

def build_use_case():
    facade = FileFacade(pdf_extractor=PdfExtractor(), txt_extractor=TxtExtractor())
    tokenizer = SimpleTokenizer(lang="pt")
    classifier = OpenAIClassifier() if settings.USE_OPENAI else RuleBasedClassifier()
    responder = SimpleResponder()
    return ClassifyEmailUseCase(facade, tokenizer, classifier, responder)

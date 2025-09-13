from typing import List
from app.domain.entities import Email, ClassificationResult, Category
from app.domain.ports import ClassifierPort

PROD = {
    "reunião","agenda","contrato","proposta","orçamento","prazo","entrega","fatura","boleto",
    "currículo","vaga","entrevista","support","suporte","pedido","invoice","payment","pagamento"
}
IMPROD = {
    "promoção","desconto","oferta","newsletter","spam","inscreva-se","ganhe","cupom","marketing"
}

class RuleBasedClassifier(ClassifierPort):
    def classify(self, email: Email, tokens: List[str]) -> ClassificationResult:
        score_prod = sum(t in PROD for t in tokens)
        score_imp  = sum(t in IMPROD for t in tokens)
        if score_prod > score_imp:
            return ClassificationResult(Category.PRODUCTIVE, confidence=min(0.95, 0.6 + 0.1*score_prod),
                                        reason=f"palavras indicativas produtivas: {score_prod}")
        if score_imp > score_prod:
            return ClassificationResult(Category.UNPRODUCTIVE, confidence=min(0.95, 0.6 + 0.1*score_imp),
                                        reason=f"palavras indicativas improdutivas: {score_imp}")
        
        if len(email.body) > 10000:
            return ClassificationResult(Category.PRODUCTIVE, 0.55, "fallback pelo tamanho do corpo")
        return ClassificationResult(Category.UNPRODUCTIVE, 0.5, "fallback neutro")

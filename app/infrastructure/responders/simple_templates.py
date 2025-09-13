from app.domain.entities import ClassificationResult, Email, Category
from app.domain.ports import ReplySuggesterPort

class SimpleResponder(ReplySuggesterPort):
    def suggest(self, result: ClassificationResult, email: Email) -> str:
        if result.category is Category.PRODUCTIVE:
            return (
                "Olá! Obrigado pelo contato. "
                "Recebemos sua mensagem e vamos prosseguir com os próximos passos. "
                "Pode me indicar datas/horários disponíveis para alinharmos?"
            )
        # improdutivo
        return (
            "Olá! Obrigado pela mensagem. "
            "No momento, não temos interesse/necessidade. "
            "Caso algo mude, entraremos em contato."
        )

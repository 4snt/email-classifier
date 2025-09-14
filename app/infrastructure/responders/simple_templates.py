from app.domain.entities import ClassificationResult, Email, Category
from app.domain.ports import ReplySuggesterPort

class SimpleResponder(ReplySuggesterPort):
    def suggest(self, result: ClassificationResult, email: Email) -> str:
        if (result.suggested_reply or "").strip():
            return result.suggested_reply

        if result.category == Category.UNPRODUCTIVE:
            return ""

        lang = ((result.extra or {}).get("lang") or "pt").lower()

        if lang == "en":
            return ("Hi! Thanks for reaching out. We received your message and will proceed with the next steps. "
                    "Could you share a few available dates/times so we can align?")
        if lang == "es":
            return ("¡Hola! Gracias por el contacto. Recibimos tu mensaje y avanzaremos con los próximos pasos. "
                    "¿Podrías indicarnos fechas/horarios disponibles para alinear?")
        return ("Olá! Obrigado pelo contato. Recebemos sua mensagem e vamos prosseguir com os próximos passos. "
                "Pode me indicar datas/horários disponíveis para alinharmos?")

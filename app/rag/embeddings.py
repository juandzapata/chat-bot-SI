from config.settings import settings
import google.generativeai as genai
from chromadb.api.types import EmbeddingFunction

# Configurar Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiEmbeddingFunction(EmbeddingFunction):
    """
    Función de embeddings compatible con ChromaDB,
    utilizando el modelo de Gemini.
    """

    def __call__(self, input: str) -> list:
        if isinstance(input, list):
            # Si recibe una lista de textos
            return [self._embed_text(text) for text in input]
        # Si recibe un solo texto
        return [self._embed_text(input)]

    def _embed_text(self, text: str) -> list:
        if not text or text.strip() == "":
            raise ValueError("El texto para embedding no puede estar vacío.")

        # Usar directamente genai.embed_content en lugar de GenerativeModel
        response = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return response["embedding"]

# Instancia única para usar en todo el proyecto
embedding_function = GeminiEmbeddingFunction()

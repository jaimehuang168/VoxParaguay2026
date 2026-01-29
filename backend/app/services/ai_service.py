"""
VoxParaguay 2026 - AI Service
Claude 3.5 Sonnet integration for Jopara analysis and sentiment scoring
"""

from anthropic import Anthropic
from typing import Optional
from app.core.config import settings


class AIService:
    """
    AI-powered analysis service using Claude 3.5 Sonnet.
    Specialized for Jopara (Spanish-Guaraní) language processing.
    """

    JOPARA_SYSTEM_PROMPT = """Eres un experto en semántica paraguaya. Tu tarea es:

1. IDENTIFICACIÓN DE IDIOMA:
   - Detectar si la respuesta está en español, guaraní, o Jopara (mezcla)
   - Identificar palabras o frases en guaraní

2. TRADUCCIÓN:
   - Convertir respuestas en Jopara al español estándar
   - Preservar el significado cultural y emocional original
   - Mantener expresiones idiomáticas paraguayas

3. ANÁLISIS DE SENTIMIENTO:
   - Clasificar: positivo (0.1 a 1.0), negativo (-1.0 a -0.1), neutro (-0.1 a 0.1)
   - Considerar el contexto cultural paraguayo
   - Detectar sarcasmo o ironía

4. EXTRACCIÓN DE ETIQUETAS:
   - tendencia_politica: izquierda, centro-izquierda, centro, centro-derecha, derecha, sin_definir
   - demanda_ciudadana: salud, educación, seguridad, empleo, infraestructura, corrupción, economía, otro
   - percepcion_marca: positiva, negativa, neutra (para encuestas de marca)

5. CONTEXTO REGIONAL:
   - Considerar diferencias entre Asunción, Central, Alto Paraná, e Itapúa
   - Ajustar interpretación según dialecto regional

Responde siempre en formato JSON estructurado."""

    def __init__(self):
        self._client: Optional[Anthropic] = None

    @property
    def client(self) -> Anthropic:
        if self._client is None:
            self._client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    async def analyze_response(
        self,
        text: str,
        question_context: Optional[str] = None,
        region: Optional[str] = None,
    ) -> dict:
        """
        Analyze a survey response for sentiment and extract tags.

        Args:
            text: The respondent's answer
            question_context: The question that was asked
            region: Geographic region for context

        Returns:
            Analysis result with sentiment score, translation, and tags
        """
        user_prompt = f"""Analiza la siguiente respuesta de encuesta:

RESPUESTA: "{text}"
{f'PREGUNTA: "{question_context}"' if question_context else ''}
{f'REGIÓN: {region}' if region else ''}

Proporciona tu análisis en el siguiente formato JSON:
{{
    "idioma_detectado": "español|guaraní|jopara",
    "traduccion_espanol": "traducción al español estándar",
    "palabras_guarani": ["lista", "de", "palabras"],
    "sentimiento": {{
        "clasificacion": "positivo|negativo|neutro",
        "puntaje": <número entre -1.0 y 1.0>,
        "confianza": <número entre 0 y 1>
    }},
    "etiquetas": {{
        "tendencia_politica": "categoria",
        "demanda_ciudadana": ["lista", "de", "temas"],
        "percepcion_marca": "categoria"
    }},
    "notas_culturales": "observaciones relevantes"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=self.JOPARA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # Parse JSON response
        import json
        try:
            content = response.content[0].text
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())
        except (json.JSONDecodeError, IndexError):
            return {
                "error": "No se pudo parsear la respuesta",
                "raw_response": response.content[0].text
            }

    async def translate_jopara(self, text: str) -> dict:
        """
        Translate Jopara text to standard Spanish.

        Args:
            text: Text in Jopara or Guaraní

        Returns:
            Translation result with original words identified
        """
        user_prompt = f"""Traduce el siguiente texto de Jopara/Guaraní al español:

TEXTO: "{text}"

Responde en formato JSON:
{{
    "traduccion": "texto traducido al español",
    "palabras_guarani": [
        {{"original": "palabra", "significado": "traducción"}}
    ],
    "nivel_mezcla": "porcentaje aproximado de guaraní"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=self.JOPARA_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )

        import json
        try:
            content = response.content[0].text
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            return json.loads(content.strip())
        except:
            return {"traduccion": text, "palabras_guarani": [], "nivel_mezcla": "0%"}

    async def calculate_weighted_sentiment(
        self,
        responses: list[dict],
    ) -> dict:
        """
        Calculate final sentiment score using weighted formula.
        S_final = Σ(w_i * s_i) / N

        Args:
            responses: List of dicts with 'score' and 'weight' keys

        Returns:
            Weighted sentiment calculation
        """
        if not responses:
            return {"puntaje_final": 0.0, "total_respuestas": 0}

        total_weighted = sum(
            r.get("score", 0) * r.get("weight", 1.0)
            for r in responses
        )
        n = len(responses)

        return {
            "puntaje_final": round(total_weighted / n, 4),
            "total_respuestas": n,
            "formula": "S_final = Σ(w_i × s_i) / N"
        }

    async def generate_survey_summary(
        self,
        responses: list[str],
        question: str,
    ) -> str:
        """
        Generate a natural language summary of survey responses.

        Args:
            responses: List of response texts
            question: The survey question

        Returns:
            Summary text in Spanish
        """
        user_prompt = f"""Resume las siguientes respuestas a una encuesta:

PREGUNTA: "{question}"

RESPUESTAS:
{chr(10).join(f'- {r}' for r in responses[:50])}  # Limit to 50

Proporciona:
1. Resumen general (2-3 oraciones)
2. Temas principales mencionados
3. Sentimiento predominante
4. Citas textuales representativas (máximo 3)"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system="Eres un analista de encuestas experto en Paraguay.",
            messages=[{"role": "user", "content": user_prompt}]
        )

        return response.content[0].text


# Singleton instance
ai_service = AIService()

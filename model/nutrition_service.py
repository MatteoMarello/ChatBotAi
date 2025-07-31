import httpx
import os
from typing import Dict, Optional
import asyncio

# Import delle eccezioni che funziona con tutte le versioni di httpx
try:
    # Prova prima l'import moderno (httpx >= 0.24)
    from httpx import RequestError, HTTPStatusError, TimeoutException
except ImportError:
    try:
        # Fallback per versioni più vecchie
        from httpx.exceptions import RequestError, HTTPStatusError, TimeoutException
    except ImportError:
        # Se non riesce, usa le eccezioni base
        RequestError = Exception
        HTTPStatusError = Exception
        TimeoutException = Exception


class NutritionService:
    """Servizio per gestire le chiamate API del coach nutrizionale"""

    def __init__(self, api_key: Optional[str] = None):
        # CORREZIONE: Prima prova il parametro, poi la variabile d'ambiente, infine usa la chiave hardcoded
        self.api_key = (
                api_key or
                os.getenv("OPENROUTER_API_KEY") or
                "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"
        )

        if not self.api_key:
            raise ValueError(
                "API Key mancante. Imposta OPENROUTER_API_KEY come variabile d'ambiente "
                "o passa la chiave nel costruttore."
            )

        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1:free"
        self.timeout = 30

    async def get_nutrition_advice(self, user_message: str, context: str) -> str:
        """
        Ottiene consigli nutrizionali dall'AI

        Args:
            user_message: Messaggio dell'utente
            context: Contesto nutrizionale (dati TDEE, ecc.)

        Returns:
            Risposta dell'AI coach
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Prompt migliorato per il coach nutrizionale
        system_prompt = self._create_system_prompt(context)

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 1000,
            "temperature": 0.7,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )

                if response.status_code != 200:
                    error_detail = await self._parse_error(response)
                    raise Exception(f"Errore API ({response.status_code}): {error_detail}")

                result = response.json()

                if 'choices' not in result or not result['choices']:
                    raise Exception("Risposta API malformata")

                return result['choices'][0]['message']['content'].strip()

        except RequestError as e:  # Gestisce errori di connessione e timeout
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise Exception("Timeout nella richiesta API")
            else:
                raise Exception(f"Errore di connessione: {str(e)}")
        except HTTPStatusError as e:  # Gestione specifica per errori HTTP
            try:
                raise Exception(f"Errore HTTP: {e.response.status_code} - {e.response.text}")
            except AttributeError:
                raise Exception(f"Errore HTTP: {str(e)}")
        except TimeoutException as e:  # Gestione specifica per timeout
            raise Exception("Timeout nella richiesta API")
        except Exception as e:
            if "Errore API" in str(e) or "Timeout" in str(e) or "connessione" in str(e):
                raise
            else:
                raise Exception(f"Errore imprevisto: {str(e)}")

    def _create_system_prompt(self, context: str) -> str:
        """Crea un prompt di sistema ottimizzato per il coach nutrizionale"""

        base_prompt = """Sei un esperto coach nutrizionale qualificato con anni di esperienza. 
Il tuo compito è fornire consigli personalizzati, pratici e basati su evidenze scientifiche.

LINEE GUIDA IMPORTANTI:
1. Fornisci sempre consigli sicuri e bilanciati
2. Se l'utente ha condizioni mediche, suggerisci di consultare un medico
3. Sii specifico e pratico nei tuoi consigli
4. Includi esempi concreti quando possibile
5. Mantieni un tono professionale ma amichevole
6. Se suggerisci pasti, assicurati che rispettino i macro dell'utente

LIMITAZIONI:
- Non fare diagnosi mediche
- Non prescrivere integratori senza supervisione medica
- Non dare consigli estremi o pericolosi
"""

        return f"{base_prompt}\n\nCONTESTO UTENTE:\n{context}"

    async def _parse_error(self, response) -> str:
        """Analizza gli errori dell'API per fornire messaggi utili"""
        try:
            error_data = response.json()
            if 'error' in error_data:
                return error_data['error'].get('message', 'Errore sconosciuto')
        except:
            pass

        # Errori comuni
        if response.status_code == 401:
            return "Chiave API non valida o scaduta"
        elif response.status_code == 429:
            return "Troppi richieste. Riprova tra qualche minuto"
        elif response.status_code >= 500:
            return "Servizio temporaneamente non disponibile"
        else:
            return f"Errore HTTP {response.status_code}"


class NutritionCache:
    """Cache semplice per le risposte del coach per evitare richieste duplicate"""

    def __init__(self, max_size: int = 50):
        self.cache: Dict[str, str] = {}
        self.max_size = max_size

    def get(self, key: str) -> Optional[str]:
        return self.cache.get(self._hash_key(key))

    def set(self, key: str, value: str):
        hashed_key = self._hash_key(key)

        if len(self.cache) >= self.max_size:
            # Rimuovi il primo elemento (FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[hashed_key] = value

    def _hash_key(self, key: str) -> str:
        """Crea un hash semplice della chiave"""
        return str(hash(key) % 1000000)

    def clear(self):
        """Pulisce la cache"""
        self.cache.clear()



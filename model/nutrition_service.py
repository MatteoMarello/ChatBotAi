import httpx
import os
from typing import Dict, Optional
import asyncio
import re

# Import delle eccezioni che funziona con tutte le versioni di httpx
try:
    from httpx import RequestError, HTTPStatusError, TimeoutException
except ImportError:
    try:
        from httpx.exceptions import RequestError, HTTPStatusError, TimeoutException
    except ImportError:
        RequestError = Exception
        HTTPStatusError = Exception
        TimeoutException = Exception


class SafetyFilter:
    """Filtro di sicurezza per domande nutrizionali"""

    def __init__(self):
        # Solo situazioni realmente rischiose che richiedono attenzione medica
        self.high_risk_keywords = [
            'diabete', 'diabetico', 'insulina', 'gravidanza', 'incinta', 'allattamento',
            'bambino', 'neonato', 'anziano over 80', 'farmaco', 'medicina', 'terapia',
            'malattia grave', 'cancro', 'tumore', 'chemio', 'dialisi', 'trapianto'
        ]

        # Richieste veramente pericolose (diete estreme)
        self.dangerous_keywords = [
            'digiuno prolungato', 'non mangiare per giorni', 'solo acqua per',
            'perdere 10 kg in una settimana', 'anabolizzanti', 'steroidi',
            'pillole dimagranti forti', 'lassativi per dimagrire'
        ]

        # Condizioni che richiedono solo un breve accenno alla consulenza medica
        self.medical_conditions = [
            'colesterolo', 'pressione', 'celiachia', 'allergia', 'intolleranza',
            'gastrite', 'reflusso', 'tiroide', 'anemia', 'osteoporosi'
        ]

    def get_risk_level(self, text: str) -> str:
        """Determina il livello di rischio: none, low, high, dangerous"""
        text_lower = text.lower()

        if any(keyword in text_lower for keyword in self.dangerous_keywords):
            return 'dangerous'
        elif any(keyword in text_lower for keyword in self.high_risk_keywords):
            return 'high'
        elif any(keyword in text_lower for keyword in self.medical_conditions):
            return 'low'
        else:
            return 'none'


class NutritionService:
    """Servizio per gestire le chiamate API del coach nutrizionale"""

    def __init__(self, api_key: Optional[str] = None):
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
        self.timeout = 45  # Aumentato timeout
        self.safety_filter = SafetyFilter()

    async def get_nutrition_advice(self, user_message: str, context: str) -> str:
        """
        Ottiene consigli nutrizionali dall'AI con controlli di sicurezza bilanciati

        Args:
            user_message: Messaggio dell'utente
            context: Contesto nutrizionale (dati TDEE, ecc.)

        Returns:
            Risposta dell'AI coach con disclaimer proporzionati al rischio
        """

        risk_level = self.safety_filter.get_risk_level(user_message)

        # Solo per richieste veramente pericolose
        if risk_level == 'dangerous':
            return self._get_safety_response(user_message)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        system_prompt = self._create_system_prompt(context, risk_level)

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 2500,  # AUMENTATO da 1000 a 2500
            "temperature": 0.7,
            "stream": False,
            "stop": None  # Rimosso qualsiasi stop token
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

                ai_response = result['choices'][0]['message']['content'].strip()

                # Controlla se la risposta è stata troncata
                finish_reason = result['choices'][0].get('finish_reason', '')

                if finish_reason == 'length':
                    # Se troncata, prova a continuare la risposta
                    ai_response = await self._complete_truncated_response(
                        ai_response, user_message, context, headers
                    )

                # Aggiungi disclaimer solo quando necessario
                final_response = self._add_appropriate_disclaimer(ai_response, risk_level)

                return final_response

        except RequestError as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                raise Exception("Timeout nella richiesta API")
            else:
                raise Exception(f"Errore di connessione: {str(e)}")
        except HTTPStatusError as e:
            try:
                raise Exception(f"Errore HTTP: {e.response.status_code} - {e.response.text}")
            except AttributeError:
                raise Exception(f"Errore HTTP: {str(e)}")
        except TimeoutException as e:
            raise Exception("Timeout nella richiesta API")
        except Exception as e:
            if "Errore API" in str(e) or "Timeout" in str(e) or "connessione" in str(e):
                raise
            else:
                raise Exception(f"Errore imprevisto: {str(e)}")

    async def _complete_truncated_response(self, truncated_response: str,
                                           user_message: str, context: str,
                                           headers: dict) -> str:
        """
        Cerca di completare una risposta che è stata troncata
        """
        try:
            # Prompt per continuare la risposta
            continue_prompt = f"""Continua la risposta nutrizionale precedente che si è interrotta qui:

"{truncated_response[-200:]}"

Completa la risposta in modo naturale e coerente, fornendo tutti i dettagli mancanti."""

            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._create_system_prompt(context, 'none')},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": truncated_response},
                    {"role": "user", "content": continue_prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7,
                "stream": False
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )

                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        continuation = result['choices'][0]['message']['content'].strip()
                        # Unisci le due parti
                        return truncated_response + "\n\n" + continuation

        except Exception as e:
            print(f"Errore nel completamento: {e}")
            # Se fallisce, restituisci la risposta troncata originale
            pass

        return truncated_response

    def _get_safety_response(self, user_message: str) -> str:
        """Risposta solo per richieste veramente pericolose"""
        return """⚠️ **Non posso aiutarti con questa richiesta**

La tua domanda riguarda pratiche alimentari potenzialmente rischiose. 

**Consulta un medico o nutrizionista** per:
- Diete molto restrittive o digiuni prolungati
- Perdite di peso molto rapide
- Uso di sostanze o integratori specifici

💡 **Prova invece a chiedermi:**
- Consigli per pasti bilanciati
- Come organizzare una dieta sana
- Informazioni sui nutrienti
- Ricette equilibrate

Sono qui per aiutarti in modo sicuro! 😊"""

    def _create_system_prompt(self, context: str, risk_level: str) -> str:
        """Crea un prompt di sistema proporzionato al rischio"""

        base_prompt = f"""Sei un coach nutrizionale esperto e pratico. Fornisci consigli completi, dettagliati e bilanciati sull'alimentazione.

CONTESTO UTENTE:
{context}

LINEE GUIDA:
- Dai consigli pratici e realizzabili
- Basa le tue risposte su principi nutrizionali solidi
- Sii diretto e utile, evita eccessiva cautela
- Fornisci informazioni concrete e actionable
- IMPORTANTE: Completa sempre le tue risposte con tutti i dettagli necessari
- Non interrompere mai le spiegazioni a metà
- Fornisci esempi concreti e piani dettagliati quando richiesto
- Usa formattazione markdown per rendere le risposte più leggibili
- Includi sempre tutte le sezioni richieste nella domanda"""

        # Aggiungi avvertenze solo per rischio alto
        if risk_level == 'high':
            base_prompt += """

IMPORTANTE: Se la domanda riguarda condizioni mediche serie, ricorda di suggerire consulenza medica oltre ai tuoi consigli generali."""

        elif risk_level == 'low':
            base_prompt += """

NOTA: Se appropriato, ricorda che per condizioni specifiche è sempre bene consultare un professionista."""

        return base_prompt

    def _add_appropriate_disclaimer(self, ai_response: str, risk_level: str) -> str:
        """Aggiunge disclaimer proporzionati al livello di rischio"""

        if risk_level == 'high':
            # Solo per situazioni ad alto rischio
            disclaimer = "\n\n💡 **Nota importante**: Per condizioni mediche specifiche, è sempre consigliabile consultare il tuo medico o un nutrizionista qualificato."
            return ai_response + disclaimer

        elif risk_level == 'low':
            # Disclaimer minimo per condizioni minori
            disclaimer = "\n\n📋 *Per condizioni specifiche, considera di consultare un professionista.*"
            return ai_response + disclaimer

        else:
            # Nessun disclaimer per domande normali
            return ai_response

    async def _parse_error(self, response) -> str:
        """Analizza gli errori dell'API per fornire messaggi utili"""
        try:
            error_data = response.json()
            if 'error' in error_data:
                return error_data['error'].get('message', 'Errore sconosciuto')
        except:
            pass

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
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[hashed_key] = value

    def _hash_key(self, key: str) -> str:
        return str(hash(key) % 1000000)

    def clear(self):
        self.cache.clear()

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class Esercizio:
    """DataClass per rappresentare un esercizio di allenamento."""
    id: int
    nome: str
    attrezzatura: Union[list[str], str]
    livello: int
    muscolo_primario: str
    muscoli_secondari: Union[list[str], str]
    recupero_secondi: int
    affaticamento: int
    tipologia: str
    articolazioni: Union[list[str], str]
    descrizione: str
    range_ripetizioni: Union[list[int], str]
    created_at: datetime
    updated_at: datetime

    def _post_init_(self):
        """Conversione automatica dei campi stringa JSON in liste."""
        for attr in ['attrezzatura', 'muscoli_secondari', 'articolazioni']:
            val = getattr(self, attr)
            if isinstance(val, str):
                try:
                    setattr(self, attr, json.loads(val))
                except (json.JSONDecodeError, Exception):
                    setattr(self, attr, [val] if val else [])
            elif not isinstance(val, list):
                setattr(self, attr, [str(val)] if val else [])

        if isinstance(self.range_ripetizioni, str):
            try:
                self.range_ripetizioni = json.loads(self.range_ripetizioni)
            except json.JSONDecodeError:
                if '-' in self.range_ripetizioni:
                    parts = self.range_ripetizioni.split('-')
                    try:
                        self.range_ripetizioni = [int(parts[0]), int(parts[1])]
                    except ValueError:
                        self.range_ripetizioni = [5, 10]
                else:
                    try:
                        num_rep = int(self.range_ripetizioni)
                        self.range_ripetizioni = [num_rep, num_rep + 2]
                    except ValueError:
                        self.range_ripetizioni = [5, 10]

        if not isinstance(self.range_ripetizioni, list) or len(self.range_ripetizioni) < 2:
            self.range_ripetizioni = [5, 10]
        if self.range_ripetizioni[0] > self.range_ripetizioni[1]:
            self.range_ripetizioni.reverse()

    def __hash__(self):
        return hash(self.id)  # Assuming each exercise has a unique id

    def __eq__(self, other):
        return isinstance(other, Esercizio) and self.id == other.id

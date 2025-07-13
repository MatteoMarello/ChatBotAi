from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from esercizio import Esercizio  # Import della tua classe Esercizio


@dataclass
class WorkoutDay:
    id_giorno: int  # Ordine del giorno nella settimana
    settimana: int  # Numero della settimana
    split_type: str  # Tipo di split (es. Full Body, Upper, etc.)
    data: datetime  # Data del workout
    esercizi: List[Esercizio] = field(default_factory=list)

    # Metriche di feedback
    performance_log: Dict[int, Dict] = field(
        default_factory=dict)  # key = esercizio.id, value = {carico, ripetizioni, rir, note}
    doms_per_muscolo: Dict[str, int] = field(default_factory=dict)  # Es: {'Petto': 2, 'Schiena': 1}
    pump_per_muscolo: Dict[str, int] = field(default_factory=dict)  # Es: {'Petto': 3, 'Schiena': 2}
    mmc_per_muscolo: Dict[str, int] = field(default_factory=dict)  # Es: {'Petto': 2, 'Schiena': 3}

    def registra_performance(self, esercizio: Esercizio, carico: float, ripetizioni: int, rir: int, note: str = ""):
        self.performance_log[esercizio.id] = {
            "nome": esercizio.nome,
            "muscolo_primario": esercizio.muscolo_primario,
            "carico": carico,
            "ripetizioni": ripetizioni,
            "rir": rir,
            "note": note
        }

    def registra_feedback_muscolo(self, muscolo: str, doms: int, pump: int, mmc: int):
        self.doms_per_muscolo[muscolo] = doms
        self.pump_per_muscolo[muscolo] = pump
        self.mmc_per_muscolo[muscolo] = mmc

    def muscoli_lavorati(self) -> List[str]:
        return list({e.muscolo_primario for e in self.esercizi})

    def totale_serie_giornata(self) -> int:
        # Supponiamo che ogni esercizio abbia un attributo 'serie' se ti serve, oppure da performance_log
        return sum(perf.get("ripetizioni", 0) for perf in self.performance_log.values())

    def __str__(self):
        descrizione = f"Workout Giorno {self.id_giorno} (Settimana {self.settimana} - Split: {self.split_type})\n"
        for e in self.esercizi:
            perf = self.performance_log.get(e.id, {})
            carico = perf.get('carico', '-')
            reps = perf.get('ripetizioni', '-')
            rir = perf.get('rir', '-')
            descrizione += f"- {e.nome}: {reps} reps @ {carico}kg (RIR: {rir})\n"
        descrizione += f"DOMS: {self.doms_per_muscolo}\n"
        descrizione += f"Pump: {self.pump_per_muscolo}\n"
        descrizione += f"MMC: {self.mmc_per_muscolo}\n"
        return descrizione

    def aggiungi_esercizio(self, esercizio: Esercizio, serie: int):
        self.esercizi.append(esercizio)
        self.performance_log[esercizio.id] = {
            "nome": esercizio.nome,
            "muscolo_primario": esercizio.muscolo_primario,
            "serie": serie,
            "carico": 0,
            "ripetizioni": 0,
            "rir": 0,
            "note": ""
        }


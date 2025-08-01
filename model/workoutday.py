from dataclasses import field, dataclass
from datetime import datetime
from model.esercizio import Esercizio


@dataclass
class WorkoutDay:
    """Rappresenta un singolo giorno di allenamento."""
    id_giorno: int
    settimana: int
    split_type: str
    data: datetime
    esercizi: list[Esercizio] = field(default_factory=list)
    performance_log: dict[int, dict] = field(default_factory=dict)
    ordine_muscoli: dict[str, int] = field(default_factory=dict)
    adjustment_message: str = ""  # Messaggio dall'algoritmo di autoregolazione

    def aggiungi_esercizio(self, esercizio: Esercizio, serie: int, reps: list[str], ordine_muscolo: int = None):
        """
        Aggiunge un esercizio al giorno di allenamento.

        Args:
            esercizio: L'esercizio da aggiungere
            serie: Numero di serie
            reps: Lista di stringhe con i rep ranges (es. ["6-8", "6-8", "12-14"])
            ordine_muscolo: Ordine del muscolo nella gerarchia (opzionale)
        """
        if esercizio not in self.esercizi:
            self.esercizi.append(esercizio)

        if ordine_muscolo is not None:
            self.ordine_muscoli[esercizio.muscolo_primario] = ordine_muscolo

        # Converti reps in lista se è una stringa singola
        if isinstance(reps, str):
            reps = [reps] * serie

        # Assicurati che ci siano abbastanza rep ranges
        if len(reps) < serie:
            reps.extend([reps[-1]] * (serie - len(reps)))

        self.performance_log[esercizio.id] = {
            "nome": esercizio.nome,
            "muscolo_primario": esercizio.muscolo_primario,
            "serie": serie,
            "reps": reps  # Salva la lista completa dei rep ranges
        }
    def __str__(self):
        descrizione = f"┌─ GIORNO {self.id_giorno} ({self.split_type}) ─ {self.data.strftime('%d/%m/%Y')} ─┐\n"

        if not self.esercizi:
            descrizione += "│  💤 GIORNO DI RIPOSO                     │\n"
            descrizione += "└─────────────────────────────────────────┘\n"
            return descrizione

        def get_ordine_muscolo(item):
            muscolo = item[0]
            return self.ordine_muscoli.get(muscolo, 999)

        esercizi_per_muscolo = {}
        for esercizio in esercizi:
            perf = self.performance_log.get(esercizio.id, {})
            serie_txt = f"{perf.get('serie', 0)} serie"
            reps = perf.get('reps', ['N/D'])
            note_txt = ", ".join(reps)  # Unisce i rep ranges con virgole
            descrizione += f"│   • {esercizio.nome:<30} │ {serie_txt:<8} │ {note_txt:<18} │\n"

        muscoli_ordinati = sorted(esercizi_per_muscolo.items(), key=get_ordine_muscolo)

        for muscolo, esercizi in muscoli_ordinati:
            descrizione += f"│\n│ 🎯 {muscolo.upper()}\n"
            for esercizio in esercizi:
                perf = self.performance_log.get(esercizio.id, {})
                serie_txt = f"{perf.get('serie', 0)} serie"
                note_txt = perf.get('note', 'N/A')
                descrizione += f"│   • {esercizio.nome:<30} │ {serie_txt:<8} │ {note_txt:<18} │\n"

        descrizione += "└────────────────────────────────────────────────────────────────────────┘\n"
        return descrizione

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
    # Aggiungi un campo per tenere traccia dell'ordine dei muscoli
    ordine_muscoli: dict[str, int] = field(default_factory=dict)

    def aggiungi_esercizio(self, esercizio: Esercizio, serie: int, rep_range: list[str], ordine_muscolo: int = None):
        """
        Aggiunge un esercizio al giorno di allenamento.

        Args:
            esercizio: L'esercizio da aggiungere
            serie: Numero di serie
            rep_range: Lista dei range di ripetizioni
            ordine_muscolo: Ordine del muscolo nella gerarchia (opzionale)
        """
        if esercizio not in self.esercizi:
            self.esercizi.append(esercizio)

        # Memorizza l'ordine del muscolo se fornito
        if ordine_muscolo is not None:
            self.ordine_muscoli[esercizio.muscolo_primario] = ordine_muscolo

        log = self.performance_log.setdefault(esercizio.id, {
            "nome": esercizio.nome,
            "muscolo_primario": esercizio.muscolo_primario,
            "serie": 0,
            "ripetizioni": [],
            "note": ""
        })
        log["serie"] += serie
        log["ripetizioni"].extend(rep_range)
        # Crea una nota sintetica dei range di ripetizioni per quel giorno
        unique_reps = sorted(list(set(log["ripetizioni"])))
        log["note"] = f"Range {' & '.join(unique_reps)} reps"

    def __str__(self):
        descrizione = f"┌─ GIORNO {self.id_giorno} ({self.split_type}) ─ {self.data.strftime('%d/%m/%Y')} ─┐\n"

        if not self.esercizi:
            descrizione += "│  💤 GIORNO DI RIPOSO                     │\n"
            descrizione += "└─────────────────────────────────────────┘\n"
            return descrizione

        # Raggruppa esercizi per muscolo per una migliore organizzazione
        esercizi_per_muscolo = {}
        for esercizio in self.esercizi:
            muscolo = esercizio.muscolo_primario
            if muscolo not in esercizi_per_muscolo:
                esercizi_per_muscolo[muscolo] = []
            esercizi_per_muscolo[muscolo].append(esercizio)

        # Ordina i muscoli secondo la gerarchia invece che alfabeticamente
        def get_ordine_muscolo(item):
            muscolo = item[0]
            return self.ordine_muscoli.get(muscolo, 999)  # 999 per muscoli senza ordine definito

        muscoli_ordinati = sorted(esercizi_per_muscolo.items(), key=get_ordine_muscolo)

        for muscolo, esercizi in muscoli_ordinati:
            descrizione += f"│\n│ 🎯 {muscolo.upper()}\n"
            for esercizio in esercizi:
                perf = self.performance_log.get(esercizio.id, {})
                serie = perf.get('serie', 0)
                ripetizioni = perf.get('ripetizioni', [])

                # Formatta le ripetizioni in modo più leggibile
                if ripetizioni:
                    # Conta le occorrenze di ogni range
                    rep_counts = {}
                    for rep in ripetizioni:
                        rep_counts[rep] = rep_counts.get(rep, 0) + 1

                    # Crea una stringa formattata
                    rep_string = " + ".join([f"{count}x{rep}" for rep, count in sorted(rep_counts.items())])
                else:
                    rep_string = "N/A"

                descrizione += f"│   • {esercizio.nome:<30} │ {serie:2d} serie │ {rep_string:<15} │ RIR 4 │\n"

        descrizione += "└─────────────────────────────────────────────────────────────────────────┘\n"
        return descrizione

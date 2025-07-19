from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import math
from collections import defaultdict

# Importa le tue classi esistenti
from model.esercizio import Esercizio
from model.workoutday import WorkoutDay
from model.trainingweek import TrainingWeek


@dataclass
class PerformanceData:
    """Dati di performance per un esercizio in un giorno specifico."""
    esercizio_id: int
    giorno: int
    settimana: int
    muscolo_primario: str  # <-- AGGIUNGI QUESTA RIGA
    mmc: int  # Mind Muscle Connection (1-3)
    pump: int  # Pump (1-3)
    dolori_articolari: int  # Dolori articolari (1-3)
    sets: List[Tuple[float, int, str]]
    rsm: float = 0.0
    fi: float = 0.0
    sfr: float = 0.0
    one_rm: float = 0.0
    perdita_performance: float = 0.0

    def __post_init__(self):
        self.rsm = self.mmc + self.pump
        self.one_rm = self.calcola_1rm_migliore()

    def _calcola_1rm_epley(self, carico: float, ripetizioni: int) -> float:
        if ripetizioni <= 0 or carico <= 0:
            return 0.0
        return carico * (1 + ripetizioni / 30)

    def calcola_1rm_migliore(self) -> float:
        if not self.sets:
            return 0.0
        max_one_rm = 0.0
        for carico, ripetizioni, _ in self.sets:  # Ignora il rep_range_target qui
            one_rm_serie = self._calcola_1rm_epley(carico, ripetizioni)
            if one_rm_serie > max_one_rm:
                max_one_rm = one_rm_serie
        return max_one_rm


@dataclass
class DOMSData:
    """Dati DOMS per un gruppo muscolare."""
    muscolo: str
    giorno: int
    settimana: int
    doms_value: int  # 1-3


@dataclass
class TrainingAlgorithm:
    """Algoritmo completo di allenamento per 3 settimane."""
    performance_data: Dict[int, List[PerformanceData]] = field(default_factory=dict)
    doms_data: Dict[int, List[DOMSData]] = field(default_factory=dict)
    sfr_settimana_1: Dict[int, float] = field(default_factory=dict)
    sfr_settimana_3: Dict[int, float] = field(default_factory=dict)
    sfr_medio_finale: Dict[int, float] = field(default_factory=dict)
    rir_progressivo: Dict[int, int] = field(default_factory=lambda: {1: 4, 2: 3, 3: 2})

    def aggiungi_performance(self, settimana: int, performance: PerformanceData):
        if settimana not in self.performance_data:
            self.performance_data[settimana] = []
        self.performance_data[settimana].append(performance)

    def aggiungi_doms(self, settimana: int, doms: DOMSData):
        if settimana not in self.doms_data:
            self.doms_data[settimana] = []
        self.doms_data[settimana].append(doms)

    def _calcola_1rm_epley(self, carico: float, ripetizioni: int) -> float:
        """Helper per calcolare 1RM per una singola serie."""
        if ripetizioni <= 0 or carico <= 0: return 0.0
        return carico * (1 + ripetizioni / 30)
    # ===== SETTIMANA 1 =====

    def calcola_sfr_settimana_1(self) -> Dict[int, float]:
        """Calcola SFR per settimana 1."""
        sfr_per_esercizio = {}

        if 1 not in self.performance_data:
            return sfr_per_esercizio

        for perf in self.performance_data[1]:
            # FI = max(1, Dolori + Perdita Performance)
            # In settimana 1, Perdita Performance = 0
            perf.fi = max(1, perf.dolori_articolari + 0)
            perf.sfr = perf.rsm / perf.fi

            # Salva SFR per esercizio
            if perf.esercizio_id not in sfr_per_esercizio:
                sfr_per_esercizio[perf.esercizio_id] = []
            sfr_per_esercizio[perf.esercizio_id].append(perf.sfr)

        # Calcola media SFR per esercizio
        self.sfr_settimana_1 = {
            esercizio_id: sum(sfr_list) / len(sfr_list)
            for esercizio_id, sfr_list in sfr_per_esercizio.items()
        }

        return self.sfr_settimana_1

    # In adattaScheda.py

    def calcola_previsione_serie_settimana_2(self, muscolo: str, esperienza: str) -> tuple[str, str | None]:
        """
        Calcola previsione serie per settimana 2, differenziando per esperienza.
        Restituisce raccomandazione e motivo.
        """
        if 2 not in self.doms_data:
            return "mantieni", "Dati DOMS non disponibili per la settimana 2."

        doms_muscolo = None
        for doms in self.doms_data[2]:
            if doms.muscolo.lower() == muscolo.lower():
                doms_muscolo = doms.doms_value
                break

        if doms_muscolo is None:
            return "mantieni", f"Valore DOMS non inserito per {muscolo}."

        esercizi_muscolo = self.get_esercizi_per_muscolo(muscolo, 1)
        if not esercizi_muscolo:
            return "mantieni", f"Dati performance mancanti per {muscolo} in settimana 1."

        x_values = []
        for esercizio_id in esercizi_muscolo:
            if esercizio_id in self.sfr_settimana_1:
                rsm = self.get_rsm_esercizio(esercizio_id, 1)
                x_values.append(rsm + doms_muscolo)

        if not x_values:
            return "mantieni", f"Dati RSM non calcolabili per {muscolo} in settimana 1."

        x_medio = sum(x_values) / len(x_values)

        # --- LOGICA DIFFERENZIATA PER ESPERIENZA ---
        if x_medio <= 4:  # Condizione per aumentare il volume
            if esperienza == "principiante":
                return "+2 serie", None
            else:  # intermedio o avanzato
                return "+3 serie", None
        elif 5 <= x_medio <= 7:  # Condizione per mantenere
            return "mantieni", None
        else:  # x_medio > 7, condizione per diminuire
            if esperienza == "principiante":
                return "-2 serie", None
            else:  # intermedio o avanzato
                return "-3 serie", None

    def calcola_miglioramento_performance_settimana_2(self) -> Dict[int, float]:
        """
        Calcola il miglioramento % della performance tra settimana 1 e 2, confrontando
        le serie solo all'interno dello stesso rep range target.
        """
        if 1 not in self.performance_data or 2 not in self.performance_data:
            return {}

        # Struttura dati: { (esercizio_id, rep_range_target): { settimana: [lista_1rm] } }
        dati_per_gruppo = defaultdict(lambda: defaultdict(list))

        # Popola la struttura dati con gli 1RM di ogni serie
        for settimana, performances in self.performance_data.items():
            if settimana in [1, 2]:
                for perf in performances:
                    for carico, reps, rep_range in perf.sets:
                        one_rm = self._calcola_1rm_epley(carico, reps)
                        if one_rm > 0:
                            chiave = (perf.esercizio_id, rep_range)
                            dati_per_gruppo[chiave][settimana].append(one_rm)

        # Calcola i miglioramenti per ogni gruppo
        miglioramenti_per_esercizio = defaultdict(list)
        for (esercizio_id, rep_range), dati_settimanali in dati_per_gruppo.items():
            if 1 in dati_settimanali and 2 in dati_settimanali:
                avg_1rm_sett1 = sum(dati_settimanali[1]) / len(dati_settimanali[1])
                avg_1rm_sett2 = sum(dati_settimanali[2]) / len(dati_settimanali[2])

                if avg_1rm_sett1 > 0:
                    miglioramento_pct = ((avg_1rm_sett2 - avg_1rm_sett1) / avg_1rm_sett1) * 100
                    miglioramenti_per_esercizio[esercizio_id].append(miglioramento_pct)

        # Calcola la media dei miglioramenti per ogni esercizio
        risultato_finale = {}
        for esercizio_id, lista_miglioramenti in miglioramenti_per_esercizio.items():
            if lista_miglioramenti:
                risultato_finale[esercizio_id] = sum(lista_miglioramenti) / len(lista_miglioramenti)

        return risultato_finale

    def calcola_punti_performance_settimana_2(self) -> Dict[int, int]:
        """
        Calcola punti performance per settimana 2 basati sui miglioramenti medi.
        """
        miglioramenti = self.calcola_miglioramento_performance_settimana_2()
        punti = {}

        for esercizio_id, miglioramento_pct in miglioramenti.items():
            if miglioramento_pct >= 5:
                punti[esercizio_id] = 2
            elif 2 <= miglioramento_pct < 5:
                punti[esercizio_id] = 1
            elif 0 <= miglioramento_pct < 2:
                punti[esercizio_id] = 0
            elif -2 <= miglioramento_pct < 0:
                punti[esercizio_id] = -1
            else:  # miglioramento_pct < -2
                punti[esercizio_id] = -2

        return punti

    def calcola_serie_settimana_3(self, muscolo: str) -> str:
        """
        Calcola serie per settimana 3 basata sulla media dei punti performance
        di tutti gli esercizi del gruppo muscolare.
        """
        punti = self.calcola_punti_performance_settimana_2()
        esercizi_muscolo = self.get_esercizi_per_muscolo(muscolo, 2)

        if not esercizi_muscolo:
            return "mantieni"

        # Calcola media punti per gruppo muscolare
        punti_muscolo = [punti.get(esercizio_id, 0) for esercizio_id in esercizi_muscolo]
        media_punti = sum(punti_muscolo) / len(punti_muscolo)

        # Debug info (opzionale)
        print(f"Muscolo {muscolo}: Punti individuali = {punti_muscolo}, Media = {media_punti:.2f}")

        # Converte in raccomandazione serie
        if media_punti >= 1.5:
            return "+3 serie"
        elif 0.5 <= media_punti < 1.5:
            return "+2 serie"
        elif -0.4 <= media_punti <= 0.4:
            return "mantieni"
        elif -1.4 <= media_punti < -0.5:
            return "-1 serie"
        else:  # media_punti <= -1.5
            return "-2 serie"
    # ===== SETTIMANA 3 =====

    def calcola_sfr_settimana_3(self) -> Dict[int, float]:
        """Calcola SFR per settimana 3 con perdita performance."""
        sfr_per_esercizio = {}

        if 3 not in self.performance_data:
            return sfr_per_esercizio

        # Calcola 1RM medi settimana 2 per confronto
        one_rm_sett2 = {}
        if 2 in self.performance_data:
            for perf in self.performance_data[2]:
                if perf.esercizio_id not in one_rm_sett2:
                    one_rm_sett2[perf.esercizio_id] = []
                one_rm_sett2[perf.esercizio_id].append(perf.one_rm)

            # Media 1RM settimana 2
            one_rm_sett2 = {
                esercizio_id: sum(one_rm_list) / len(one_rm_list)
                for esercizio_id, one_rm_list in one_rm_sett2.items()
            }

        # Calcola SFR settimana 3
        for perf in self.performance_data[3]:
            # Calcola perdita performance
            if perf.esercizio_id in one_rm_sett2:
                rm_sett2 = one_rm_sett2[perf.esercizio_id]
                if rm_sett2 > 0:
                    perdita_pct = ((rm_sett2 - perf.one_rm) / rm_sett2) * 100
                    perf.perdita_performance = max(0, perdita_pct)  # Solo valori positivi

            # FI = max(1, Dolori + Perdita Performance)
            perf.fi = max(1, perf.dolori_articolari + perf.perdita_performance)
            perf.sfr = perf.rsm / perf.fi

            # Salva SFR per esercizio
            if perf.esercizio_id not in sfr_per_esercizio:
                sfr_per_esercizio[perf.esercizio_id] = []
            sfr_per_esercizio[perf.esercizio_id].append(perf.sfr)

        # Calcola media SFR per esercizio
        self.sfr_settimana_3 = {
            esercizio_id: sum(sfr_list) / len(sfr_list)
            for esercizio_id, sfr_list in sfr_per_esercizio.items()
        }

        return self.sfr_settimana_3

    # ===== ANALISI FINALE =====

    def calcola_sfr_medio_finale(self) -> Dict[int, float]:
        """Calcola SFR medio finale (settimana 1 + settimana 3) / 2."""
        if not self.sfr_settimana_1 or not self.sfr_settimana_3:
            return {}

        esercizi_comuni = set(self.sfr_settimana_1.keys()) & set(self.sfr_settimana_3.keys())

        self.sfr_medio_finale = {
            esercizio_id: (self.sfr_settimana_1[esercizio_id] + self.sfr_settimana_3[esercizio_id]) / 2
            for esercizio_id in esercizi_comuni
        }

        return self.sfr_medio_finale

    def get_ranking_esercizi(self) -> List[Tuple[int, float]]:
        """Restituisce ranking esercizi per SFR medio finale (dal migliore al peggiore)."""
        sfr_medio = self.calcola_sfr_medio_finale()
        return sorted(sfr_medio.items(), key=lambda x: x[1], reverse=True)

    def get_esercizio_peggiore(self) -> Optional[int]:
        """Restituisce l'esercizio con SFR medio più basso."""
        ranking = self.get_ranking_esercizi()
        return ranking[-1][0] if ranking else None

    def get_esercizio_migliore(self) -> Optional[int]:
        """Restituisce l'esercizio con SFR medio più alto."""
        ranking = self.get_ranking_esercizi()
        return ranking[0][0] if ranking else None

    # ===== UTILITY =====

    def get_esercizi_per_muscolo(self, muscolo: str, settimana: int) -> List[int]:
        """Restituisce lista esercizi per un muscolo specifico in una settimana."""
        if settimana not in self.performance_data:
            return []

        esercizi = []
        for perf in self.performance_data[settimana]:
            # --- MODIFICA LA LOGICA QUI ---
            if perf.muscolo_primario.lower() == muscolo.lower():
                esercizi.append(perf.esercizio_id)

        return list(set(esercizi))

    def get_rsm_esercizio(self, esercizio_id: int, settimana: int) -> float:
        """Restituisce RSM medio per un esercizio in una settimana."""
        if settimana not in self.performance_data:
            return 0.0

        rsm_values = []
        for perf in self.performance_data[settimana]:
            if perf.esercizio_id == esercizio_id:
                rsm_values.append(perf.rsm)

        return sum(rsm_values) / len(rsm_values) if rsm_values else 0.0

    # ===== REPORT =====

    def genera_report_completo(self) -> str:
        """Genera report completo dell'analisi."""
        report = "=" * 60 + "\n"
        report += "           REPORT ANALISI TRAINING ALGORITHM\n"
        report += "=" * 60 + "\n\n"

        # Settimana 1
        report += "📊 SETTIMANA 1 - SFR INIZIALE\n"
        report += "-" * 40 + "\n"
        for esercizio_id, sfr in self.sfr_settimana_1.items():
            report += f"Esercizio {esercizio_id}: SFR = {sfr:.2f}\n"
        report += "\n"

        # Settimana 2
        report += "📈 SETTIMANA 2 - MIGLIORAMENTO PERFORMANCE\n"
        report += "-" * 40 + "\n"
        miglioramenti = self.calcola_miglioramento_performance_settimana_2()
        punti = self.calcola_punti_performance_settimana_2()
        for esercizio_id, miglioramento in miglioramenti.items():
            punto = punti.get(esercizio_id, 0)
            report += f"Esercizio {esercizio_id}: {miglioramento:+.1f}% → {punto:+d} punti\n"
        report += "\n"

        # Settimana 3
        report += "📊 SETTIMANA 3 - SFR FINALE\n"
        report += "-" * 40 + "\n"
        for esercizio_id, sfr in self.sfr_settimana_3.items():
            report += f"Esercizio {esercizio_id}: SFR = {sfr:.2f}\n"
        report += "\n"

        # Ranking finale
        report += "🏆 RANKING FINALE ESERCIZI\n"
        report += "-" * 40 + "\n"
        ranking = self.get_ranking_esercizi()
        for i, (esercizio_id, sfr_medio) in enumerate(ranking, 1):
            report += f"{i}. Esercizio {esercizio_id}: SFR medio = {sfr_medio:.2f}\n"
        report += "\n"

        # Raccomandazioni
        report += "💡 RACCOMANDAZIONI MESOCICLO SUCCESSIVO\n"
        report += "-" * 40 + "\n"
        migliore = self.get_esercizio_migliore()
        peggiore = self.get_esercizio_peggiore()

        if migliore:
            report += f"✅ Priorità serie: Esercizio {migliore} (SFR: {self.sfr_medio_finale[migliore]:.2f})\n"
        if peggiore:
            report += f"❌ Candidato sostituzione: Esercizio {peggiore} (SFR: {self.sfr_medio_finale[peggiore]:.2f})\n"

        report += "\n" + "=" * 60 + "\n"
        return report


# ===== ESEMPIO DI UTILIZZO =====

def esempio_utilizzo():
    """Esempio di utilizzo dell'algoritmo."""

    # Inizializza algoritmo
    algo = TrainingAlgorithm()

    # Simula dati settimana 1
    print("📊 SETTIMANA 1 - Raccolta dati SFR...")

    # Esempio: 2 esercizi, 3 giorni
    # Panca Piana (ID: 1)
    algo.aggiungi_performance(1, PerformanceData(
        esercizio_id=1, giorno=1, settimana=1,
        mmc=2, pump=2, dolori_articolari=1,
        carico=100, ripetizioni=8
    ))

    # Panca Manubri (ID: 2)
    algo.aggiungi_performance(1, PerformanceData(
        esercizio_id=2, giorno=1, settimana=1,
        mmc=3, pump=2, dolori_articolari=1,
        carico=40, ripetizioni=10
    ))

    # Calcola SFR settimana 1
    sfr_1 = algo.calcola_sfr_settimana_1()
    print(f"SFR Settimana 1: {sfr_1}")

    # Simula DOMS per settimana 2
    algo.aggiungi_doms(2, DOMSData(muscolo="Petto", giorno=1, settimana=2, doms_value=2))

    # Previsione serie settimana 2
    previsione = algo.calcola_previsione_serie_settimana_2("Petto")
    print(f"Previsione serie settimana 2: {previsione}")

    # Simula dati settimana 2
    print("\n📈 SETTIMANA 2 - Raccolta dati performance...")

    algo.aggiungi_performance(2, PerformanceData(
        esercizio_id=1, giorno=1, settimana=2,
        mmc=2, pump=2, dolori_articolari=1,
        carico=102, ripetizioni=8
    ))

    algo.aggiungi_performance(2, PerformanceData(
        esercizio_id=2, giorno=1, settimana=2,
        mmc=3, pump=2, dolori_articolari=1,
        carico=42, ripetizioni=10
    ))

    # Calcola serie settimana 3
    serie_3 = algo.calcola_serie_settimana_3("Petto")
    print(f"Serie settimana 3: {serie_3}")

    # Simula dati settimana 3
    print("\n📊 SETTIMANA 3 - Raccolta dati finali...")

    algo.aggiungi_performance(3, PerformanceData(
        esercizio_id=1, giorno=1, settimana=3,
        mmc=2, pump=1, dolori_articolari=2,
        carico=100, ripetizioni=7
    ))

    algo.aggiungi_performance(3, PerformanceData(
        esercizio_id=2, giorno=1, settimana=3,
        mmc=3, pump=2, dolori_articolari=1,
        carico=44, ripetizioni=10
    ))

    # Calcola SFR settimana 3
    sfr_3 = algo.calcola_sfr_settimana_3()
    print(f"SFR Settimana 3: {sfr_3}")

    # Analisi finale
    print("\n🏆 ANALISI FINALE")
    print(algo.genera_report_completo())


if __name__ == "__main__":
    esempio_utilizzo()

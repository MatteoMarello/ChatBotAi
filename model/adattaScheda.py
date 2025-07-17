from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import math

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
    mmc: int  # Mind Muscle Connection (1-3)
    pump: int  # Pump (1-3)
    dolori_articolari: int  # Dolori articolari (1-3)
    carico: float  # kg
    ripetizioni: int
    rsm: float = 0.0  # RSM = MMC + Pump
    fi: float = 0.0  # Fattore Impedimento
    sfr: float = 0.0  # SFR = RSM / FI
    one_rm: float = 0.0  # 1RM calcolato
    perdita_performance: float = 0.0  # % perdita performance (solo settimana 3)

    def __post_init__(self):
        self.rsm = self.mmc + self.pump
        self.one_rm = self.calcola_1rm()

    def calcola_1rm(self) -> float:
        """Calcola 1RM usando formula di Epley."""
        if self.ripetizioni <= 0:
            return 0.0
        return self.carico * (1 + self.ripetizioni / 30)


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

    # Dati di performance raccolti
    performance_data: Dict[int, List[PerformanceData]] = field(default_factory=dict)  # settimana -> lista performance
    doms_data: Dict[int, List[DOMSData]] = field(default_factory=dict)  # settimana -> lista DOMS

    # Risultati analisi
    sfr_settimana_1: Dict[int, float] = field(default_factory=dict)  # esercizio_id -> SFR medio
    sfr_settimana_3: Dict[int, float] = field(default_factory=dict)  # esercizio_id -> SFR medio
    sfr_medio_finale: Dict[int, float] = field(default_factory=dict)  # esercizio_id -> SFR medio (sett1+sett3)/2

    # Configurazione
    rir_progressivo: Dict[int, int] = field(default_factory=lambda: {1: 4, 2: 3, 3: 2})  # settimana -> RIR

    def aggiungi_performance(self, settimana: int, performance: PerformanceData):
        """Aggiunge dati di performance."""
        if settimana not in self.performance_data:
            self.performance_data[settimana] = []
        self.performance_data[settimana].append(performance)

    def aggiungi_doms(self, settimana: int, doms: DOMSData):
        """Aggiunge dati DOMS."""
        if settimana not in self.doms_data:
            self.doms_data[settimana] = []
        self.doms_data[settimana].append(doms)

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

    def calcola_previsione_serie_settimana_2(self, muscolo: str) -> str:
        """Calcola previsione serie per settimana 2 basata su DOMS."""
        if 2 not in self.doms_data:
            return "mantieni"

        # Trova DOMS per il muscolo specifico
        doms_muscolo = None
        for doms in self.doms_data[2]:
            if doms.muscolo.lower() == muscolo.lower():
                doms_muscolo = doms.doms_value
                break

        if doms_muscolo is None:
            return "mantieni"

        # Trova esercizi per questo muscolo
        esercizi_muscolo = self.get_esercizi_per_muscolo(muscolo, 1)
        if not esercizi_muscolo:
            return "mantieni"

        # Calcola X = media(RSM + DOMS) per tutti gli esercizi del muscolo
        x_values = []
        for esercizio_id in esercizi_muscolo:
            if esercizio_id in self.sfr_settimana_1:
                # Trova RSM dell'esercizio (SFR * FI = RSM, ma più semplice ricalcolare)
                rsm = self.get_rsm_esercizio(esercizio_id, 1)
                x_values.append(rsm + doms_muscolo)

        if not x_values:
            return "mantieni"

        x_medio = sum(x_values) / len(x_values)

        # Applica regola
        if x_medio <= 3:
            return "+2/4 serie"
        elif 4 <= x_medio <= 6:
            return "mantieni"
        else:  # x_medio >= 7
            return "-2 serie"

    # ===== SETTIMANA 2 =====

    def calcola_miglioramento_performance_settimana_2(self) -> Dict[int, float]:
        """
        Calcola miglioramento % performance settimana 2 vs settimana 1.
        Confronta giorno per giorno lo stesso esercizio e fa la media settimanale.
        """
        miglioramenti = {}

        if 1 not in self.performance_data or 2 not in self.performance_data:
            return miglioramenti

        # Organizza i dati per esercizio e giorno
        # Struttura: {esercizio_id: {giorno: {settimana: performance}}}
        dati_organizzati = {}

        # Raccoglie dati settimana 1
        for perf in self.performance_data[1]:
            if perf.esercizio_id not in dati_organizzati:
                dati_organizzati[perf.esercizio_id] = {}
            if perf.giorno not in dati_organizzati[perf.esercizio_id]:
                dati_organizzati[perf.esercizio_id][perf.giorno] = {}
            dati_organizzati[perf.esercizio_id][perf.giorno][1] = perf

        # Raccoglie dati settimana 2
        for perf in self.performance_data[2]:
            if perf.esercizio_id not in dati_organizzati:
                dati_organizzati[perf.esercizio_id] = {}
            if perf.giorno not in dati_organizzati[perf.esercizio_id]:
                dati_organizzati[perf.esercizio_id][perf.giorno] = {}
            dati_organizzati[perf.esercizio_id][perf.giorno][2] = perf

        # Calcola miglioramento per ogni esercizio
        for esercizio_id, giorni_data in dati_organizzati.items():
            miglioramenti_giornalieri = []

            # Per ogni giorno in cui l'esercizio è stato fatto
            for giorno, settimane_data in giorni_data.items():
                # Controlla se l'esercizio è stato fatto lo stesso giorno in entrambe le settimane
                if 1 in settimane_data and 2 in settimane_data:
                    perf_sett1 = settimane_data[1]
                    perf_sett2 = settimane_data[2]

                    # Calcola miglioramento % per questo giorno specifico
                    if perf_sett1.one_rm > 0:
                        miglioramento_giornaliero = ((perf_sett2.one_rm - perf_sett1.one_rm) / perf_sett1.one_rm) * 100
                        miglioramenti_giornalieri.append(miglioramento_giornaliero)

                        # Debug info (opzionale)
                        print(f"Esercizio {esercizio_id}, Giorno {giorno}: "
                              f"Sett1={perf_sett1.one_rm:.1f}kg → Sett2={perf_sett2.one_rm:.1f}kg "
                              f"({miglioramento_giornaliero:+.1f}%)")

            # Calcola la media settimanale per l'esercizio
            if miglioramenti_giornalieri:
                miglioramento_medio = sum(miglioramenti_giornalieri) / len(miglioramenti_giornalieri)
                miglioramenti[esercizio_id] = miglioramento_medio

                # Debug info (opzionale)
                print(f"Esercizio {esercizio_id}: Media settimanale = {miglioramento_medio:+.1f}%")

        return miglioramenti

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
            # Qui dovresti avere accesso ai dati dell'esercizio per verificare il muscolo
            # Per ora assumiamo che sia già filtrato correttamente
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

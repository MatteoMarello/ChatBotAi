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
    """
    Raccoglie e struttura tutti i dati di performance relativi a un singolo esercizio
    eseguito in un determinato giorno di allenamento.
    Calcola automaticamente l'1RM (One-Rep Max) e l'RSM (Rapporto Stimolo-Fatica)
    al momento della creazione dell'oggetto.

    Attributes:
        esercizio_id (int): L'identificatore univoco dell'esercizio.
        giorno (int): Il numero del giorno di allenamento nella settimana.
        settimana (int): Il numero della settimana di allenamento nel mesociclo.
        muscolo_primario (str): Il muscolo principale allenato dall'esercizio.
        mmc (int): Mind Muscle Connection, un valore da 1 a 3 che indica la qualità della connessione mente-muscolo.
        pump (int): Il livello di pump muscolare percepito, da 1 a 3.
        dolori_articolari (int): Il livello di dolore articolare percepito, da 1 a 3.
        sets (List[Tuple[float, int, str]]): Una lista di tuple, where ogni tupla rappresenta una serie e contiene (carico, ripetizioni, rep_range_target).
        rsm (float): Rapporto Stimolo-Fatica, calcolato come (MMC + Pump). Valore più alto indica uno stimolo migliore.
        fi (float): Fattore di Interferenza, indica quanto l'esercizio è stato "fastidioso" o ha generato fatica non produttiva.
        sfr (float): Stimulus-to-Fatigue Ratio, il rapporto tra lo stimolo (RSM) e la fatica (FI). È l'indicatore chiave per valutare l'efficacia di un esercizio.
        one_rm (float): Il massimale teorico per una ripetizione (1RM), calcolato sulla base della migliore serie eseguita.
        perdita_performance (float): La percentuale di calo della performance rispetto alla settimana precedente, usata in settimana 3.
    """
    esercizio_id: int
    giorno: int
    settimana: int
    muscolo_primario: str  # Il muscolo principale allenato
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
        """
        Metodo speciale che viene eseguito subito dopo la creazione dell'oggetto.
        Calcola l'RSM e l'1RM basandosi sui dati forniti.
        """
        self.rsm = self.mmc + self.pump
        self.one_rm = self.calcola_1rm_migliore()

    def _calcola_1rm_epley(self, carico: float, ripetizioni: int) -> float:
        """
        Calcola il massimale teorico (1RM) per una singola serie usando la formula di Epley.
        La formula di Epley è uno standard comune per stimare il massimale.

        Args:
            carico (float): Il peso sollevato nella serie.
            ripetizioni (int): Il numero di ripetizioni completate.

        Returns:
            float: Il valore dell'1RM stimato. Restituisce 0 se i dati non sono validi.
        """
        if ripetizioni <= 0 or carico <= 0:
            return 0.0
        return carico * (1 + ripetizioni / 30)

    def calcola_1rm_migliore(self) -> float:
        """
        Scorre tutte le serie registrate per questo esercizio e trova quella con l'1RM stimato più alto.
        Questo valore viene considerato l'1RM di riferimento per questa sessione.

        Returns:
            float: Il valore massimo di 1RM calcolato tra tutte le serie.
        """
        if not self.sets:
            return 0.0
        max_one_rm = 0.0
        for carico, ripetizioni, _ in self.sets:  # Ignora il rep_range_target
            one_rm_serie = self._calcola_1rm_epley(carico, ripetizioni)
            if one_rm_serie > max_one_rm:
                max_one_rm = one_rm_serie
        return max_one_rm


@dataclass
class DOMSData:
    """
    Rappresenta i dati sui DOMS (Delayed Onset Muscle Soreness - dolori muscolari a insorgenza ritardata)
    per un specifico gruppo muscolare.

    Attributes:
        muscolo (str): Il nome del gruppo muscolare.
        giorno (int): Il giorno in cui sono stati registrati i DOMS.
        settimana (int): La settimana in cui sono stati registrati i DOMS.
        doms_value (int): L'intensità dei DOMS su una scala da 1 a 3.
    """
    muscolo: str
    giorno: int
    settimana: int
    doms_value: int  # 1-3


@dataclass
class TrainingAlgorithm:
    """
    Classe centrale che gestisce la logica di adattamento dell'allenamento su un mesociclo di 3 settimane.
    Raccoglie dati di performance e DOMS, li analizza e fornisce raccomandazioni per
    le settimane successive.

    Attributes:
        performance_data (Dict[int, List[PerformanceData]]): Un dizionario che mappa il numero della settimana a una lista di dati di performance.
        doms_data (Dict[int, List[DOMSData]]): Un dizionario che mappa il numero della settimana a una lista di dati DOMS.
        sfr_settimana_1 (Dict[int, float]): Dizionario che memorizza l'SFR medio per ogni esercizio nella settimana 1.
        sfr_settimana_3 (Dict[int, float]): Dizionario che memorizza l'SFR medio per ogni esercizio nella settimana 3.
        sfr_medio_finale (Dict[int, float]): Dizionario che memorizza l'SFR medio finale (media di sett. 1 e 3) per ogni esercizio.
        rir_progressivo (Dict[int, int]): Mappa il RIR (Reps in Reserve) target per ogni settimana del ciclo.
    """
    performance_data: Dict[int, List[PerformanceData]] = field(default_factory=dict) # Con default_factory, ogni istanza ottiene il suo dizionario separato.
    doms_data: Dict[int, List[DOMSData]] = field(default_factory=dict)
    sfr_settimana_1: Dict[int, float] = field(default_factory=dict)
    sfr_settimana_3: Dict[int, float] = field(default_factory=dict)
    sfr_medio_finale: Dict[int, float] = field(default_factory=dict)
    rir_progressivo: Dict[int, int] = field(default_factory=lambda: {1: 4, 2: 3, 3: 2})
    exercise_details_map: Dict[int, Esercizio] = field(default_factory=dict)

    def aggiungi_performance(self, settimana: int, performance: PerformanceData):
        """
        Aggiunge i dati di performance di un esercizio al database dell'algoritmo.

        Args:
            settimana (int): Il numero della settimana a cui appartengono i dati.
            performance (PerformanceData): L'oggetto PerformanceData da aggiungere.
        """
        if settimana not in self.performance_data:
            self.performance_data[settimana] = []
        self.performance_data[settimana].append(performance)

    def aggiungi_doms(self, settimana: int, doms: DOMSData):
        """
        Aggiunge i dati sui DOMS di un gruppo muscolare al database dell'algoritmo.

        Args:
            settimana (int): Il numero della settimana a cui appartengono i dati.
            doms (DOMSData): L'oggetto DOMSData da aggiungere.
        """
        if settimana not in self.doms_data:
            self.doms_data[settimana] = []
        self.doms_data[settimana].append(doms)

    def _calcola_1rm_epley(self, carico: float, ripetizioni: int) -> float:
        """
        Funzione helper interna per calcolare l'1RM di una singola serie.
        Duplica la logica presente in PerformanceData per un uso interno all'algoritmo.

        Args:
            carico (float): Il peso sollevato.
            ripetizioni (int): Le ripetizioni completate.

        Returns:
            float: L'1RM stimato.
        """
        if ripetizioni <= 0 or carico <= 0: return 0.0
        return carico * (1 + ripetizioni / 30)

    # ===== SETTIMANA 1 =====

    def calcola_sfr_settimana_1(self) -> Dict[int, float]:
        """
        Calcola lo Stimulus-to-Fatigue Ratio (SFR) per ogni esercizio eseguito nella settimana 1.
        In questa settimana, la perdita di performance è considerata 0.
        L'SFR è calcolato come RSM / FI, dove FI = max(1, DoloriArticolari).

        Returns:
            Dict[int, float]: Un dizionario che mappa l'ID di ogni esercizio al suo SFR medio calcolato.
        """
        sfr_per_esercizio = {}

        if 1 not in self.performance_data:
            return sfr_per_esercizio

        for perf in self.performance_data[1]:
            # FI = max(1, Dolori + Perdita Performance). In settimana 1, Perdita Performance = 0.
            perf.fi = max(1, perf.dolori_articolari + 0)
            perf.sfr = perf.rsm / perf.fi

            if perf.esercizio_id not in sfr_per_esercizio:
                sfr_per_esercizio[perf.esercizio_id] = []
            sfr_per_esercizio[perf.esercizio_id].append(perf.sfr)

        # Calcola la media dell'SFR per ogni esercizio e la memorizza nell'attributo di classe.
        self.sfr_settimana_1 = {
            esercizio_id: sum(sfr_list) / len(sfr_list)
            for esercizio_id, sfr_list in sfr_per_esercizio.items()
        }

        return self.sfr_settimana_1

    def calcola_previsione_serie_settimana_2(self, muscolo: str, esperienza: str) -> tuple[str, str | None]:
        """
        Analizza i dati di DOMS e RSM della settimana 1 per raccomandare un aggiustamento del volume (numero di serie)
        per la settimana 2 per un dato gruppo muscolare.
        La logica è differenziata per atleti principianti e intermedi/avanzati.

        Args:
            muscolo (str): Il gruppo muscolare da analizzare.
            esperienza (str): Il livello di esperienza dell'atleta ("principiante" o "intermedio").

        Returns:
            tuple[str, str | None]: Una tupla contenente la raccomandazione (es. "+2 serie", "mantieni") e un motivo opzionale.
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

        # Calcola un valore 'X' combinando RSM e DOMS.
        x_values = []
        for esercizio_id in esercizi_muscolo:
            if esercizio_id in self.sfr_settimana_1:
                rsm = self.get_rsm_esercizio(esercizio_id, 1)
                x_values.append(rsm + doms_muscolo)

        if not x_values:
            return "mantieni", f"Dati RSM non calcolabili per {muscolo} in settimana 1."

        x_medio = sum(x_values) / len(x_values)

        # Logica differenziata per esperienza
        if x_medio <= 4:  # Se lo stimolo è basso e il recupero buono, aumenta il volume.
            return ("+2 serie", None) if esperienza == "principiante" else ("+3 serie", None)
        elif 5 <= x_medio <= 7:  # Se l'equilibrio è corretto, mantieni il volume.
            return "mantieni", None
        else:  # Se lo stimolo è eccessivo o il recupero scarso, diminuisci il volume.
            return ("-2 serie", None) if esperienza == "principiante" else ("-3 serie", None)

    def calcola_miglioramento_performance_settimana_2(self) -> Dict[int, float]:
        """
        Confronta la performance (in termini di 1RM medio) tra la settimana 1 e la settimana 2 per ogni esercizio.
        Il confronto viene fatto solo tra serie eseguite nello stesso range di ripetizioni target.

        Returns:
            Dict[int, float]: Un dizionario che mappa l'ID di ogni esercizio al suo miglioramento percentuale medio.
        """
        if 1 not in self.performance_data or 2 not in self.performance_data:
            return {}

        # Raggruppa gli 1RM per (esercizio_id, rep_range) e per settimana.
        dati_per_gruppo = defaultdict(lambda: defaultdict(list))
        for settimana, performances in self.performance_data.items():
            if settimana in [1, 2]:
                for perf in performances:
                    for carico, reps, rep_range in perf.sets:
                        one_rm = self._calcola_1rm_epley(carico, reps)
                        if one_rm > 0:
                            chiave = (perf.esercizio_id, rep_range)
                            dati_per_gruppo[chiave][settimana].append(one_rm)

        miglioramenti_per_esercizio = defaultdict(list)
        for (esercizio_id, rep_range), dati_settimanali in dati_per_gruppo.items():
            if 1 in dati_settimanali and 2 in dati_settimanali:
                avg_1rm_sett1 = sum(dati_settimanali[1]) / len(dati_settimanali[1])
                avg_1rm_sett2 = sum(dati_settimanali[2]) / len(dati_settimanali[2])

                if avg_1rm_sett1 > 0:
                    miglioramento_pct = ((avg_1rm_sett2 - avg_1rm_sett1) / avg_1rm_sett1) * 100
                    miglioramenti_per_esercizio[esercizio_id].append(miglioramento_pct)

        # Calcola la media dei miglioramenti per ogni esercizio.
        risultato_finale = {}
        for esercizio_id, lista_miglioramenti in miglioramenti_per_esercizio.items():
            if lista_miglioramenti:
                risultato_finale[esercizio_id] = sum(lista_miglioramenti) / len(lista_miglioramenti)

        return risultato_finale

    def calcola_punti_performance_settimana_2(self) -> Dict[int, int]:
        """
        Converte il miglioramento percentuale di performance della settimana 2 in un sistema a punti.
        I punti vanno da -2 (grande peggioramento) a +2 (grande miglioramento).

        Returns:
            Dict[int, int]: Un dizionario che mappa l'ID di ogni esercizio al suo punteggio.
        """
        miglioramenti = self.calcola_miglioramento_performance_settimana_2()
        punti = {}

        for esercizio_id, miglioramento_pct in miglioramenti.items():
            if miglioramento_pct >= 4:
                punti[esercizio_id] = 2
            elif 1.5 <= miglioramento_pct < 4:
                punti[esercizio_id] = 1
            elif 0 <= miglioramento_pct < 1.5:
                punti[esercizio_id] = 0
            elif -2.5 <= miglioramento_pct < 0:
                punti[esercizio_id] = -1
            else:  # peggioramento > 2.5%
                punti[esercizio_id] = -2

        return punti

    def calcola_serie_settimana_3(self, muscolo: str) -> str:
        """
        Raccomanda un aggiustamento del volume per la settimana 3 basandosi sulla media dei punti performance
        ottenuti da tutti gli esercizi per un dato gruppo muscolare nella settimana 2.

        Args:
            muscolo (str): Il gruppo muscolare da analizzare.

        Returns:
            str: Una stringa che indica la raccomandazione sul volume (es. "+3 serie", "mantieni").
        """
        punti = self.calcola_punti_performance_settimana_2()
        esercizi_muscolo = self.get_esercizi_per_muscolo(muscolo, 2)

        if not esercizi_muscolo:
            return "mantieni"

        punti_muscolo = [punti.get(esercizio_id, 0) for esercizio_id in esercizi_muscolo]

        if not punti_muscolo:
            return "mantieni"

        media_punti = sum(punti_muscolo) / len(punti_muscolo)

        # Se la media dei punti è alta, si aumenta il volume. Se è bassa, si diminuisce.
        if media_punti >= 1.2:
            return "+3 serie"
        elif 0.5 <= media_punti < 1.2:
            return "+2 serie"
        elif -0.5 <= media_punti < 0.5:
            return "mantieni"
        elif -1.2 <= media_punti < -0.5:
            return "-1 serie"
        else:
            return "-2 serie"

    def calcola_sfr_settimana_3(self) -> Dict[int, float]:
        """
        Calcola l'SFR per ogni esercizio nella settimana 3.
        A differenza della settimana 1, qui si tiene conto della "perdita di performance" rispetto alla settimana 2.
        Questo serve a modellare l'accumulo di fatica.
        FI = max(1, DoloriArticolari + PerditaPerformance)

        Returns:
            Dict[int, float]: Un dizionario che mappa l'ID di ogni esercizio al suo SFR medio calcolato.
        """
        sfr_per_esercizio = {}

        if 3 not in self.performance_data:
            return sfr_per_esercizio

        # Calcola 1RM medi della settimana 2 per il confronto
        one_rm_sett2 = defaultdict(list)
        if 2 in self.performance_data:
            for perf in self.performance_data[2]:
                one_rm_sett2[perf.esercizio_id].append(perf.one_rm)

        avg_one_rm_sett2 = {
            ex_id: sum(rm_list) / len(rm_list) for ex_id, rm_list in one_rm_sett2.items()
        }

        # Calcola SFR per la settimana 3
        for perf in self.performance_data[3]:
            # Calcola la perdita di performance in percentuale
            if perf.esercizio_id in avg_one_rm_sett2:
                rm_sett2 = avg_one_rm_sett2[perf.esercizio_id]
                if rm_sett2 > 0:
                    perdita_pct = ((rm_sett2 - perf.one_rm) / rm_sett2) * 100
                    perf.perdita_performance = max(0, perdita_pct)  # Considera solo cali

            perf.fi = max(1, perf.dolori_articolari + perf.perdita_performance)
            perf.sfr = perf.rsm / perf.fi

            if perf.esercizio_id not in sfr_per_esercizio:
                sfr_per_esercizio[perf.esercizio_id] = []
            sfr_per_esercizio[perf.esercizio_id].append(perf.sfr)

        self.sfr_settimana_3 = {
            ex_id: sum(sfr_list) / len(sfr_list) for ex_id, sfr_list in sfr_per_esercizio.items()
        }

        return self.sfr_settimana_3

    # ===== ANALISI FINALE =====

    def calcola_sfr_medio_finale(self) -> Dict[int, float]:
        """
        Calcola l'SFR medio finale per ogni esercizio, facendo la media tra l'SFR della settimana 1 e quello della settimana 3.
        Questo valore finale è l'indicatore chiave per valutare l'efficacia generale di un esercizio nel mesociclo.

        Returns:
            Dict[int, float]: Un dizionario che mappa l'ID di ogni esercizio al suo SFR medio finale.
        """
        if not self.sfr_settimana_1 or not self.sfr_settimana_3:
            return {}

        esercizi_comuni = set(self.sfr_settimana_1.keys()) & set(self.sfr_settimana_3.keys())

        self.sfr_medio_finale = {
            esercizio_id: (self.sfr_settimana_1[esercizio_id] + self.sfr_settimana_3[esercizio_id]) / 2
            for esercizio_id in esercizi_comuni
        }

        return self.sfr_medio_finale

    def analizza_sfr_per_gruppo_muscolare(self) -> Dict[str, Dict[str, Optional[Tuple[int, float]]]]:
        """
        Analizza l'SFR medio finale e raggruppa gli esercizi per gruppo muscolare.
        Per ogni gruppo, identifica l'esercizio con SFR più alto ('migliore') e,
        se disponibile, quello con SFR più basso ('peggiore').
        Questo metodo è la base per il nuovo report di fine mesociclo.

        Returns:
            Dict[str, Dict[str, Optional[Tuple[int, float]]]]: Un dizionario che mappa
            un gruppo muscolare a un altro dizionario con le chiavi 'migliore' e 'peggiore'.
            'peggiore' può essere None se è stato eseguito un solo esercizio.
            Esempio:
            {
                'Petto': {
                    'migliore': (1, 5.0),  # (esercizio_id, sfr_medio)
                    'peggiore': (2, 3.5)
                },
                'Schiena': {
                    'migliore': (4, 4.8),
                    'peggiore': None
                }
            }
        """
        # Calcola l'SFR medio finale se non è già stato fatto
        sfr_finali = self.calcola_sfr_medio_finale()
        if not sfr_finali or not self.exercise_details_map:
            print("Dati SFR o mappa esercizi mancanti per l'analisi.")
            return {}

        # Raggruppa gli esercizi e i loro SFR per muscolo primario
        sfr_per_muscolo = defaultdict(list)
        for esercizio_id, sfr in sfr_finali.items():
            esercizio = self.exercise_details_map.get(esercizio_id)
            if esercizio:
                muscolo = esercizio.muscolo_primario
                sfr_per_muscolo[muscolo].append((esercizio_id, sfr))

        # Analizza ogni gruppo muscolare
        risultati_analisi = {}
        for muscolo, esercizi in sfr_per_muscolo.items():
            if not esercizi:
                continue

            # Ordina gli esercizi in base all'SFR, dal più alto al più basso
            esercizi.sort(key=lambda x: x[1], reverse=True)

            migliore = esercizi[0]
            peggiore = esercizi[-1] if len(esercizi) >= 2 else None

            risultati_analisi[muscolo] = {
                'migliore': migliore,
                'peggiore': peggiore
            }
        return risultati_analisi

    # ===== UTILITY =====

    def get_esercizi_per_muscolo(self, muscolo: str, settimana: int) -> List[int]:
        """
        Funzione di utilità per ottenere una lista di tutti gli ID degli esercizi
        eseguiti per un dato gruppo muscolare in una specifica settimana.

        Args:
            muscolo (str): Il nome del gruppo muscolare.
            settimana (int): Il numero della settimana.

        Returns:
            List[int]: Una lista di ID di esercizi unici.
        """
        if settimana not in self.performance_data:
            return []

        esercizi = {perf.esercizio_id for perf in self.performance_data[settimana] if perf.muscolo_primario.lower() == muscolo.lower()}
        return list(esercizi)

    def get_rsm_esercizio(self, esercizio_id: int, settimana: int) -> float:
        """
        Funzione di utilità per calcolare l'RSM medio per un singolo esercizio
        in una specifica settimana.

        Args:
            esercizio_id (int): L'ID dell'esercizio.
            settimana (int): Il numero della settimana.

        Returns:
            float: L'RSM medio calcolato.
        """
        if settimana not in self.performance_data:
            return 0.0

        rsm_values = [perf.rsm for perf in self.performance_data[settimana] if perf.esercizio_id == esercizio_id]

        return sum(rsm_values) / len(rsm_values) if rsm_values else 0.0

    # ===== REPORT =====
    def genera_report_completo(self) -> str:
        """
        Crea un report testuale completo che riassume l'analisi dell'intero mesociclo.
        Il report ora si concentra sul confronto degli esercizi all'interno di ogni
        gruppo muscolare, evidenziando il migliore e il peggiore in base all'SFR.
        """
        report = "=" * 60 + "\n"
        report += "      ANALISI DI FINE MESOCICLO PER GRUPPO MUSCOLARE\n"
        report += "=" * 60 + "\n\n"

        analisi_per_muscolo = self.analizza_sfr_per_gruppo_muscolare()

        if not analisi_per_muscolo:
            return "Nessun dato sufficiente per generare un'analisi comparativa degli esercizi. \n\nAssicurati di aver completato almeno due esercizi diversi per gruppo muscolare nelle settimane 1 e 3 per un'analisi completa."

        report += "💡 RACCOMANDAZIONI PER IL PROSSIMO MESOCICLO\n"
        report += "-" * 50 + "\n"
        report += "L'analisi si basa sullo Stimulus-to-Fatigue Ratio (SFR): un valore più alto indica un esercizio più efficace per te.\n\n"

        for muscolo, dati in analisi_per_muscolo.items():
            report += f"--- {muscolo.upper()} ---\n"

            # Esercizio migliore (ci sarà sempre se il muscolo è nell'analisi)
            id_migliore, sfr_migliore = dati['migliore']
            esercizio_migliore_obj = self.exercise_details_map.get(id_migliore)
            nome_migliore = esercizio_migliore_obj.nome if esercizio_migliore_obj else f"Esercizio ID {id_migliore}"
            report += f"✅ Esercizio Più Efficace: {nome_migliore}\n"
            report += f"   (SFR Medio: {sfr_migliore:.2f})\n"

            # Esercizio peggiore (potrebbe non esserci)
            if dati['peggiore']:
                id_peggiore, sfr_peggiore = dati['peggiore']
                esercizio_peggiore_obj = self.exercise_details_map.get(id_peggiore)
                nome_peggiore = esercizio_peggiore_obj.nome if esercizio_peggiore_obj else f"Esercizio ID {id_peggiore}"

                report += f"❌ Esercizio Meno Efficace: {nome_peggiore}\n"
                report += f"   (SFR Medio: {sfr_peggiore:.2f})\n\n"
                report += f"-> Raccomandazione: Nel prossimo blocco, mantieni '{nome_migliore}' e considera di sostituire '{nome_peggiore}' con una variante per ottimizzare lo stimolo.\n"
            else:
                report += "\n-> Nota: È stato eseguito un solo tipo di esercizio per questo muscolo. Per un'analisi comparativa, includi almeno due varianti nel prossimo ciclo.\n"

            report += "-" * 50 + "\n\n"

        report += "=" * 60 + "\n"
        return report


# ===== ESEMPIO DI UTILIZZO =====

def esempio_utilizzo():
    """
    Funzione di esempio aggiornata che simula un ciclo per due gruppi muscolari (Petto e Schiena)
    e dimostra la nuova analisi per gruppo muscolare.
    """
    # Per questo esempio, definiamo una classe Esercizio fittizia.
    # Nel tuo progetto reale, la importeresti da model.esercizio
    from dataclasses import dataclass
    @dataclass
    class Esercizio:
        id: int
        nome: str
        muscolo_primario: str

    # 1. Creare una mappa degli esercizi (nel tuo codice la recupereresti dal DB)
    exercise_map = {
        1: Esercizio(id=1, nome="Panca Piana Bilanciere", muscolo_primario="Petto"),
        2: Esercizio(id=2, nome="Panca Inclinata Manubri", muscolo_primario="Petto"),
        3: Esercizio(id=3, nome="Trazioni alla Sbarra", muscolo_primario="Schiena"),
        4: Esercizio(id=4, nome="Rematore Bilanciere", muscolo_primario="Schiena")
    }

    # 2. Inizializzare l'algoritmo passando la mappa degli esercizi
    algo = TrainingAlgorithm(exercise_details_map=exercise_map)

    # --- SIMULAZIONE DATI SETTIMANA 1 ---
    # Petto
    algo.aggiungi_performance(1, PerformanceData(1, 1, 1, "Petto", mmc=3, pump=3, dolori_articolari=1,
                                                 sets=[(100, 8, "6-8")]))
    algo.aggiungi_performance(1, PerformanceData(2, 1, 1, "Petto", mmc=2, pump=2, dolori_articolari=2,
                                                 sets=[(40, 10, "8-12")]))
    # Schiena
    algo.aggiungi_performance(1, PerformanceData(3, 2, 1, "Schiena", mmc=2, pump=1, dolori_articolari=1,
                                                 sets=[(0, 8, "6-8")]))
    algo.aggiungi_performance(1, PerformanceData(4, 2, 1, "Schiena", mmc=3, pump=2, dolori_articolari=1,
                                                 sets=[(70, 10, "8-12")]))

    # Calcolo necessario per la settimana 1
    algo.calcola_sfr_settimana_1()

    # --- SIMULAZIONE DATI SETTIMANA 2 (saltiamo i calcoli intermedi per brevità) ---
    # Petto
    algo.aggiungi_performance(2, PerformanceData(1, 1, 2, "Petto", mmc=3, pump=3, dolori_articolari=1,
                                                 sets=[(102.5, 8, "6-8")]))
    algo.aggiungi_performance(2, PerformanceData(2, 1, 2, "Petto", mmc=2, pump=2, dolori_articolari=2,
                                                 sets=[(40, 11, "8-12")]))
    # Schiena
    algo.aggiungi_performance(2, PerformanceData(3, 2, 2, "Schiena", mmc=2, pump=1, dolori_articolari=1,
                                                 sets=[(0, 9, "6-8")]))
    algo.aggiungi_performance(2, PerformanceData(4, 2, 2, "Schiena", mmc=3, pump=2, dolori_articolari=1,
                                                 sets=[(72.5, 10, "8-12")]))

    # --- SIMULAZIONE DATI SETTIMANA 3 ---
    # Petto
    algo.aggiungi_performance(3, PerformanceData(1, 1, 3, "Petto", mmc=3, pump=2, dolori_articolari=1,
                                                 sets=[(102.5, 7, "6-8")]))
    algo.aggiungi_performance(3, PerformanceData(2, 1, 3, "Petto", mmc=2, pump=1, dolori_articolari=3,
                                                 sets=[(40, 10, "8-12")]))
    # Schiena
    algo.aggiungi_performance(3, PerformanceData(3, 2, 3, "Schiena", mmc=1, pump=1, dolori_articolari=2,
                                                 sets=[(0, 8, "6-8")]))
    algo.aggiungi_performance(3, PerformanceData(4, 2, 3, "Schiena", mmc=3, pump=3, dolori_articolari=1,
                                                 sets=[(75, 9, "8-12")]))

    # Calcolo necessario per la settimana 3
    algo.calcola_sfr_settimana_3()

    # --- ANALISI FINALE E REPORT ---
    print("\n🏆 ANALISI FINALE E RACCOMANDAZIONI 🏆")
    print(algo.genera_report_completo())

import copy
from datetime import datetime
import random

from database.DAO import DAO
from model.trainingweek import TrainingWeek
from model.workoutday import WorkoutDay


class Model:
    def __init__(self):
        # Map muscoli target per split (puoi personalizzare)
        self.split_muscoli = {
            "Full Body": ["Petto", "Schiena", "Spalle", "Bicipiti", "Tricipiti",
                          "Quadricipiti", "Femorali", "Glutei", "Polpacci"],
            "Upper": ["Petto", "Schiena", "Spalle", "Bicipiti", "Tricipiti"],
            "Lower": ["Quadricipiti", "Femorali", "Glutei", "Polpacci"],
            "Push": ["Petto", "Spalle", "Tricipiti"],
            "Pull": ["Schiena", "Bicipiti"],
            "Legs": ["Quadricipiti", "Femorali", "Glutei", "Polpacci"],
            "Full Body Metabolico": ["Petto", "Schiena", "Spalle", "Bicipiti", "Tricipiti",
                                     "Quadricipiti", "Femorali", "Glutei", "Polpacci"]
        }

    def selezionaSplit(self, livello, frequenza):
        split = []  # lista dei giorni con focus (es: "full body", "upper", etc.)

        if livello == "principiante":
            if frequenza == 2:
                split = ["Full Body", "Full Body"]
            elif frequenza == 3:
                split = ["Full Body", "Full Body", "Full Body"]
            elif frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]

        elif livello == "intermedio":
            if frequenza == 3:
                split = ["Upper", "Lower", "Full Body"]
            elif frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]

        elif livello == "avanzato":
            if frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]
            elif frequenza == 5:
                split = ["Lower", "Upper", "Lower", "Upper", "Full Body Metabolico"]
            elif frequenza == 6:
                split = ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]

        else:
            raise ValueError("Livello non valido")

        return split

    def get_weekly_sets(self, livello, muscolo, mesociclo):
        # qui ritorni solo settimana1 come int
        base_volumes = {
            "principiante": {
                "Petto": (10, 16), "Schiena": (12, 18), "Spalle": (16, 22),
                "Bicipiti": (8, 14), "Tricipiti": (8, 14), "Quadricipiti": (10, 18),
                "Femorali": (6, 12), "Glutei": (8, 14), "Polpacci": (6, 12)
            },
            "intermedio": {
                "Petto": (11, 20), "Schiena": (13, 20), "Spalle": (18, 24),
                "Bicipiti": (9, 16), "Tricipiti": (9, 16), "Quadricipiti": (11, 20),
                "Femorali": (7, 14), "Glutei": (9, 16), "Polpacci": (8, 14)
            },
            "avanzato": {
                "Petto": (12, 22), "Schiena": (14, 22), "Spalle": (20, 26),
                "Bicipiti": (10, 18), "Tricipiti": (10, 18), "Quadricipiti": (12, 22),
                "Femorali": (8, 16), "Glutei": (10, 18), "Polpacci": (8, 18)
            }
        }
        start, end = base_volumes[livello][muscolo]
        incremento = mesociclo - 1
        volum = min(start + incremento, end)
        return volum

    def _calcola_coinvolgimento_indiretto(self, esercizi_scelti, esercizi_serie, muscoli_target):
        """
        Calcola il volume indiretto per ogni muscolo basato sui muscoli secondari degli esercizi
        """
        volume_indiretto = {}

        for muscolo in muscoli_target:
            volume_indiretto[muscolo] = 0

            # Controlla tutti gli esercizi scelti per altri muscoli
            for esercizio_id, esercizio in esercizi_scelti.items():
                serie = esercizi_serie.get(esercizio_id, 0)
                if esercizio.muscolo_primario != muscolo and serie > 0:
                    # Controlla se questo muscolo è coinvolto indirettamente
                    muscoli_secondari = esercizio.muscoli_secondari
                    if isinstance(muscoli_secondari, str):
                        muscoli_secondari = [muscoli_secondari] if muscoli_secondari else []
                    elif muscoli_secondari is None:
                        muscoli_secondari = []

                    if muscolo in muscoli_secondari:
                        volume_indiretto[muscolo] += serie * 0.5  # Metà del volume

        return volume_indiretto

    def _calcola_distribuzione_rep_range(self, volume_effettivo):
        """
        Calcola la distribuzione delle serie per rep range:
        50% nel range 5-7 rep
        40% nel range 12-14 rep
        10% nel range 20-22 rep
        """
        tot_5_7 = max(1, int(round(volume_effettivo * 0.50)))
        tot_12_14 = max(0, int(round(volume_effettivo * 0.40)))
        tot_20_22 = volume_effettivo - tot_5_7 - tot_12_14

        # Assicurati che non ci siano valori negativi
        if tot_20_22 < 0:
            tot_20_22 = 0
            tot_12_14 = volume_effettivo - tot_5_7

        return tot_5_7, tot_12_14, tot_20_22

    def _redistribusci_serie_singole(self, reps_distribution, giorni):
        """
        Sposta le serie singole da un giorno all'altro per evitare esercizi con 1 sola serie
        """
        print("--- Redistribuzione serie singole ---")

        for esercizio_id in list(reps_distribution[0].keys()):
            # Controlla tutti i giorni per questo esercizio
            for day_idx in range(giorni):
                if esercizio_id in reps_distribution[day_idx]:
                    serie_attuali = reps_distribution[day_idx][esercizio_id]

                    # Se ha solo 1 serie, spostala
                    if len(serie_attuali) == 1:
                        serie_da_spostare = serie_attuali[0]

                        # Rimuovi la serie da questo giorno
                        del reps_distribution[day_idx][esercizio_id]

                        # Trova il giorno con meno esercizi totali per spostarla
                        giorni_carichi = []
                        for i in range(giorni):
                            if i != day_idx:
                                num_esercizi = len(reps_distribution[i])
                                giorni_carichi.append((i, num_esercizi))

                        # Ordina per numero di esercizi (meno carico = meglio)
                        giorni_carichi.sort(key=lambda x: x[1])
                        giorno_destinazione = giorni_carichi[0][0]

                        # Sposta la serie
                        if esercizio_id not in reps_distribution[giorno_destinazione]:
                            reps_distribution[giorno_destinazione][esercizio_id] = []
                        reps_distribution[giorno_destinazione][esercizio_id].append(serie_da_spostare)

                        print(
                            f"  Spostata 1 serie di esercizio {esercizio_id} dal giorno {day_idx + 1} al giorno {giorno_destinazione + 1}")

        return reps_distribution

    def _concentra_serie_su_meno_giorni(self, volume_effettivo, giorni):
        """
        Concentra le serie su 2 giorni invece di 3 per evitare troppa dispersione
        """
        if volume_effettivo <= 4:
            # Volume basso: concentra su 2 giorni
            day1 = volume_effettivo // 2
            day2 = volume_effettivo - day1
            return [day1, day2, 0] if giorni == 3 else [day1, day2]
        elif volume_effettivo <= 8:
            # Volume medio: usa 2 giorni principali + eventuale terzo con minimo 2 serie
            day1 = int(volume_effettivo * 0.5)
            day2 = int(volume_effettivo * 0.3)
            day3 = volume_effettivo - day1 - day2

            if giorni == 3 and day3 < 2:
                # Se il terzo giorno ha meno di 2 serie, redistribuisci
                day2 += day3
                day3 = 0

            return [day1, day2, day3] if giorni == 3 else [day1, day2]
        else:
            # Volume alto: distribuzione normale ma con soglia minima
            if giorni == 3:
                day1 = int(volume_effettivo * 0.4)
                day2 = int(volume_effettivo * 0.35)
                day3 = volume_effettivo - day1 - day2

                # Assicurati che ogni giorno abbia almeno 2 serie
                if day3 < 2:
                    day2 += day3
                    day3 = 0

                return [day1, day2, day3]
            else:
                day1 = volume_effettivo // 2
                day2 = volume_effettivo - day1
                return [day1, day2]

    def _crea_fullbody_giorni(self, context, muscolo_target, giorni):
        gruppi = self.split_muscoli["Full Body"]
        settimana_numero = 1
        oggi = datetime.now()
        days = [WorkoutDay(id_giorno=i + 1, settimana=settimana_numero,
                           split_type="Full Body", data=oggi) for i in range(giorni)]

        ordered = [muscolo_target] + [m for m in gruppi if m != muscolo_target]

        # Struttura per raccogliere tutte le distribuzioni prima di creare i giorni
        all_reps_distribution = [{} for _ in range(giorni)]
        esercizi_map_globale = {}
        esercizi_scelti = {}  # Dizionario per tracciare tutti gli esercizi scelti (ID -> oggetto esercizio)
        esercizi_serie = {}  # Dizionario per tracciare le serie per esercizio (ID -> numero serie)

        # Prima passata: calcola volumi e crea distribuzioni
        for muscolo in ordered:
            esercizi = DAO.getEsercizi(context, muscolo)
            if not esercizi:
                continue

            base = self.get_weekly_sets("principiante", muscolo, settimana_numero)
            if muscolo == muscolo_target:
                base = int(round(base * 1.2))

            print(f"Muscolo: {muscolo}")
            print(f"  Volume base necessario: {base}")

            # Calcola il volume indiretto già accumulato
            volume_indiretto = self._calcola_coinvolgimento_indiretto(esercizi_scelti, esercizi_serie, [muscolo])
            volume_indiretto_muscolo = volume_indiretto.get(muscolo, 0)

            print(f"  Volume indiretto accumulato: {volume_indiretto_muscolo}")

            # Calcola il volume effettivo necessario
            volume_effettivo = max(0, int(base - volume_indiretto_muscolo))
            print(f"  Volume effettivo necessario: {volume_effettivo}")

            # Se il volume è già coperto dal coinvolgimento indiretto, salta
            if volume_effettivo <= 0:
                print(f"  Volume per {muscolo} già coperto dal coinvolgimento indiretto")
                continue

            e1, e2 = sorted(esercizi[:2], key=lambda e: e.range_ripetizioni[0])
            esercizi_map_globale[e1.id] = e1
            esercizi_map_globale[e2.id] = e2

            # Aggiungi agli esercizi scelti per il calcolo del coinvolgimento indiretto
            esercizi_scelti[e1.id] = e1
            esercizi_scelti[e2.id] = e2

            # Calcola distribuzione delle serie con concentrazione
            distribuzione_giorni = self._concentra_serie_su_meno_giorni(volume_effettivo, giorni)

            # Calcola la distribuzione per rep range (50% 5-7, 40% 12-14, 10% 20-22)
            tot_5_7, tot_12_14, tot_20_22 = self._calcola_distribuzione_rep_range(volume_effettivo)

            # Aggiorna il volume delle serie per esercizio
            esercizi_serie[e1.id] = tot_5_7
            esercizi_serie[e2.id] = tot_12_14 + tot_20_22

            print(f"  Distribuzione: {distribuzione_giorni}")
            print(f"  Heavy (5-7): {tot_5_7}, Medium (12-14): {tot_12_14}, Light (20-22): {tot_20_22}")

            # Crea la distribuzione per i giorni attivi
            giorni_attivi = [i for i, serie in enumerate(distribuzione_giorni) if serie > 0]

            if len(giorni_attivi) == 1:
                # Tutto in un giorno
                day_idx = giorni_attivi[0]
                all_reps_distribution[day_idx][e1.id] = ["5-7"] * tot_5_7
                if tot_12_14 + tot_20_22 > 0:
                    all_reps_distribution[day_idx][e2.id] = ["12-14"] * tot_12_14 + ["20-22"] * tot_20_22

            elif len(giorni_attivi) == 2:
                # Distribuisci su 2 giorni
                day1, day2 = giorni_attivi

                # Giorno 1: principalmente heavy
                serie_day1 = distribuzione_giorni[day1]
                heavy_day1 = min(tot_5_7, serie_day1)
                resto_day1 = serie_day1 - heavy_day1

                # Inizializza le variabili per evitare UnboundLocalError
                medium_day1 = 0
                light_day1 = 0

                if heavy_day1 > 0:
                    all_reps_distribution[day1][e1.id] = ["5-7"] * heavy_day1
                if resto_day1 > 0:
                    medium_day1 = min(tot_12_14, resto_day1)
                    light_day1 = resto_day1 - medium_day1
                    if medium_day1 > 0 or light_day1 > 0:
                        all_reps_distribution[day1][e2.id] = ["12-14"] * medium_day1 + ["20-22"] * light_day1

                # Giorno 2: resto
                serie_day2 = distribuzione_giorni[day2]
                heavy_day2 = tot_5_7 - heavy_day1
                medium_day2 = tot_12_14 - medium_day1
                light_day2 = tot_20_22 - light_day1

                if heavy_day2 > 0:
                    all_reps_distribution[day2][e1.id] = ["5-7"] * heavy_day2
                if medium_day2 > 0 or light_day2 > 0:
                    all_reps_distribution[day2][e2.id] = ["12-14"] * max(0, medium_day2) + ["20-22"] * max(0,
                                                                                                           light_day2)

            # Gestione per 3 giorni (se necessario)
            elif len(giorni_attivi) == 3:
                # Distribuisci su 3 giorni
                day1, day2, day3 = giorni_attivi

                # Giorno 1: principalmente heavy
                serie_day1 = distribuzione_giorni[day1]
                heavy_day1 = min(tot_5_7, serie_day1)
                resto_day1 = serie_day1 - heavy_day1

                if heavy_day1 > 0:
                    all_reps_distribution[day1][e1.id] = ["5-7"] * heavy_day1

                # Giorno 2: medium e parte del resto
                serie_day2 = distribuzione_giorni[day2]
                heavy_day2 = min(tot_5_7 - heavy_day1, serie_day2)
                medium_day2 = min(tot_12_14, serie_day2 - heavy_day2)

                if heavy_day2 > 0:
                    all_reps_distribution[day2][e1.id] = ["5-7"] * heavy_day2
                if medium_day2 > 0:
                    all_reps_distribution[day2][e2.id] = ["12-14"] * medium_day2

                # Giorno 3: resto
                serie_day3 = distribuzione_giorni[day3]
                heavy_day3 = tot_5_7 - heavy_day1 - heavy_day2
                medium_day3 = tot_12_14 - medium_day2
                light_day3 = tot_20_22

                if heavy_day3 > 0:
                    all_reps_distribution[day3][e1.id] = ["5-7"] * heavy_day3
                if medium_day3 > 0 or light_day3 > 0:
                    all_reps_distribution[day3][e2.id] = ["12-14"] * max(0, medium_day3) + ["20-22"] * max(0,
                                                                                                           light_day3)

        # Seconda passata: redistribuisci le serie singole
        all_reps_distribution = self._redistribusci_serie_singole(all_reps_distribution, giorni)

        # Terza passata: crea i giorni di allenamento
        for day_idx, day in enumerate(days):
            for esercizio_id, rip in all_reps_distribution[day_idx].items():
                if len(rip) > 0:
                    esercizio = esercizi_map_globale[esercizio_id]
                    cnt = len(rip)
                    day.aggiungi_esercizio(esercizio, cnt)
                    day.performance_log[esercizio.id] = {
                        "nome": esercizio.nome,
                        "muscolo_primario": esercizio.muscolo_primario,
                        "serie": cnt,
                        "carico": 0,
                        "ripetizioni": rip,
                        "rir": 4,
                        "note": f"Range {' & '.join(sorted(set(rip)))} reps"
                    }

        return TrainingWeek(
            numero_settimana=settimana_numero,
            start_date=oggi,
            workout_days=days
        )

    def getSchedaFullBodyTreGiorniPrincipianti(self, context, muscolo_target):
        return self._crea_fullbody_giorni(context, muscolo_target, giorni=3)

    def getSchedaFullBodyDueGiorniPrincipianti(self, context, muscolo_target):
        return self._crea_fullbody_giorni(context, muscolo_target, giorni=2)


# Utilizzo
if __name__ == "__main__":
    model = Model()
    print(model.getSchedaFullBodyTreGiorniPrincipianti("Home Manubri", "Petto"))
    print(model.getSchedaFullBodyDueGiorniPrincipianti("Home Manubri", "Schiena"))

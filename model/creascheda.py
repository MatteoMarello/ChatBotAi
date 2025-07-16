from datetime import datetime
import random

from database.DAO import DAO
from model.trainingweek import TrainingWeek
from model.workoutday import WorkoutDay


# ===============================================================
# FILE: model.py (LOGICA PRINCIPALE)
# ===============================================================
class Model:
    # --- METODO __init__ AGGIUNTO ---
    def __init__(self):
        """
        Costruttore della classe Model.
        Inizializza gli attributi necessari, come la mappatura degli split.
        """
        self.split_muscoli = {
            "Full Body": ["Petto", "Schiena", "Spalle", "Bicipiti", "Tricipiti", "Quadricipiti", "Femorali", "Glutei",
                          "Polpacci"],
            "Upper": ["Petto", "Schiena", "Spalle", "Bicipiti", "Tricipiti"],
            "Lower": ["Quadricipiti", "Femorali", "Glutei", "Polpacci"],
            "Push": ["Petto", "Spalle", "Tricipiti"],
            "Pull": ["Schiena", "Bicipiti"],
            "Legs": ["Quadricipiti", "Femorali", "Glutei", "Polpacci"],
        }

        # Gerarchia per Full Body: petto, schiena, braccia, quadricipiti, glutei, femorali, spalle, polpacci
        self.gerarchia_fullbody = [
            "Petto",
            "Schiena",
            "Bicipiti",
            "Tricipiti",
            "Quadricipiti",
            "Glutei",
            "Femorali",
            "Spalle",
            "Polpacci"
        ]

    # --------------------------------

    def get_weekly_sets(self, livello, muscolo, mesociclo):
        """Calcola il volume settimanale target per un muscolo."""
        base_volumes = {
            "principiante": {"Petto": (10, 16), "Schiena": (12, 18), "Spalle": (16, 22), "Bicipiti": (8, 14),
                             "Tricipiti": (8, 14), "Quadricipiti": (10, 18), "Femorali": (6, 12), "Glutei": (8, 14),
                             "Polpacci": (6, 12)},
            "intermedio": {"Petto": (11, 20), "Schiena": (13, 20), "Spalle": (18, 24), "Bicipiti": (9, 16),
                           "Tricipiti": (9, 16), "Quadricipiti": (11, 20), "Femorali": (7, 14), "Glutei": (9, 16),
                           "Polpacci": (8, 14)},
            "avanzato": {"Petto": (12, 22), "Schiena": (14, 22), "Spalle": (20, 26), "Bicipiti": (10, 18),
                         "Tricipiti": (10, 18), "Quadricipiti": (12, 22), "Femorali": (8, 16), "Glutei": (10, 18),
                         "Polpacci": (8, 18)}
        }
        start, end = base_volumes[livello][muscolo]
        incremento = mesociclo - 1
        return min(start + incremento, end)

    def _calcola_coinvolgimento_indiretto(self, esercizi_scelti, muscoli_target):
        """Calcola il volume indiretto (come muscolo secondario)."""
        volume_indiretto = {muscolo: 0 for muscolo in muscoli_target}
        for esercizio, serie in esercizi_scelti.items():
            if not esercizio.muscoli_secondari:
                continue
            for muscolo_target in muscoli_target:
                if muscolo_target in esercizio.muscoli_secondari and muscolo_target != esercizio.muscolo_primario:
                    volume_indiretto[muscolo_target] += serie * 0.5  # Metà del volume per lavoro indiretto
        return volume_indiretto

    def _calcola_distribuzione_rep_range(self, volume_effettivo):
        """Distribuisce le serie per rep range (50% pesante, 40% medio, 10% leggero)."""
        if volume_effettivo == 0: return 0, 0, 0

        tot_5_7 = round(volume_effettivo * 0.50)
        tot_12_14 = round(volume_effettivo * 0.35)
        # Assicura che la somma sia corretta
        tot_20_22_prov = volume_effettivo - tot_5_7 - tot_12_14

        if tot_20_22_prov < 0:
            tot_12_14 += tot_20_22_prov
            tot_20_22 = 0
        else:
            tot_20_22 = tot_20_22_prov

        # Correzione finale per arrotondamenti
        if (tot_5_7 + tot_12_14 + tot_20_22) != volume_effettivo:
            tot_5_7 = volume_effettivo - tot_12_14 - tot_20_22

        return int(tot_5_7), int(tot_12_14), int(tot_20_22)

    def _distribuisci_serie_giorni(self, volume_totale, giorni):
        """Distribuisce le serie totali nei giorni disponibili, evitando giorni con 1 sola serie."""
        if giorni <= 0: return []
        if volume_totale <= 0: return [0] * giorni

        # Assicura almeno 2 serie per giorno attivo, se possibile
        serie_per_giorno = [0] * giorni
        giorni_da_usare = min(giorni, volume_totale // 2 if volume_totale > 1 else 1)
        if giorni_da_usare == 0 and volume_totale > 0:
            giorni_da_usare = 1

        if giorni_da_usare > 0:
            base, extra = divmod(volume_totale, giorni_da_usare)
            for i in range(giorni_da_usare):
                serie_per_giorno[i] = base + (1 if i < extra else 0)

        random.shuffle(serie_per_giorno)
        return serie_per_giorno

    def _ordina_muscoli_fullbody(self, muscoli_da_allenare, muscolo_target):
        """
        Ordina i muscoli per Full Body mettendo il muscolo target per primo,
        seguito dalla gerarchia specificata.
        """
        # Inizia sempre con il muscolo target
        muscoli_ordinati = [muscolo_target]

        # Aggiungi gli altri muscoli seguendo la gerarchia
        for muscolo in self.gerarchia_fullbody:
            if muscolo in muscoli_da_allenare and muscolo != muscolo_target:
                muscoli_ordinati.append(muscolo)

        # Aggiungi eventuali muscoli rimanenti non presenti nella gerarchia
        for muscolo in muscoli_da_allenare:
            if muscolo not in muscoli_ordinati:
                muscoli_ordinati.append(muscolo)

        return muscoli_ordinati

    def _parse_rep_range(self, rep_str):
        """Parse string like '[5,7]' into tuple of integers (5,7)"""
        try:
            # Remove brackets and split
            clean_str = rep_str.strip('[]')
            low, high = map(int, clean_str.split(','))
            return low, high
        except:
            return (0, 0)  # Default if parsing fails

    def _crea_fullbody_giorni(self, context, muscolo_target, giorni):
        """Crea una settimana di allenamento Full Body con la nuova logica."""

        MIN_DIRECT_SETS = 4
        settimana_numero = 1
        oggi = datetime.now()
        days = [WorkoutDay(id_giorno=i + 1, settimana=settimana_numero, split_type="Full Body", data=oggi) for i in
                range(giorni)]

        esercizi_map_globale = {}
        esercizi_scelti = {}

        muscoli_da_allenare = self.split_muscoli["Full Body"]
        # Usa la nuova funzione per ordinare i muscoli
        ordered_muscles = self._ordina_muscoli_fullbody(muscoli_da_allenare, muscolo_target)

        # Dizionario per memorizzare gli esercizi da aggiungere per ogni giorno
        # Struttura: {giorno_index: [(esercizio, serie, reps, ordine_muscolo)]}
        esercizi_per_giorno = {i: [] for i in range(giorni)}

        for ordine_muscolo, muscolo in enumerate(ordered_muscles):
            print(f"Processing: {muscolo}")

            volume_totale_target = self.get_weekly_sets("principiante", muscolo, settimana_numero)
            if muscolo == muscolo_target:
                volume_totale_target = int(round(volume_totale_target * 1.2))
            print(f"  - Target volume: {volume_totale_target}")

            volume_indiretto_accumulato = self._calcola_coinvolgimento_indiretto(esercizi_scelti, [muscolo])[muscolo]
            print(f"  - Indirect volume from other exercises: {volume_indiretto_accumulato:.1f}")

            volume_mancante = volume_totale_target - volume_indiretto_accumulato
            volume_effettivo_da_aggiungere = max(MIN_DIRECT_SETS, volume_mancante)
            volume_effettivo = max(0, int(round(volume_effettivo_da_aggiungere)))

            print(
                f"  - Required direct sets to add (max of {MIN_DIRECT_SETS} and {volume_mancante:.1f}): {volume_effettivo}")

            if volume_effettivo <= 0:
                print(f"  - Skipping direct work for {muscolo}, target met.")
                continue

            # MODIFICA PRINCIPALE: Prendi sempre i primi due esercizi dalla lista ordinata per priorità
            esercizi_disponibili = DAO.getEsercizi(context, muscolo)
            if not esercizi_disponibili:
                print(f"  - No exercises found for {muscolo}.")
                continue

            # Prendi i primi due esercizi dalla lista ordinata per priorità
            if len(esercizi_disponibili) >= 2:
                primo_esercizio = esercizi_disponibili[0]
                secondo_esercizio = esercizi_disponibili[1]
                print(f"  - Selected exercises: {primo_esercizio.nome} and {secondo_esercizio.nome}")
            else:
                # Se c'è solo un esercizio, usalo per entrambi
                primo_esercizio = esercizi_disponibili[0]
                secondo_esercizio = esercizi_disponibili[0]
                print(f"  - Only one exercise available: {primo_esercizio.nome}")

            # Determina quale è "pesante" e quale è "leggero" in base al range di ripetizioni
            range_primo = self._parse_rep_range(primo_esercizio.range_ripetizioni)
            range_secondo = self._parse_rep_range(secondo_esercizio.range_ripetizioni)

            # L'esercizio con il minimo più basso del range è quello "pesante"
            if range_primo[0] < range_secondo[0]:
                e_heavy = primo_esercizio
                e_light = secondo_esercizio
            elif range_primo[0] > range_secondo[0]:
                e_heavy = secondo_esercizio
                e_light = primo_esercizio
            else:
                # Se hanno lo stesso minimo, il primo è considerato "pesante"
                e_heavy = primo_esercizio
                e_light = secondo_esercizio

            print(f"  - Heavy exercise: {e_heavy.nome} (range: {e_heavy.range_ripetizioni})")
            print(f"  - Light exercise: {e_light.nome} (range: {e_light.range_ripetizioni})")

            esercizi_map_globale[e_heavy.id] = e_heavy
            esercizi_map_globale[e_light.id] = e_light

            tot_5_7, tot_12_14, tot_20_22 = self._calcola_distribuzione_rep_range(volume_effettivo)
            print(
                f"  - Sets distribution: Heavy(5-7): {tot_5_7}, Medium(12-14): {tot_12_14}, Light(20-22): {tot_20_22}")

            esercizi_scelti[e_heavy] = esercizi_scelti.get(e_heavy, 0) + tot_5_7
            esercizi_scelti[e_light] = esercizi_scelti.get(e_light, 0) + tot_12_14 + tot_20_22

            distribuzione_giorni_heavy = self._distribuisci_serie_giorni(tot_5_7, giorni)
            distribuzione_giorni_light = self._distribuisci_serie_giorni(tot_12_14 + tot_20_22, giorni)

            for i in range(giorni):
                if distribuzione_giorni_heavy[i] > 0:
                    esercizi_per_giorno[i].append((e_heavy, distribuzione_giorni_heavy[i],
                                                   ["5-7"] * distribuzione_giorni_heavy[i], ordine_muscolo))
                if distribuzione_giorni_light[i] > 0:
                    reps_light_disponibili = ["12-14"] * tot_12_14 + ["20-22"] * tot_20_22
                    reps_da_assegnare = random.sample(reps_light_disponibili,
                                                      min(len(reps_light_disponibili), distribuzione_giorni_light[i]))
                    if reps_da_assegnare:
                        esercizi_per_giorno[i].append((e_light, distribuzione_giorni_light[i],
                                                       reps_da_assegnare, ordine_muscolo))

        # Ora aggiungi gli esercizi ai giorni rispettando l'ordine
        for i in range(giorni):
            # Ordina gli esercizi per questo giorno secondo la gerarchia dei muscoli
            esercizi_per_giorno[i].sort(key=lambda x: x[3])  # Ordina per ordine_muscolo

            # Aggiungi gli esercizi al giorno nell'ordine corretto
            for esercizio, serie, reps, ordine_muscolo in esercizi_per_giorno[i]:
                days[i].aggiungi_esercizio(esercizio, serie, reps, ordine_muscolo)

        return TrainingWeek(numero_settimana=settimana_numero, start_date=oggi, workout_days=days)

    def getSchedaFullBody(self, context, muscolo_target, giorni):
        """Metodo unificato per generare schede Full Body."""
        if giorni not in [2, 3]:
            raise ValueError("La frequenza per Full Body deve essere 2 o 3.")
        return self._crea_fullbody_giorni(context, muscolo_target, giorni)


# ===============================================================
# Esempio di Utilizzo (invariato ma ora funzionante)
# ===============================================================
if __name__ == "__main__":
    model = Model()

    print("********** GENERAZIONE SCHEDA 3 GIORNI - FOCUS PETTO **********\n")
    scheda_3_giorni = model.getSchedaFullBody("Palestra Completa", "Petto", giorni=3)
    print(scheda_3_giorni)

    print("\n\n********** GENERAZIONE SCHEDA 2 GIORNI - FOCUS SPALLE **********\n")
    scheda_2_giorni = model.getSchedaFullBody("Home Manubri", "Spalle", giorni=2)
    print(scheda_2_giorni)

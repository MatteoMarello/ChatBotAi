from datetime import datetime
import random

from database.DAO import DAO
from model.trainingweek import TrainingWeek
from model.workoutday import WorkoutDay


# ===============================================================
# FILE: model.py (LOGICA PRINCIPALE)
# ===============================================================
class Model:
    # --- METODO __init__ AGGIORNATO ---
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
            "principiante": {"Petto": (10, 16), "Schiena": (12, 18), "Spalle": (12, 18), "Bicipiti": (8, 14),
                             "Tricipiti": (8, 14), "Quadricipiti": (10, 18), "Femorali": (6, 12), "Glutei": (8, 14),
                             "Polpacci": (6, 12)},
            "intermedio": {"Petto": (11, 20), "Schiena": (13, 20), "Spalle": (13, 20), "Bicipiti": (9, 16),
                           "Tricipiti": (9, 16), "Quadricipiti": (11, 20), "Femorali": (7, 14), "Glutei": (9, 16),
                           "Polpacci": (8, 14)},
            "avanzato": {"Petto": (12, 22), "Schiena": (14, 22), "Spalle": (14, 22), "Bicipiti": (10, 18),
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

        tot_pesante = round(volume_effettivo * 0.50)
        tot_medio = round(volume_effettivo * 0.40)
        # Assicura che la somma sia corretta
        tot_leggero_prov = volume_effettivo - tot_pesante - tot_medio

        if tot_leggero_prov < 0:
            tot_medio += tot_leggero_prov
            tot_leggero = 0
        else:
            tot_leggero = tot_leggero_prov

        # Correzione finale per arrotondamenti
        if (tot_pesante + tot_medio + tot_leggero) != volume_effettivo:
            tot_pesante = volume_effettivo - tot_medio - tot_leggero

        return int(tot_pesante), int(tot_medio), int(tot_leggero)

    def _distribuisci_serie_giorni_intermedio(self, volume_totale, giorni=3):
        """
        Distribuisce le serie totali nei 3 giorni per atleti intermedi.
        Logica:
        - Fino a 6 serie: distribuzione su 2 giorni, evitando serie singole
        - Da 7 serie in su: distribuzione su 3 giorni, evitando serie singole quando possibile
        """
        if volume_totale <= 0:
            return [0, 0, 0]

        if volume_totale <= 6:
            # Distribuzione su 2 giorni - evita serie singole
            serie_per_giorno = [0, 0, 0]

            if volume_totale == 2:
                # 2 serie = 2-0-0
                giorni_attivi = random.sample(range(3), 1)
                serie_per_giorno[giorni_attivi[0]] = 2
            elif volume_totale == 3:
                # 3 serie = 3-0-0
                giorni_attivi = random.sample(range(3), 1)
                serie_per_giorno[giorni_attivi[0]] = 3
            elif volume_totale == 4:
                # 4 serie = 2-2-0
                giorni_attivi = random.sample(range(3), 2)
                serie_per_giorno[giorni_attivi[0]] = 2
                serie_per_giorno[giorni_attivi[1]] = 2
            elif volume_totale == 5:
                # 5 serie = 3-2-0
                giorni_attivi = random.sample(range(3), 2)
                serie_per_giorno[giorni_attivi[0]] = 3
                serie_per_giorno[giorni_attivi[1]] = 2
            elif volume_totale == 6:
                # 6 serie = 3-3-0
                giorni_attivi = random.sample(range(3), 2)
                serie_per_giorno[giorni_attivi[0]] = 3
                serie_per_giorno[giorni_attivi[1]] = 3

        else:
            # Distribuzione su 3 giorni - evita serie singole quando possibile
            serie_per_giorno = [0, 0, 0]

            if volume_totale == 7:
                # 7 serie = 3-2-2
                serie_per_giorno = [3, 2, 2]
            elif volume_totale == 8:
                # 8 serie = 3-3-2
                serie_per_giorno = [3, 3, 2]
            elif volume_totale == 9:
                # 9 serie = 3-3-3
                serie_per_giorno = [3, 3, 3]
            elif volume_totale == 10:
                # 10 serie = 4-3-3
                serie_per_giorno = [4, 3, 3]
            elif volume_totale == 11:
                # 11 serie = 4-4-3
                serie_per_giorno = [4, 4, 3]
            elif volume_totale == 12:
                # 12 serie = 4-4-4
                serie_per_giorno = [4, 4, 4]
            else:
                # Per volumi maggiori, distribuzione standard evitando serie singole
                base = volume_totale // 3
                extra = volume_totale % 3

                serie_per_giorno = [base] * 3

                # Distribuisci le serie extra
                for i in range(extra):
                    serie_per_giorno[i] += 1

                # Se ci sono serie singole, ridistribuisci
                if min(serie_per_giorno) == 1:
                    # Sposta le serie singole verso gli altri giorni
                    for i in range(3):
                        if serie_per_giorno[i] == 1:
                            serie_per_giorno[i] = 0
                            # Aggiungi la serie al giorno con meno serie (esclusi quelli con 0)
                            giorni_non_zero = [j for j in range(3) if serie_per_giorno[j] > 0]
                            if giorni_non_zero:
                                min_idx = min(giorni_non_zero, key=lambda x: serie_per_giorno[x])
                                serie_per_giorno[min_idx] += 1

            # Mescola per randomizzare la distribuzione
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

    def _crea_fullbody_intermedio(self, context, muscolo_target, giorni=3, volume_overrides=None):
        """Crea una settimana di allenamento Full Body per atleti intermedi."""

        MIN_DIRECT_SETS = 6  # Cambiato da 4 a 6 per intermedi
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

            # *** INIZIO MODIFICA: Gestione volume_overrides ***
            if volume_overrides and muscolo in volume_overrides:
                volume_totale_target = volume_overrides[muscolo]
                print(
                    f"  - Volume OVERRIDDEN to {volume_totale_target} (original: {self.get_weekly_sets('intermedio', muscolo, settimana_numero)})")
            else:
                # Calcolo normale del volume
                volume_base = self.get_weekly_sets("intermedio", muscolo, settimana_numero)

                # Se è il muscolo target, aggiungi 30% di volume
                if muscolo == muscolo_target:
                    volume_totale_target = int(round(volume_base * 1.3))
                    print(f"  - Target muscle detected! Base: {volume_base}, With 30% bonus: {volume_totale_target}")
                else:
                    volume_totale_target = volume_base
            # *** FINE MODIFICA ***

            print(f"  - Target volume: {volume_totale_target}")

            volume_indiretto_accumulato = self._calcola_coinvolgimento_indiretto(esercizi_scelti, [muscolo])[muscolo]
            print(f"  - Indirect volume from other exercises: {volume_indiretto_accumulato:.1f}")

            # Calcola le serie effettive (dirette + indirette)
            serie_effettive_attuali = volume_indiretto_accumulato
            volume_mancante = volume_totale_target - serie_effettive_attuali

            # Vincolo: almeno 6 serie dirette per ogni muscolo
            volume_diretto_da_aggiungere = max(MIN_DIRECT_SETS, volume_mancante)
            volume_effettivo = max(0, int(round(volume_diretto_da_aggiungere)))

            print(f"  - Current effective sets: {serie_effettive_attuali:.1f}")
            print(f"  - Missing volume: {volume_mancante:.1f}")
            print(f"  - Direct sets to add (min {MIN_DIRECT_SETS}): {volume_effettivo}")

            if volume_effettivo <= 0:
                print(f"  - Skipping direct work for {muscolo}, target met.")
                continue

            # Prendi i primi due esercizi dalla lista ordinata per priorità
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

            # Distribuzione: 50% pesante (6-8), 40% medio (12-14), 10% leggero (20-22)
            tot_pesante, tot_medio, tot_leggero = self._calcola_distribuzione_rep_range(volume_effettivo)
            print(
                f"  - Sets distribution: Heavy(6-8): {tot_pesante}, Medium(12-14): {tot_medio}, Light(20-22): {tot_leggero}")

            # Aggiorna il conteggio degli esercizi scelti
            esercizi_scelti[e_heavy] = esercizi_scelti.get(e_heavy, 0) + tot_pesante
            esercizi_scelti[e_light] = esercizi_scelti.get(e_light, 0) + tot_medio + tot_leggero

            # Distribuisci le serie sui giorni usando la logica per intermedi
            distribuzione_giorni_heavy = self._distribuisci_serie_giorni_intermedio(tot_pesante, giorni)
            distribuzione_giorni_light = self._distribuisci_serie_giorni_intermedio(tot_medio + tot_leggero, giorni)

            print(f"  - Heavy distribution across days: {distribuzione_giorni_heavy}")
            print(f"  - Light distribution across days: {distribuzione_giorni_light}")

            # Assegna gli esercizi ai giorni
            for i in range(giorni):
                if distribuzione_giorni_heavy[i] > 0:
                    esercizi_per_giorno[i].append((e_heavy, distribuzione_giorni_heavy[i],
                                                   ["6-8"] * distribuzione_giorni_heavy[i], ordine_muscolo))
                if distribuzione_giorni_light[i] > 0:
                    reps_light_disponibili = ["12-14"] * tot_medio + ["20-22"] * tot_leggero
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

    def _distribuisci_serie_due_giorni(self, volume_totale):
        """
        Distribuisce le serie totali su 2 giorni per atleti intermedi (4 giorni totali).
        Ogni muscolo viene allenato esattamente 2 volte.
        """
        if volume_totale <= 0:
            return [0, 0]

        if volume_totale <= 2:
            # 2 serie = 1-1
            return [1, 1]
        elif volume_totale <= 4:
            # 3-4 serie = distribuzione più equilibrata possibile
            base = volume_totale // 2
            extra = volume_totale % 2
            return [base + extra, base]
        else:
            # 5+ serie = distribuzione equilibrata
            base = volume_totale // 2
            extra = volume_totale % 2
            return [base + extra, base]

    def _crea_fullbody_intermedio_4giorni(self, context, muscolo_target, volume_overrides=None):
        """Crea una settimana di allenamento Full Body per atleti intermedi a 4 giorni."""

        MIN_DIRECT_SETS = 6
        settimana_numero = 1
        oggi = datetime.now()

        # Definisci i gruppi muscolari per ogni tipo di giorno
        muscoli_giorni_1_3 = ["Spalle", "Petto", "Schiena", "Polpacci"]  # Giorni 1 e 3
        muscoli_giorni_2_4 = ["Quadricipiti", "Glutei", "Femorali", "Bicipiti", "Tricipiti"]  # Giorni 2 e 4

        # Crea i 4 giorni di allenamento
        days = [WorkoutDay(id_giorno=i + 1, settimana=settimana_numero, split_type="Full Body 4 Days", data=oggi) for i
                in range(4)]

        esercizi_map_globale = {}
        esercizi_scelti = {}

        # Definisci le gerarchie per i due tipi di giorno
        def _get_muscle_order_day_1_3(muscolo_target):
            """Ordine per giorni 1 e 3: target first, poi petto pesante, schiena pesante, petto leggero, schiena leggero, spalle, polpacci"""
            base_order = ["Petto", "Schiena", "Spalle", "Polpacci"]
            if muscolo_target in base_order:
                # Metti il target per primo
                ordered = [muscolo_target]
                for muscle in base_order:
                    if muscle != muscolo_target:
                        ordered.append(muscle)
                return ordered
            return base_order

        def _get_muscle_order_day_2_4(muscolo_target):
            """Ordine per giorni 2 e 4: target first, poi quadricipiti, glutei, femorali, bicipiti, tricipiti"""
            base_order = ["Quadricipiti", "Glutei", "Femorali", "Bicipiti", "Tricipiti"]
            if muscolo_target in base_order:
                # Metti il target per primo
                ordered = [muscolo_target]
                for muscle in base_order:
                    if muscle != muscolo_target:
                        ordered.append(muscle)
                return ordered
            return base_order

        # Determina in quale gruppo appartiene il muscolo target
        if muscolo_target in muscoli_giorni_1_3:
            muscoli_da_processare = muscoli_giorni_1_3
            ordered_muscles = _get_muscle_order_day_1_3(muscolo_target)
            giorni_target = [0, 2]  # Giorni 1 e 3 (indici 0 e 2)
        else:
            muscoli_da_processare = muscoli_giorni_2_4
            ordered_muscles = _get_muscle_order_day_2_4(muscolo_target)
            giorni_target = [1, 3]  # Giorni 2 e 4 (indici 1 e 3)

        # Processa anche l'altro gruppo di muscoli
        if muscolo_target in muscoli_giorni_1_3:
            altri_muscoli = muscoli_giorni_2_4
            ordered_altri_muscoli = _get_muscle_order_day_2_4(muscolo_target)
            giorni_altri = [1, 3]  # Giorni 2 e 4
        else:
            altri_muscoli = muscoli_giorni_1_3
            ordered_altri_muscoli = _get_muscle_order_day_1_3(muscolo_target)
            giorni_altri = [0, 2]  # Giorni 1 e 3

        # Struttura per memorizzare esercizi: {giorno_index: [(esercizio, serie, reps, ordine_muscolo)]}
        esercizi_per_giorno = {i: [] for i in range(4)}

        # Processa prima il gruppo del muscolo target
        for ordine_muscolo, muscolo in enumerate(ordered_muscles):
            self._processa_muscolo_4giorni(context, muscolo, muscolo_target, ordine_muscolo, giorni_target,
                                           esercizi_per_giorno, esercizi_scelti, esercizi_map_globale,
                                           MIN_DIRECT_SETS, settimana_numero, volume_overrides)

        # Processa l'altro gruppo di muscoli
        for ordine_muscolo, muscolo in enumerate(ordered_altri_muscoli):
            self._processa_muscolo_4giorni(context, muscolo, muscolo_target, ordine_muscolo + len(ordered_muscles),
                                           giorni_altri, esercizi_per_giorno, esercizi_scelti, esercizi_map_globale,
                                           MIN_DIRECT_SETS, settimana_numero, volume_overrides)

        # Aggiungi gli esercizi ai giorni rispettando l'ordine specifico
        for i in range(4):
            if i in [0, 2]:  # Giorni 1 e 3
                self._aggiungi_esercizi_giorni_1_3(days[i], esercizi_per_giorno[i], muscolo_target)
            else:  # Giorni 2 e 4
                self._aggiungi_esercizi_giorni_2_4(days[i], esercizi_per_giorno[i], muscolo_target)

        return TrainingWeek(numero_settimana=settimana_numero, start_date=oggi, workout_days=days)

    def _processa_muscolo_4giorni(self, context, muscolo, muscolo_target, ordine_muscolo, giorni_target,
                                  esercizi_per_giorno, esercizi_scelti, esercizi_map_globale,
                                  MIN_DIRECT_SETS, settimana_numero, volume_overrides=None):
        """Processa un singolo muscolo per l'allenamento a 4 giorni."""

        print(f"Processing: {muscolo}")

        # *** INIZIO MODIFICA: Gestione volume_overrides ***
        if volume_overrides and muscolo in volume_overrides:
            volume_totale_target = volume_overrides[muscolo]
            print(
                f"  - Volume OVERRIDDEN to {volume_totale_target} (original: {self.get_weekly_sets('intermedio', muscolo, settimana_numero)})")
        else:
            # Calcolo normale del volume
            volume_base = self.get_weekly_sets("intermedio", muscolo, settimana_numero)

            # Se è il muscolo target, aggiungi 30% di volume
            if muscolo == muscolo_target:
                volume_totale_target = int(round(volume_base * 1.3))
                print(f"  - Target muscle detected! Base: {volume_base}, With 30% bonus: {volume_totale_target}")
            else:
                volume_totale_target = volume_base
        # *** FINE MODIFICA ***

        print(f"  - Target volume: {volume_totale_target}")

        volume_indiretto_accumulato = self._calcola_coinvolgimento_indiretto(esercizi_scelti, [muscolo])[muscolo]
        print(f"  - Indirect volume from other exercises: {volume_indiretto_accumulato:.1f}")

        # Calcola le serie effettive (dirette + indirette)
        serie_effettive_attuali = volume_indiretto_accumulato
        volume_mancante = volume_totale_target - serie_effettive_attuali

        # Vincolo: almeno 6 serie dirette per ogni muscolo
        volume_diretto_da_aggiungere = max(MIN_DIRECT_SETS, volume_mancante)
        volume_effettivo = max(0, int(round(volume_diretto_da_aggiungere)))

        print(f"  - Current effective sets: {serie_effettive_attuali:.1f}")
        print(f"  - Missing volume: {volume_mancante:.1f}")
        print(f"  - Direct sets to add (min {MIN_DIRECT_SETS}): {volume_effettivo}")

        if volume_effettivo <= 0:
            print(f"  - Skipping direct work for {muscolo}, target met.")
            return

        # Prendi i primi due esercizi dalla lista ordinata per priorità
        esercizi_disponibili = DAO.getEsercizi(context, muscolo)
        if not esercizi_disponibili:
            print(f"  - No exercises found for {muscolo}.")
            return

        # Prendi i primi due esercizi
        if len(esercizi_disponibili) >= 2:
            primo_esercizio = esercizi_disponibili[0]
            secondo_esercizio = esercizi_disponibili[1]
        else:
            primo_esercizio = esercizi_disponibili[0]
            secondo_esercizio = esercizi_disponibili[0]

        print(f"  - Selected exercises: {primo_esercizio.nome} and {secondo_esercizio.nome}")

        # Determina quale è "pesante" e quale è "leggero"
        range_primo = self._parse_rep_range(primo_esercizio.range_ripetizioni)
        range_secondo = self._parse_rep_range(secondo_esercizio.range_ripetizioni)

        if range_primo[0] < range_secondo[0]:
            e_heavy = primo_esercizio
            e_light = secondo_esercizio
        elif range_primo[0] > range_secondo[0]:
            e_heavy = secondo_esercizio
            e_light = primo_esercizio
        else:
            e_heavy = primo_esercizio
            e_light = secondo_esercizio

        print(f"  - Heavy exercise: {e_heavy.nome} (range: {e_heavy.range_ripetizioni})")
        print(f"  - Light exercise: {e_light.nome} (range: {e_light.range_ripetizioni})")

        esercizi_map_globale[e_heavy.id] = e_heavy
        esercizi_map_globale[e_light.id] = e_light

        # Distribuzione: 50% pesante (6-8), 40% medio (12-14), 10% leggero (20-22)
        tot_pesante, tot_medio, tot_leggero = self._calcola_distribuzione_rep_range(volume_effettivo)
        print(
            f"  - Sets distribution: Heavy(6-8): {tot_pesante}, Medium(12-14): {tot_medio}, Light(20-22): {tot_leggero}")

        # Aggiorna il conteggio degli esercizi scelti
        esercizi_scelti[e_heavy] = esercizi_scelti.get(e_heavy, 0) + tot_pesante
        esercizi_scelti[e_light] = esercizi_scelti.get(e_light, 0) + tot_medio + tot_leggero

        # Distribuisci le serie sui 2 giorni (ogni esercizio viene ripetuto 2 volte)
        distribuzione_heavy = self._distribuisci_serie_due_giorni(tot_pesante)
        distribuzione_light = self._distribuisci_serie_due_giorni(tot_medio + tot_leggero)

        print(f"  - Heavy distribution across 2 days: {distribuzione_heavy}")
        print(f"  - Light distribution across 2 days: {distribuzione_light}")

        # Assegna gli esercizi ai giorni target
        for i, giorno_idx in enumerate(giorni_target):
            if distribuzione_heavy[i] > 0:
                esercizi_per_giorno[giorno_idx].append((e_heavy, distribuzione_heavy[i],
                                                        ["6-8"] * distribuzione_heavy[i], ordine_muscolo))
            if distribuzione_light[i] > 0:
                reps_light_disponibili = ["12-14"] * tot_medio + ["20-22"] * tot_leggero
                # Distribuisci le ripetizioni tra i due giorni
                if i == 0:  # Primo giorno
                    reps_da_assegnare = reps_light_disponibili[:distribuzione_light[i]]
                else:  # Secondo giorno
                    reps_da_assegnare = reps_light_disponibili[distribuzione_light[0]:]

                if reps_da_assegnare:
                    esercizi_per_giorno[giorno_idx].append((e_light, distribuzione_light[i],
                                                            reps_da_assegnare, ordine_muscolo))

    def _aggiungi_esercizi_giorni_1_3(self, day, esercizi_giorno, muscolo_target):
        """Aggiungi esercizi ai giorni 1 e 3 con ordine specifico: target first, poi petto pesante, schiena pesante, petto leggero, schiena leggero, spalle, polpacci"""

        # Raggruppa esercizi per muscolo e tipo
        esercizi_per_muscolo = {}
        for esercizio, serie, reps, ordine_muscolo in esercizi_giorno:
            muscolo = esercizio.muscolo_primario
            if muscolo not in esercizi_per_muscolo:
                esercizi_per_muscolo[muscolo] = {'heavy': [], 'light': []}

            # Determina se è pesante o leggero dal range di ripetizioni
            if "6-8" in reps:
                esercizi_per_muscolo[muscolo]['heavy'].append((esercizio, serie, reps, ordine_muscolo))
            else:
                esercizi_per_muscolo[muscolo]['light'].append((esercizio, serie, reps, ordine_muscolo))

        # Ordine specifico: target first, poi petto pesante, schiena pesante, petto leggero, schiena leggero, spalle, polpacci
        order = []

        # Prima il muscolo target (se presente)
        if muscolo_target in esercizi_per_muscolo:
            for ex in esercizi_per_muscolo[muscolo_target]['heavy']:
                order.append(ex)
            for ex in esercizi_per_muscolo[muscolo_target]['light']:
                order.append(ex)

        # Poi petto pesante
        if "Petto" in esercizi_per_muscolo and muscolo_target != "Petto":
            for ex in esercizi_per_muscolo["Petto"]['heavy']:
                order.append(ex)

        # Poi schiena pesante
        if "Schiena" in esercizi_per_muscolo and muscolo_target != "Schiena":
            for ex in esercizi_per_muscolo["Schiena"]['heavy']:
                order.append(ex)

        # Poi petto leggero
        if "Petto" in esercizi_per_muscolo and muscolo_target != "Petto":
            for ex in esercizi_per_muscolo["Petto"]['light']:
                order.append(ex)

        # Poi schiena leggero
        if "Schiena" in esercizi_per_muscolo and muscolo_target != "Schiena":
            for ex in esercizi_per_muscolo["Schiena"]['light']:
                order.append(ex)

        # Poi spalle
        if "Spalle" in esercizi_per_muscolo and muscolo_target != "Spalle":
            for ex in esercizi_per_muscolo["Spalle"]['heavy']:
                order.append(ex)
            for ex in esercizi_per_muscolo["Spalle"]['light']:
                order.append(ex)

        # Infine polpacci
        if "Polpacci" in esercizi_per_muscolo and muscolo_target != "Polpacci":
            for ex in esercizi_per_muscolo["Polpacci"]['heavy']:
                order.append(ex)
            for ex in esercizi_per_muscolo["Polpacci"]['light']:
                order.append(ex)

        # Aggiungi al giorno
        for esercizio, serie, reps, ordine_muscolo in order:
            day.aggiungi_esercizio(esercizio, serie, reps, ordine_muscolo)

    def _aggiungi_esercizi_giorni_2_4(self, day, esercizi_giorno, muscolo_target):
        """Aggiungi esercizi ai giorni 2 e 4 con ordine specifico: target first, poi quadricipiti pesante, poi tutto il resto, infine bicipiti e tricipiti"""

        # Raggruppa esercizi per muscolo e tipo
        esercizi_per_muscolo = {}
        for esercizio, serie, reps, ordine_muscolo in esercizi_giorno:
            muscolo = esercizio.muscolo_primario
            if muscolo not in esercizi_per_muscolo:
                esercizi_per_muscolo[muscolo] = {'heavy': [], 'light': []}

            # Determina se è pesante o leggero dal range di ripetizioni
            if "6-8" in reps:
                esercizi_per_muscolo[muscolo]['heavy'].append((esercizio, serie, reps, ordine_muscolo))
            else:
                esercizi_per_muscolo[muscolo]['light'].append((esercizio, serie, reps, ordine_muscolo))

        # Ordine specifico: target first, poi quadricipiti pesante, poi tutto il resto, infine bicipiti e tricipiti
        order = []

        # Prima il muscolo target (se presente)
        if muscolo_target in esercizi_per_muscolo:
            for ex in esercizi_per_muscolo[muscolo_target]['heavy']:
                order.append(ex)
            for ex in esercizi_per_muscolo[muscolo_target]['light']:
                order.append(ex)

        # Poi quadricipiti pesante
        if "Quadricipiti" in esercizi_per_muscolo and muscolo_target != "Quadricipiti":
            for ex in esercizi_per_muscolo["Quadricipiti"]['heavy']:
                order.append(ex)

        # Poi glutei e femorali
        for muscolo in ["Glutei", "Femorali"]:
            if muscolo in esercizi_per_muscolo and muscolo_target != muscolo:
                for ex in esercizi_per_muscolo[muscolo]['heavy']:
                    order.append(ex)
                for ex in esercizi_per_muscolo[muscolo]['light']:
                    order.append(ex)

        # Poi quadricipiti leggero
        if "Quadricipiti" in esercizi_per_muscolo and muscolo_target != "Quadricipiti":
            for ex in esercizi_per_muscolo["Quadricipiti"]['light']:
                order.append(ex)

        # Infine bicipiti e tricipiti
        for muscolo in ["Bicipiti", "Tricipiti"]:
            if muscolo in esercizi_per_muscolo and muscolo_target != muscolo:
                for ex in esercizi_per_muscolo[muscolo]['heavy']:
                    order.append(ex)
                for ex in esercizi_per_muscolo[muscolo]['light']:
                    order.append(ex)

        # Aggiungi al giorno
        for esercizio, serie, reps, ordine_muscolo in order:
            day.aggiungi_esercizio(esercizio, serie, reps, ordine_muscolo)

    def getSchedaFullBodyIntermedio(self, context, muscolo_target, giorni=3, volume_overrides=None):
        """Metodo per generare schede Full Body per atleti intermedi (3 o 4 giorni)."""
        if giorni == 3:
            return self._crea_fullbody_intermedio(context, muscolo_target, giorni=3, volume_overrides=volume_overrides)
        elif giorni == 4:
            return self._crea_fullbody_intermedio_4giorni(context, muscolo_target, volume_overrides=volume_overrides)
        else:
            raise ValueError("Per intermedi sono supportati solo 3 o 4 giorni di allenamento.")

    def getSchedaFullBody(self, context, muscolo_target, giorni, volume_overrides=None):
        """Metodo unificato per generare schede Full Body (mantenuto per compatibilità)."""
        if giorni not in [2, 3]:
            raise ValueError("La frequenza per Full Body deve essere 2 o 3.")
        return self._crea_fullbody_giorni(context, muscolo_target, giorni, volume_overrides=volume_overrides)


# ===============================================================
# Esempio di Utilizzo
# ===============================================================
if __name__ == "__main__":
    model = Model()

    print("********** GENERAZIONE SCHEDA FULL BODY INTERMEDIO 3 GIORNI - FOCUS PETTO **********\n")
    scheda_intermedio_3 = model.getSchedaFullBodyIntermedio("Palestra Completa", "Petto", giorni=3)
    print(scheda_intermedio_3)

    print("\n\n********** GENERAZIONE SCHEDA FULL BODY INTERMEDIO 4 GIORNI - FOCUS SPALLE **********\n")
    scheda_intermedio_4 = model.getSchedaFullBodyIntermedio("Palestra Completa", "Spalle", giorni=4)
    print(scheda_intermedio_4)

    print("\n\n********** GENERAZIONE SCHEDA FULL BODY INTERMEDIO 4 GIORNI - FOCUS QUADRICIPITI **********\n")
    scheda_intermedio_4_quad = model.getSchedaFullBodyIntermedio("Palestra Completa", "Quadricipiti", giorni=4)
    print(scheda_intermedio_4_quad)

    print("\n\n********** TEST CON VOLUME OVERRIDES **********\n")
    volume_overrides = {"Petto": 15, "Schiena": 18, "Spalle": 12}
    scheda_con_override = model.getSchedaFullBodyIntermedio("Palestra Completa", "Petto", giorni=3,
                                                            volume_overrides=volume_overrides)
    print(scheda_con_override)

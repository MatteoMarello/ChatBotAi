from model.creascheda import Model as CreaSchedaModel
from model.adattaScheda import TrainingAlgorithm, PerformanceData, DOMSData
from model.trainingweek import TrainingWeek
from copy import deepcopy
from collections import defaultdict
import re
import traceback
from model.daily_readiness_adjuster import DailyReadinessAdjuster, ReadinessInput, WorkoutAdjustment
import re
from collections import defaultdict
import traceback

from UI.progress_view import *
from model.workoutday import WorkoutDay


class Controller:
    def __init__(self):
        self.view = None
        self.crea_scheda_model = CreaSchedaModel()
        self.training_algo = TrainingAlgorithm()
        self.readiness_adjuster = DailyReadinessAdjuster()
        self.pending_workout_day: WorkoutDay = None  # Per memorizzare il giorno in attesa di valutazione
        self.training_week: TrainingWeek = None
        self.current_week_num = 0
        self.current_day_index = -1
        self.config_values = {}
        self.volume_history = {}
        # Aggiunta per la nuova vista
        self.progress_view = None
        self.exercise_name_map = {}
        self.exercise_details_map = {}  # Mappa con i dettagli completi degli esercizi
        self.nutrition_view = None  # Aggiungi riferimento alla TDEE View
        self.context = None

    def handle_navigation_change(self, e):
        selected_index = e.control.selected_index

        if selected_index == 0:  # Allenamento
            # Se c'è una scheda attiva, mostrala, altrimenti mostra la configurazione
            if self.view.scheda_container.content.controls:
                self._activate_view('scheda')
            else:
                self._activate_view('config')

        elif selected_index == 1:  # Progressi
            self._activate_view('progress')
            try:
                self._prepare_and_show_progress()
            except Exception as ex:
                print("--- ERRORE DURANTE LA PREPARAZIONE DELLA VISTA PROGRESSI ---")
                traceback.print_exc()
                print("---------------------------------------------------------")
                if hasattr(self.progress_view, 'show_error'):
                    self.progress_view.show_error(f"Impossibile caricare i dati: {ex}")

        elif selected_index == 2:  # Nutrizione
            self._activate_view('nutrition')

    # --- FUNZIONE _prepare_and_show_progress COMPLETAMENTE SOSTITUITA ---
    def _prepare_and_show_progress(self):
        """
        Prepara i dati calcolando la variazione % dell'1RM rispetto alla settimana precedente
        per gli esercizi 'heavy' e il volume, poi aggiorna la vista dei progressi.
        """
        # 1. Raccogli i dati settimanali dell'1RM (logica invariata)
        perf_by_muscle = defaultdict(list)
        for week in sorted(self.training_algo.performance_data.keys()):
            for perf in self.training_algo.performance_data[week]:
                perf_by_muscle[perf.muscolo_primario].append(perf)

        if not self.exercise_details_map:
            self.exercise_details_map = self.crea_scheda_model.get_all_exercises_details_map()
        if not self.exercise_name_map:
            self.exercise_name_map = {ex_id: ex.nome for ex_id, ex in self.exercise_details_map.items()}

        weekly_1rm_data = {}
        for muscolo, performances in perf_by_muscle.items():
            if not performances: continue
            exercise_ids = {p.esercizio_id for p in performances}
            heavy_exercise_id = None
            min_rep = float('inf')
            for ex_id in exercise_ids:
                exercise_obj = self.exercise_details_map.get(ex_id)
                if exercise_obj and exercise_obj.range_ripetizioni:
                    low_rep, _ = CreaSchedaModel.parse_rep_range(exercise_obj.range_ripetizioni)
                    if low_rep < min_rep:
                        min_rep = low_rep
                        heavy_exercise_id = ex_id

            if heavy_exercise_id:
                nome_esercizio = self.exercise_name_map.get(heavy_exercise_id, f"ID:{heavy_exercise_id}")
                chiave_grafico = f"{muscolo} ({nome_esercizio})"
                weekly_max_1rm = defaultdict(float)
                for p in performances:
                    if p.esercizio_id == heavy_exercise_id:
                        weekly_max_1rm[p.settimana] = max(weekly_max_1rm[p.settimana], p.one_rm)
                if weekly_max_1rm:
                    weekly_1rm_data[chiave_grafico] = sorted(weekly_max_1rm.items())

        # 2. Calcola la variazione percentuale settimana su settimana
        wow_improvement_data = {}  # wow = Week-over-Week
        for exercise_name, weekly_data in weekly_1rm_data.items():
            if len(weekly_data) < 2: continue

            rm_by_week = dict(weekly_data)
            weekly_changes = []
            sorted_weeks = sorted(rm_by_week.keys())

            for i in range(1, len(sorted_weeks)):
                current_week = sorted_weeks[i]
                previous_week = sorted_weeks[i - 1]

                current_rm = rm_by_week.get(current_week)
                previous_rm = rm_by_week.get(previous_week)

                if previous_rm and current_rm and previous_rm > 0:
                    percentage_change = ((current_rm - previous_rm) / previous_rm) * 100
                    weekly_changes.append((current_week, percentage_change))

            if weekly_changes:
                wow_improvement_data[exercise_name] = weekly_changes

        # 3. Prepara i dati del volume (invariato)
        volume_data = self.volume_history

        # 4. Invia i nuovi dati (variazione % settimanale e volume) alla vista
        if self.progress_view:
            self.progress_view.update_view(wow_improvement_data, volume_data)

    # Il resto del file rimane invariato...
    def set_view(self, view):
        self.view = view
        self.carica_opzioni_iniziali()

    def carica_opzioni_iniziali(self):
        try:
            muscoli = self.crea_scheda_model.split_muscoli["Full Body"]
            self.view.dd_muscolo_target.options = [ft.dropdown.Option(m) for m in muscoli]
            self.view.dd_muscolo_target.value = muscoli[0] if muscoli else None
            self.aggiorna_opzioni_frequenza("intermedio")
            self.view.update_view()
        except Exception as ex:
            if self.view:
                self.view.show_snackbar(f"Errore nel caricamento iniziale: {ex}", ft.Colors.RED)

    def aggiorna_opzioni_frequenza(self, esperienza: str):
        try:
            if esperienza == "principiante":
                self.view.dd_frequenza.options = [ft.dropdown.Option("2"), ft.dropdown.Option("3")]
                self.view.dd_frequenza.value = "3"
            else:
                self.view.dd_frequenza.options = [ft.dropdown.Option("3"), ft.dropdown.Option("4")]
                self.view.dd_frequenza.value = "3"
            self.view.update_view()
        except Exception as ex:
            if self.view:
                self.view.show_snackbar(f"Errore nell'aggiornamento frequenza: {ex}", ft.Colors.RED)

    def handle_crea_scheda(self, e):
        self.config_values = self.view.get_config_values()
        if not all(self.config_values.values()):
            self.view.show_snackbar("Per favore, compila tutti i campi!", "error")
            return

        self.view.btn_crea_scheda.disabled = True
        self.view.update_view()

        try:
            # Carica i dettagli degli esercizi se non già presenti
            if not self.exercise_details_map:
                self.exercise_details_map = self.crea_scheda_model.get_all_exercises_details_map()
                self.exercise_name_map = {ex_id: ex.nome for ex_id, ex in self.exercise_details_map.items()}

            # Genera la scheda in base all'esperienza
            esperienza = self.config_values["esperienza"]
            params = self._get_scheda_params()
            if esperienza == "principiante":
                self.training_week = self.crea_scheda_model.getSchedaFullBodyPrincipiante(**params)
            else:
                self.training_week = self.crea_scheda_model.getSchedaFullBodyIntermedio(**params)

            # Controlla che la scheda sia stata creata correttamente
            if not self.training_week or not any(day.esercizi for day in self.training_week.workout_days):
                self.view.show_snackbar("Errore: Nessun esercizio trovato per generare la scheda. Controlla il DB.",
                                        color="error", duration=6000)
                self.view.btn_crea_scheda.disabled = False
                self.view.update_view()
                return

            self._reset_ciclo()
            self.view.show_snackbar("Scheda creata con successo!", "success")
            self.prosegui_al_prossimo_giorno()

        except Exception as ex:
            self.view.show_snackbar(f"Errore critico nella creazione: {ex}", "error")
            self._activate_view('config')  # Torna alla config in caso di errore
        finally:
            if self.view.btn_crea_scheda.disabled:
                self.view.btn_crea_scheda.disabled = False
            self.view.update_view()

    def handle_salva_performance(self, e):
        print("\n--- DEBUG: Chiamato handle_salva_performance ---")  # <--- AGGIUNGI
        performance_list_raw = self.view.get_performance_data_from_cards()
        if not performance_list_raw:
            self.view.show_snackbar("Nessuna performance inserita. Compila almeno una serie.", ft.Colors.ORANGE)
            return
        self.view.btn_salva_performance.disabled = True
        self.view.update_view()
        try:
            for p_data in performance_list_raw:
                if not p_data["sets"]: continue
                if "muscolo_primario" not in p_data:
                    self.view.show_snackbar(
                        f"Errore: muscolo primario mancante per esercizio ID {p_data['esercizio_id']}", ft.Colors.RED)
                    continue
                performance = PerformanceData(esercizio_id=p_data["esercizio_id"], giorno=p_data["giorno"],
                                              settimana=self.current_week_num,
                                              muscolo_primario=p_data["muscolo_primario"], sets=p_data["sets"],
                                              mmc=int(p_data["controls"]["mmc"].value),
                                              pump=int(p_data["controls"]["pump"].value),
                                              dolori_articolari=int(p_data["controls"]["dolori"].value))
                self.training_algo.aggiungi_performance(self.current_week_num, performance)
            self.view.show_snackbar("Performance del giorno salvate!", ft.Colors.GREEN)
            print("--- DEBUG: Performance salvate, chiamo prosegui_al_prossimo_giorno ---") # <--- AGGIUNGI
            self.prosegui_al_prossimo_giorno()
        except (ValueError, TypeError) as ex:
            print(f"--- DEBUG: ERRORE in handle_salva_performance: {ex} ---")  # <--- AGGIUNGI
            self.view.show_snackbar(f"Dati non validi: {ex}", ft.Colors.RED)
        except Exception as ex:
            print(f"--- DEBUG: ERRORE in handle_salva_performance: {ex} ---")  # <--- AGGIUNGI
            self.view.show_snackbar(f"Errore nel salvataggio: {ex}", ft.Colors.RED)
        finally:
            self.view.btn_salva_performance.disabled = False
            self.view.update_view()

    def handle_doms_salvati(self, e):
        """
        Gestisce il salvataggio dei DOMS e la generazione della settimana 2.
        Aggiunta una guardia per prevenire esecuzioni in stati imprevisti.
        """
        # --- INIZIO BLOCCO MODIFICATO ---
        # Guardia di sicurezza: questa logica deve girare solo alla fine della settimana 1.
        if self.current_week_num != 1:
            self.view.show_snackbar(
                f"Errore di stato: rilevata settimana {self.current_week_num} invece di 1.",
                ft.Colors.RED
            )
            return
        # --- FINE BLOCCO MODIFICATO ---

        doms_data = self.view.get_doms_data_from_view()
        if not doms_data:
            self.view.show_snackbar("Errore nel recuperare i dati DOMS.", ft.Colors.RED)
            return

        self.view.btn_salva_doms.disabled = True
        self.view.update_view()

        try:
            # --- INIZIO BLOCCO MODIFICATO ---
            # Usa una variabile per rendere esplicito che i DOMS sono per la settimana successiva
            prossima_settimana = self.current_week_num + 1

            for doms in doms_data:
                self.training_algo.aggiungi_doms(
                    prossima_settimana,
                    DOMSData(
                        muscolo=doms["muscolo"],
                        giorno=1,  # Convenzione: i DOMS si valutano a inizio settimana
                        settimana=prossima_settimana,
                        doms_value=doms["value"]
                    )
                )
            # --- FINE BLOCCO MODIFICATO ---

            tutti_i_muscoli_dello_split = self.crea_scheda_model.split_muscoli["Full Body"]
            volume_registrato_sett_1 = self.volume_history.get(1, {})
            volume_completo_sett_1 = {muscolo: volume_registrato_sett_1.get(muscolo, 0) for muscolo in
                                      tutti_i_muscoli_dello_split}

            aggiustamenti = {}
            esperienza = self.config_values["esperienza"]
            for muscolo in tutti_i_muscoli_dello_split:
                raccomandazione, motivo = self.training_algo.calcola_previsione_serie_settimana_2(muscolo, esperienza)
                aggiustamenti[muscolo] = raccomandazione
                if motivo:
                    messaggio_notifica = f"Info per {muscolo}: {motivo}"
                    if "mantenuto" not in motivo:
                        messaggio_notifica = f"Volume per {muscolo} mantenuto: {motivo}"
                    self.view.show_snackbar(messaggio_notifica, ft.Colors.ORANGE)

            volume_overrides = self._calcola_nuovo_volume(volume_completo_sett_1, aggiustamenti)
            self.training_week = self._genera_prossima_settimana(volume_overrides)

            self.view.show_snackbar("DOMS salvati! Generazione settimana 2...", ft.Colors.GREEN)
            self._passa_a_settimana_successiva()

        except Exception as ex:
            self.view.show_snackbar(f"Errore nel salvataggio DOMS: {ex}", ft.Colors.RED)
        finally:
            self.view.btn_salva_doms.disabled = False
            self.view.update_view()

    def prosegui_al_prossimo_giorno(self,
                                    e=None):  # MODIFICA: Aggiunto e=None per gestire la chiamata dall'evento del pulsante
        # Usa un ciclo per trovare il prossimo giorno di allenamento valido
        while True:
            self.current_day_index += 1

            # Se l'indice supera i giorni disponibili, la settimana è finita
            if self.current_day_index >= len(self.training_week.workout_days):
                self.handle_fine_settimana()
                return  # Esce dalla funzione

            giorno_corrente = self.training_week.workout_days[self.current_day_index]

            # Se il giorno ha esercizi, è un giorno valido. Interrompi il ciclo.
            if giorno_corrente.esercizi:
                break
            # Altrimenti, il ciclo continua e passa al giorno successivo

        # Una volta trovato un giorno valido, mostra la schermata di preparazione
        self.pending_workout_day = giorno_corrente
        muscoli_del_giorno = sorted(list({ex.muscolo_primario for ex in giorno_corrente.esercizi}))
        self.view.mostra_schermata_readiness(muscoli_del_giorno)

    def handle_readiness_submitted(self, e):
        """
        Chiamato quando l'utente invia i dati di prontezza.
        """
        if not self.pending_workout_day:
            self.view.show_snackbar("Errore: nessun giorno di allenamento in attesa.", self.view.colors['error'])
            return

        readiness_input_data = self.view.get_readiness_data()
        if not readiness_input_data:
            self.view.show_snackbar("Per favore, compila tutti i campi.", self.view.colors['warning'])
            return

        readiness_input = ReadinessInput(**readiness_input_data)
        adjustment = self.readiness_adjuster.get_adjustments(readiness_input, self.pending_workout_day)

        # Applica gli aggiustamenti a una copia del giorno
        adjusted_day = self._apply_adjustments_to_day(adjustment, self.pending_workout_day)

        # --- INIZIO BLOCCO MODIFICATO ---
        if not adjusted_day.esercizi:
            # È un giorno ROSSO (giorno di riposo)
            self.view.show_snackbar("Giorno di riposo consigliato. Prenditi una pausa.", self.view.colors['primary'])

            # Pulisci il container e mostra il messaggio di riposo con il pulsante per proseguire
            container = self.view.scheda_container
            container.content.controls.clear()
            container.content.controls.extend([
                ft.Text("GIORNO DI RIPOSO 🛌", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Divider(height=2, color=self.view.colors['border']),
                ft.Container(
                    content=ft.Text(
                        adjustment.user_message,
                        size=16,
                        color=self.view.colors['text_secondary'],
                        text_align=ft.TextAlign.CENTER
                    ),
                    padding=20,
                    border=ft.border.all(1, self.view.colors['error']),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.1, self.view.colors['error'])
                ),
                ft.Container(height=20),
                # Usa il pulsante specifico per questa situazione
                self.view.btn_prosegui_riposo
            ])
            self._activate_view('scheda')  # Mostra il container della scheda con il messaggio di riposo
        else:
            # È un giorno VERDE o GIALLO, visualizza l'allenamento come prima
            try:
                is_deload = self.current_week_num == 4
                self.view.visualizza_giorno(adjusted_day, self.current_week_num, is_deload)
                self._activate_view('scheda')
            except Exception as ex:
                print(f"--- ERRORE DURANTE LA VISUALIZZAZIONE DEL GIORNO: {ex} ---")
                traceback.print_exc()
                self.view.show_snackbar(f"Errore imprevisto nella visualizzazione: {ex}", self.view.colors['error'])

        self.pending_workout_day = None  # Resetta il giorno in attesa in entrambi i casi
        # --- FINE BLOCCO MODIFICATO ---

    def _apply_adjustments_to_day(self, adjustment: WorkoutAdjustment, day: WorkoutDay) -> WorkoutDay:
        """
        Applica le modifiche calcolate creando una copia dell'oggetto WorkoutDay
        per evitare effetti collaterali sullo stato originale.
        """
        # Lavora su una copia per non modificare l'oggetto originale nella training_week
        adjusted_day = deepcopy(day)
        adjusted_day.adjustment_message = adjustment.user_message

        # Se è un giorno "rosso", la copia viene trasformata in un giorno di riposo
        if adjustment.day_category == "RED":
            adjusted_day.esercizi = []
            adjusted_day.performance_log = {}
            return adjusted_day

        # Altrimenti, applica le modifiche alla copia
        # Aggiorna il log per riflettere il nuovo RIR e le riduzioni di serie
        for ex_id, log in adjusted_day.performance_log.items():
            # Applica riduzione serie
            if ex_id in adjustment.set_reductions:
                reduction_count = adjustment.set_reductions[ex_id]
                original_series = log.get("serie", 0)
                log["serie"] = max(1, original_series - reduction_count)

                # Rimuovi i rep range per le serie tagliate, controllando che la chiave esista
                if "reps" in log:
                    log["reps"] = log["reps"][:log["serie"]]

            # Aggiungi il RIR aggiustato nel log per mostrarlo nella card
            log["rir_adjustment"] = adjustment.global_rir_adjustment

        return adjusted_day

    def handle_fine_settimana(self):
        print(f"\n--- DEBUG: Chiamato handle_fine_settimana ---")  # <--- AGGIUNGI
        print(f"--- DEBUG: Stato attuale: current_week_num = {self.current_week_num}")  # <--- AGGIUNGI
        self._aggiorna_volume_history_effettivo()
        self.view.show_snackbar(f"Settimana {self.current_week_num} completata! Analisi...", ft.Colors.BLUE)
        try:
            if self.current_week_num == 1:
                print("--- DEBUG: Entrato nel blocco logica per settimana 1 ---")  # <--- AGGIUNGI
                self.training_algo.calcola_sfr_settimana_1()
                muscoli = list(self.volume_history[1].keys())
                self.view.visualizza_schermata_doms(muscoli)
            elif self.current_week_num == 2:
                print("--- DEBUG: Entrato nel blocco logica per settimana 2 ---")  # <--- AGGIUNGI
                self.training_algo.calcola_punti_performance_settimana_2()
                aggiustamenti = {m: self.training_algo.calcola_serie_settimana_3(m) for m in
                                 self.volume_history[2].keys()}
                volume_overrides = self._calcola_nuovo_volume(self.volume_history[2], aggiustamenti)
                self.training_week = self._genera_prossima_settimana(volume_overrides)
                self._passa_a_settimana_successiva()
            elif self.current_week_num == 3:
                print("--- DEBUG: Entrato nel blocco logica per settimana 3 ---")
                self.view.show_snackbar("Generazione della settimana di scarico...", ft.Colors.CYAN)
                volume_settimana_3 = self.volume_history.get(3, {})
                volume_scarico = {muscolo: max(2, round(volume / 2)) for muscolo, volume in volume_settimana_3.items()}
                self.training_week = self._genera_prossima_settimana(volume_scarico)
                self._passa_a_settimana_successiva()


            elif self.current_week_num >= 4:
                print("--- DEBUG: Entrato nel blocco logica per settimana >= 4 (REPORT) ---")

                # --- CORREZIONE FONDAMENTALE: Assicurati che questa riga sia presente ---
                self.training_algo.exercise_details_map = self.exercise_details_map

                self.training_algo.calcola_sfr_settimana_3()
                print("--- DEBUG: Chiamo genera_report_completo ---")
                report = self.training_algo.genera_report_completo()
                print(f"--- DEBUG: Report generato:\n---\n{report}\n---")
                self.view.visualizza_report_finale(report)
                print("--- DEBUG: Chiamato visualizza_report_finale ---")

        except Exception as ex:
            print(f"--- DEBUG: ERRORE in handle_fine_settimana: {ex} ---")  # <--- AGGIUNGI
            self.view.show_snackbar(f"Errore nell'analisi della settimana: {ex}", ft.Colors.RED)

    def _reset_ciclo(self):
        # CORREZIONE: Passiamo la mappa con i dettagli degli esercizi all'istanza
        # dell'algoritmo al momento della sua creazione.
        self.training_algo = TrainingAlgorithm(exercise_details_map=self.exercise_details_map)
        self.current_week_num = 1
        self.current_day_index = -1

    def _passa_a_settimana_successiva(self):
        self.current_week_num += 1
        self.current_day_index = -1
        self.prosegui_al_prossimo_giorno()

    def _get_scheda_params(self, volume_overrides=None):
        attrezzatura_value = self.config_values.get("attrezzatura", "palestra_completa")
        context = "Home Manubri" if attrezzatura_value == "home_manubri" else "Palestra Completa"
        params = {"context": context, "muscolo_target": self.config_values["muscolo_target"],
                  "giorni": int(self.config_values["frequenza"])}
        if volume_overrides:
            params["volume_overrides"] = volume_overrides
        return params

    def _genera_prossima_settimana(self, volume_overrides):
        esperienza = self.config_values["esperienza"]
        params = self._get_scheda_params(volume_overrides)
        params["settimana"] = self.current_week_num + 1
        if esperienza == "principiante":
            return self.crea_scheda_model.getSchedaFullBodyPrincipiante(**params)
        else:
            return self.crea_scheda_model.getSchedaFullBodyIntermedio(**params)

    def _aggiorna_volume_history_effettivo(self):
        """
        Calcola il volume EFFETTIVO della settimana corrente basandosi sui dati di performance salvati.
        Questo metodo è la fonte di verità per il volume realmente svolto.
        """
        volume_effettivo = defaultdict(int)

        # Recupera tutti i dati di performance salvati per la settimana corrente
        dati_performance_settimana = self.training_algo.performance_data.get(self.current_week_num, [])

        for performance in dati_performance_settimana:
            # La performance è un oggetto PerformanceData. Il numero di serie è la lunghezza della lista 'sets'.
            numero_serie = len(performance.sets)
            volume_effettivo[performance.muscolo_primario] += numero_serie

        # Assicuriamoci che anche i muscoli pianificati ma non allenati (volume 0) siano presenti.
        muscoli_pianificati = set()
        if self.training_week and self.training_week.workout_days:
            for day in self.training_week.workout_days:
                for esercizio in day.esercizi:
                    muscoli_pianificati.add(esercizio.muscolo_primario)

        # Crea il dizionario finale assicurando che tutti i muscoli pianificati abbiano una voce
        volume_finale = {muscolo: volume_effettivo.get(muscolo, 0) for muscolo in muscoli_pianificati}

        # Salva questo volume effettivo nella cronologia
        self.volume_history[self.current_week_num] = volume_finale

    def _calcola_nuovo_volume(self, volume_precedente: dict, aggiustamenti: dict) -> dict:
        nuovo_volume = {}
        print("\n--- CALCOLO NUOVO VOLUME SETTIMANA SUCCESSIVA ---")
        for muscolo, volume in volume_precedente.items():
            raccomandazione = aggiustamenti.get(muscolo, "mantieni")
            numeri = [int(n) for n in re.findall(r'([+-]?\d+)', raccomandazione)]
            print(f"\n- Muscolo: {muscolo.upper()}")
            print(f"  - Volume precedente: {volume} serie")
            print(f"  - Raccomandazione ricevuta: '{raccomandazione}'")
            variazione = 0
            if numeri:
                variazione = numeri[0]
                print(f"  - Azione: Variazione diretta -> {variazione:+}")
            else:
                print("  - Azione: Mantenere il volume")
            volume_calcolato = max(4, volume + variazione)
            nuovo_volume[muscolo] = volume_calcolato
            print(f"  ==> Nuovo Volume: {volume_calcolato} serie")
        print("-------------------------------------------------\n")
        return nuovo_volume

    def _activate_view(self, view_name: str):
        """Attiva la vista specificata e disattiva tutte le altre."""
        self.view.config_view.visible = (view_name == 'config')
        self.view.scheda_container.visible = (view_name == 'scheda')
        self.view.readiness_view.visible = (view_name == 'readiness')
        self.view.progress_view.visible = (view_name == 'progress')
        if hasattr(self, 'nutrition_view') and self.nutrition_view:
            self.view.nutrition_view.visible = (view_name == 'nutrition')

        # Aggiorna la pagina per mostrare i cambiamenti
        self.view.update_view()

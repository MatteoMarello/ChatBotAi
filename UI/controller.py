import flet as ft
from creascheda import Model as CreaSchedaModel
from adattaScheda import TrainingAlgorithm, PerformanceData, DOMSData
from model.trainingweek import TrainingWeek
import re

from UI.progress_view import *


class Controller:
    def __init__(self):
        self.view = None
        self.crea_scheda_model = CreaSchedaModel()
        self.training_algo = TrainingAlgorithm()
        self.training_week: TrainingWeek = None
        self.current_week_num = 0
        self.current_day_index = -1
        self.config_values = {}
        self.volume_history = {}
        # Aggiunta per la nuova vista
        self.progress_view = None

        # NUOVA FUNZIONE per gestire la navigazione

    def handle_navigation_change(self, e):
        selected_index = e.control.selected_index
        if selected_index == 0:
            # Mostra Allenamento, nascondi Progressi
            self.view.scheda_container.visible = True
            if self.progress_view:
                self.progress_view.visible = False
        elif selected_index == 1:
            # Mostra Progressi, nascondi Allenamento
            self.view.scheda_container.visible = False
            if self.progress_view:
                self.progress_view.visible = True
                self._prepare_and_show_progress()  # Prepara i dati e aggiorna la vista
        self.view.update_view()

    # NUOVA FUNZIONE per preparare i dati del grafico
    def _prepare_and_show_progress(self):
        # Definisci qui gli ID degli esercizi "fondamentali" che vuoi tracciare
        # Dovresti ottenere questi ID dal tuo DB o definirli staticamente
        # Esempio: {1: "Panca Piana", 4: "Squat", 7: "Stacco"}
        esercizi_fondamentali = {
            1: "Panca Piana", 2: "Panca Manubri",  # Esempio, da adattare
        }

        progress_data = {}
        # Itera sui dati di performance raccolti
        for settimana, performances in self.training_algo.performance_data.items():
            for perf in performances:
                if perf.esercizio_id in esercizi_fondamentali:
                    nome_esercizio = esercizi_fondamentali[perf.esercizio_id]
                    one_rm = perf.one_rm

                    if nome_esercizio not in progress_data:
                        progress_data[nome_esercizio] = []

                    # Aggiungi il punto dati (settimana, 1RM)
                    progress_data[nome_esercizio].append((settimana, one_rm))

        # Rimuovi duplicati e ordina
        for nome, data in progress_data.items():
            progress_data[nome] = sorted(list(set(data)))

        # Invia i dati alla vista dei progressi
        if self.progress_view:
            self.progress_view.update_view(progress_data)


    def set_view(self, view):
        """Imposta la view e carica le opzioni iniziali."""
        self.view = view
        self.carica_opzioni_iniziali()

    def carica_opzioni_iniziali(self):
        """Carica le opzioni iniziali per i dropdown."""
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
        """Aggiorna le opzioni di frequenza basate sull'esperienza."""
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
        """Gestisce la creazione della scheda iniziale."""
        self.config_values = self.view.get_config_values()

        # Validazione input
        if not all(self.config_values.values()):
            self.view.show_snackbar("Per favore, compila tutti i campi!", ft.Colors.RED)
            return

        # Disabilita il pulsante per evitare doppi click
        self.view.btn_crea_scheda.disabled = True
        self.view.update_view()

        try:
            esperienza = self.config_values["esperienza"]
            params = self._get_scheda_params()

            if esperienza == "principiante":
                self.training_week = self.crea_scheda_model.getSchedaFullBodyPrincipiante(**params)
            else:
                self.training_week = self.crea_scheda_model.getSchedaFullBodyIntermedio(**params)

            self._reset_ciclo()
            self.view.mostra_schermata_config(visible=False)
            self.view.show_snackbar("Scheda creata con successo!", ft.Colors.GREEN)
            self.prosegui_al_prossimo_giorno()

        except Exception as ex:
            self.view.show_snackbar(f"Errore nella creazione della scheda: {ex}", ft.Colors.RED)
            self.view.mostra_schermata_config(visible=True)
        finally:
            self.view.btn_crea_scheda.disabled = False
            self.view.update_view()

    def handle_salva_performance(self, e):
        """Gestisce il salvataggio delle performance del giorno."""
        performance_list_raw = self.view.get_performance_data_from_cards()

        if not performance_list_raw:
            self.view.show_snackbar("Nessuna performance inserita. Compila almeno una serie.", ft.Colors.ORANGE)
            return

        # Disabilita il pulsante per evitare doppi salvataggi
        self.view.btn_salva_performance.disabled = True
        self.view.update_view()

        try:
            for p_data in performance_list_raw:
                if not p_data["sets"]:
                    continue

                # Assicurati che p_data contenga "muscolo_primario"
                if "muscolo_primario" not in p_data:
                    self.view.show_snackbar(
                        f"Errore: muscolo primario mancante per esercizio ID {p_data['esercizio_id']}", ft.Colors.RED)
                    continue

                performance = PerformanceData(
                    esercizio_id=p_data["esercizio_id"],
                    giorno=p_data["giorno"],
                    settimana=self.current_week_num,
                    muscolo_primario=p_data["muscolo_primario"],  # <-- AGGIUNGI QUESTO
                    sets=p_data["sets"],
                    mmc=int(p_data["controls"]["mmc"].value),
                    pump=int(p_data["controls"]["pump"].value),
                    dolori_articolari=int(p_data["controls"]["dolori"].value)
                )

                self.training_algo.aggiungi_performance(self.current_week_num, performance)

            self.view.show_snackbar("Performance del giorno salvate!", ft.Colors.GREEN)
            self.prosegui_al_prossimo_giorno()

        except (ValueError, TypeError) as ex:
            self.view.show_snackbar(f"Dati non validi: {ex}", ft.Colors.RED)
        except Exception as ex:
            self.view.show_snackbar(f"Errore nel salvataggio: {ex}", ft.Colors.RED)
        finally:
            self.view.btn_salva_performance.disabled = False
            self.view.update_view()

    def handle_doms_salvati(self, e):
        """Gestisce il salvataggio dei DOMS e la generazione della settimana 2."""
        doms_data = self.view.get_doms_data_from_view()

        if not doms_data:
            self.view.show_snackbar("Errore nel recuperare i dati DOMS.", ft.Colors.RED)
            return

        self.view.btn_salva_doms.disabled = True
        self.view.update_view()

        try:
            for doms in doms_data:
                self.training_algo.aggiungi_doms(2, DOMSData(
                    muscolo=doms["muscolo"],
                    giorno=1,
                    settimana=2,
                    doms_value=doms["value"]
                ))

            # --- INIZIO MODIFICA ---

            # 1. Ottieni la lista completa dei muscoli per lo split corrente.
            #    Questo assicura che consideriamo tutti i muscoli, anche quelli con volume 0.
            tutti_i_muscoli_dello_split = self.crea_scheda_model.split_muscoli["Full Body"]

            # 2. Crea un dizionario di volumi completo per la settimana 1, inserendo 0 per i muscoli mancanti.
            volume_registrato_sett_1 = self.volume_history.get(1, {})
            volume_completo_sett_1 = {
                muscolo: volume_registrato_sett_1.get(muscolo, 0)
                for muscolo in tutti_i_muscoli_dello_split
            }

            # 3. Calcola gli aggiustamenti iterando sulla lista completa dei muscoli.
            aggiustamenti = {}
            esperienza = self.config_values["esperienza"]

            for muscolo in tutti_i_muscoli_dello_split:
                raccomandazione, motivo = self.training_algo.calcola_previsione_serie_settimana_2(muscolo, esperienza)
                aggiustamenti[muscolo] = raccomandazione

                # Se c'è un motivo, mostra una notifica all'utente
                if motivo:
                    # Rendi il messaggio più specifico per evitare confusione
                    messaggio_notifica = f"Info per {muscolo}: {motivo}"
                    if "mantenuto" not in motivo:
                        messaggio_notifica = f"Volume per {muscolo} mantenuto: {motivo}"
                    self.view.show_snackbar(messaggio_notifica, ft.colors.ORANGE)

            # 4. Calcola il nuovo volume usando il dizionario di volumi completo.
            volume_overrides = self._calcola_nuovo_volume(volume_completo_sett_1, aggiustamenti)

            # --- FINE MODIFICA ---

            self.training_week = self._genera_prossima_settimana(volume_overrides)

            self.view.show_snackbar("DOMS salvati! Generazione settimana 2...", ft.Colors.GREEN)
            self._passa_a_settimana_successiva()

        except Exception as ex:
            self.view.show_snackbar(f"Errore nel salvataggio DOMS: {ex}", ft.Colors.RED)
        finally:
            self.view.btn_salva_doms.disabled = False
            self.view.update_view()

    def prosegui_al_prossimo_giorno(self):
        """Procede al prossimo giorno di allenamento."""
        self.current_day_index += 1

        if self.current_day_index < len(self.training_week.workout_days):
            giorno_corrente = self.training_week.workout_days[self.current_day_index]
            self.view.visualizza_giorno(giorno_corrente, self.current_week_num)
        else:
            self.handle_fine_settimana()

    def handle_fine_settimana(self):
        """Gestisce la fine di una settimana di allenamento."""
        self.view.show_snackbar(f"Settimana {self.current_week_num} completata! Analisi...", ft.Colors.BLUE)

        try:
            if self.current_week_num == 1:
                # Fine settimana 1: mostra schermata DOMS
                self.training_algo.calcola_sfr_settimana_1()
                muscoli = list(self.volume_history[1].keys())
                self.view.visualizza_schermata_doms(muscoli)

            elif self.current_week_num == 2:
                # Fine settimana 2: calcola e genera settimana 3
                self.training_algo.calcola_punti_performance_settimana_2()
                aggiustamenti = {m: self.training_algo.calcola_serie_settimana_3(m)
                                 for m in self.volume_history[2].keys()}
                volume_overrides = self._calcola_nuovo_volume(self.volume_history[2], aggiustamenti)
                self.training_week = self._genera_prossima_settimana(volume_overrides)
                self._passa_a_settimana_successiva()

            elif self.current_week_num >= 3:
                # Fine ciclo: mostra report finale
                self.training_algo.calcola_sfr_settimana_3()
                report = self.training_algo.genera_report_completo()
                self.view.visualizza_report_finale(report)

        except Exception as ex:
            self.view.show_snackbar(f"Errore nell'analisi della settimana: {ex}", ft.Colors.RED)

    # --- Funzioni Helper ---
    def _reset_ciclo(self):
        """Resetta lo stato per un nuovo ciclo di allenamento."""
        self.training_algo = TrainingAlgorithm()
        self.current_week_num = 1
        self.current_day_index = -1
        self._registra_volume_settimanale()

    def _passa_a_settimana_successiva(self):
        """Incrementa il contatore della settimana e prepara il nuovo stato."""
        self.current_week_num += 1
        self.current_day_index = -1
        self._registra_volume_settimanale()
        self.prosegui_al_prossimo_giorno()

    def _get_scheda_params(self, volume_overrides=None):
        """Restituisce un dizionario di parametri per creare una scheda."""
        params = {
            "context": "Palestra Completa",
            "muscolo_target": self.config_values["muscolo_target"],
            "giorni": int(self.config_values["frequenza"]),
        }
        if volume_overrides:
            params["volume_overrides"] = volume_overrides
        return params

    # controller.py

    def _genera_prossima_settimana(self, volume_overrides):
        """Funzione helper per generare la scheda della settimana successiva."""
        esperienza = self.config_values["esperienza"]
        params = self._get_scheda_params(volume_overrides)

        # --- AGGIUNGI QUESTA RIGA ---
        # La settimana da generare è la successiva a quella corrente
        params["settimana"] = self.current_week_num + 1

        if esperienza == "principiante":
            return self.crea_scheda_model.getSchedaFullBodyPrincipiante(**params)
        else:
            return self.crea_scheda_model.getSchedaFullBodyIntermedio(**params)

    def _registra_volume_settimanale(self):
        """Registra il volume settimanale per ogni muscolo."""
        volume_corrente = {}

        for day in self.training_week.workout_days:
            for esercizio in day.esercizi:
                muscolo = esercizio.muscolo_primario
                serie = day.performance_log[esercizio.id]['serie']
                volume_corrente[muscolo] = volume_corrente.get(muscolo, 0) + serie

        self.volume_history[self.current_week_num] = volume_corrente

    # In controller.py

    def _calcola_nuovo_volume(self, volume_precedente: dict, aggiustamenti: dict) -> dict:
        """Calcola il nuovo volume basato sugli aggiustamenti."""
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
                # Prende il primo (e unico) numero trovato nella stringa
                variazione = numeri[0]
                print(f"  - Azione: Variazione diretta -> {variazione:+}")
            else:
                print("  - Azione: Mantenere il volume")

            volume_calcolato = max(4, volume + variazione)  # Minimo 4 serie
            nuovo_volume[muscolo] = volume_calcolato
            print(f"  ==> Nuovo Volume: {volume_calcolato} serie")

        print("-------------------------------------------------\n")
        return nuovo_volume

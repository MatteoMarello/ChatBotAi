import flet as ft
from creascheda import Model as CreaSchedaModel
from adattaScheda import TrainingAlgorithm, PerformanceData, DOMSData
from model.trainingweek import TrainingWeek
import random
import re


class Controller:
    def __init__(self):
        self.view = None  # Inizializzato a None
        self.crea_scheda_model = CreaSchedaModel()
        self.training_algo = TrainingAlgorithm()

        # Stato dell'applicazione
        self.training_week: TrainingWeek = None
        self.current_week_num = 0
        self.current_day_index = -1
        self.config_values = {}
        self.volume_history = {}  # {settimana: {muscolo: volume}}

    def set_view(self, view):
        """Collega la View al Controller"""
        self.view = view
        self.carica_opzioni_iniziali()  # Ora possiamo caricare le opzioni

    def carica_opzioni_iniziali(self):
        """Carica le opzioni dei dropdown all'avvio."""
        if self.view is None:
            raise ValueError("La View non è stata collegata al Controller")

        muscoli = self.crea_scheda_model.split_muscoli["Full Body"]
        self.view.dd_muscolo_target.options = [ft.dropdown.Option(m) for m in muscoli]

        # Frequenza (default per intermedio)
        self.aggiorna_opzioni_frequenza("intermedio")
        self.view.update_view()

    def aggiorna_opzioni_frequenza(self, esperienza: str):
        """Aggiorna le opzioni di frequenza in base all'esperienza."""
        if esperienza == "principiante":
            self.view.dd_frequenza.options = [ft.dropdown.Option("2"), ft.dropdown.Option("3")]
            self.view.dd_frequenza.value = "3"
        else:  # intermedio
            self.view.dd_frequenza.options = [ft.dropdown.Option("3"), ft.dropdown.Option("4")]
            self.view.dd_frequenza.value = "3"
        self.view.update_view()

    def handle_crea_scheda(self, e):
        """Gestisce la creazione della prima scheda di allenamento."""
        self.config_values = self.view.get_config_values()

        if not all(self.config_values.values()):
            self.view.show_snackbar("Per favore, compila tutti i campi!", ft.Colors.RED)
            return

        self.view.btn_crea_scheda.disabled = True
        self.view.update_view()

        try:
            self.training_week = self.crea_scheda_model.getSchedaFullBodyIntermedio(
                context="Palestra Completa",
                muscolo_target=self.config_values["muscolo_target"],
                giorni=int(self.config_values["frequenza"])
            )

            # Reset stato per un nuovo ciclo
            self.training_algo = TrainingAlgorithm()
            self.current_week_num = 1
            self.current_day_index = -1
            self._registra_volume_settimanale()

            self.view.mostra_schermata_config(visible=False)
            self.prosegui_al_prossimo_giorno()

        except Exception as ex:
            self.view.show_snackbar(f"Errore nella creazione: {ex}", ft.Colors.RED)

        self.view.btn_crea_scheda.disabled = False
        self.view.update_view()

    def handle_salva_performance(self, e):
        """Salva i dati di performance e passa al giorno/settimana successiva."""
        performance_list = self.view.get_performance_data_from_cards()

        try:
            for p_data in performance_list:
                controls = p_data["controls"]
                performance = PerformanceData(
                    esercizio_id=p_data["esercizio_id"],
                    giorno=p_data["giorno"],
                    settimana=self.current_week_num,
                    carico=float(controls["carico"].value),
                    ripetizioni=int(controls["ripetizioni"].value),
                    mmc=int(controls["mmc"].value),
                    pump=int(controls["pump"].value),
                    dolori_articolari=int(controls["dolori"].value)
                )
                self.training_algo.aggiungi_performance(self.current_week_num, performance)

        except (ValueError, TypeError):
            self.view.show_snackbar("Dati non validi. Compila tutti i campi numerici correttamente.", ft.Colors.RED)
            return

        self.view.show_snackbar(f"Performance del giorno salvate!", ft.Colors.GREEN)
        self.prosegui_al_prossimo_giorno()

    def prosegui_al_prossimo_giorno(self):
        """Avanza al giorno successivo o gestisce la fine della settimana."""
        self.current_day_index += 1

        if self.current_day_index < len(self.training_week.workout_days):
            giorno_corrente = self.training_week.workout_days[self.current_day_index]
            self.view.visualizza_giorno(giorno_corrente, self.current_week_num)
        else:
            self.handle_fine_settimana()

    def handle_fine_settimana(self):
        """Gestisce la logica di fine settimana: analizza i dati e prepara la settimana successiva."""
        self.view.show_snackbar(f"Settimana {self.current_week_num} completata! Analisi in corso...", ft.Colors.BLUE)

        if self.current_week_num == 1:
            # --- Logica per generare Settimana 2 ---
            self.training_algo.calcola_sfr_settimana_1()

            # Simula DOMS (poiché non c'è input UI)
            for muscolo in self.crea_scheda_model.split_muscoli["Full Body"]:
                self.training_algo.aggiungi_doms(2, DOMSData(muscolo=muscolo, giorno=1, settimana=2,
                                                             doms_value=random.randint(1, 2)))

            aggiustamenti = {}
            for muscolo in self.volume_history[1].keys():
                aggiustamenti[muscolo] = self.training_algo.calcola_previsione_serie_settimana_2(muscolo)

            volume_overrides = self._calcola_nuovo_volume(self.volume_history[1], aggiustamenti)

            self.training_week = self.crea_scheda_model.getSchedaFullBodyIntermedio(
                context="Palestra Completa",
                muscolo_target=self.config_values["muscolo_target"],
                giorni=int(self.config_values["frequenza"]),
                volume_overrides=volume_overrides
            )
            self.current_week_num = 2

        elif self.current_week_num == 2:
            # --- Logica per generare Settimana 3 ---
            self.training_algo.calcola_punti_performance_settimana_2()

            aggiustamenti = {}
            for muscolo in self.volume_history[2].keys():
                aggiustamenti[muscolo] = self.training_algo.calcola_serie_settimana_3(muscolo)

            volume_overrides = self._calcola_nuovo_volume(self.volume_history[2], aggiustamenti)

            self.training_week = self.crea_scheda_model.getSchedaFullBodyIntermedio(
                context="Palestra Completa",
                muscolo_target=self.config_values["muscolo_target"],
                giorni=int(self.config_values["frequenza"]),
                volume_overrides=volume_overrides
            )
            self.current_week_num = 3

        elif self.current_week_num == 3:
            # --- Fine del ciclo ---
            self.training_algo.calcola_sfr_settimana_3()
            report = self.training_algo.genera_report_completo()
            self.view.visualizza_report_finale(report)
            return

        # Prepara per la prossima settimana
        self.current_day_index = -1
        self._registra_volume_settimanale()
        self.prosegui_al_prossimo_giorno()

    def _registra_volume_settimanale(self):
        """Calcola e salva il volume totale (n. di serie) per ogni muscolo nella settimana corrente."""
        volume_corrente = {}
        for day in self.training_week.workout_days:
            for esercizio in day.esercizi:
                muscolo = esercizio.muscolo_primario
                serie = day.performance_log[esercizio.id]['serie']
                volume_corrente[muscolo] = volume_corrente.get(muscolo, 0) + serie
        self.volume_history[self.current_week_num] = volume_corrente

    def _calcola_nuovo_volume(self, volume_precedente: dict, aggiustamenti: dict) -> dict:
        """
        Calcola il nuovo target di volume per ogni muscolo basandosi sulle raccomandazioni testuali.
        Esempio: "+2 serie", "-1 serie", "mantieni", "+2/4 serie"
        """
        nuovo_volume = {}
        for muscolo, volume in volume_precedente.items():
            raccomandazione = aggiustamenti.get(muscolo, "mantieni")

            # Trova tutti i numeri (positivi o negativi) nella stringa
            numeri = [int(n) for n in re.findall(r'([+-]?\d+)', raccomandazione)]

            if "mantieni" in raccomandazione or not numeri:
                variazione = 0
            elif "/" in raccomandazione:  # Es: "+2/4 serie"
                variazione = random.choice(numeri)
            else:  # Es: "+2 serie"
                variazione = numeri[0]

            nuovo_volume[muscolo] = max(4, volume + variazione)  # Minimo 4 serie per muscolo

        return nuovo_volume

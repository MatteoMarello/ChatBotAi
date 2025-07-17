import flet as ft
from model.esercizio import Esercizio
from model.workoutday import WorkoutDay
from model.trainingweek import TrainingWeek


class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller

        # --- Elementi UI ---
        self.dd_esperienza = ft.Dropdown(
            label="Esperienza",
            options=[
                ft.dropdown.Option("principiante"),
                ft.dropdown.Option("intermedio"),
            ],
            value="intermedio",
            on_change=self._aggiorna_frequenza
        )
        self.dd_obiettivo = ft.Dropdown(
            label="Obiettivo (non usato attualmente)",
            options=[ft.dropdown.Option("ipertrofia"), ft.dropdown.Option("dimagrimento")],
            value="ipertrofia",
            disabled=True
        )
        self.dd_muscolo_target = ft.Dropdown(label="Muscolo Target")  # Opzioni caricate dal controller
        self.dd_frequenza = ft.Dropdown(label="Frequenza Settimanale")  # Opzioni dipendenti dall'esperienza
        self.btn_crea_scheda = ft.ElevatedButton(text="Crea Scheda", on_click=self.controller.handle_crea_scheda)
        self.btn_salva_performance = ft.ElevatedButton(
            "Salva Performance e Prosegui",
            on_click=self.controller.handle_salva_performance,
            icon=ft.Icons.SAVE
        )

        # Contenitore per la configurazione
        self.config_view = ft.Column(
            [
                ft.Text("Configura il tuo Allenamento", size=24, weight=ft.FontWeight.BOLD),
                self.dd_esperienza,
                self.dd_obiettivo,
                self.dd_muscolo_target,
                self.dd_frequenza,
                ft.Container(height=20),
                self.btn_crea_scheda,
            ],
            width=400,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        # Contenitore per la scheda di allenamento
        self.scheda_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        self.main_view = ft.Column([self.config_view, self.scheda_container], expand=True)

        # Carica le opzioni iniziali
        # Collega la View al Controller DOPO aver inizializzato tutti i componenti
        self.controller.set_view(self)

    def update_view(self):
        """Aggiorna la pagina"""
        self.page.update()


    def build(self):
        """Costruisce l'intera UI."""
        return self.main_view

    def _aggiorna_frequenza(self, e):
        """Informa il controller di aggiornare le opzioni di frequenza."""
        self.controller.aggiorna_opzioni_frequenza(self.dd_esperienza.value)

    def get_config_values(self):
        """Restituisce i valori selezionati nella form di configurazione."""
        return {
            "esperienza": self.dd_esperienza.value,
            "muscolo_target": self.dd_muscolo_target.value,
            "frequenza": self.dd_frequenza.value
        }

    def crea_card_esercizio(self, esercizio: Esercizio, log: dict, settimana: int, giorno: int):
        """Crea una Card Flet per un singolo esercizio con i campi di input."""
        txt_carico = ft.TextField(label="Carico (kg)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        txt_ripetizioni = ft.TextField(label="Reps Fatte", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        radio_mmc = ft.RadioGroup(content=ft.Row(
            [ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")]),
                                  value="2")
        radio_pump = ft.RadioGroup(content=ft.Row(
            [ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")]),
                                   value="2")
        radio_dolori = ft.RadioGroup(content=ft.Row(
            [ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")]),
                                     value="1")

        return ft.Card(
            content=ft.Container(
                padding=15,
                content=ft.Column([
                    ft.Text(f"{esercizio.nome.upper()}", weight=ft.FontWeight.BOLD, size=16),
                    ft.Text(f"Target: {log.get('serie')} serie x {log.get('note', '')}"),
                    ft.Divider(),
                    ft.Row([txt_carico, txt_ripetizioni], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([ft.Text("Connessione Mente-Muscolo:"), radio_mmc]),
                    ft.Row([ft.Text("Pump Muscolare:"), radio_pump]),
                    ft.Row([ft.Text("Dolori Articolari:"), radio_dolori]),
                ])
            ),
            data={
                "esercizio_id": esercizio.id, "settimana": settimana, "giorno": giorno,
                "controls": {"carico": txt_carico, "ripetizioni": txt_ripetizioni, "mmc": radio_mmc, "pump": radio_pump,
                             "dolori": radio_dolori}
            }
        )

    def get_performance_data_from_cards(self):
        """Estrae i dati di performance inseriti dall'utente nelle card."""
        performance_list = []
        for card in self.scheda_container.controls:
            if isinstance(card, ft.Card):
                performance_list.append(card.data)
        return performance_list

    def visualizza_giorno(self, giorno_allenamento: WorkoutDay, settimana_num: int):
        """Mostra gli esercizi per il giorno specificato."""
        self.scheda_container.controls.clear()

        titolo = ft.Text(
            f"SETTIMANA {settimana_num} - GIORNO {giorno_allenamento.id_giorno} ({giorno_allenamento.split_type})",
            size=24, weight=ft.FontWeight.BOLD)
        self.scheda_container.controls.append(titolo)

        if not giorno_allenamento.esercizi:
            self.scheda_container.controls.append(ft.Text("Oggi è giorno di riposo! 😴", size=18))
        else:
            for esercizio in giorno_allenamento.esercizi:
                log_esercizio = giorno_allenamento.performance_log.get(esercizio.id, {})
                card = self.crea_card_esercizio(esercizio, log_esercizio, settimana_num, giorno_allenamento.id_giorno)
                self.scheda_container.controls.append(card)

            self.scheda_container.controls.append(self.btn_salva_performance)

        self.update_view()

    def visualizza_report_finale(self, report: str):
        """Mostra il report di fine mesociclo."""
        self.scheda_container.controls.clear()
        self.scheda_container.controls.append(ft.Text("Fine del Mesociclo!", size=24, weight=ft.FontWeight.BOLD))
        self.scheda_container.controls.append(ft.Text("Ecco il tuo report e le raccomandazioni:", size=16))

        report_text = ft.Text(report, font_family="monospace")
        container = ft.Container(content=report_text, padding=10, border=ft.border.all(1, ft.Colors.GREY),
                                 border_radius=5)

        self.scheda_container.controls.append(container)
        self.scheda_container.controls.append(ft.Text("Puoi ora configurare un nuovo ciclo di allenamento.", size=16))

        self.config_view.visible = True
        self.update_view()

    def mostra_schermata_config(self, visible=True):
        """Mostra o nasconde la schermata di configurazione."""
        self.config_view.visible = visible
        if not visible:
            self.scheda_container.controls.clear()
        self.update_view()

    def show_snackbar(self, message: str, color: str = ft.Colors.GREEN):
        """Mostra una snackbar."""
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()

    def update_view(self):
        """Aggiorna la pagina."""
        self.page.update()

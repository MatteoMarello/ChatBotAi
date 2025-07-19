import flet as ft
from model.esercizio import Esercizio
from model.workoutday import WorkoutDay
from typing import List, Dict, Any
# All'inizio di view.py
from UI.progress_view import *


class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller

        # Configurazione pagina
        self.page.title = "TrainAI - Scheda Allenamento"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0f172a"
        self.page.padding = 0

        # Colori e stili
        self.colors = {
            'primary': '#3b82f6',
            'surface': '#1e293b',
            'surface_light': '#334155',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#475569',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        self.button_style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=self.colors['primary'],
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(vertical=12, horizontal=20)
        )

        # Componenti UI
        self._create_components()

        # NUOVO: istanza della vista dei progressi
        self.progress_view = ProgressView()
        self.controller.progress_view = self.progress_view

        # Layout
        self._create_layout()

        # Collegamento controller
        self.controller.set_view(self)

    def _create_components(self):
        """Crea i componenti UI principali."""
        # Dropdown esperienza
        self.dd_esperienza = ft.Dropdown(
            label="Esperienza",
            options=[
                ft.dropdown.Option("principiante"),
                ft.dropdown.Option("intermedio"),
            ],
            value="intermedio",
            on_change=self._aggiorna_frequenza,
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8
        )

        # Dropdown muscolo target
        self.dd_muscolo_target = ft.Dropdown(
            label="Muscolo Target",
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8
        )

        # Dropdown frequenza
        self.dd_frequenza = ft.Dropdown(
            label="Frequenza Settimanale",
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8
        )

        # Pulsanti
        self.btn_crea_scheda = ft.ElevatedButton(
            text="Crea Scheda",
            on_click=self.controller.handle_crea_scheda,
            style=self.button_style,
            icon=ft.Icons.CREATE
        )

        self.btn_salva_performance = ft.ElevatedButton(
            text="Salva e Prosegui",
            on_click=self.controller.handle_salva_performance,
            style=self.button_style,
            icon=ft.Icons.SAVE
        )

        self.btn_salva_doms = ft.ElevatedButton(
            text="Salva DOMS e Genera Sett. 2",
            on_click=self.controller.handle_doms_salvati,
            style=self.button_style,
            icon=ft.Icons.ARROW_FORWARD
        )

    def _create_layout(self):
        """Crea il layout dell'applicazione."""
        # NUOVO: NavigationDrawer
        self.drawer = ft.NavigationDrawer(
            on_change=self.controller.handle_navigation_change,
            controls=[
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.FITNESS_CENTER_OUTLINED,
                    label="Allenamento",
                    selected_icon=ft.Icons.FITNESS_CENTER
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.SHOW_CHART_OUTLINED,
                    label="Progressi",
                    selected_icon=ft.Icons.SHOW_CHART
                ),
            ]
        )

        # NUOVO: AppBar
        self.page.appbar = ft.AppBar(
            title=ft.Text("TrainAI", color=ft.Colors.WHITE),
            bgcolor=self.colors['surface'],
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: self.page.open(self.drawer),
            ),
        )

        # La Vista di configurazione
        self.config_view = ft.Container(
            content=ft.Column([
                ft.Text("Configura il tuo Mesociclo",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Text("Imposta i parametri per la scheda personalizzata",
                        color=self.colors['text_secondary']),
                ft.Container(height=20),
                self.dd_esperienza,
                self.dd_muscolo_target,
                self.dd_frequenza,
                ft.Container(height=20),
                self.btn_crea_scheda
            ], spacing=12),
            padding=20,
            visible=True
        )

        # Il container della scheda - IMPORTANTE: deve avere scroll per funzionare
        self.scheda_container = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,  # Abilita lo scroll
                expand=True
            ),
            visible=False,  # Nascosto inizialmente
            expand=True,
            padding=20
        )

        # Contenuto principale - IMPORTANTE: deve essere scrollabile
        main_content = ft.Container(
            content=ft.Column(
                [
                    self.config_view,
                    self.scheda_container,
                    self.progress_view  # Aggiunta la vista progressi
                ],
                scroll=ft.ScrollMode.AUTO,  # Abilita lo scroll per l'intera colonna
                expand=True
            ),
            expand=True
        )

        # Aggiungi il contenuto alla pagina
        self.page.add(main_content)

    def crea_card_esercizio(self, esercizio: Esercizio, log: dict, settimana: int, giorno: int):
        """Crea una card per l'esercizio."""
        rir_map = {1: 4, 2: 3, 3: 2}
        rir_obiettivo = rir_map.get(settimana, "N/D")

        # Header esercizio
        header_row = ft.Row([
            ft.Icon(ft.Icons.FITNESS_CENTER, color=self.colors['primary'], size=20),
            ft.Text(esercizio.nome,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['text_primary'],
                    expand=True),
            ft.Container(
                content=ft.Text(f"RIR: {rir_obiettivo}",
                                size=12,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                bgcolor=self.colors['primary'],
                border_radius=15
            )
        ])

        # Serie inputs
        serie_inputs = []
        num_serie = log.get('serie', 1)
        rep_ranges = log.get('reps', [''])

        for i in range(num_serie):
            rep_target = rep_ranges[i] if i < len(rep_ranges) else (rep_ranges[-1] if rep_ranges else '')

            carico_field = ft.TextField(
                label="Carico (kg)",
                width=120,
                value="5",  # Aggiunto valore predefinito
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor=self.colors['surface_light'],
                border_color=self.colors['border'],
                color=self.colors['text_primary'],
                border_radius=8
            )

            reps_field = ft.TextField(
                label="Reps",
                width=80,
                value="5",  # Aggiunto valore predefinito
                keyboard_type=ft.KeyboardType.NUMBER,
                bgcolor=self.colors['surface_light'],
                border_color=self.colors['border'],
                color=self.colors['text_primary'],
                border_radius=8
            )


            # Modifica qui: mostra sempre il range target in modo più visibile
            target_text = f"Target: {rep_target}" if rep_target else "Target: N/D"

            serie_row = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"Serie {i + 1}",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors['text_primary']),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(target_text,
                                            size=12,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.BOLD),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            bgcolor=self.colors['warning'],
                            border_radius=10
                        )
                    ]),
                    ft.Row([
                        carico_field,
                        ft.Container(width=10),
                        reps_field
                    ])
                ], spacing=8),
                padding=ft.padding.symmetric(vertical=8, horizontal=12),
                bgcolor=self.colors['surface_light'],
                border_radius=8,
                border=ft.border.all(1, self.colors['border'])
            )

            # Salva i dati nella row per il recupero
            serie_row.data = {
                "carico": carico_field,
                "reps": reps_field,
                "rep_range": rep_target
            }

            serie_inputs.append(serie_row)

        # Feedback controls
        def create_radio_group(default_value="2"):
            return ft.RadioGroup(
                content=ft.Row([
                    ft.Radio(value="1", label="1"),
                    ft.Radio(value="2", label="2"),
                    ft.Radio(value="3", label="3")
                ]),
                value=default_value
            )

        mmc_radio = create_radio_group("3")
        pump_radio = create_radio_group("3")
        dolori_radio = create_radio_group("1")

        feedback_section = ft.Container(
            content=ft.Column([
                ft.Text("Feedback Allenamento",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Row([
                    ft.Text("Connessione Mente-Muscolo",
                            color=self.colors['text_primary'],
                            expand=True),
                    mmc_radio
                ]),
                ft.Row([
                    ft.Text("Pump Muscolare",
                            color=self.colors['text_primary'],
                            expand=True),
                    pump_radio
                ]),
                ft.Row([
                    ft.Text("Dolori Articolari",
                            color=self.colors['text_primary'],
                            expand=True),
                    dolori_radio
                ])
            ], spacing=8),
            padding=16,
            bgcolor=self.colors['surface_light'],
            border_radius=8,
            border=ft.border.all(1, self.colors['border'])
        )

        # Controlli per il controller
        exercise_controls = {
            "serie_rows": serie_inputs,
            "mmc": mmc_radio,
            "pump": pump_radio,
            "dolori": dolori_radio
        }

        # Card container
        card = ft.Container(
            content=ft.Column([
                header_row,
                ft.Divider(height=1, color=self.colors['border']),
                ft.Column(serie_inputs, spacing=8),
                ft.Divider(height=1, color=self.colors['border']),
                feedback_section
            ], spacing=12),
            padding=20,
            bgcolor=self.colors['surface'],
            border_radius=12,
            border=ft.border.all(1, self.colors['border']),
            margin=ft.margin.only(bottom=16)
        )

        # Salva i dati nella card - MODIFICA: aggiungi muscolo_primario
        card.data = {
            "esercizio_id": esercizio.id,
            "muscolo_primario": esercizio.muscolo_primario,  # <-- AGGIUNTA
            "settimana": settimana,
            "giorno": giorno,
            "controls": exercise_controls
        }

        return card

    def get_performance_data_from_cards(self):
        """Estrae i dati performance dalle card."""
        performance_list = []

        # Ottieni i controlli dalla colonna interna del container
        controls = self.scheda_container.content.controls if hasattr(self.scheda_container.content, 'controls') else []

        for card in controls:
            if isinstance(card, ft.Container) and hasattr(card, 'data') and card.data and "controls" in card.data:
                sets_data = []
                serie_rows = card.data["controls"]["serie_rows"]

                for row in serie_rows:
                    if hasattr(row, 'data') and row.data:
                        carico_field = row.data["carico"]
                        reps_field = row.data["reps"]
                        rep_range = row.data["rep_range"]

                        if carico_field.value and reps_field.value:
                            try:
                                sets_data.append((
                                    float(carico_field.value),
                                    int(reps_field.value),
                                    rep_range
                                ))
                            except (ValueError, TypeError):
                                continue

                if sets_data:
                    # MODIFICA: aggiungi muscolo_primario nei dati estratti
                    performance_data = {
                        "esercizio_id": card.data["esercizio_id"],
                        "muscolo_primario": card.data["muscolo_primario"],  # <-- AGGIUNTA
                        "settimana": card.data["settimana"],
                        "giorno": card.data["giorno"],
                        "sets": sets_data,
                        "controls": card.data["controls"]
                    }
                    performance_list.append(performance_data)

        return performance_list

    def visualizza_giorno(self, giorno_allenamento: WorkoutDay, settimana_num: int):
        """Visualizza il giorno di allenamento."""
        # Pulisci i controlli della colonna interna
        self.scheda_container.content.controls.clear()

        # Titolo
        title = ft.Text(
            f"SETTIMANA {settimana_num} - GIORNO {giorno_allenamento.id_giorno}",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self.colors['text_primary']
        )

        subtitle = ft.Text(
            f"Split: {giorno_allenamento.split_type}",
            size=16,
            color=self.colors['text_secondary']
        )

        self.scheda_container.content.controls.extend([title, subtitle])

        if not giorno_allenamento.esercizi:
            # Giorno di riposo
            rest_card = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HOTEL, size=40, color=self.colors['text_secondary']),
                    ft.Text("Giorno di Riposo",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors['text_primary']),
                    ft.Text("Rilassati e recupera!",
                            color=self.colors['text_secondary'])
                ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=self.colors['surface'],
                border_radius=12,
                alignment=ft.alignment.center,
                margin=ft.margin.only(bottom=16)
            )
            self.scheda_container.content.controls.append(rest_card)
        else:
            # Esercizi
            for esercizio in giorno_allenamento.esercizi:
                log_esercizio = giorno_allenamento.performance_log.get(esercizio.id, {})
                card = self.crea_card_esercizio(esercizio, log_esercizio, settimana_num, giorno_allenamento.id_giorno)
                self.scheda_container.content.controls.append(card)

            # Pulsante salva
            save_button_container = ft.Container(
                content=self.btn_salva_performance,
                padding=ft.padding.symmetric(vertical=20),
                alignment=ft.alignment.center
            )
            self.scheda_container.content.controls.append(save_button_container)

        # Mostra la scheda e nascondi la config
        self.config_view.visible = False
        self.scheda_container.visible = True
        self.progress_view.visible = False
        self.update_view()

    def visualizza_schermata_doms(self, muscoli: List[str]):
        """Visualizza la schermata per i DOMS."""
        self.scheda_container.content.controls.clear()

        # Titolo
        title = ft.Text(
            "Valuta i tuoi DOMS",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self.colors['text_primary']
        )

        description = ft.Text(
            "Valuta l'indolenzimento medio percepito (1=Nessuno, 2=Moderato, 3=Elevato)",
            color=self.colors['text_secondary']
        )

        self.scheda_container.content.controls.extend([title, description])

        # Input DOMS
        doms_inputs = []
        for muscolo in muscoli:
            radio_group = ft.RadioGroup(
                content=ft.Row([
                    ft.Radio(value="1", label="1"),
                    ft.Radio(value="2", label="2"),
                    ft.Radio(value="3", label="3")
                ]),
                value="1"
            )

            row = ft.Container(
                content=ft.Row([
                    ft.Text(muscolo.upper(),
                            size=16,
                            color=self.colors['text_primary'],
                            expand=True),
                    radio_group
                ]),
                padding=16,
                bgcolor=self.colors['surface'],
                border_radius=8,
                border=ft.border.all(1, self.colors['border']),
                margin=ft.margin.only(bottom=8)
            )

            doms_inputs.append({"muscolo": muscolo, "control": radio_group})
            self.scheda_container.content.controls.append(row)

        # Salva nella pagina per il recupero
        self.page.data = {"doms_inputs": doms_inputs}

        # Pulsante salva
        save_button_container = ft.Container(
            content=self.btn_salva_doms,
            padding=ft.padding.symmetric(vertical=20),
            alignment=ft.alignment.center
        )
        self.scheda_container.content.controls.append(save_button_container)

        self.config_view.visible = False
        self.scheda_container.visible = True
        self.progress_view.visible = False
        self.update_view()

    def get_doms_data_from_view(self) -> List[dict]:
        """Estrae i dati DOMS dalla view."""
        doms_values = []
        if hasattr(self.page, 'data') and self.page.data and "doms_inputs" in self.page.data:
            for item in self.page.data["doms_inputs"]:
                doms_values.append({
                    "muscolo": item["muscolo"],
                    "value": int(item["control"].value)
                })
        return doms_values

    def visualizza_report_finale(self, report: str):
        """Visualizza il report finale."""
        self.scheda_container.content.controls.clear()

        # Titolo
        title = ft.Text(
            "Fine del Mesociclo!",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=self.colors['text_primary']
        )

        # Report
        report_container = ft.Container(
            content=ft.Text(report,
                            color=self.colors['text_primary'],
                            size=14,
                            selectable=True),
            padding=20,
            bgcolor=self.colors['surface'],
            border_radius=8,
            border=ft.border.all(1, self.colors['border']),
            margin=ft.margin.only(bottom=16)
        )

        self.scheda_container.content.controls.extend([
            title,
            ft.Text("Ecco il tuo report:", color=self.colors['text_secondary']),
            report_container
        ])

        self.config_view.visible = True
        self.scheda_container.visible = True
        self.progress_view.visible = False
        self.update_view()

    def get_config_values(self):
        """Restituisce i valori di configurazione."""
        return {
            "esperienza": self.dd_esperienza.value,
            "muscolo_target": self.dd_muscolo_target.value,
            "frequenza": self.dd_frequenza.value
        }

    def mostra_schermata_config(self, visible=True):
        """Mostra/nasconde la schermata di configurazione."""
        self.config_view.visible = visible
        if not visible:
            self.scheda_container.content.controls.clear()
        self.update_view()

    def show_snackbar(self, message: str, color: str = None):
        """Mostra una notifica."""
        if color is None:
            color = self.colors['success']

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()

    def update_view(self):
        """Aggiorna la view."""
        self.page.update()

    def build(self):
        """Costruisce l'interfaccia (metodo legacy - layout già creato nel costruttore)."""
        # Il layout è già stato creato nel costruttore __init__
        # Questo metodo è mantenuto per compatibilità ma non è necessario
        return None

    def _aggiorna_frequenza(self, e):
        """Aggiorna le opzioni di frequenza."""
        self.controller.aggiorna_opzioni_frequenza(self.dd_esperienza.value)

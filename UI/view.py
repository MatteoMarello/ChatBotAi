import flet as ft
from model.esercizio import Esercizio
from model.workoutday import WorkoutDay
from typing import List, Dict, Any
from UI.progress_view import *
from UI.nutrition_view import *


class View:
    def __init__(self, page: ft.Page, controller):
        """Inizializza la vista principale dell'applicazione."""
        self.page = page
        self.controller = controller

        # Configurazione iniziale della pagina
        self._setup_page_config()

        # Inizializzazione delle viste
        self._init_views()

        # Creazione dei componenti UI
        self._create_components()

        # Setup del layout
        self._create_layout()

        # Collegamento con il controller
        self.controller.set_view(self)

    def _setup_page_config(self):
        """Configura le proprietà base della pagina."""
        self.page.title = "Magno - Scheda Allenamento"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0f172a"
        self.page.padding = 0
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def _init_views(self):
        """Inizializza le diverse viste dell'applicazione."""
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

        self.nutrition_view = NutritionView(controller=self.controller)
        self.progress_view = ProgressView()
        self.controller.progress_view = self.progress_view
        self.controller.nutrition_view = self.nutrition_view

    def _create_components(self):
        """Crea tutti i componenti UI principali."""
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
            border_radius=8,
            width=300
        )

        self.dd_attrezzatura = ft.Dropdown(
            label="Attrezzatura Disponibile",
            options=[
                ft.dropdown.Option("palestra_completa", "Palestra Completa"),
                ft.dropdown.Option("home_manubri", "Home Gym"),
            ],
            value="palestra_completa",
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8,
            width=300
        )

        # Dropdown muscolo target
        self.dd_muscolo_target = ft.Dropdown(
            label="Muscolo Target",
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8,
            width=300
        )

        # Dropdown frequenza
        self.dd_frequenza = ft.Dropdown(
            label="Frequenza Settimanale",
            bgcolor=self.colors['surface_light'],
            border_color=self.colors['border'],
            color=self.colors['text_primary'],
            border_radius=8,
            width=300
        )

        # Pulsanti principali
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

        self.btn_prosegui_riposo = ft.ElevatedButton(
            text="Prosegui",
            on_click=self.controller.prosegui_al_prossimo_giorno,
            style=self.button_style,
            icon=ft.Icons.ARROW_FORWARD
        )

    def _create_layout(self):
        """Crea il layout principale dell'applicazione."""
        # Navigation Drawer
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
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.RESTAURANT_OUTLINED,
                    label="Nutrizione",
                    selected_icon=ft.Icons.RESTAURANT
                ),
            ]
        )

        # AppBar
        self.page.appbar = ft.AppBar(
            title=ft.Row([
                ft.Image(
                    src="assets/images/logomagno.png",
                    width=32,
                    height=32,
                    fit=ft.ImageFit.CONTAIN
                ),
                ft.Container(width=10),
                ft.Text("Magno Virtual Coach",
                        color=ft.Colors.WHITE,
                        size=20,
                        weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=self.colors['surface'],
            leading=ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: self.page.open(self.drawer),
            ),
            center_title=True
        )

        # Vista di configurazione
        self.config_view = ft.Container(
            content=ft.Column([
                ft.Text("Configura il tuo Mesociclo",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Text("Imposta i parametri per la scheda personalizzata",
                        color=self.colors['text_secondary']),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        self.dd_esperienza,
                        self.dd_attrezzatura,
                        self.dd_muscolo_target,
                        self.dd_frequenza,
                        ft.Container(height=20),
                        self.btn_crea_scheda
                    ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=400,
                    padding=20,
                    bgcolor=self.colors['surface'],
                    border_radius=12
                )
            ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            visible=True
        )

        # Container per la scheda
        self.scheda_container = ft.Container(
            content=ft.Column(
                controls=[],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            ),
            visible=False,
            expand=True,
            padding=20,
            width=800
        )

        self.readiness_view = ft.Container(
            content=ft.Column(
                controls=[],  # Verrà popolato dinamicamente
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            visible=False  # Inizialmente nascosto
        )

        main_content = ft.Container(
            content=ft.Stack(
                [
                    self.config_view,
                    self.readiness_view, # Aggiunto qui
                    self.scheda_container,
                    self.progress_view,
                    self.nutrition_view
                ]
            ),
            expand=True,
            alignment=ft.alignment.center
        )


        # Nascondi viste non iniziali
        self.progress_view.visible = False
        self.nutrition_view.visible = False

        # Aggiungi il contenuto alla pagina
        self.page.add(main_content)

    def crea_card_esercizio(self, esercizio: Esercizio, log: dict, settimana: int, giorno: int):
        """Crea una card per l'esercizio."""
        rir_map = {1: 4, 2: 3, 3: 2, 4: 5} # Aggiunto 4 per deload
        rir_obiettivo_base = rir_map.get(settimana, "N/D")

        # --- NUOVA LOGICA PER RIR AGGIUSTATO ---
        rir_adjustment = log.get("rir_adjustment", 0)
        rir_obiettivo_finale = rir_obiettivo_base + rir_adjustment
        rir_display_text = f"RIR: {rir_obiettivo_finale}"
        if rir_adjustment > 0:
            rir_display_text += f" ({rir_obiettivo_base}+{rir_adjustment})"
        header_row = ft.Row([
            ft.Icon(ft.Icons.FITNESS_CENTER, color=self.colors['primary'], size=20),
            ft.Text(esercizio.nome,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['text_primary'],
                    expand=True),
            ft.Container(
                content=ft.Text(rir_display_text,  # Usa il testo aggiornato
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
            target_text = f"Target: {rep_target} rep" if rep_target else "Target: N/D"

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

    # Nel view.py, sostituisci il metodo visualizza_giorno con questo:

    def visualizza_giorno(self, giorno_allenamento: WorkoutDay, settimana_num: int, is_deload: bool = False):
        """Visualizza il giorno di allenamento."""
        self.scheda_container.content.controls.clear()

        # Titolo con indicazione se è settimana di scarico
        week_label = f"SETTIMANA {settimana_num}"
        if is_deload:
            week_label += " (SCARICO)"

        title = ft.Text(
            f"{week_label} - GIORNO {giorno_allenamento.id_giorno}",
            size=20, weight=ft.FontWeight.BOLD, color=self.colors['text_primary']
        )
        subtitle = ft.Text(
            f"Split: {giorno_allenamento.split_type}",
            size=16, color=self.colors['text_secondary']
        )
        self.scheda_container.content.controls.extend([title, subtitle])

        # Mostra il messaggio di aggiustamento se presente
        if giorno_allenamento.adjustment_message:
            category_color = self.colors['success']  # Default GREEN
            if "GIALLO" in giorno_allenamento.adjustment_message:
                category_color = self.colors['warning']
            elif "ROSSO" in giorno_allenamento.adjustment_message:
                category_color = self.colors['error']

            adjustment_card = ft.Container(
                content=ft.Text(giorno_allenamento.adjustment_message, color=ft.Colors.BLACK, size=14),
                padding=15, bgcolor=category_color, border_radius=8, margin=ft.margin.only(bottom=16)
            )
            self.scheda_container.content.controls.append(adjustment_card)

        # Crea le card per gli esercizi
        for esercizio in giorno_allenamento.esercizi:
            log_esercizio = giorno_allenamento.performance_log.get(esercizio.id, {})
            card = self.crea_card_esercizio(esercizio, log_esercizio, settimana_num, giorno_allenamento.id_giorno)
            self.scheda_container.content.controls.append(card)

        # Aggiungi sempre il pulsante per salvare
        save_button_container = ft.Container(
            content=self.btn_salva_performance,
            padding=ft.padding.symmetric(vertical=20),
            alignment=ft.alignment.center
        )
        self.scheda_container.content.controls.append(save_button_container)

        # Attiva la vista della scheda
        self.scheda_container.visible = True
        self.update_view()

    def mostra_schermata_readiness(self, muscoli_del_giorno: List[str]):
        """Crea e visualizza la schermata per l'input di prontezza giornaliera."""
        controls = self.readiness_view.content.controls
        controls.clear()

        def create_slider(label: str, default_value: int = 4):
            return ft.Column([
                ft.Text(label, color=self.colors['text_primary']),
                ft.Slider(min=1, max=5, divisions=4, value=default_value, label="{value}")
            ])

        # CORREZIONE: Impostati valori di default più sensati
        self.slider_energia = create_slider("Livello di Energia (1=Basso, 5=Alto)", default_value=4)
        self.slider_sonno = create_slider("Qualità del Sonno (1=Pessima, 5=Ottima)", default_value=4)
        self.slider_doms = create_slider(f"Dolore Muscolare (DOMS) per: {', '.join(muscoli_del_giorno)}",
                                         default_value=2)
        self.slider_dolori_articolari = create_slider("Dolore Articolare (1=Nessuno, 5=Forte)", default_value=1)
        self.switch_tempo = ft.Switch(label="Ho poco tempo a disposizione", value=False)

        btn_inizia_allenamento = ft.ElevatedButton(
            text="Inizia Allenamento",
            on_click=self.controller.handle_readiness_submitted,
            style=self.button_style,
            icon=ft.Icons.PLAY_ARROW
        )

        controls.extend([
            ft.Text("Come ti senti oggi?", size=22, weight=ft.FontWeight.BOLD, color=self.colors['text_primary']),
            ft.Text("Sii onesto, il tuo allenamento si adatterà di conseguenza.", color=self.colors['text_secondary']),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    self.slider_energia,
                    self.slider_sonno,
                    self.slider_doms,
                    self.slider_dolori_articolari,
                    self.switch_tempo,
                    ft.Container(height=20),
                    btn_inizia_allenamento
                ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=450,
                padding=20,
                bgcolor=self.colors['surface'],
                border_radius=12
            )
        ])

        # Il controller si occuperà di rendere questa vista visibile
        self.controller._activate_view('readiness')

    def get_readiness_data(self) -> Dict:
        """Estrae i dati dalla schermata di prontezza."""
        try:
            return {
                "energy": int(self.slider_energia.controls[1].value),
                "sleep": int(self.slider_sonno.controls[1].value),
                "soreness": int(self.slider_doms.controls[1].value),
                "joint_pain": int(self.slider_dolori_articolari.controls[1].value),
                "time_is_limited": self.switch_tempo.value
            }
        except (ValueError, AttributeError):
            return {}

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

        # --- CORREZIONE: Imposta correttamente la visibilità per mostrare SOLO il report ---
        self.config_view.visible = False  # Imposta a False
        self.scheda_container.visible = True
        self.progress_view.visible = False
        self.update_view()

    def get_config_values(self):
        """Restituisce i valori di configurazione."""
        return {
            "esperienza": self.dd_esperienza.value,
            "attrezzatura": self.dd_attrezzatura.value,
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


    def _aggiorna_frequenza(self, e):
        """Aggiorna le opzioni di frequenza."""
        self.controller.aggiorna_opzioni_frequenza(self.dd_esperienza.value)

    def mostra_nutrition_view(self, visible: bool = True):
        """Mostra/nasconde la vista nutrizionale"""
        self.config_view.visible = False
        self.scheda_container.visible = False
        self.progress_view.visible = False
        self.nutrition_view.visible = visible

        # Assicurati che la nutrition view sia correttamente posizionata
        if visible:
            self.nutrition_view.expand = True
            self.nutrition_view.alignment = ft.alignment.center

        self.update_view()

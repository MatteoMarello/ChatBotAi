import flet as ft
from typing import Optional, Dict, Any
from model.nutrition_service import NutritionService, NutritionCache
import re


class NutritionView(ft.Container):
    def __init__(self, controller=None, api_key: Optional[str] = None):
        super().__init__()
        self.controller = controller
        self.expand = True
        self.padding = 20

        # Inizializza il servizio API e la cache
        try:
            self.nutrition_service = NutritionService(api_key)
            self.cache = NutritionCache()
        except ValueError as e:
            self.nutrition_service = None
            self.cache = None
            print(f"Errore inizializzazione servizio: {e}")

        # Configurazione colori
        self.colors = {
            'primary': '#3b82f6',
            'surface': '#1e293b',
            'surface_light': '#334155',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#475569',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'safety': '#dc2626'  # Rosso per avvertenze di sicurezza
        }

        # Dati utente
        self.user_data = {}

        # Stato della chat
        self.is_loading = False
        self.terms_accepted = False  # Controllo accettazione termini

        # Flag per verificare se sono stati mostrati i disclaimer
        self.medical_disclaimer_shown = False
        self.safety_terms_shown = False

        # Componenti UI
        self._create_tabs()
        self._create_disclaimer_section()
        self._create_tdee_section()
        self._create_chat_section()

        # Layout principale
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.RESTAURANT_MENU, color=self.colors['primary'], size=28),
                        ft.Column([
                            ft.Text("Nutrition App",
                                    size=22,
                                    weight=ft.FontWeight.BOLD,
                                    color=self.colors['text_primary']),
                            ft.Text("Educazione alimentare e calcolo TDEE",
                                    size=12,
                                    color=self.colors['text_secondary'])
                        ], spacing=2)
                    ], spacing=15),
                    padding=ft.padding.only(bottom=20)
                ),
                self.tabs
            ],
            spacing=10,
            expand=True
        )

    def _create_tabs(self):
        """Crea il sistema a schede"""
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="⚠️ Disclaimer", icon=ft.Icons.WARNING),
                ft.Tab(text="📊 Calcolatore TDEE", icon=ft.Icons.CALCULATE),
                ft.Tab(text="🤖 Assistant (Beta)", icon=ft.Icons.CHAT),
            ],
            expand=True,
            on_change=self._on_tab_change
        )

    def _on_tab_change(self, e):
        """Gestisce il cambio di tab"""
        # Se l'utente prova ad andare al chat senza aver accettato i termini
        if e.control.selected_index == 2 and not self.terms_accepted:
            e.control.selected_index = 0  # Ritorna al disclaimer
            self._show_snackbar(
                "⚠️ Devi accettare i termini di sicurezza prima di usare l'assistant!",
                self.colors['error']
            )
            self.update()

    def _create_disclaimer_section(self):
        """Crea la sezione disclaimer semplificata"""

        # Checkbox per accettazione termini
        self.terms_checkbox = ft.Checkbox(
            label="Ho letto e accetto i termini d'uso",
            value=False,
            on_change=self._on_terms_change
        )

        # Pulsante per procedere
        self.proceed_btn = ft.ElevatedButton(
            text="Inizia",
            icon=ft.Icons.ARROW_FORWARD,
            disabled=True,
            on_click=self._proceed_to_app,
            style=ft.ButtonStyle(
                bgcolor=self.colors['success'],
                padding=20
            )
        )

        disclaimer_content = ft.Column([
            # AVVERTENZA PRINCIPALE - Semplificata
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.INFO, color=self.colors['primary'], size=24),
                        ft.Text("Informazioni Importanti",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors['text_primary'])
                    ], spacing=10),

                    ft.Text(
                        "Questa app fornisce informazioni educative sulla nutrizione. "
                        "Non sostituisce il parere di medici o nutrizionisti qualificati.",
                        size=14,
                        color=self.colors['text_primary']
                    ),
                ], spacing=10),
                bgcolor=self.colors['surface_light'],
                padding=20,
                border_radius=10,
                border=ft.border.all(1, self.colors['primary'])
            ),

            ft.Container(height=20),

            # PUNTI ESSENZIALI - Ridotti
            ft.Container(
                content=ft.Column([
                    ft.Text("⚠️ Consulta un professionista per:",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors['warning']),
                    ft.Container(height=5),

                    *[ft.Text(f"• {item}", size=13, color=self.colors['text_primary'])
                      for item in [
                          "Allergie, intolleranze o patologie mediche",
                          "Gravidanza, allattamento o età minorile",
                          "Piani alimentari personalizzati",
                          "Farmaci o integratori specifici"
                      ]]
                ], spacing=3),
                bgcolor=self.colors['surface_light'],
                padding=15,
                border_radius=8,
                border=ft.border.all(1, self.colors['warning'])
            ),

            ft.Container(height=30),

            # CHECKBOX E PULSANTE
            ft.Container(
                content=ft.Column([
                    self.terms_checkbox,
                    ft.Container(height=15),
                    self.proceed_btn
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            )

        ], spacing=15, scroll=ft.ScrollMode.AUTO)

        # Assegna al primo tab
        self.tabs.tabs[0].content = ft.Container(
            content=disclaimer_content,
            padding=20
        )

    def _on_terms_change(self, e):
        """Gestisce l'accettazione dei termini"""
        self.terms_accepted = e.control.value
        self.proceed_btn.disabled = not self.terms_accepted
        self.update()

    def _proceed_to_app(self, e):
        """Procede all'applicazione dopo l'accettazione dei termini"""
        if self.terms_accepted:
            self.tabs.selected_index = 1  # Vai al calcolatore TDEE
            self._show_snackbar(
                "✅ Termini accettati. Usa l'app responsabilmente!",
                self.colors['success']
            )
        self.update()

    def _create_tdee_section(self):
        """Sezione per il calcolo TDEE con disclaimer aggiuntivi"""

        # Disclaimer per il TDEE
        tdee_disclaimer = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO, color=self.colors['primary'], size=20),
                    ft.Text("ℹ️ Informazioni importanti sul calcolo TDEE",
                            weight=ft.FontWeight.BOLD,
                            color=self.colors['primary'])
                ], spacing=10),
                ft.Text(
                    "• Il TDEE è una STIMA basata su formule standard\n"
                    "• I valori reali possono variare del ±20% tra individui\n"
                    "• Non considera condizioni mediche specifiche\n"
                    "• Per piani personalizzati consulta un nutrizionista",
                    size=12,
                    color=self.colors['text_secondary']
                )
            ], spacing=8),
            bgcolor=self.colors['surface'],
            padding=15,
            border_radius=8,
            border=ft.border.all(1, self.colors['primary'])
        )

        # Input fields con validazione migliorata
        self.weight_input = self._create_safe_input_field("Peso (kg)", "70", 30, 300)
        self.height_input = self._create_safe_input_field("Altezza (cm)", "175", 100, 250)
        self.age_input = self._create_safe_input_field("Età", "30", 16, 90)

        # Dropdowns
        self.activity_input = self._create_dropdown("Livello Attività", [
            "Sedentario (poco o nessun esercizio)",
            "Leggermente attivo (esercizio 1-3x/settimana)",
            "Moderatamente attivo (esercizio 3-5x/settimana)",
            "Molto attivo (esercizio 6-7x/settimana)",
            "Estremamente attivo (lavoro fisico + esercizio intenso)"
        ])

        self.goal_input = self._create_dropdown("Obiettivo", [
            "Perdita di peso (deficit calorico)",
            "Mantenimento",
            "Aumento muscolare (surplus calorico)"
        ])

        # Gender selection
        self.gender_selector = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="male", label="Uomo"),
                ft.Radio(value="female", label="Donna")
            ], spacing=20),
            value="male"
        )

        # Age warning
        self.age_warning = ft.Container(
            content=ft.Text(
                "⚠️ Se hai meno di 18 anni, consulta un pediatra prima di modificare la tua alimentazione",
                size=12,
                color=self.colors['warning'],
                weight=ft.FontWeight.BOLD
            ),
            visible=False,
            padding=10,
            bgcolor=self.colors['surface'],
            border_radius=5
        )

        # Results display
        self.result_card = ft.Container(
            padding=20,
            border_radius=12,
            bgcolor=self.colors['surface_light'],
            border=ft.border.all(1, self.colors['border']),
            content=ft.Column(spacing=10),
            visible=False
        )

        # Calculate button
        self.calculate_btn = ft.ElevatedButton(
            text="Calcola TDEE (Solo Stima)",
            icon=ft.Icons.CALCULATE,
            on_click=self.calculate_tdee,
            style=ft.ButtonStyle(
                padding=20,
                bgcolor=self.colors['primary']
            )
        )

        # Assemble TDEE section
        tdee_content = ft.Column([
            ft.Text("📊 Calcolatore TDEE (Stima Educativa)",
                    size=18,
                    weight=ft.FontWeight.BOLD),
            tdee_disclaimer,
            ft.Container(height=10),
            ft.Row([self.weight_input, self.height_input, self.age_input], spacing=20),
            self.age_warning,
            ft.Container(height=10),
            ft.Text("Sesso", color=self.colors['text_secondary']),
            self.gender_selector,
            ft.Container(height=10),
            self.activity_input,
            self.goal_input,
            ft.Container(height=20),
            self.calculate_btn,
            ft.Container(height=20),
            self.result_card
        ], spacing=15)

        # Assegna al secondo tab
        # Assegna al secondo tab con scroll
        self.tabs.tabs[1].content = ft.Container(
            content=ft.Column([
                ft.Text("📊 Calcolatore TDEE (Stima Educativa)",
                        size=18,
                        weight=ft.FontWeight.BOLD),
                tdee_disclaimer,
                ft.Container(height=10),
                ft.Row([self.weight_input, self.height_input, self.age_input], spacing=20),
                self.age_warning,
                ft.Container(height=10),
                ft.Text("Sesso", color=self.colors['text_secondary']),
                self.gender_selector,
                ft.Container(height=10),
                # Dropdown in colonna per migliore usabilità
                ft.Column([
                    self.activity_input,
                    ft.Container(height=10),
                    self.goal_input
                ], spacing=10),
                ft.Container(height=20),
                self.calculate_btn,
                ft.Container(height=20),
                self.result_card
            ], spacing=15, scroll=ft.ScrollMode.AUTO),  # Aggiunto scroll qui
            padding=20
        )

    def _create_chat_section(self):
        """Sezione chat più pulita e spaziosa"""

        # Loading indicator migliorato - DEFINITO PRIMA
        self.loading_indicator = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=self.colors['primary']),
                ft.Text("Elaborazione...", size=12, italic=True, color=self.colors['text_secondary'])
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            padding=15,
            visible=False
        )

        # Header semplificato
        chat_header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SMART_TOY, color=self.colors['primary'], size=20),
                ft.Text("Assistant Nutrizionale",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Container(expand=True),  # Spacer
                ft.Container(
                    content=ft.Text(
                        "🟢 Online" if self.nutrition_service else "🔴 Offline",
                        size=11,
                        color=self.colors['success'] if self.nutrition_service else self.colors['error']
                    ),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    bgcolor=self.colors['surface'],
                    border_radius=12
                )
            ], spacing=10),
            padding=ft.padding.only(bottom=10)
        )

        # Chat display più grande
        self.chat_display = ft.ListView(
            auto_scroll=True,
            expand=True,
            spacing=8,
            padding=ft.padding.symmetric(horizontal=5, vertical=10)
        )

        # Container chat principale
        chat_container = ft.Container(
            content=ft.Column([
                self.chat_display,
                self.loading_indicator
            ]),
            border=ft.border.all(1, self.colors['border']),
            border_radius=12,
            padding=0,
            expand=True,
            bgcolor=self.colors['surface']
        )

        # Input area migliorata
        self.chat_input = ft.TextField(
            hint_text="Scrivi la tua domanda sulla nutrizione...",
            multiline=True,
            min_lines=1,
            max_lines=4,
            expand=True,
            on_submit=self.send_chat_message,
            border_color=self.colors['border'],
            focused_border_color=self.colors['primary'],
            bgcolor=self.colors['surface'],
            border_radius=8
        )

        self.send_btn = ft.IconButton(
            icon=ft.Icons.SEND_ROUNDED,
            icon_color=self.colors['primary'],
            on_click=self.send_chat_message,
            tooltip="Invia messaggio"
        )

        # Status message più discreto
        self.status_message = ft.Container(
            content=ft.Text(
                "💡 Calcola il TDEE per consigli più precisi",
                size=11,
                color=self.colors['text_secondary'],
                italic=True
            ),
            padding=ft.padding.only(left=5, bottom=5),
            visible=True
        )

        # Input row
        input_row = ft.Container(
            content=ft.Row([
                self.chat_input,
                self.send_btn
            ], spacing=8),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            bgcolor=self.colors['surface_light'],
            border_radius=ft.border_radius.only(bottom_left=12, bottom_right=12)
        )

        # Layout finale più pulito
        chat_content = ft.Column([
            chat_header,
            self.status_message,
            ft.Container(
                content=ft.Column([
                    chat_container,
                    input_row
                ], spacing=0),
                expand=True
            )
        ], spacing=5, expand=True)

        # Assegna al terzo tab
        self.tabs.tabs[2].content = ft.Container(
            content=chat_content,
            padding=20
        )

    def _validate_user_input(self, e):
        """Valida l'input dell'utente in tempo reale"""
        text = e.control.value.lower()

        # Parole chiave che richiedono attenzione
        warning_keywords = [
            'allergia', 'allergico', 'intolleranza', 'intollerante',
            'diabete', 'diabetico', 'farmaco', 'medicina', 'malattia',
            'gravidanza', 'incinta', 'bambino', 'figlio', 'pediatrico',
            'digiuno', 'detox', 'perdere peso veloce', 'dimagrire veloce',
            'pillole', 'integratori', 'supplementi'
        ]

        found_warnings = [kw for kw in warning_keywords if kw in text]

        if found_warnings and len(text) > 10:  # Solo se il messaggio è abbastanza lungo
            self.input_warning.content.value = (
                f"⚠️ Hai menzionato: {', '.join(found_warnings)}. "
                "Ricorda: per questi argomenti consulta un professionista!"
            )
            self.input_warning.visible = True
        else:
            self.input_warning.visible = False

        self.update()

    def _create_safe_input_field(self, label: str, hint: str, min_val: float, max_val: float) -> ft.TextField:
        """Crea un campo input con validazione di sicurezza"""
        field = ft.TextField(
            label=label,
            hint_text=f"{hint} (range: {min_val}-{max_val})",
            border_color=self.colors['border'],
            filled=True,
            bgcolor=self.colors['surface'],
            color=self.colors['text_primary'],
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            expand=True,
            on_change=lambda e: self._validate_numeric_input(e, min_val, max_val)
        )
        return field

    def _validate_numeric_input(self, e, min_val: float, max_val: float):
        """Valida input numerici"""
        try:
            if e.control.value:
                value = float(e.control.value)
                if value < min_val or value > max_val:
                    e.control.error_text = f"Valore deve essere tra {min_val} e {max_val}"
                else:
                    e.control.error_text = None

                # Avvertenza per età minorenne
                if e.control.label == "Età" and value < 18:
                    self.age_warning.visible = True
                elif e.control.label == "Età":
                    self.age_warning.visible = False

                self.update()
        except ValueError:
            e.control.error_text = "Inserisci un numero valido"
            self.update()

    def _add_enhanced_welcome_message(self):
        """Messaggio di benvenuto più conciso"""
        welcome_msg = """👋 Ciao! Sono il tuo Assistant Nutrizionale.
    
        🎯 **Posso aiutarti con:**
        • Concetti base di nutrizione
        • Informazioni sui macronutrienti  
        • Principi di alimentazione equilibrata
        • Lettura delle etichette alimentari
    
        ⚠️ **Importante**: Fornisco solo informazioni educative generali, non consigli medici personalizzati.
    
        💡 Calcola prima il tuo TDEE per ricevere suggerimenti più specifici!"""

        self._add_chat_message("Assistant", welcome_msg, is_user=False, is_welcome=True)

    def did_mount(self):
        """Chiamato quando il controllo è aggiunto alla pagina"""
        super().did_mount()
        # Aggiungi il messaggio di benvenuto solo dopo che il controllo è montato
        self._add_enhanced_welcome_message()

    def _create_dropdown(self, label: str, options: list) -> ft.Dropdown:
        return ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(opt) for opt in options],
            border_color=self.colors['border'],
            filled=True,
            bgcolor=self.colors['surface'],
            color=self.colors['text_primary'],
            width=300  # Usa width invece di expand per i dropdown
        )

    async def calculate_tdee(self, e: ft.ControlEvent):
        """Calcola il TDEE con controlli di sicurezza aggiuntivi"""
        try:
            # Validazione input
            if not all([self.weight_input.value, self.height_input.value, self.age_input.value]):
                self._show_snackbar("⚠️ Compila tutti i campi numerici!", self.colors['error'])
                return

            if not all([self.activity_input.value, self.goal_input.value]):
                self._show_snackbar("⚠️ Seleziona livello di attività e obiettivo!", self.colors['error'])
                return

            # Validazione valori di sicurezza
            weight = float(self.weight_input.value)
            height = float(self.height_input.value)
            age = int(self.age_input.value)

            # Controlli di sicurezza
            if weight < 30 or weight > 300:
                self._show_snackbar("⚠️ Peso deve essere tra 30 e 300 kg", self.colors['error'])
                return

            if height < 100 or height > 250:
                self._show_snackbar("⚠️ Altezza deve essere tra 100 e 250 cm", self.colors['error'])
                return

            if age < 16 or age > 90:
                self._show_snackbar("⚠️ Età deve essere tra 16 e 90 anni", self.colors['error'])
                return

            # Avvertenza per minorenni
            if age < 18:
                self._show_snackbar(
                    "⚠️ ATTENZIONE: Sei minorenne. Consulta un pediatra prima di modificare la tua alimentazione!",
                    self.colors['warning']
                )

            # Disabilita il pulsante durante il calcolo
            self.calculate_btn.disabled = True
            self.calculate_btn.text = "Calcolando..."
            self.update()

            # Resto del calcolo (uguale a prima)
            gender = self.gender_selector.value
            activity_level = self.activity_input.value
            goal = self.goal_input.value

            # Calcolo BMR (Mifflin-St Jeor Equation)
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            # Moltiplicatori attività
            activity_multipliers = {
                "Sedentario": 1.2,
                "Leggermente": 1.375,
                "Moderatamente": 1.55,
                "Molto": 1.725,
                "Estremamente": 1.9
            }

            activity_key = activity_level.split()[0]
            multiplier = activity_multipliers.get(activity_key, 1.55)
            tdee = bmr * multiplier

            # Aggiustamenti per obiettivo (più conservativi)
            goal_adjustments = {
                "Perdita": -250,  # Ridotto per sicurezza
                "Mantenimento": 0,
                "Aumento": 250  # Ridotto per sicurezza
            }

            goal_key = goal.split()[0]
            adjustment = goal_adjustments.get(goal_key, 0)
            adjusted_tdee = tdee + adjustment

            # Calcolo macronutrienti
            protein = weight * 2.2  # 2.2g per kg
            fat = (adjusted_tdee * 0.25) / 9  # 25% delle calorie
            carbs = (adjusted_tdee - (protein * 4 + fat * 9)) / 4

            # Salva i dati per il chatbot
            self.user_data = {
                'tdee': round(tdee),
                'adjusted_tdee': round(adjusted_tdee),
                'protein': round(protein),
                'carbs': round(carbs),
                'fat': round(fat),
                'goal': goal,
                'weight': weight,
                'height': height,
                'age': age,
                'gender': gender,
                'activity_level': activity_level,
                'bmr': round(bmr)
            }

            # Mostra risultati
            self._display_results()

            # Aggiorna lo status della chat
            self.status_message.content.value = "✅ Perfetto! Ora il coach può darti consigli personalizzati."
            self.status_message.content.color = self.colors['success']

            self._show_snackbar("TDEE calcolato con successo!", self.colors['success'])

        except ValueError as ex:
            self._show_snackbar(f"Errore nei dati: {str(ex)}", self.colors['error'])
        except Exception as ex:
            self._show_snackbar(f"Errore nel calcolo: {str(ex)}", self.colors['error'])
        finally:
            # Riabilita il pulsante
            self.calculate_btn.disabled = False
            self.calculate_btn.text = "Calcola TDEE"
            self.update()

    def _display_results(self):
        """Mostra i risultati del calcolo TDEE"""
        data = self.user_data

        self.result_card.content.controls = [
            ft.Text("📊 I tuoi risultati",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['primary']),
            ft.Divider(color=self.colors['border']),

            self._create_result_row("Metabolismo Basale (BMR)", f"{data['bmr']} kcal", ft.Icons.FAVORITE),
            self._create_result_row("TDEE Base", f"{data['tdee']} kcal", ft.Icons.SPEED),
            self._create_result_row("Calorie per Obiettivo", f"{data['adjusted_tdee']} kcal", ft.Icons.TRENDING_UP),

            ft.Container(height=10),
            ft.Text("🥗 Macronutrienti giornalieri",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['text_primary']),
            ft.Divider(color=self.colors['border']),

            self._create_result_row("Proteine", f"{data['protein']}g ({data['protein'] * 4} kcal)",
                                    ft.Icons.FITNESS_CENTER),
            self._create_result_row("Carboidrati", f"{data['carbs']}g ({data['carbs'] * 4} kcal)",
                                    ft.Icons.BREAKFAST_DINING),
            self._create_result_row("Grassi", f"{data['fat']}g ({data['fat'] * 9} kcal)", ft.Icons.OIL_BARREL),

            ft.Container(height=10),
            ft.Container(
                content=ft.Text("💡 Vai nella tab 'Coach Nutrizionale' per consigli personalizzati!",
                                size=12,
                                color=self.colors['primary'],
                                italic=True),
                bgcolor=self.colors['surface'],
                padding=10,
                border_radius=8
            )
        ]
        self.result_card.visible = True
        self.update()

    def _create_result_row(self, label: str, value: str, icon: Optional[str] = None) -> ft.Row:
        return ft.Row([
            ft.Icon(icon, color=self.colors['primary'], size=20) if icon else ft.Container(width=24),
            ft.Text(label, color=self.colors['text_primary'], expand=True),
            ft.Text(value, color=self.colors['text_primary'], weight=ft.FontWeight.BOLD)
        ], spacing=10)

    async def send_chat_message(self, e: ft.ControlEvent):
        """Invia un messaggio al coach nutrizionale"""
        user_message = self.chat_input.value.strip()
        if not user_message:
            return

        if not self.nutrition_service:
            self._add_chat_message(
                "Sistema",
                "❌ Coach AI non disponibile. Controlla la configurazione dell'API key.",
                is_user=False
            )
            return

        if self.is_loading:
            return  # Previeni messaggi multipli durante il caricamento

        # Disabilita input durante la richiesta
        self.is_loading = True
        self.send_btn.disabled = True
        self.chat_input.disabled = True
        self.loading_indicator.visible = True

        # Aggiungi messaggio utente alla chat
        self._add_chat_message("Tu", user_message, is_user=True)
        self.chat_input.value = ""
        self.update()

        try:
            # Verifica cache
            cache_key = f"{user_message}_{hash(str(self.user_data))}"
            cached_response = self.cache.get(cache_key) if self.cache else None

            if cached_response:
                response = cached_response
            else:
                # Prepara il contesto e chiama l'API
                context = self._create_chat_context()
                response = await self.nutrition_service.get_nutrition_advice(user_message, context)

                # Salva in cache
                if self.cache:
                    self.cache.set(cache_key, response)

            self._add_chat_message("Coach Nutrizionale", response, is_user=False)

        except Exception as ex:
            error_msg = f"⚠️ Errore: {str(ex)}"
            if "API" in str(ex):
                error_msg += "\n\nSuggerimenti:\n• Verifica la connessione internet\n• Controlla che l'API key sia valida\n• Riprova tra qualche minuto"

            self._add_chat_message("Sistema", error_msg, is_user=False)

        finally:
            # Riabilita input
            self.is_loading = False
            self.send_btn.disabled = False
            self.chat_input.disabled = False
            self.loading_indicator.visible = False
            self.update()

    def _add_chat_message(self, sender: str, message: str, is_user: bool, is_welcome: bool = False):
        """Messaggi chat con design più moderno"""

        if is_user:
            # Messaggio utente - design più moderno
            message_container = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(expand=True),  # Spacer per allineamento a destra
                        ft.Text(message, color=ft.Colors.WHITE, selectable=True, size=14)
                    ]),
                    ft.Row([
                        ft.Container(expand=True),
                        ft.Text("Tu", size=10, color=ft.Colors.WHITE70, italic=True)
                    ])
                ], spacing=3),
                bgcolor=self.colors['primary'],
                border_radius=ft.border_radius.only(
                    top_left=16, top_right=16, bottom_left=16, bottom_right=4
                ),
                padding=12,
                margin=ft.margin.only(left=60, right=10, bottom=8),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
                )
            )
        else:
            # Messaggio assistant - design più pulito
            sender_color = self.colors['success'] if is_welcome else self.colors['primary']

            message_container = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(
                            ft.Icons.SMART_TOY if sender == "Assistant" else ft.Icons.INFO,
                            size=16,
                            color=sender_color
                        ),
                        ft.Text(sender, size=10, color=sender_color, weight=ft.FontWeight.BOLD)
                    ], spacing=5),
                    ft.Container(height=2),
                    ft.Text(message, color=self.colors['text_primary'], selectable=True, size=14)
                ], spacing=0),
                bgcolor=self.colors['surface_light'],
                border_radius=ft.border_radius.only(
                    top_left=4, top_right=16, bottom_left=16, bottom_right=16
                ),
                padding=12,
                margin=ft.margin.only(left=10, right=60, bottom=8),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, self.colors['border']))
            )

        self.chat_display.controls.append(message_container)

        if hasattr(self, 'page') and self.page:
            self.update()

    def _create_chat_context(self) -> str:
        """Crea il contesto nutrizionale per l'AI"""
        if not self.user_data:
            return """L'utente non ha ancora calcolato il suo TDEE. 
Suggerisci di farlo prima per ricevere consigli personalizzati.
Puoi comunque rispondere a domande generali sulla nutrizione."""

        data = self.user_data

        return f"""PROFILO UTENTE:
- Età: {data['age']} anni
- Sesso: {'Uomo' if data['gender'] == 'male' else 'Donna'}  
- Peso: {data['weight']} kg
- Altezza: {data['height']} cm
- Livello attività: {data['activity_level']}
- Obiettivo: {data['goal']}

DATI NUTRIZIONALI:
- Metabolismo Basale (BMR): {data['bmr']} kcal
- TDEE base: {data['tdee']} kcal
- Calorie per obiettivo: {data['adjusted_tdee']} kcal

MACRONUTRIENTI GIORNALIERI:
- Proteine: {data['protein']}g ({data['protein'] * 4} kcal)
- Carboidrati: {data['carbs']}g ({data['carbs'] * 4} kcal)  
- Grassi: {data['fat']}g ({data['fat'] * 9} kcal)

Fornisci consigli specifici e personalizzati basati su questi dati."""

    def _show_snackbar(self, message: str, color: str):
        """Mostra una snackbar con il messaggio"""
        if hasattr(self, 'page') and self.page:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color=ft.Colors.WHITE),
                bgcolor=color
            )
            self.page.snack_bar.open = True
            self.page.update()

    def reset_chat(self):
        """Pulisce la chat e resetta lo stato"""
        self.chat_display.controls.clear()
        if self.cache:
            self.cache.clear()
        self._add_welcome_message()
        # Solo aggiorna se il controllo è collegato alla pagina
        if hasattr(self, 'page') and self.page:
            self.update()

    def reset_all_data(self):
        """Resetta tutti i dati (TDEE e chat)"""
        self.user_data = {}
        self.result_card.visible = False

        # Resetta i campi input
        self.weight_input.value = ""
        self.height_input.value = ""
        self.age_input.value = ""
        self.activity_input.value = None
        self.goal_input.value = None
        self.gender_selector.value = "male"

        # Resetta il messaggio di stato
        self.status_message.content.value = "💡 Suggerimento: Calcola prima il tuo TDEE per ricevere consigli personalizzati!"
        self.status_message.content.color = self.colors['text_secondary']

        # Pulisce la chat
        self.reset_chat()

        # Solo aggiorna se il controllo è collegato alla pagina
        if hasattr(self, 'page') and self.page:
            self.update()

    def get_user_data(self) -> Dict[str, Any]:
        """Ritorna i dati utente calcolati"""
        return self.user_data.copy()

    def set_user_data(self, data: Dict[str, Any]):
        """Imposta i dati utente (per caricamento da file)"""
        self.user_data = data.copy()
        if self.user_data:
            self._display_results()
            self.status_message.content.value = "✅ Dati caricati! Il coach può darti consigli personalizzati."
            self.status_message.content.color = self.colors['success']
            # Solo aggiorna se il controllo è collegato alla pagina
            if hasattr(self, 'page') and self.page:
                self.update()

    def export_data(self) -> Optional[Dict[str, Any]]:
        """Esporta i dati per il salvataggio"""
        if not self.user_data:
            return None

        export_data = {
            'user_data': self.user_data,
            'timestamp': ft.datetime.now().isoformat(),
            'version': '1.0'
        }
        return export_data

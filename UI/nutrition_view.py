import flet as ft
from typing import Optional, Dict, Any
from nutrition_service import NutritionService, NutritionCache
from datetime import *


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
            'error': '#ef4444'
        }

        # Dati utente
        self.user_data = {}

        # Stato della chat
        self.is_loading = False

        # Componenti UI
        self._create_tabs()
        self._create_tdee_section()
        self._create_chat_section()

        # Layout principale
        self.content = ft.Column(
            controls=[
                ft.Text("Nutrizione & Alimentazione 🍎",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Divider(color=self.colors['border']),
                self.tabs
            ],
            spacing=20,
            expand=True
        )

    def _create_tabs(self):
        """Crea il sistema a schede"""
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Calcolatore TDEE", icon=ft.Icons.CALCULATE),
                ft.Tab(text="Coach Nutrizionale", icon=ft.Icons.CHAT),
            ],
            expand=True
        )

    def _create_tdee_section(self):
        """Sezione per il calcolo TDEE"""
        # Input fields
        self.weight_input = self._create_input_field("Peso (kg)", "70")
        self.height_input = self._create_input_field("Altezza (cm)", "175")
        self.age_input = self._create_input_field("Età", "30")

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
            text="Calcola TDEE",
            icon=ft.Icons.CALCULATE,
            on_click=self.calculate_tdee,
            style=ft.ButtonStyle(
                padding=20,
                bgcolor=self.colors['primary']
            )
        )

        # Assemble TDEE section
        tdee_content = ft.Column([
            ft.Text("Calcola il tuo fabbisogno calorico",
                    size=18,
                    weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            ft.Row([self.weight_input, self.height_input, self.age_input], spacing=20),
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

        # Assegna al primo tab
        self.tabs.tabs[0].content = ft.Container(
            content=tdee_content,
            padding=20
        )

    def _create_chat_section(self):
        """Sezione per il chatbot nutrizionale"""
        # Chat display
        self.chat_display = ft.ListView(
            auto_scroll=True,
            expand=True,
            spacing=10,
            padding=10
        )

        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, stroke_width=2),
                ft.Text("Coach sta pensando...", size=12, italic=True)
            ], spacing=10),
            padding=10,
            visible=False
        )

        # User input
        self.chat_input = ft.TextField(
            hint_text="Scrivi la tua domanda nutrizionale...",
            multiline=True,
            min_lines=1,
            max_lines=3,
            expand=True,
            on_submit=self.send_chat_message  # Invio con Enter
        )

        # Send button
        self.send_btn = ft.IconButton(
            icon=ft.Icons.SEND,
            on_click=self.send_chat_message,
            icon_size=30,
            disabled=False
        )

        # Status message
        self.status_message = ft.Container(
            content=ft.Text(
                "💡 Suggerimento: Calcola prima il tuo TDEE per ricevere consigli personalizzati!",
                size=12,
                color=self.colors['text_secondary'],
                italic=True
            ),
            padding=10,
            visible=True
        )

        # API status indicator
        api_status_color = self.colors['success'] if self.nutrition_service else self.colors['error']
        api_status_text = "🟢 Coach AI disponibile" if self.nutrition_service else "🔴 Coach AI non disponibile (API key mancante)"

        self.api_status = ft.Container(
            content=ft.Text(api_status_text, size=11, color=api_status_color),
            padding=ft.padding.only(left=10, right=10, bottom=5)
        )

        # Assemble chat section
        chat_content = ft.Column([
            ft.Text("Parla con il coach nutrizionale",
                    size=18,
                    weight=ft.FontWeight.BOLD),
            self.api_status,
            self.status_message,
            ft.Container(
                content=ft.Column([
                    self.chat_display,
                    self.loading_indicator
                ]),
                border=ft.border.all(1, self.colors['border']),
                border_radius=8,
                padding=10,
                expand=True
            ),
            ft.Row([self.chat_input, self.send_btn], spacing=10)
        ], spacing=15, expand=True)

        # Assegna al secondo tab
        self.tabs.tabs[1].content = ft.Container(
            content=chat_content,
            padding=20
        )

    def _add_welcome_message(self):
        """Aggiunge un messaggio di benvenuto alla chat"""
        welcome_msg = """Ciao! 👋 Sono il tuo coach nutrizionale personale.

Posso aiutarti con:
• Consigli su alimentazione e macro
• Suggerimenti per pasti bilanciati  
• Strategie per raggiungere i tuoi obiettivi
• Risposte alle tue domande nutrizionali

Per consigli personalizzati, calcola prima il tuo TDEE nella tab precedente!"""

        self._add_chat_message("Coach Nutrizionale", welcome_msg, is_user=False, is_welcome=True)

    def did_mount(self):
        """Chiamato quando il controllo è aggiunto alla pagina"""
        super().did_mount()
        # Aggiungi il messaggio di benvenuto solo dopo che il controllo è montato
        self._add_welcome_message()

    def _create_input_field(self, label: str, hint: str) -> ft.TextField:
        return ft.TextField(
            label=label,
            hint_text=hint,
            border_color=self.colors['border'],
            filled=True,
            bgcolor=self.colors['surface'],
            color=self.colors['text_primary'],
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.NumbersOnlyInputFilter(),
            expand=True
        )

    def _create_dropdown(self, label: str, options: list) -> ft.Dropdown:
        return ft.Dropdown(
            label=label,
            options=[ft.dropdown.Option(opt) for opt in options],
            border_color=self.colors['border'],
            filled=True,
            bgcolor=self.colors['surface'],
            color=self.colors['text_primary'],
            expand=True
        )

    async def calculate_tdee(self, e: ft.ControlEvent):
        """Calcola il TDEE e aggiorna i dati utente"""
        try:
            # Validazione input
            if not all([self.weight_input.value, self.height_input.value, self.age_input.value]):
                self._show_snackbar("Compila tutti i campi numerici!", self.colors['error'])
                return

            if not all([self.activity_input.value, self.goal_input.value]):
                self._show_snackbar("Seleziona livello di attività e obiettivo!", self.colors['error'])
                return

            # Disabilita il pulsante durante il calcolo
            self.calculate_btn.disabled = True
            self.calculate_btn.text = "Calcolando..."
            self.update()

            # Estrai i valori
            weight = float(self.weight_input.value)
            height = float(self.height_input.value)
            age = int(self.age_input.value)
            gender = self.gender_selector.value
            activity_level = self.activity_input.value
            goal = self.goal_input.value

            # Validazione valori
            if weight <= 0 or height <= 0 or age <= 0:
                raise ValueError("I valori devono essere positivi")
            if weight > 300 or height > 250 or age > 120:
                raise ValueError("Valori non realistici inseriti")

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

            # Aggiustamenti per obiettivo
            goal_adjustments = {
                "Perdita": -300,
                "Mantenimento": 0,
                "Aumento": 300
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
        """Aggiunge un messaggio alla chat"""
        # Colore e allineamento basato sul tipo di messaggio
        if is_user:
            bg_color = self.colors['primary']
            text_color = ft.Colors.WHITE
            alignment = ft.alignment.center_right
            sender_color = ft.Colors.WHITE
        elif is_welcome:
            bg_color = self.colors['surface_light']
            text_color = self.colors['text_primary']
            alignment = ft.alignment.center_left
            sender_color = self.colors['success']
        else:
            bg_color = self.colors['surface_light']
            text_color = self.colors['text_primary']
            alignment = ft.alignment.center_left
            sender_color = self.colors['primary']

        # Crea il container del messaggio
        message_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    sender,
                    color=sender_color,
                    weight=ft.FontWeight.BOLD,
                    size=12
                ),
                ft.Text(
                    message,
                    color=text_color,
                    selectable=True  # Permette di selezionare il testo
                )
            ], spacing=5),
            bgcolor=bg_color,
            border_radius=12,
            padding=15,
            alignment=alignment,
            margin=ft.margin.only(
                left=50 if is_user else 0,
                right=50 if not is_user else 0
            )
        )

        self.chat_display.controls.append(message_container)
        # Solo aggiorna se il controllo è collegato alla pagina
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

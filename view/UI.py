import flet as ft
from typing import Dict

# Importa le tue classi esistenti
from adattaScheda import TrainingAlgorithm, PerformanceData, DOMSData


class TrainingGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.algorithm = TrainingAlgorithm()
        self.current_week = 1
        self.current_day = 1

        # Configurazione pagina
        self.page.title = "Training Algorithm - Analisi Performance"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

        # Dati esercizi (da personalizzare)
        self.esercizi = {
            1: {"nome": "Panca Piana", "muscolo": "Petto"},
            2: {"nome": "Panca Manubri", "muscolo": "Petto"},
            3: {"nome": "Croci", "muscolo": "Petto"},
            4: {"nome": "Squat", "muscolo": "Quadricipiti"},
            5: {"nome": "Pressa", "muscolo": "Quadricipiti"},
            6: {"nome": "Trazioni", "muscolo": "Dorsali"},
            7: {"nome": "Rematore", "muscolo": "Dorsali"},
        }

        # Componenti UI
        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        """Configura l'interfaccia utente."""

        # Header
        self.title = ft.Text(
            "🏋️ Training Algorithm - Analisi Performance",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700
        )

        # Selezione settimana
        self.week_selector = ft.Dropdown(
            label="Settimana",
            value="1",
            options=[
                ft.dropdown.Option("1", "Settimana 1"),
                ft.dropdown.Option("2", "Settimana 2"),
                ft.dropdown.Option("3", "Settimana 3"),
            ],
            on_change=self.on_week_change
        )

        # Selezione giorno
        self.day_selector = ft.Dropdown(
            label="Giorno",
            value="1",
            options=[
                ft.dropdown.Option(str(i), f"Giorno {i}") for i in range(1, 8)
            ],
            on_change=self.on_day_change
        )

        # Contenitore principale
        self.main_container = ft.Column(
            controls=[
                self.title,
                ft.Divider(),
                ft.Row([self.week_selector, self.day_selector]),
                ft.Divider(),
            ],
            spacing=20
        )

        # Contenitore dinamico per i form
        self.form_container = ft.Column(spacing=20)

        # Pulsanti azione
        self.action_buttons = ft.Row(
            controls=[
                ft.ElevatedButton(
                    "📊 Analizza Settimana",
                    on_click=self.analyze_week,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.BLUE_600
                ),
                ft.ElevatedButton(
                    "📈 Report Completo",
                    on_click=self.show_report,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.GREEN_600
                ),
                ft.ElevatedButton(
                    "🗑️ Reset Dati",
                    on_click=self.reset_data,
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_600
                ),
            ],
            spacing=10
        )

        # Risultati
        self.results_container = ft.Column(spacing=10)

        # Aggiungi tutto alla pagina
        self.page.add(
            self.main_container,
            self.form_container,
            ft.Divider(),
            self.action_buttons,
            ft.Divider(),
            self.results_container
        )

    def update_ui(self):
        """Aggiorna l'interfaccia in base alla settimana selezionata."""
        self.form_container.controls.clear()

        if self.current_week == 1:
            self.setup_week1_form()
        elif self.current_week == 2:
            self.setup_week2_form()
        elif self.current_week == 3:
            self.setup_week3_form()

        self.page.update()

    def setup_week1_form(self):
        """Form per inserimento dati Settimana 1."""
        header = ft.Text("📊 Settimana 1 - Inserimento Performance",
                         size=18, weight=ft.FontWeight.BOLD)

        self.form_container.controls.append(header)

        # Form per ogni esercizio
        for esercizio_id, info in self.esercizi.items():
            card = self.create_performance_card(esercizio_id, info)
            self.form_container.controls.append(card)

    def setup_week2_form(self):
        """Form per inserimento dati Settimana 2."""
        header = ft.Text("📈 Settimana 2 - Performance + DOMS",
                         size=18, weight=ft.FontWeight.BOLD)

        self.form_container.controls.append(header)

        # Form performance
        for esercizio_id, info in self.esercizi.items():
            card = self.create_performance_card(esercizio_id, info)
            self.form_container.controls.append(card)

        # Form DOMS
        self.form_container.controls.append(
            ft.Text("💪 Valutazione DOMS", size=16, weight=ft.FontWeight.BOLD)
        )

        # Gruppi muscolari unici
        muscoli = list(set(info["muscolo"] for info in self.esercizi.values()))
        for muscolo in muscoli:
            doms_card = self.create_doms_card(muscolo)
            self.form_container.controls.append(doms_card)

    def setup_week3_form(self):
        """Form per inserimento dati Settimana 3."""
        header = ft.Text("🎯 Settimana 3 - Performance Finale",
                         size=18, weight=ft.FontWeight.BOLD)

        self.form_container.controls.append(header)

        # Form per ogni esercizio
        for esercizio_id, info in self.esercizi.items():
            card = self.create_performance_card(esercizio_id, info)
            self.form_container.controls.append(card)

    def create_performance_card(self, esercizio_id: int, info: dict) -> ft.Card:
        """Crea card per inserimento dati performance."""

        # Campi input
        mmc_field = ft.Dropdown(
            label="MMC",
            value="2",
            options=[ft.dropdown.Option(str(i), str(i)) for i in range(1, 4)],
            width=80
        )

        pump_field = ft.Dropdown(
            label="Pump",
            value="2",
            options=[ft.dropdown.Option(str(i), str(i)) for i in range(1, 4)],
            width=80
        )

        dolori_field = ft.Dropdown(
            label="Dolori",
            value="1",
            options=[ft.dropdown.Option(str(i), str(i)) for i in range(1, 4)],
            width=80
        )

        carico_field = ft.TextField(
            label="Carico (kg)",
            value="0",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        ripetizioni_field = ft.TextField(
            label="Ripetizioni",
            value="0",
            width=100,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        save_button = ft.ElevatedButton(
            "💾 Salva",
            on_click=lambda e: self.save_performance_data(
                esercizio_id, mmc_field, pump_field, dolori_field,
                carico_field, ripetizioni_field
            ),
            bgcolor=ft.Colors.BLUE_500,
            color=ft.Colors.WHITE
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"🏋️ {info['nome']} ({info['muscolo']})",
                            weight=ft.FontWeight.BOLD),
                    ft.Row([
                        mmc_field, pump_field, dolori_field,
                        carico_field, ripetizioni_field, save_button
                    ], spacing=10)
                ]),
                padding=15
            ),
            elevation=2
        )

    def create_doms_card(self, muscolo: str) -> ft.Card:
        """Crea card per inserimento DOMS."""

        doms_field = ft.Dropdown(
            label=f"DOMS {muscolo}",
            value="1",
            options=[ft.dropdown.Option(str(i), str(i)) for i in range(1, 4)],
            width=120
        )

        save_button = ft.ElevatedButton(
            "💾 Salva DOMS",
            on_click=lambda e: self.save_doms_data(muscolo, doms_field),
            bgcolor=ft.Colors.ORANGE_500,
            color=ft.Colors.WHITE
        )

        return ft.Card(
            content=ft.Container(
                content=ft.Row([
                    ft.Text(f"💪 {muscolo}", weight=ft.FontWeight.BOLD),
                    doms_field,
                    save_button
                ], spacing=10),
                padding=15
            ),
            elevation=2
        )

    def save_performance_data(self, esercizio_id: int, mmc_field, pump_field,
                              dolori_field, carico_field, ripetizioni_field):
        """Salva i dati di performance."""
        try:
            performance = PerformanceData(
                esercizio_id=esercizio_id,
                giorno=self.current_day,
                settimana=self.current_week,
                mmc=int(mmc_field.value),
                pump=int(pump_field.value),
                dolori_articolari=int(dolori_field.value),
                carico=float(carico_field.value),
                ripetizioni=int(ripetizioni_field.value)
            )

            self.algorithm.aggiungi_performance(self.current_week, performance)

            # Feedback visivo
            self.show_snackbar(f"✅ Dati salvati per {self.esercizi[esercizio_id]['nome']}")

        except ValueError as e:
            self.show_snackbar(f"❌ Errore: Inserisci valori numerici validi")

    def save_doms_data(self, muscolo: str, doms_field):
        """Salva i dati DOMS."""
        try:
            doms = DOMSData(
                muscolo=muscolo,
                giorno=self.current_day,
                settimana=self.current_week,
                doms_value=int(doms_field.value)
            )

            self.algorithm.aggiungi_doms(self.current_week, doms)

            # Feedback visivo
            self.show_snackbar(f"✅ DOMS salvato per {muscolo}")

        except ValueError as e:
            self.show_snackbar(f"❌ Errore: Valore DOMS non valido")

    def analyze_week(self, e):
        """Analizza la settimana corrente."""
        self.results_container.controls.clear()

        if self.current_week == 1:
            results = self.algorithm.calcola_sfr_settimana_1()
            self.show_week1_results(results)
        elif self.current_week == 2:
            improvements = self.algorithm.calcola_miglioramento_performance_settimana_2()
            points = self.algorithm.calcola_punti_performance_settimana_2()
            self.show_week2_results(improvements, points)
        elif self.current_week == 3:
            results = self.algorithm.calcola_sfr_settimana_3()
            self.show_week3_results(results)

        self.page.update()

    def show_week1_results(self, results: Dict[int, float]):
        """Mostra risultati Settimana 1."""
        header = ft.Text("📊 Risultati Settimana 1 - SFR",
                         size=18, weight=ft.FontWeight.BOLD)
        self.results_container.controls.append(header)

        for esercizio_id, sfr in results.items():
            nome = self.esercizi[esercizio_id]["nome"]
            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text(f"🏋️ {nome}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"SFR: {sfr:.2f}", color=ft.Colors.BLUE_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=2
            )
            self.results_container.controls.append(card)

    def show_week2_results(self, improvements: Dict[int, float], points: Dict[int, int]):
        """Mostra risultati Settimana 2."""
        header = ft.Text("📈 Risultati Settimana 2 - Miglioramento",
                         size=18, weight=ft.FontWeight.BOLD)
        self.results_container.controls.append(header)

        for esercizio_id, improvement in improvements.items():
            nome = self.esercizi[esercizio_id]["nome"]
            point = points.get(esercizio_id, 0)

            # Colore in base al miglioramento
            color = ft.Colors.GREEN if improvement > 0 else ft.Colors.RED if improvement < 0 else ft.Colors.ORANGE

            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text(f"🏋️ {nome}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{improvement:+.1f}%", color=color),
                        ft.Text(f"Punti: {point:+d}", color=color)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=2
            )
            self.results_container.controls.append(card)

        # Raccomandazioni serie
        self.show_series_recommendations()

    def show_week3_results(self, results: Dict[int, float]):
        """Mostra risultati Settimana 3."""
        header = ft.Text("🎯 Risultati Settimana 3 - SFR Finale",
                         size=18, weight=ft.FontWeight.BOLD)
        self.results_container.controls.append(header)

        for esercizio_id, sfr in results.items():
            nome = self.esercizi[esercizio_id]["nome"]
            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text(f"🏋️ {nome}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"SFR: {sfr:.2f}", color=ft.Colors.BLUE_600)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=2
            )
            self.results_container.controls.append(card)

    def show_series_recommendations(self):
        """Mostra raccomandazioni serie per settimana 3."""
        header = ft.Text("💡 Raccomandazioni Serie Settimana 3",
                         size=16, weight=ft.FontWeight.BOLD)
        self.results_container.controls.append(header)

        # Gruppi muscolari unici
        muscoli = list(set(info["muscolo"] for info in self.esercizi.values()))

        for muscolo in muscoli:
            raccomandazione = self.algorithm.calcola_serie_settimana_3(muscolo)

            # Colore in base alla raccomandazione
            if "+" in raccomandazione:
                color = ft.Colors.GREEN
                icon = "📈"
            elif "-" in raccomandazione:
                color = ft.Colors.RED
                icon = "📉"
            else:
                color = ft.Colors.ORANGE
                icon = "➡️"

            card = ft.Card(
                content=ft.Container(
                    content=ft.Row([
                        ft.Text(f"{icon} {muscolo}", weight=ft.FontWeight.BOLD),
                        ft.Text(raccomandazione, color=color, weight=ft.FontWeight.BOLD)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=15
                ),
                elevation=2
            )
            self.results_container.controls.append(card)

    def show_report(self, e):
        """Mostra report completo."""
        report = self.algorithm.genera_report_completo()

        # Finestra di dialogo per il report
        dialog = ft.AlertDialog(
            title=ft.Text("📋 Report Completo"),
            content=ft.Container(
                content=ft.Text(report, selectable=True),
                width=600,
                height=400
            ),
            actions=[
                ft.TextButton("Chiudi", on_click=lambda e: self.close_dialog())
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def reset_data(self, e):
        """Reset di tutti i dati."""
        self.algorithm = TrainingAlgorithm()
        self.results_container.controls.clear()
        self.show_snackbar("🗑️ Dati resettati")
        self.page.update()

    def on_week_change(self, e):
        """Gestisce il cambio settimana."""
        self.current_week = int(e.control.value)
        self.update_ui()

    def on_day_change(self, e):
        """Gestisce il cambio giorno."""
        self.current_day = int(e.control.value)

    def close_dialog(self):
        """Chiude la finestra di dialogo."""
        self.page.dialog.open = False
        self.page.update()

    def show_snackbar(self, message: str):
        """Mostra snackbar con messaggio."""
        snackbar = ft.SnackBar(content=ft.Text(message))
        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()


def main(page: ft.Page):
    """Funzione main per Flet."""
    gui = TrainingGUI(page)


if __name__ == "__main__":
    ft.app(target=main)

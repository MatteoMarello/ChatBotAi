import flet as ft
from creascheda import Model as CreaSchedaModel
from adattaScheda import TrainingAlgorithm, PerformanceData
from model.workoutday import WorkoutDay
from model.esercizio import Esercizio
from model.trainingweek import TrainingWeek


def main(page: ft.Page):
    page.title = "Generatore Schede Allenamento"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # Modello per creare la scheda
    crea_scheda_model = CreaSchedaModel()

    # --- Elementi UI ---

    dd_esperienza = ft.Dropdown(
        label="Esperienza",
        options=[
            ft.dropdown.Option("principiante"),
            ft.dropdown.Option("intermedio"),
        ],
        value="intermedio"
    )

    dd_obiettivo = ft.Dropdown(
        label="Obiettivo (non usato attualmente)",
        options=[
            ft.dropdown.Option("ipertrofia"),
            ft.dropdown.Option("dimagrimento"),
        ],
        value="ipertrofia",
        disabled=True
    )

    dd_muscolo_target = ft.Dropdown(
        label="Muscolo Target",
        options=[ft.dropdown.Option(m) for m in crea_scheda_model.split_muscoli["Full Body"]]
    )

    dd_frequenza = ft.Dropdown(
        label="Frequenza Settimanale",
        options=[ft.dropdown.Option("3"), ft.dropdown.Option("4")]  # Default per intermedio
    )

    btn_crea_scheda = ft.ElevatedButton(text="Crea Scheda", on_click=None)

    # Vista principale: contenitore per la scheda
    scheda_view = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    # --- Logica di Interazione ---

    def aggiorna_frequenza(e):
        """Aggiorna le opzioni di frequenza in base all'esperienza."""
        if dd_esperienza.value == "principiante":
            dd_frequenza.options = [ft.dropdown.Option("2"), ft.dropdown.Option("3")]
            dd_frequenza.value = "3"
        else:  # intermedio
            dd_frequenza.options = [ft.dropdown.Option("3"), ft.dropdown.Option("4")]
            dd_frequenza.value = "3"
        page.update()

    dd_esperienza.on_change = aggiorna_frequenza

    def crea_scheda_click(e):
        """
        Handler per il click del pulsante "Crea Scheda".
        Genera la scheda e la visualizza.
        """
        if not all([dd_esperienza.value, dd_muscolo_target.value, dd_frequenza.value]):
            page.snack_bar = ft.SnackBar(content=ft.Text("Per favore, compila tutti i campi!"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        btn_crea_scheda.disabled = True
        page.update()

        # Logica di creazione scheda
        try:
            # Per ora l'algoritmo è più robusto per intermedio
            if dd_esperienza.value == "intermedio":
                training_week = crea_scheda_model.getSchedaFullBodyIntermedio(
                    context="Palestra Completa",  # Contesto fisso per il mock DAO
                    muscolo_target=dd_muscolo_target.value,
                    giorni=int(dd_frequenza.value)
                )
            else:
                # TODO: Implementare una logica specifica per principianti se diversa
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Logica per principianti non ancora implementata, uso intermedio."),
                    bgcolor=ft.Colors.ORANGE)
                page.snack_bar.open = True
                training_week = crea_scheda_model.getSchedaFullBodyIntermedio(
                    context="Palestra Completa",
                    muscolo_target=dd_muscolo_target.value,
                    giorni=int(dd_frequenza.value)
                )

            # Salva la scheda e inizializza l'algoritmo nella sessione della pagina
            page.session.set("training_week", training_week)
            page.session.set("training_algorithm", TrainingAlgorithm())

            # Nasconde la form di creazione e mostra la scheda
            config_view.visible = False
            visualizza_giorno(0)  # Mostra il primo giorno

        except Exception as ex:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Errore nella creazione: {ex}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True

        btn_crea_scheda.disabled = False
        page.update()

    btn_crea_scheda.on_click = crea_scheda_click

    def crea_card_esercizio(esercizio: Esercizio, log: dict, settimana: int, giorno: int):
        """Crea una Card Flet per un singolo esercizio con i campi di input."""

        # Questi controlli conterranno i dati di performance
        txt_carico = ft.TextField(label="Carico (kg)", width=120, keyboard_type=ft.KeyboardType.NUMBER)
        txt_ripetizioni = ft.TextField(label="Reps Fatte", width=120, keyboard_type=ft.KeyboardType.NUMBER)

        radio_mmc = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")
        ]), value="2")

        radio_pump = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")
        ]), value="2")

        radio_dolori = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="1", label="1"), ft.Radio(value="2", label="2"), ft.Radio(value="3", label="3")
        ]), value="1")

        # Associa i controlli all'ID dell'esercizio per recuperarli dopo
        card = ft.Card(
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
            # Salva i dati necessari per creare l'oggetto PerformanceData
            data={
                "esercizio_id": esercizio.id,
                "settimana": settimana,
                "giorno": giorno,
                "controls": {
                    "carico": txt_carico, "ripetizioni": txt_ripetizioni,
                    "mmc": radio_mmc, "pump": radio_pump, "dolori": radio_dolori
                }
            }
        )
        return card

    def salva_performance_giorno(e):
        """Raccoglie i dati dalle card, li salva nell'algoritmo e passa al giorno successivo."""

        algo: TrainingAlgorithm = page.session.get("training_algorithm")

        for card in scheda_view.controls:
            if isinstance(card, ft.Card):
                data = card.data
                controls = data["controls"]

                # Validazione input
                try:
                    carico_val = float(controls["carico"].value)
                    reps_val = int(controls["ripetizioni"].value)
                    mmc_val = int(controls["mmc"].value)
                    pump_val = int(controls["pump"].value)
                    dolori_val = int(controls["dolori"].value)
                except (ValueError, TypeError):
                    page.snack_bar = ft.SnackBar(ft.Text(
                        f"Dati non validi per l'esercizio ID {data['esercizio_id']}. Compila tutto correttamente.",
                        bgcolor=ft.Colors.RED))
                    page.snack_bar.open = True
                    page.update()
                    return

                performance = PerformanceData(
                    esercizio_id=data["esercizio_id"],
                    giorno=data["giorno"],
                    settimana=data["settimana"],
                    carico=carico_val,
                    ripetizioni=reps_val,
                    mmc=mmc_val,
                    pump=pump_val,
                    dolori_articolari=dolori_val
                )

                algo.aggiungi_performance(data["settimana"], performance)

        page.session.set("training_algorithm", algo)

        page.snack_bar = ft.SnackBar(ft.Text(f"Performance del giorno salvate!", bgcolor=ft.Colors.GREEN))
        page.snack_bar.open = True

        # Passa al giorno successivo
        current_day_idx = page.session.get("current_day_index")
        training_week: TrainingWeek = page.session.get("training_week")

        if current_day_idx < len(training_week.workout_days) - 1:
            visualizza_giorno(current_day_idx + 1)
        else:
            # Fine settimana
            scheda_view.controls.clear()
            scheda_view.controls.append(
                ft.Text("Hai completato la settimana! Premi 'Nuova Scheda' per ricominciare.", size=20,
                        text_align=ft.TextAlign.CENTER))
            config_view.visible = True  # Mostra di nuovo la config
            page.update()

    def visualizza_giorno(giorno_idx: int):
        """Pulisce la vista e mostra gli esercizi per il giorno specificato."""

        page.session.set("current_day_index", giorno_idx)
        training_week = page.session.get("training_week")

        if not training_week or giorno_idx >= len(training_week.workout_days):
            return

        giorno_allenamento: WorkoutDay = training_week.workout_days[giorno_idx]

        scheda_view.controls.clear()

        titolo_giorno = ft.Text(f"GIORNO {giorno_allenamento.id_giorno} - {giorno_allenamento.split_type}", size=24,
                                weight=ft.FontWeight.BOLD)
        scheda_view.controls.append(titolo_giorno)

        if not giorno_allenamento.esercizi:
            scheda_view.controls.append(ft.Text("Oggi è giorno di riposo! 😴", size=18))
        else:
            for esercizio in giorno_allenamento.esercizi:
                log_esercizio = giorno_allenamento.performance_log.get(esercizio.id, {})
                card = crea_card_esercizio(esercizio, log_esercizio, training_week.numero_settimana,
                                           giorno_allenamento.id_giorno)
                scheda_view.controls.append(card)

            btn_salva = ft.ElevatedButton("Salva Performance e Vai al Prossimo Giorno",
                                          on_click=salva_performance_giorno, icon=ft.Icons.SAVE)
            scheda_view.controls.append(btn_salva)

        page.update()

    # --- Layout Iniziale ---

    config_view = ft.Column(
        [
            ft.Text("Configura il tuo Allenamento", size=24, weight=ft.FontWeight.BOLD),
            dd_esperienza,
            dd_obiettivo,
            dd_muscolo_target,
            dd_frequenza,
            ft.Container(height=20),
            btn_crea_scheda,
        ],
        width=400,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    page.add(config_view, scheda_view)


# Avvia l'applicazione Flet
ft.app(target=main, assets_dir="assets")

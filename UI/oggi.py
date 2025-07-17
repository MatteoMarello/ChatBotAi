import flet as ft
from datetime import datetime

def main(page: ft.Page):
    # Configurazione della pagina
    page.title = "Coach Virtuale - Allenamento Oggi"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#667eea"
    page.padding = 0
    page.fonts = {
        "SegoeUI": "https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap"
    }

    # Stili come TextStyle (corretto!)
    HEADER_STYLE = {
        "style": ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color="#2c3e50", font_family="SegoeUI")
    }

    SECTION_TITLE_STYLE = {
        "style": ft.TextStyle(size=18, weight=ft.FontWeight.W_600, color="#2E8B57", font_family="SegoeUI")
    }

    TEXT_STYLE = {
        "size": 14,
        "color": "#555",
        "font_family": "SegoeUI"
    }

    # Funzione per creare campi feedback
    def create_feedback_field(hint_text):
        return ft.TextField(
            multiline=True,
            min_lines=3,
            hint_text=hint_text,
            border_radius=10,
            border_color="#ddd",
            focused_border_color="#2E8B57",
            content_padding=15
        )

    # Funzione feedback veloce
    def set_quick_feedback(text):
        pre_workout_feedback.value = text
        page.update()

    # Header
    header = ft.Row([
        ft.Icon(name=ft.Icons.FITNESS_CENTER, color="#2E8B57", size=28),
        ft.Text(" ALLENAMENTO OGGI", **HEADER_STYLE)
    ], spacing=10)

    date_display = ft.Text("Mercoledì 9 Luglio - Pull Day", color="#666", size=16)

    # Feedback pre-allenamento
    pre_workout_feedback = create_feedback_field("Scrivi qui il tuo stato... es: 'Ho dormito poco e sono stanco' o 'Mi sento carico!'")

    quick_feedback_buttons = ft.Row([
        ft.OutlinedButton("😴 Stanco", on_click=lambda e: set_quick_feedback("😴 Sono stanco oggi")),
        ft.OutlinedButton("🔥 Carico", on_click=lambda e: set_quick_feedback("🔥 Mi sento carico!")),
        ft.OutlinedButton("⏰ Poco tempo", on_click=lambda e: set_quick_feedback("⏰ Ho solo 30 minuti")),
        ft.OutlinedButton("💪 Normale", on_click=lambda e: set_quick_feedback("💪 Tutto normale")),
    ], wrap=True, spacing=10, run_spacing=10)

    adapt_button = ft.ElevatedButton(
        "ADATTA ALLENAMENTO 🎯",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        )
    )

    feedback_pre_section = ft.Container(
        content=ft.Column([
            ft.Text("💬 COME TI SENTI OGGI?", **SECTION_TITLE_STYLE),
            pre_workout_feedback,
            quick_feedback_buttons,
            adapt_button
        ], spacing=15),
        bgcolor="#f0f8ff",
        border_radius=15,
        padding=20,
        border=ft.border.all(2, "#87CEEB")
    )

    # Esercizi
    exercises = [
        ("Trazioni 4x6-8", "ex1"),
        ("Rematore 3x10-12", "ex2"),
        ("Bicep curl 3x12-15", "ex3")
    ]

    exercise_checkboxes = ft.Column([
        ft.Checkbox(label=ex[0], label_style=ft.TextStyle(**TEXT_STYLE), fill_color="#2E8B57", check_color=ft.Colors.WHITE)
        for ex in exercises
    ], spacing=10)

    exercises_section = ft.Container(
        content=ft.Column([
            ft.Text("📋 ESERCIZI DI OGGI:", **SECTION_TITLE_STYLE),
            exercise_checkboxes
        ], spacing=15),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20
    )

    start_button = ft.ElevatedButton(
        "INIZIA ALLENAMENTO 🚀",
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=10)
        ),
        width=400
    )

    # Feedback post-allenamento
    post_workout_feedback = create_feedback_field("Come è andato oggi? es: 'Troppo facile' o 'Perfetto' o 'Molto impegnativo'")

    feedback_post_section = ft.Container(
        content=ft.Column([
            ft.Text("💭 FEEDBACK POST-ALLENAMENTO", **SECTION_TITLE_STYLE),
            post_workout_feedback,
            ft.ElevatedButton(
                "SALVA FEEDBACK 📝",
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    padding=20,
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
        ], spacing=15),
        bgcolor="#f0f8ff",
        border_radius=15,
        padding=20,
        border=ft.border.all(2, "#87CEEB")
    )

    # Layout
    content = ft.Column([
        header,
        date_display,
        feedback_pre_section,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        exercises_section,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        ft.Row([start_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        feedback_post_section
    ], spacing=10, scroll=ft.ScrollMode.AUTO)

    main_container = ft.Container(
        content=content,
        width=500,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=30,
        margin=20
    )

    page.add(
        ft.Container(
            content=main_container,
            alignment=ft.alignment.center,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=["#667eea", "#764ba2"]
            ),
            expand=True
        )
    )

ft.app(target=main)

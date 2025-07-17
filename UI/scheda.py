import flet as ft
from datetime import datetime


def main(page: ft.Page):
    # Configurazione della pagina
    page.title = "Coach Virtuale - La Mia Scheda"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#667eea"
    page.padding = 0
    page.fonts = {
        "SegoeUI": "https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap"
    }

    # Stili
    HEADER_STYLE = {
        "size": 24,
        "weight": ft.FontWeight.BOLD,
        "color": "#2c3e50",
        "font_family": "SegoeUI"
    }

    DAY_TITLE_STYLE = {
        "size": 18,
        "weight": ft.FontWeight.W_600,
        "color": "#2E8B57",
        "font_family": "SegoeUI"
    }

    EXERCISE_STYLE = {
        "color": "#555",
        "size": 14,
        "font_family": "SegoeUI"
    }

    # Componenti
    week_indicator = ft.Container(
        content=ft.Row([
            ft.Icon(name=ft.Icons.CALENDAR_TODAY, color="#2E8B57"),
            ft.Text(" Settimana corrente (2/4)", color="#2E8B57", weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.CENTER),
        bgcolor=ft.Colors.with_opacity(0.1, "#2E8B57"),
        padding=15,
        border_radius=10,
        margin=ft.margin.only(bottom=20)
    )

    # Sezione Lunedì
    monday_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(name=ft.Icons.FITNESS_CENTER, color="#2E8B57"),
                ft.Text(" LUNEDÌ - Push (Upper)", **DAY_TITLE_STYLE)
            ]),
            ft.Column([
                ft.Text("├─ Panca piana 4x8-10", **EXERCISE_STYLE),
                ft.Text("├─ Spinte manubri 3x10-12", **EXERCISE_STYLE),
                ft.Text("├─ Dip 3x8-10", **EXERCISE_STYLE),
                ft.Text("└─ Tricep extension 3x12-15", **EXERCISE_STYLE)
            ], spacing=4)
        ], spacing=12),
        bgcolor="#f8f9fa",
        border_radius=15,
        padding=20,
        border=ft.border.only(left=ft.border.BorderSide(4, "#2E8B57")),
        margin=ft.margin.only(bottom=15)
    )

    # Sezione Mercoledì
    wednesday_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(name=ft.Icons.FITNESS_CENTER, color="#2E8B57"),
                ft.Text(" MERCOLEDÌ - Pull (Upper)", **DAY_TITLE_STYLE)
            ]),
            ft.Column([
                ft.Text("├─ Trazioni 4x6-8", **EXERCISE_STYLE),
                ft.Text("├─ Rematore 3x10-12", **EXERCISE_STYLE),
                ft.Text("└─ Bicep curl 3x12-15", **EXERCISE_STYLE)
            ], spacing=4)
        ], spacing=12),
        bgcolor="#f8f9fa",
        border_radius=15,
        padding=20,
        border=ft.border.only(left=ft.border.BorderSide(4, "#2E8B57")),
        margin=ft.margin.only(bottom=15)
    )

    # Sezione Venerdì
    friday_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(name=ft.Icons.FITNESS_CENTER, color="#2E8B57"),
                ft.Text(" VENERDÌ - Legs", **DAY_TITLE_STYLE)
            ]),
            ft.Column([
                ft.Text("├─ Squat 4x8-10", **EXERCISE_STYLE),
                ft.Text("├─ Stacchi 3x8-10", **EXERCISE_STYLE),
                ft.Text("└─ Calf raises 3x15-20", **EXERCISE_STYLE)
            ], spacing=4)
        ], spacing=12),
        bgcolor="#f8f9fa",
        border_radius=15,
        padding=20,
        border=ft.border.only(left=ft.border.BorderSide(4, "#2E8B57"))
    )

    # Pulsanti
    buttons = ft.Row([
        ft.ElevatedButton(
            "MODIFICA SCHEDA",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        ),
        ft.ElevatedButton(
            "RIGENERA",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    # Schermata principale
    scheda_screen = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(name=ft.Icons.LIST_ALT, color="#2E8B57", size=28),
                ft.Text(" LA MIA SCHEDA", **HEADER_STYLE)
            ], spacing=10),

            week_indicator,
            monday_section,
            wednesday_section,
            friday_section,

            ft.Divider(height=30),

            buttons
        ], scroll=ft.ScrollMode.AUTO),
        width=500,
        bgcolor=ft.Colors.WHITE,
        border_radius=20,
        padding=30,
        margin=20
    )

    page.add(
        ft.Container(
            content=scheda_screen,
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

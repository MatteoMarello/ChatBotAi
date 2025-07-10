import flet as ft

def main(page: ft.Page):
    page.title = "Coach Virtuale - I Miei Progressi"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#667eea"
    page.padding = 0
    page.fonts = {
        "SegoeUI": "https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap"
    }

    # Stili corretti
    HEADER_STYLE = {
        "style": ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color="#2C3E50", font_family="SegoeUI")
    }

    SECTION_TITLE_STYLE = {
        "style": ft.TextStyle(size=18, weight=ft.FontWeight.W_600, color="#2E8B57", font_family="SegoeUI")
    }

    TEXT_STYLE = {
        "size": 14,
        "color": "#555",
        "font_family": "SegoeUI"
    }

    header = ft.Row([
        ft.Icon(name=ft.Icons.TRENDING_UP, color="#2E8B57", size=28),
        ft.Text(" I MIEI PROGRESSI", **HEADER_STYLE)
    ], spacing=10)

    stats_row = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("12", style=ft.TextStyle(size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
                ft.Text("🔥 Streak giorni", style=ft.TextStyle(color=ft.Colors.WHITE, size=14, font_family="SegoeUI"), opacity=0.9)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.8, "#667eea"),
            border_radius=15,
            padding=20,
            expand=True
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("2/3", style=ft.TextStyle(size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)),
                ft.Text("📊 Questa settimana", style=ft.TextStyle(color=ft.Colors.WHITE, size=14, font_family="SegoeUI"), opacity=0.9)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.8, "#667eea"),
            border_radius=15,
            padding=20,
            expand=True
        )
    ], spacing=15)

    strength_progress = [
        ("Panca piana", "65kg → 70kg (+5kg) 📈"),
        ("Squat", "80kg → 85kg (+5kg) 📈"),
        ("Trazioni", "6 → 8 reps (+2) 📈")
    ]

    strength_section = ft.Container(
        content=ft.Column([
            ft.Text("💪 FORZA (ultimi 30 giorni)", **SECTION_TITLE_STYLE),
            *[
                ft.Row([
                    ft.Text(item[0], style=ft.TextStyle(**TEXT_STYLE)),
                    ft.Text(item[1], style=ft.TextStyle(color="#32CD32", weight=ft.FontWeight.BOLD))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                for item in strength_progress
            ]
        ], spacing=15),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20
    )

    workout_history = [
        ("9 Lug - Pull Day ✅", "(45 min)"),
        ("7 Lug - Push Day ✅", "(50 min)"),
        ("5 Lug - Legs Day ✅", "(40 min)"),
        ("3 Lug - Pull Day ✅", "(42 min)")
    ]

    history_section = ft.Container(
        content=ft.Column([
            ft.Text("📅 STORICO ALLENAMENTI", **SECTION_TITLE_STYLE),
            *[
                ft.Row([
                    ft.Text(item[0], style=ft.TextStyle(**TEXT_STYLE)),
                    ft.Text(item[1], style=ft.TextStyle(color="#666"))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                for item in workout_history
            ]
        ], spacing=12),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20
    )

    action_buttons = ft.Row([
        ft.ElevatedButton(
            "ESPORTA DATI",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        ),
        ft.ElevatedButton(
            "STATISTICHE",
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.ORANGE,
                color=ft.Colors.WHITE,
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    content = ft.Column([
        header,
        stats_row,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        strength_section,
        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
        history_section,
        ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
        action_buttons
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

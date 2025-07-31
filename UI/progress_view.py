import flet as ft
from typing import Dict, List, Tuple
from collections import defaultdict

# Colori per i grafici - Palette moderna
CHART_COLORS = [
    "#4f46e5",  # Indigo vivace
    "#06b6d4",  # Cyan
    "#10b981",  # Emerald
    "#f59e0b",  # Amber
    "#ef4444",  # Red
    "#8b5cf6",  # Violet
    "#ec4899",  # Pink
    "#84cc16"  # Lime
]

# Gradiente per miglioramenti positivi/negativi
IMPROVEMENT_COLORS = {
    'positive': "#10b981",  # Verde emerald
    'negative': "#ef4444",  # Rosso
    'neutral': "#6b7280"  # Grigio
}


class ProgressView(ft.Container):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.expand = True
        self.padding = 20

        # Tema dark moderno
        self.colors = {
            'primary': '#4f46e5',
            'secondary': '#06b6d4',
            'surface': '#0f172a',
            'surface_light': '#1e293b',
            'surface_lighter': '#334155',
            'text_primary': '#f8fafc',
            'text_secondary': '#94a3b8',
            'text_muted': '#64748b',
            'border': '#334155',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'accent': '#8b5cf6'
        }

        # Header con design moderno
        self.header = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.TRENDING_UP_ROUNDED,
                        size=32,
                        color=self.colors['primary']
                    ),
                    ft.Text(
                        "Dashboard Progressi",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']
                    )
                ], spacing=12, alignment=ft.MainAxisAlignment.START),
                ft.Text(
                    "Monitora i tuoi miglioramenti settimanali e il volume di allenamento",
                    size=16,
                    color=self.colors['text_secondary'],
                    italic=True
                )
            ], spacing=8),
            padding=ft.padding.symmetric(vertical=20, horizontal=24),
            bgcolor=self.colors['surface'],
            border_radius=16,
            border=ft.border.all(1, self.colors['border']),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4)
            )
        )

        self.chart_container = ft.Column(
            spacing=24,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        self.content = ft.Column([
            self.header,
            self.chart_container
        ], spacing=24, scroll=ft.ScrollMode.AUTO, expand=True)

    def update_view(self, wow_improvement_data: Dict[str, List[Tuple[int, float]]],
                    volume_data: Dict[int, Dict[str, int]]):
        """Aggiorna la vista con i grafici migliorati."""
        self.chart_container.controls.clear()
        has_content = False

        if wow_improvement_data:
            self._crea_grafico_miglioramento_moderno(wow_improvement_data)
            has_content = True

        if volume_data and any(volume_data.values()):
            self._crea_grafico_volume_moderno(volume_data)
            has_content = True

        if not has_content:
            self._show_empty_state()

        self.update()

    def _show_empty_state(self):
        """Stato vuoto con design moderno."""
        empty_state = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.INSIGHTS_ROUNDED,
                        size=80,
                        color=self.colors['text_muted']
                    ),
                    padding=20,
                    bgcolor=self.colors['surface_light'],
                    border_radius=50,
                ),
                ft.Text(
                    "Nessun dato disponibile",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['text_primary'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Text(
                    "Completa almeno due settimane di allenamento\nper visualizzare i tuoi progressi!",
                    size=16,
                    color=self.colors['text_secondary'],
                    text_align=ft.TextAlign.CENTER
                )
            ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=60,
            bgcolor=self.colors['surface'],
            border_radius=20,
            border=ft.border.all(2, self.colors['border']),
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 6)
            )
        )
        self.chart_container.controls.append(empty_state)

    def _crea_grafico_miglioramento_moderno(self, wow_improvement_data: Dict[str, List[Tuple[int, float]]]):
        """Crea un grafico miglioramento con design moderno."""

        # Preparazione dati
        exercises = sorted(wow_improvement_data.keys())
        if not exercises:
            return

        data_by_week = defaultdict(list)
        for exercise, changes in wow_improvement_data.items():
            for week, change in changes:
                data_by_week[week].append((exercise, change))

        sorted_weeks = sorted(data_by_week.keys())
        if not sorted_weeks:
            return

        all_values = [change for changes in wow_improvement_data.values() for _, change in changes]

        # Creazione gruppi di barre con colori dinamici
        bar_groups = []
        for week in sorted_weeks:
            changes_in_week = data_by_week[week]
            rods = []

            sorted_changes = sorted(changes_in_week, key=lambda item: exercises.index(item[0]))

            for i, (exercise, change) in enumerate(sorted_changes):
                # Colore basato sul miglioramento
                if change > 5:
                    color = IMPROVEMENT_COLORS['positive']
                elif change < -2:
                    color = IMPROVEMENT_COLORS['negative']
                else:
                    color = CHART_COLORS[i % len(CHART_COLORS)]

                rods.append(
                    ft.BarChartRod(
                        from_y=0,
                        to_y=change,
                        width=max(12, 50 // len(exercises)),
                        color=color,
                        tooltip=f"📈 {exercise.split('(')[-1].strip(')')}\nSettimana {week}: {change:+.1f}%",
                        border_radius=6,
                        # Effetto gradiente simulato con bordo
                        border_side=ft.BorderSide(
                            width=1,
                            color=ft.Colors.with_opacity(0.3, ft.Colors.WHITE)
                        )
                    )
                )

            if rods:
                bar_groups.append(
                    ft.BarChartGroup(
                        x=week,
                        bar_rods=rods,
                        bars_space=6
                    )
                )

        # Calcolo limiti assi
        min_y = min(-5, min(all_values) if all_values else -5)
        max_y = max(15, max(all_values) if all_values else 15)
        y_padding = (abs(max_y) + abs(min_y)) * 0.15

        # Creazione grafico con stile moderno
        max_week = max(sorted_weeks) if sorted_weeks else 1
        chart = ft.BarChart(
            bar_groups=bar_groups,
            height=380,
            left_axis=ft.ChartAxis(
                title=ft.Text(
                    "Miglioramento %",
                    color=self.colors['text_secondary'],
                    size=14,
                    weight=ft.FontWeight.W_500
                ),
                labels_size=32,
                show_labels=True,
            ),
            bottom_axis=ft.ChartAxis(
                title=ft.Text(
                    "Settimana",
                    color=self.colors['text_secondary'],
                    size=14,
                    weight=ft.FontWeight.W_500
                ),
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(
                            f"W{i}",
                            color=self.colors['text_secondary'],
                            size=12,
                            weight=ft.FontWeight.W_500
                        )
                    )
                    for i in range(2, max(6, max_week + 2))
                ],
                labels_size=28,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.1, self.colors['text_secondary']),
                width=1,
                interval=5
            ),
            min_y=min_y - y_padding,
            max_y=max_y + y_padding,
            expand=True,
            tooltip_bgcolor=self.colors['surface_lighter'],
            groups_space=40,
            bgcolor=self.colors['surface']
        )

        # Legenda migliorata
        legend_items = []
        for i, exercise in enumerate(exercises):
            exercise_name = exercise.split('(')[-1].strip(')')
            legend_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=16,
                            height=16,
                            bgcolor=CHART_COLORS[i % len(CHART_COLORS)],
                            border_radius=8,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=4,
                                color=ft.Colors.with_opacity(0.3, CHART_COLORS[i % len(CHART_COLORS)]),
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Text(
                            exercise_name,
                            color=self.colors['text_primary'],
                            size=13,
                            weight=ft.FontWeight.W_500
                        )
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=self.colors['surface_light'],
                    border_radius=20,
                    border=ft.border.all(1, self.colors['border'])
                )
            )

        # Container principale del grafico
        improvement_chart = ft.Container(
            content=ft.Column([
                # Header della sezione
                ft.Row([
                    ft.Icon(
                        ft.Icons.TRENDING_UP_ROUNDED,
                        color=self.colors['success'],
                        size=24
                    ),
                    ft.Column([
                        ft.Text(
                            "Miglioramenti Settimanali",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors['text_primary']
                        ),
                        ft.Text(
                            "Variazione % del massimale stimato (1RM)",
                            size=14,
                            color=self.colors['text_secondary']
                        )
                    ], spacing=2, expand=True)
                ], spacing=12),

                ft.Divider(color=self.colors['border'], height=1),

                chart,

                # Legenda con layout migliorato
                ft.Container(
                    content=ft.Row(
                        controls=legend_items,
                        spacing=12,
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(top=16)
                )
            ], spacing=16),
            padding=24,
            bgcolor=self.colors['surface'],
            border_radius=16,
            border=ft.border.all(1, self.colors['border']),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 6)
            )
        )

        self.chart_container.controls.append(improvement_chart)

    def _crea_grafico_volume_moderno(self, volume_data: Dict[int, Dict[str, int]]):
        """Crea il grafico volume con design moderno."""
        muscoli = sorted(list(set(
            m for week_vols in volume_data.values() for m in week_vols.keys()
        )))
        settimane = sorted(volume_data.keys())

        if not muscoli or not settimane:
            return

        # Mappa colori con gradiente
        color_map = {
            sett: CHART_COLORS[i % len(CHART_COLORS)]
            for i, sett in enumerate(settimane)
        }

        # Creazione barre con stile moderno
        bar_groups = []
        for i, muscolo in enumerate(muscoli):
            rods = []
            settimane_con_dati = [
                s for s in settimane
                if volume_data.get(s, {}).get(muscolo, 0) > 0
            ]

            if not settimane_con_dati:
                continue

            num_rods = len(settimane_con_dati)
            width = max(8, 32 // num_rods) if num_rods > 0 else 12

            for sett in settimane_con_dati:
                volume = volume_data[sett][muscolo]
                rods.append(
                    ft.BarChartRod(
                        from_y=0,
                        to_y=volume,
                        width=width,
                        color=color_map[sett],
                        tooltip=f"💪 {muscolo}\nSettimana {sett}: {volume} serie",
                        border_radius=4,
                        border_side=ft.BorderSide(
                            width=1,
                            color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE)
                        )
                    )
                )

            if rods:
                bar_groups.append(
                    ft.BarChartGroup(
                        x=i,
                        bar_rods=rods,
                        bars_space=4
                    )
                )

        # Grafico volume
        chart = ft.BarChart(
            bar_groups=bar_groups,
            expand=True,
            height=380,
            left_axis=ft.ChartAxis(
                labels_size=32,
                title=ft.Text(
                    "Serie Totali",
                    color=self.colors['text_secondary'],
                    size=14,
                    weight=ft.FontWeight.W_500
                ),
                labels_interval=5
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(
                            muscolo[:6] + "." if len(muscolo) > 6 else muscolo,
                            color=self.colors['text_secondary'],
                            size=11,
                            weight=ft.FontWeight.W_500
                        )
                    )
                    for i, muscolo in enumerate(muscoli)
                ],
                labels_size=28,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=5,
                color=ft.Colors.with_opacity(0.1, self.colors['text_secondary']),
                width=1
            ),
            bgcolor=self.colors['surface']
        )

        # Legenda settimane
        legend_items = [
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        width=16,
                        height=16,
                        bgcolor=color_map[sett],
                        border_radius=8,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=4,
                            color=ft.Colors.with_opacity(0.3, color_map[sett]),
                            offset=ft.Offset(0, 2)
                        )
                    ),
                    ft.Text(
                        f"Settimana {sett}",
                        color=self.colors['text_primary'],
                        size=13,
                        weight=ft.FontWeight.W_500
                    )
                ], spacing=8),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=self.colors['surface_light'],
                border_radius=20,
                border=ft.border.all(1, self.colors['border'])
            )
            for sett in settimane
        ]

        # Container volume
        volume_chart = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(
                        ft.Icons.FITNESS_CENTER_ROUNDED,
                        color=self.colors['secondary'],
                        size=24
                    ),
                    ft.Column([
                        ft.Text(
                            "Volume di Allenamento",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=self.colors['text_primary']
                        ),
                        ft.Text(
                            "Serie totali per gruppo muscolare",
                            size=14,
                            color=self.colors['text_secondary']
                        )
                    ], spacing=2, expand=True)
                ], spacing=12),

                ft.Divider(color=self.colors['border'], height=1),

                chart,

                ft.Container(
                    content=ft.Row(
                        controls=legend_items,
                        spacing=12,
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=ft.padding.only(top=16)
                )
            ], spacing=16),
            padding=24,
            bgcolor=self.colors['surface'],
            border_radius=16,
            border=ft.border.all(1, self.colors['border']),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 6)
            )
        )

        self.chart_container.controls.append(volume_chart)

    def show_error(self, message: str):
        """Messaggio errore con design moderno."""
        error_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.ERROR_OUTLINE_ROUNDED,
                        color=self.colors['danger'],
                        size=64
                    ),
                    padding=16,
                    bgcolor=ft.Colors.with_opacity(0.1, self.colors['danger']),
                    border_radius=32,
                ),
                ft.Text(
                    "Oops! Qualcosa è andato storto",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=self.colors['text_primary'],
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(
                    content=ft.Text(
                        message,
                        color=self.colors['text_secondary'],
                        text_align=ft.TextAlign.CENTER,
                        size=14,
                        selectable=True
                    ),
                    padding=12,
                    bgcolor=self.colors['surface_light'],
                    border_radius=8,
                    border=ft.border.all(1, self.colors['border'])
                )
            ],
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            bgcolor=self.colors['surface'],
            border_radius=16,
            alignment=ft.alignment.center,
            border=ft.border.all(1, self.colors['danger']),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, self.colors['danger']),
                offset=ft.Offset(0, 6)
            )
        )

        self.chart_container.controls.clear()
        self.chart_container.controls.append(error_container)
        self.update()

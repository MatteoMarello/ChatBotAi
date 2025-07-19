import flet as ft
from typing import Dict, List, Tuple

# Colori per i grafici
CHART_COLORS = [
    ft.Colors.BLUE, ft.Colors.RED, ft.Colors.GREEN, ft.Colors.ORANGE,
    ft.Colors.PURPLE, ft.Colors.TEAL, ft.Colors.PINK
]


class ProgressView(ft.Container):
    def __init__(self):
        super().__init__()
        self.visible = False  # Nascosto di default
        self.expand = True
        self.padding = 20

        # Colori per il tema scuro
        self.colors = {
            'primary': '#3b82f6',
            'surface': '#1e293b',
            'surface_light': '#334155',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#475569',
        }

        self.title = ft.Text(
            "I Tuoi Progressi 🚀",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=self.colors['text_primary']
        )

        self.subtitle = ft.Text(
            "Analisi del tuo 1RM (massimale teorico) per gli esercizi fondamentali nel corso delle settimane.",
            color=self.colors['text_secondary']
        )

        self.chart_container = ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

        # Contenuto scrollabile
        self.content = ft.Column(
            [
                self.title,
                self.subtitle,
                ft.Divider(color=self.colors['border']),
                self.chart_container
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def update_view(self, progress_data: Dict[str, List[Tuple[int, float]]]):
        """Aggiorna la vista con i nuovi dati di progresso."""
        self.chart_container.controls.clear()

        if not progress_data:
            no_data_container = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BAR_CHART, size=60, color=self.colors['text_secondary']),
                    ft.Text(
                        "Nessun dato di progresso disponibile",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary'],
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Completa almeno una settimana di allenamento per vedere i tuoi progressi!",
                        color=self.colors['text_secondary'],
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=40,
                bgcolor=self.colors['surface'],
                border_radius=12,
                alignment=ft.alignment.center,
                border=ft.border.all(1, self.colors['border'])
            )
            self.chart_container.controls.append(no_data_container)
            return

        # Trova il range dei dati per configurare il grafico
        all_weeks = []
        all_values = []

        for nome_esercizio, data_points in progress_data.items():
            for settimana, one_rm in data_points:
                all_weeks.append(settimana)
                all_values.append(one_rm)

        if not all_values:
            return

        min_week = min(all_weeks)
        max_week = max(all_weeks)
        min_value = min(all_values)
        max_value = max(all_values)

        # Crea il grafico a linee
        chart = ft.LineChart(
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY),
            expand=True,
            height=400,
            bgcolor=self.colors['surface'],
            border=ft.border.all(1, self.colors['border']),
            # Configurazione degli assi
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("1RM (kg)", color=self.colors['text_secondary']),
                title_size=14
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(
                        value=i,
                        label=ft.Text(f"Sett. {i}", color=self.colors['text_secondary'])
                    ) for i in range(min_week, max_week + 1)
                ],
                labels_size=40,
                title=ft.Text("Settimane", color=self.colors['text_secondary']),
                title_size=14
            ),
            # Linee di griglia
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max(1, (max_value - min_value) / 10),
                color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_50),
                width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                interval=1,
                color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_50),
                width=1
            ),
            # Margini
            min_y=max(0, min_value - 10),
            max_y=max_value + 10,
            min_x=min_week - 0.5,
            max_x=max_week + 0.5,
            data_series=[]
        )

        # Aggiungi una linea per ogni esercizio
        for i, (nome_esercizio, data_points) in enumerate(progress_data.items()):
            # Ordina i punti per settimana
            sorted_points = sorted(data_points, key=lambda x: x[0])

            line = ft.LineChartData(
                color=CHART_COLORS[i % len(CHART_COLORS)],
                stroke_width=3,
                curved=True,
                stroke_cap_round=True,
                data_points=[
                    ft.LineChartDataPoint(
                        x=settimana,
                        y=one_rm,
                        tooltip=f"{nome_esercizio}\nSett. {settimana}: {one_rm:.1f} kg"
                    ) for settimana, one_rm in sorted_points
                ]
            )
            chart.data_series.append(line)

        # Container per il grafico
        chart_container = ft.Container(
            content=chart,
            padding=20,
            bgcolor=self.colors['surface'],
            border_radius=12,
            border=ft.border.all(1, self.colors['border'])
        )

        self.chart_container.controls.append(chart_container)

        # Crea la legenda
        legend_items = []
        for i, nome_esercizio in enumerate(progress_data.keys()):
            legend_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            width=20,
                            height=15,
                            bgcolor=CHART_COLORS[i % len(CHART_COLORS)],
                            border_radius=5
                        ),
                        ft.Text(
                            nome_esercizio,
                            color=self.colors['text_primary'],
                            size=14
                        )
                    ],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.START
                    ),
                    padding=8,
                    margin=4
                )
            )

        legend_container = ft.Container(
            content=ft.Row(
                controls=legend_items,
                wrap=True,
                spacing=15,
                alignment=ft.MainAxisAlignment.START
            ),
            padding=20,
            bgcolor=self.colors['surface'],
            border_radius=12,
            border=ft.border.all(1, self.colors['border'])
        )

        self.chart_container.controls.append(legend_container)

        # Aggiungi statistiche di riepilogo
        stats_items = []
        for nome_esercizio, data_points in progress_data.items():
            if len(data_points) >= 2:
                first_value = data_points[0][1]
                last_value = data_points[-1][1]
                improvement = last_value - first_value
                improvement_percent = (improvement / first_value) * 100 if first_value > 0 else 0

                stats_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                nome_esercizio,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=self.colors['text_primary']
                            ),
                            ft.Text(
                                f"Primo: {first_value:.1f} kg",
                                color=self.colors['text_secondary']
                            ),
                            ft.Text(
                                f"Ultimo: {last_value:.1f} kg",
                                color=self.colors['text_secondary']
                            ),
                            ft.Text(
                                f"Miglioramento: {improvement:+.1f} kg ({improvement_percent:+.1f}%)",
                                color=ft.Colors.GREEN if improvement >= 0 else ft.Colors.RED,
                                weight=ft.FontWeight.BOLD
                            )
                        ],
                            spacing=4,
                            alignment=ft.MainAxisAlignment.START
                        ),
                        padding=15,
                        bgcolor=self.colors['surface_light'],
                        border_radius=8,
                        border=ft.border.all(1, self.colors['border']),
                        expand=True
                    )
                )

        if stats_items:
            stats_container = ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Statistiche di Miglioramento",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']
                    ),
                    ft.Row(
                        controls=stats_items,
                        wrap=True,
                        spacing=15,
                        alignment=ft.MainAxisAlignment.START
                    )
                ],
                    spacing=15
                ),
                padding=20,
                bgcolor=self.colors['surface'],
                border_radius=12,
                border=ft.border.all(1, self.colors['border'])
            )

            self.chart_container.controls.append(stats_container)

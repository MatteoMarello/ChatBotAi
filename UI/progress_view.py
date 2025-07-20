# Sostituisci l'intero file progress_view.py con questo

import flet as ft
from typing import Dict, List, Tuple

# Colori per i grafici
CHART_COLORS = [
    ft.Colors.BLUE, ft.Colors.RED, ft.Colors.GREEN, ft.Colors.ORANGE,
    ft.Colors.PURPLE, ft.Colors.TEAL, ft.Colors.PINK, ft.Colors.AMBER
]


class ProgressView(ft.Container):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.expand = True
        self.padding = 20
        self.colors = {
            'primary': '#3b82f6', 'surface': '#1e293b', 'surface_light': '#334155',
            'text_primary': '#f1f5f9', 'text_secondary': '#94a3b8', 'border': '#475569',
        }
        self.title = ft.Text("I Tuoi Progressi 🚀", size=24, weight=ft.FontWeight.BOLD,
                             color=self.colors['text_primary'])
        self.subtitle = ft.Text(
            "Analisi dei tuoi massimali (1RM) e del volume di allenamento nel corso delle settimane.",
            color=self.colors['text_secondary'])
        self.chart_container = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        self.content = ft.Column(
            [self.title, self.subtitle, ft.Divider(color=self.colors['border']), self.chart_container], spacing=10,
            scroll=ft.ScrollMode.AUTO, expand=True)

    def update_view(self, progress_data_1rm: Dict[str, List[Tuple[int, float]]],
                    volume_data: Dict[int, Dict[str, int]]):
        """Aggiorna la vista con i grafici di 1RM e volume."""
        self.chart_container.controls.clear()
        has_content = False

        if progress_data_1rm:
            self._crea_grafico_1rm(progress_data_1rm)
            has_content = True

        if volume_data and any(volume_data.values()):
            self._crea_grafico_volume(volume_data)
            has_content = True

        if not has_content:
            self.chart_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BAR_CHART, size=60, color=self.colors['text_secondary']),
                    ft.Text("Nessun dato di progresso disponibile", size=18, weight=ft.FontWeight.BOLD,
                            color=self.colors['text_primary'], text_align=ft.TextAlign.CENTER),
                    ft.Text("Completa almeno una settimana di allenamento per vedere i tuoi grafici!",
                            color=self.colors['text_secondary'], text_align=ft.TextAlign.CENTER)
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40, bgcolor=self.colors['surface'], border_radius=12, alignment=ft.alignment.center,
                border=ft.border.all(1, self.colors['border'])
            ))
        self.update()

    def _crea_grafico_1rm(self, progress_data: Dict[str, List[Tuple[int, float]]]):
        """Crea il contenitore del grafico per l'andamento del massimale (1RM)."""
        all_weeks = [w for data in progress_data.values() for w, v in data]
        all_values = [v for data in progress_data.values() for w, v in data]
        if not all_values: return

        min_week, max_week = (min(all_weeks), max(all_weeks)) if all_weeks else (1, 1)
        min_value, max_value = (min(all_values), max(all_values)) if all_values else (0, 100)

        chart = ft.LineChart(
            tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY), expand=True, height=400,
            left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("1RM (kg)", color=self.colors['text_secondary'])),
            bottom_axis=ft.ChartAxis(
                labels=[ft.ChartAxisLabel(value=i, label=ft.Text(f"S{i}", color=self.colors['text_secondary'])) for i in
                        range(min_week, max_week + 1)], labels_size=40),
            horizontal_grid_lines=ft.ChartGridLines(interval=max(1, round((max_value - min_value) / 5)),
                                                    color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_50), width=1),
            min_y=max(0, min_value - 10), max_y=max_value + 10, min_x=min_week, max_x=max_week,
            data_series=[]
        )

        for i, (nome_esercizio, data_points) in enumerate(progress_data.items()):
            chart.data_series.append(ft.LineChartData(
                color=CHART_COLORS[i % len(CHART_COLORS)], stroke_width=3, curved=True,
                data_points=[ft.LineChartDataPoint(x=settimana, y=one_rm,
                                                   tooltip=f"{nome_esercizio}\nSett. {settimana}: {one_rm:.1f} kg") for
                             settimana, one_rm in data_points]
            ))

        legend_items = [ft.Row(
            [ft.Container(width=15, height=15, bgcolor=CHART_COLORS[i % len(CHART_COLORS)], border_radius=4),
             ft.Text(nome, color=self.colors['text_primary'])]) for i, nome in enumerate(progress_data.keys())]

        container_1rm = ft.Container(
            content=ft.Column([
                ft.Text("Andamento Massimale (1RM)", size=18, weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Text("Stima del tuo massimale per gli esercizi principali.", color=self.colors['text_secondary']),
                ft.Divider(color=self.colors['border']),
                chart,
                ft.Row(controls=legend_items, spacing=15, wrap=True)
            ], spacing=10),
            padding=20, bgcolor=self.colors['surface'], border_radius=12, border=ft.border.all(1, self.colors['border'])
        )
        self.chart_container.controls.append(container_1rm)

    def _crea_grafico_volume(self, volume_data: Dict[int, Dict[str, int]]):
        """Crea il grafico a barre per il volume settimanale."""
        muscoli = sorted(list(set(m for week_vols in volume_data.values() for m in week_vols.keys())))
        settimane = sorted(volume_data.keys())
        if not muscoli or not settimane: return

        bar_groups = [
            ft.BarChartGroup(x=i, bar_rods=[
                ft.BarChartRod(
                    from_y=0, to_y=volume_data.get(sett, {}).get(muscolo, 0),
                    width=max(4, 16 / len(settimane)), color=CHART_COLORS[sett_idx % len(CHART_COLORS)],
                    tooltip=f"Sett. {sett}: {volume_data.get(sett, {}).get(muscolo, 0)} serie", border_radius=0,
                ) for sett_idx, sett in enumerate(settimane)
            ]) for i, muscolo in enumerate(muscoli)
        ]

        chart = ft.BarChart(
            bar_groups=bar_groups, expand=True, height=350,
            left_axis=ft.ChartAxis(labels_size=40, title=ft.Text("Serie Totali", color=self.colors['text_secondary']),
                                   title_size=14),
            bottom_axis=ft.ChartAxis(labels=[
                ft.ChartAxisLabel(value=i, label=ft.Text(muscolo[:4], color=self.colors['text_secondary'], size=10)) for
                i, muscolo in enumerate(muscoli)], labels_size=30),
            horizontal_grid_lines=ft.ChartGridLines(interval=5, color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_50),
                                                    width=1),
        )

        legend_items = [ft.Row(
            [ft.Container(width=15, height=15, bgcolor=CHART_COLORS[i % len(CHART_COLORS)], border_radius=4),
             ft.Text(f"Settimana {sett}", color=self.colors['text_primary'])]) for i, sett in enumerate(settimane)]

        volume_chart_container = ft.Container(
            content=ft.Column([
                ft.Text("Volume di Allenamento (Serie per Settimana)", size=18, weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Text("Numero totale di serie allenanti per gruppo muscolare.", color=self.colors['text_secondary']),
                ft.Divider(color=self.colors['border']),
                chart,
                ft.Row(controls=legend_items, spacing=15, wrap=True)
            ], spacing=10),
            padding=20, bgcolor=self.colors['surface'], border_radius=12,
            border=ft.border.all(1, self.colors['border']),
            margin=ft.margin.only(top=20)
        )
        self.chart_container.controls.append(volume_chart_container)

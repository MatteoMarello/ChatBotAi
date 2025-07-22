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

    def update_view(self, improvement_data: Dict[str, float],
                    volume_data: Dict[int, Dict[str, int]]):
        """Aggiorna la vista con i grafici di miglioramento % e volume."""
        self.chart_container.controls.clear()
        has_content = False

        # Usa la nuova funzione per creare il grafico a barre del miglioramento
        if improvement_data:
            self._crea_grafico_miglioramento(improvement_data)
            has_content = True

        if volume_data and any(volume_data.values()):
            self._crea_grafico_volume(volume_data)  # Questo grafico rimane invariato
            has_content = True

        if not has_content:
            self.chart_container.controls.append(ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SHOW_CHART, size=60, color=self.colors['text_secondary']),
                    ft.Text("Nessun dato di progresso disponibile", size=18, weight=ft.FontWeight.BOLD,
                            color=self.colors['text_primary'], text_align=ft.TextAlign.CENTER),
                    ft.Text("Completa almeno due settimane di allenamento per vedere i tuoi progressi!",
                            color=self.colors['text_secondary'], text_align=ft.TextAlign.CENTER)
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40, bgcolor=self.colors['surface'], border_radius=12, alignment=ft.alignment.center,
                border=ft.border.all(1, self.colors['border'])
            ))
        self.update()
    # In progress_view.py, SOSTITUISCI la funzione _crea_grafico_1rm

    def _crea_grafico_miglioramento(self, improvement_data: Dict[str, float]):
        """Crea un grafico a barre per il miglioramento percentuale del 1RM."""

        bar_groups = []
        all_values = list(improvement_data.values())

        # Colori per le barre: verde se positivo, rosso se negativo
        def get_color(value):
            return ft.Colors.GREEN_ACCENT_400 if value >= 0 else ft.Colors.RED_400

        for i, (nome_serie, value) in enumerate(improvement_data.items()):
            bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=value,
                            width=30,
                            color=get_color(value),
                            tooltip=f"{nome_serie}\nMiglioramento: {value:+.1f}%",
                            border_radius=4,
                        )
                    ],
                )
            )

        # Trova i limiti per l'asse Y
        min_y = min(all_values) if any(v < 0 for v in all_values) else 0
        max_y = max(all_values) if any(v > 0 for v in all_values) else 0

        y_padding = (max_y - min_y) * 0.1  # Aggiungi 10% di padding
        if y_padding == 0: y_padding = 5  # Padding minimo

        chart = ft.BarChart(
            bar_groups=bar_groups,
            expand=True,
            height=400,
            left_axis=ft.ChartAxis(
                title=ft.Text("Miglioramento %", color=self.colors['text_secondary']),
                labels_size=40,
                # Calcola l'intervallo delle griglie in modo dinamico
                labels_interval=max(1, round((max_y - min_y) / 5)) if max_y > min_y else 5
            ),
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=i,
                                      label=ft.Text(nome.split(' ')[0], size=10, color=self.colors['text_secondary']))
                    for i, nome in enumerate(improvement_data.keys())
                ],
                labels_size=30,
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                interval=max(1, round((max_y - min_y) / 5)) if max_y > min_y else 5,
                color=ft.Colors.with_opacity(0.2, ft.Colors.GREY_50),
                width=1
            ),
            min_y=min_y - y_padding,
            max_y=max_y + y_padding,
        )

        container_miglioramento = ft.Container(
            content=ft.Column([
                ft.Text("Miglioramento Percentuale Finale (1RM)", size=18, weight=ft.FontWeight.BOLD,
                        color=self.colors['text_primary']),
                ft.Text("Variazione % del massimale stimato dalla prima all'ultima settimana.",
                        color=self.colors['text_secondary']),
                ft.Divider(color=self.colors['border']),
                chart
            ], spacing=10),
            padding=20, bgcolor=self.colors['surface'], border_radius=12, border=ft.border.all(1, self.colors['border'])
        )
        self.chart_container.controls.append(container_miglioramento)

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

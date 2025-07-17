import flet as ft
from UI.view import View
from UI.controller import Controller


def main(page: ft.Page):
    # Inizializza il Controller, che gestisce la logica
    controller = Controller()
    # Inizializza la View, passandole un riferimento al Controller
    view = View(page, controller)

    # Imposta la pagina e aggiunge la UI costruita dalla View
    page.title = "Generatore Schede Allenamento"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    # CAMBIATO: Aggiungi main_view invece di solo config_view
    page.add(view.build())


# Avvia l'applicazione Flet
ft.app(target=main, assets_dir="assets")

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
    page.theme_mode = ft.ThemeMode.DARK
    # Le righe seguenti sono state rimosse per permettere lo scrolling corretto
    # page.vertical_alignment = ft.MainAxisAlignment.START
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

if __name__ == "__main__":
    ft.app(target=main)

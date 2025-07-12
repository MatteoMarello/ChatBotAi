def get_weekly_sets(livello, muscolo, mesociclo):
    # Dati base: MEV +1 e MRV per livello
    base_volumes = {
        "principiante": {
            "Petto": (10, 16), "Schiena": (12, 18), "Spalle": (10, 16), "Bicipiti": (8, 14),
            "Tricipiti": (8, 14), "Quadricipiti": (10, 18), "Femorali": (6, 12),
            "Glutei": (8, 14), "Polpacci": (6, 12)
        },
        "intermedio": {
            "Petto": (11, 20), "Schiena": (13, 20), "Spalle": (11, 18), "Bicipiti": (9, 16),
            "Tricipiti": (9, 16), "Quadricipiti": (11, 20), "Femorali": (7, 14),
            "Glutei": (9, 16), "Polpacci": (8, 14)
        },
        "avanzato": {
            "Petto": (12, 22), "Schiena": (14, 22), "Spalle": (12, 20), "Bicipiti": (10, 18),
            "Tricipiti": (10, 18), "Quadricipiti": (12, 22), "Femorali": (8, 16),
            "Glutei": (10, 18), "Polpacci": (8, 18)
        }
    }

    if livello not in base_volumes or muscolo not in base_volumes[livello]:
        raise ValueError("Livello o muscolo non valido")

    start, end = base_volumes[livello][muscolo]

    # Mesociclo 1 parte da start, meso 2 da start+1, meso 3 da start+2
    incremento = mesociclo - 1  # 0,1,2 per i mesocicli 1,2,3
    volume_iniziale = min(start + incremento, end)

    settimana1 = volume_iniziale
    settimana2 = min(settimana1 + 2, end)
    settimana3 = min(settimana2 + 2, end)
    scarico = max(round(settimana3 * 0.5), 6)  # almeno 6 serie in scarico

    return {
        "settimana1": settimana1,
        "settimana2": settimana2,
        "settimana3": settimana3,
        "scarico": scarico
    }


# Esempio d'uso:
volume = get_weekly_sets("avanzato", "Petto", 2)
print(volume)  # {'settimana1': 13, 'settimana2': 15, 'settimana3': 17, 'scarico': 8}


from database.DAO import DAO

class Model:
    def __init__(self):


    def get_scheda_mensile(self, obiettivo, livello, frequenza, attrezzautura, muscolotarget ):
        esercizi = DAO.getEsercizi(livello, attrezzautura)
        if livello == "avanzato":
            mev = 10
            mrv = 16
            if frequenza == 4:
                pass
            if frequenza == 5:
                pass
        if livello == "intermedio":
            mev = 13
            mrv = 19
            if frequenza == 3:
                pass
            if frequenza == 4:
                pass
        if livello == "principiante":
            mev = 16
            mrv = 22

    def get_mev_mrv(self, livello):
        valori = {
            "avanzato": (16, 22),
            "intermedio": (13, 19),
            "principiante": (10, 16)
        }
        return valori[livello]

    def get_volume_base(self, livello):
        mev, mrv = self.get_mev_mrv(livello)
        return mev  # valore di partenza conservativo

    def get_volume_max(self, livello):
        mev, mrv = self.get_mev_mrv(livello)
        return mrv  # valore di partenza conservativo

    def get_frequenze_consentite(self, livello):
        return {
            "principiante": [2, 3, 4],
            "intermedio": [3, 4],
            "avanzato": [4, 5, 6]
        }[livello]

    def distribuisci_volume(self, volume_settimanale, num_esercizi):
        if num_esercizi == 3:
            return [int(volume_settimanale * 0.4), int(volume_settimanale * 0.3), volume_settimanale - int(volume_settimanale * 0.4) - int(volume_settimanale * 0.3)]
        elif num_esercizi == 2:
            return [int(volume_settimanale * 0.6), volume_settimanale - int(volume_settimanale * 0.6)]
        return [volume_settimanale]

    def seleziona_esercizi(self, muscolo, attrezzatura, livello):
        # Simulazione DB, da sostituire con DAO.getEsercizi()
        esercizi = DAO.getEserciziPerMuscolo(muscolo, attrezzatura, livello)
        esercizi_filtrati = sorted(esercizi, key=lambda e: e["priority_level"])
        if muscolo in ["petto", "schiena", "quadricipiti", "glutei"]:
            return esercizi_filtrati[:3]
        return esercizi_filtrati[:2]

    def get_scheda_mensile(self, obiettivo, livello, frequenza, attrezzatura, muscolo_target):
        if frequenza not in self.get_frequenze_consentite(livello):
            raise ValueError("Frequenza non consentita per il livello selezionato")

        volume_base = self.get_volume_base(livello)

        muscoli = ["petto", "schiena", "spalle", "bicipiti", "tricipiti", "quadricipiti","glutei","femorali", "polpacci"]

        scheda = {}

        for muscolo in muscoli:
            volume = volume_base
            if muscolo == muscolo_target:
                volume = int(volume * 1.2)
                #aumento volume del 20%

            esercizi = self.seleziona_esercizi(muscolo, attrezzatura, livello)
            distribuzione = self.distribuisci_volume(volume, len(esercizi))

            scheda[muscolo] = []
            for idx, esercizio in enumerate(esercizi):
                scheda[muscolo].append({
                    "nome": esercizio["nome"],
                    "serie": distribuzione[idx],
                    "ripetizioni": esercizio["range_ripetizioni"],
                    "REAR": 4
                })

        return scheda



















#metodi esatti
    def selezionaSplit(self, livello,frequenza):
        split = []  # lista dei giorni con focus (es: "full body", "upper", etc.)

        if livello == "principiante":
            if frequenza == 2:
                split = ["Full Body", "Full Body"]
            elif frequenza == 3:
                split = ["Full Body", "Full Body", "Full Body"]
            elif frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]

        elif livello == "intermedio":
            if frequenza == 3:
                split = ["Upper", "Lower", "Full Body"]
            elif frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]

        elif livello == "avanzato":
            if frequenza == 4:
                split = ["Lower", "Upper", "Lower", "Upper"]
            elif frequenza == 5:
                split = ["Lower", "Upper", "Lower", "Upper", "Full Body Metabolico"]
            elif frequenza == 6:
                split = ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]

        else:
            raise ValueError("Livello non valido")

        # Puoi salvare o restituire questa split per costruire la scheda:
        return split


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




















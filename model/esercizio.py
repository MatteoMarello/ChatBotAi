from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union
import json


@dataclass
class Esercizio:
    """
    DataClass semplificata per rappresentare un esercizio di allenamento.
    """

    id: int
    nome: str
    attrezzatura: Union[List[str], str]
    livello: int
    muscolo_primario: str
    muscoli_secondari: Union[List[str], str]
    recupero_secondi: int
    affaticamento: int
    tipologia: str
    articolazioni: Union[List[str], str]
    descrizione: str
    range_ripetizioni: Union[List[int], str]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Conversione automatica dei campi JSON se necessario"""
        # Conversione attrezzatura
        if isinstance(self.attrezzatura, str):
            try:
                self.attrezzatura = json.loads(self.attrezzatura)
            except:
                self.attrezzatura = [self.attrezzatura]

        # Conversione muscoli_secondari
        if isinstance(self.muscoli_secondari, str):
            try:
                self.muscoli_secondari = json.loads(self.muscoli_secondari)
            except:
                self.muscoli_secondari = [self.muscoli_secondari]

        # Conversione articolazioni
        if isinstance(self.articolazioni, str):
            try:
                self.articolazioni = json.loads(self.articolazioni)
            except:
                self.articolazioni = [self.articolazioni]

        # Conversione range_ripetizioni
        if isinstance(self.range_ripetizioni, str):
            try:
                self.range_ripetizioni = json.loads(self.range_ripetizioni)
            except:
                # Se non è JSON valido, prova a parsare come "min-max"
                if '-' in self.range_ripetizioni:
                    parts = self.range_ripetizioni.split('-')
                    self.range_ripetizioni = [int(parts[0]), int(parts[1])]
                else:
                    self.range_ripetizioni = [1, 10]  # Default

        # Assicurati che range_ripetizioni sia una lista con almeno 2 elementi
        if not isinstance(self.range_ripetizioni, list):
            self.range_ripetizioni = [1, 10]
        elif len(self.range_ripetizioni) < 2:
            self.range_ripetizioni = [1, 10]

    @property
    def livello_descrizione(self) -> str:
        """Restituisce la descrizione testuale del livello"""
        livelli = {1: "Principiante", 2: "Intermedio", 3: "Avanzato"}
        return livelli.get(self.livello, "Sconosciuto")

    @property
    def recupero_minuti(self) -> float:
        """Restituisce il tempo di recupero in minuti"""
        return self.recupero_secondi / 60

    @property
    def range_ripetizioni_str(self) -> str:
        """Restituisce il range ripetizioni come stringa"""
        if isinstance(self.range_ripetizioni, list) and len(self.range_ripetizioni) >= 2:
            return f"{self.range_ripetizioni[0]}-{self.range_ripetizioni[1]}"
        return "1-10"

    def coinvolge_muscolo(self, muscolo: str) -> bool:
        """Verifica se l'esercizio coinvolge un determinato muscolo"""
        if self.muscolo_primario.lower() == muscolo.lower():
            return True

        if isinstance(self.muscoli_secondari, list):
            return any(m.lower() == muscolo.lower() for m in self.muscoli_secondari)
        return False

    def richiede_attrezzatura(self, attrezzatura: str) -> bool:
        """Verifica se l'esercizio richiede una specifica attrezzatura"""
        if isinstance(self.attrezzatura, list):
            return any(a.lower() == attrezzatura.lower() for a in self.attrezzatura)
        return False

    def coinvolge_articolazione(self, articolazione: str) -> bool:
        """Verifica se l'esercizio coinvolge una specifica articolazione"""
        if isinstance(self.articolazioni, list):
            return any(a.lower() == articolazione.lower() for a in self.articolazioni)
        return False

    def aggiorna_timestamp(self):
        """Aggiorna il timestamp di ultimo aggiornamento"""
        self.updated_at = datetime.now()

    def __str__(self) -> str:
        """Rappresentazione stringa dell'esercizio"""
        return f"Esercizio(id={self.id}, nome='{self.nome}', muscolo_primario='{self.muscolo_primario}', livello={self.livello_descrizione})"

    def __repr__(self) -> str:
        """Rappresentazione dettagliata dell'esercizio"""
        return (f"Esercizio(id={self.id}, nome='{self.nome}', "
                f"muscolo_primario='{self.muscolo_primario}', "
                f"livello={self.livello})")


# Metodo DAO semplificato
class DAO:
    @staticmethod
    def getEsercizi(context, muscolo):
        cnx = DBConnect.get_connection()
        cursor = cnx.cursor(dictionary=True)

        query = """select e.id, e.nome, e.attrezzatura, e.livello, e.muscolo_primario, 
                          e.muscoli_secondari, e.recupero_secondi, e.affaticamento, 
                          e.tipologia, e.articolazioni, e.descrizione, e.range_ripetizioni,
                          e.created_at, e.updated_at
                   from fitness_db.exercises e, fitness_db.contexts c, fitness_db.exercise_context_priority ecp 
                   where c.nome = %s and c.id = ecp.context_id and e.muscolo_primario = %s 
                   and ecp.exercise_id = e.id and ecp.priority_level <> 99
                   order by ecp.priority_level asc"""

        cursor.execute(query, (context, muscolo))

        results = []
        for row in cursor:
            try:
                results.append(Esercizio(**row))
            except Exception as e:
                print(f"Errore creando esercizio {row.get('nome', 'sconosciuto')}: {e}")
                continue

        cursor.close()
        cnx.close()
        return results

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Esercizio) and self.id == other.id


# Esempio di utilizzo
if __name__ == "__main__":
    # Creazione di un esercizio esempio
    panca_piana = Esercizio(
        id=4,
        nome="Panca Piana",
        attrezzatura=["Palestra", "Bilanciere", "Panca"],
        livello=1,
        muscolo_primario="Petto",
        muscoli_secondari=["Tricipiti", "Spalle"],
        recupero_secondi=120,
        affaticamento=8,
        tipologia="Fondamentale",
        articolazioni=["Spalla", "Gomito"],
        descrizione="Esercizio fondamentale per lo sviluppo della massa e forza del petto.",
        range_ripetizioni=[3, 10],
        created_at=datetime(2025, 7, 11, 15, 12, 13),
        updated_at=datetime(2025, 7, 11, 15, 12, 13)
    )

    print(panca_piana)
    print(f"Range ripetizioni: {panca_piana.range_ripetizioni_str}")

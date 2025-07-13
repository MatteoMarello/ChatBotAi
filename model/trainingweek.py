from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from workoutday import WorkoutDay  # Importa la classe WorkoutDay


@dataclass
class TrainingWeek:
    numero_settimana: int
    start_date: datetime
    workout_days: List[WorkoutDay] = field(default_factory=list)

    def aggiungi_workout_day(self, workout_day: WorkoutDay):
        self.workout_days.append(workout_day)

    def totale_serie_settimanale(self) -> int:
        return sum(day.totale_serie_giornata() for day in self.workout_days)

    def muscoli_lavorati_settimana(self) -> List[str]:
        muscoli = set()
        for day in self.workout_days:
            muscoli.update(day.muscoli_lavorati())
        return list(muscoli)

    def get_workout_by_day_id(self, giorno_id: int) -> WorkoutDay:
        for day in self.workout_days:
            if day.id_giorno == giorno_id:
                return day
        raise ValueError(f"Nessun workout trovato per giorno {giorno_id}")

    def __str__(self):
        descrizione = f"Training Week {self.numero_settimana} - Inizio: {self.start_date.strftime('%Y-%m-%d')}\n"
        for day in self.workout_days:
            descrizione += f"\n{day}\n"
        return descrizione

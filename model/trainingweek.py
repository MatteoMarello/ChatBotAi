from dataclasses import dataclass, field
from datetime import datetime

from model.workoutday import WorkoutDay


@dataclass
class TrainingWeek:
    """Rappresenta un'intera settimana di allenamento."""
    numero_settimana: int
    start_date: datetime
    workout_days: list[WorkoutDay] = field(default_factory=list)

    def __str__(self):
        descrizione = f"{'=' * 60}\n"
        descrizione += f"           TRAINING WEEK {self.numero_settimana}\n"
        descrizione += f"      Inizio: {self.start_date.strftime('%d/%m/%Y')}\n"
        descrizione += f"{'=' * 60}\n"

        for day in self.workout_days:
            descrizione += f"\n{day}"

        descrizione += f"\n{'=' * 60}\n"
        return descrizione

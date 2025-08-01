from collections import defaultdict # <-- AGGIUNGI QUESTO
from dataclasses import dataclass, field
from typing import Dict, List
from model.workoutday import WorkoutDay # Assicurati che il percorso sia corretto

def _get_rep_range_upper_bound(rep_range_str: str) -> int:
    """Estrae il limite superiore da una stringa di range di ripetizioni (es. '8-12' -> 12)."""
    try:
        parts = rep_range_str.split('-')
        return int(parts[1])
    except (IndexError, ValueError):
        return 0

@dataclass
class ReadinessInput:
    """Raccoglie l'input dell'utente sulla sua prontezza giornaliera."""
    energy: int  # Scala 1-5
    sleep: int   # Scala 1-5
    soreness: int # Dolori muscolari (DOMS) per i muscoli del giorno (1-5)
    joint_pain: int # Dolori articolari (1-5)
    time_is_limited: bool

@dataclass
class WorkoutAdjustment:
    """Rappresenta gli aggiustamenti calcolati per il workout del giorno."""
    day_category: str  # "GREEN", "YELLOW", "RED"
    user_message: str
    global_rir_adjustment: int = 0
    set_reductions: Dict[int, int] = field(default_factory=dict) # {esercizio_id: numero_serie_da_rimuovere}
    # Potenziale futura aggiunta: exercise_substitutions: Dict[int, int] = field(default_factory=dict)


class DailyReadinessAdjuster:
    """
    Algoritmo per analizzare la prontezza giornaliera e suggerire modifiche
    all'allenamento del giorno.
    """

    def get_adjustments(self, readiness: ReadinessInput, workout_day: WorkoutDay) -> WorkoutAdjustment:
        """
        Calcola gli aggiustamenti per il workout basandosi sulla prontezza dell'utente.
        """
        readiness_score = (readiness.energy + readiness.sleep) / 2

        # Penalità per dolori articolari (molto impattanti)
        if readiness.joint_pain > 2:
            readiness_score -= (readiness.joint_pain - 2)

        # Se i dolori articolari sono alti, è sempre un giorno rosso
        if readiness.joint_pain >= 4:
            return self._create_red_day_adjustment(
                "Dolori articolari severi. È fondamentale non peggiorare la situazione. Scegli riposo o recupero attivo."
            )

        # Se il punteggio è molto basso, è un giorno rosso
        if readiness_score < 2:
            return self._create_red_day_adjustment(
                "Energia e sonno molto bassi. Allenarsi oggi sarebbe controproducente. Riposa."
            )

        is_yellow_day_condition = readiness_score < 3.5 or readiness.soreness >= 4

        # Se è un giorno "giallo" o se il tempo è limitato, calcola gli aggiustamenti
        if is_yellow_day_condition or readiness.time_is_limited:
            return self._create_yellow_day_adjustment(readiness, workout_day, is_yellow_day_condition)

        # Altrimenti, è un giorno verde
        return self._create_green_day_adjustment()

    def _create_green_day_adjustment(self) -> WorkoutAdjustment:
        """Crea un aggiustamento per un "Go Day"."""
        return WorkoutAdjustment(
            day_category="GREEN",
            user_message="Sei al top! Esegui la scheda come programmato. Puoi puntare alla parte alta dei range di ripetizioni."
        )

    def _create_red_day_adjustment(self, reason: str) -> WorkoutAdjustment:
        """Crea un aggiustamento per un "Recovery Day"."""
        return WorkoutAdjustment(
            day_category="RED",
            user_message=f"GIORNO ROSSO: {reason} Si consiglia riposo o una sessione di cardio leggero e stretching.",
            global_rir_adjustment=3,
            set_reductions={}
        )

    def _create_yellow_day_adjustment(self, readiness: ReadinessInput, workout_day: WorkoutDay,
                                      is_yellow_day: bool) -> WorkoutAdjustment:
        """Crea un aggiustamento per un "Modulate Day" o per tempo limitato."""
        messages = []
        rir_adjustment = 0  # Di base, nessuna modifica al RIR
        set_reductions = {}

        # Logica per affaticamento (condizioni da "giorno giallo")
        if is_yellow_day:
            messages.append("GIORNO GIALLO: Modera lo sforzo.")
            rir_adjustment = 1  # Aumento RIR solo se c'è affaticamento

            if (readiness.energy + readiness.sleep) / 2 < 2.5:
                rir_adjustment = 2
                messages.append("Energia bassa, aumenta il buffer (RIR +2) e concentrati sulla tecnica.")

            if readiness.soreness >= 4:
                messages.append("DOMS elevati: Riduci leggermente il volume sugli esercizi di isolamento.")
                for ex in workout_day.esercizi:
                    if ex.tipologia.lower() == 'isolamento':
                        set_reductions[ex.id] = set_reductions.get(ex.id, 0) + 1

        # Logica per tempo limitato (indipendente dall'affaticamento)
        if readiness.time_is_limited:
            messages.append(
                "Tempo limitato: Il volume sarà ridotto sugli esercizi a ripetizioni più alte per velocizzare la sessione.")

            exercises_by_muscle = defaultdict(list)
            for ex in workout_day.esercizi:
                exercises_by_muscle[ex.muscolo_primario].append(ex)

            for muscle, exercises in exercises_by_muscle.items():
                if not exercises: continue

                highest_rep_exercise_id = None
                max_rep_upper_bound = -1

                for ex in exercises:
                    log = workout_day.performance_log.get(ex.id)
                    if not log or not log.get('reps'): continue

                    current_max_rep = 0
                    for rep_range_str in log['reps']:
                        upper_bound = _get_rep_range_upper_bound(rep_range_str)
                        if upper_bound > current_max_rep:
                            current_max_rep = upper_bound

                    if current_max_rep > max_rep_upper_bound:
                        max_rep_upper_bound = current_max_rep
                        highest_rep_exercise_id = ex.id

                if highest_rep_exercise_id:
                    set_reductions[highest_rep_exercise_id] = set_reductions.get(highest_rep_exercise_id, 0) + 1

        return WorkoutAdjustment(
            day_category="YELLOW",
            user_message="\n".join(messages),
            global_rir_adjustment=rir_adjustment,
            set_reductions=set_reductions
        )

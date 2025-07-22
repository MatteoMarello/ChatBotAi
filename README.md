# ChatBotAi
In summary, these classes work together to **create a personalized workout plan (`creascheda.py`) and then dynamically adapt it over three weeks (`adattaScheda.py`)** based on user feedback and performance.  

Here’s a detailed explanation of the two components.  

---  

### `creascheda.py` – The Workout Plan Builder  

This class, named `Model`, has the primary task of **generating a complete training week (`TrainingWeek`) from scratch**. Think of it as the architect of the workout plan.  

Its main functions are:  

* **Define Training Volume**: It calculates the total number of sets a user should perform for each muscle group in a week, based on their experience level (e.g., "intermediate"). If a muscle is selected as a "target," its volume is increased by 30% to prioritize it.  
* **Select Exercises**: It queries a database to get a list of suitable exercises for each muscle, sorted by importance. It then selects the top two and classifies them as "heavy" (for low reps, e.g., 6–8) and "light" (for high reps, e.g., 12–22) based on the suggested rep range.  
* **Distribute Sets**: It divides the total volume for a muscle into different types of sets. For example, 50% of the sets will be "heavy," 40% "medium," and 10% "light."  
* **Assemble Workout Days**: Using specific logic (`_distribuisci_serie_giorni_intermedio`), it distributes the calculated sets across the training days of the week, aiming to create balanced sessions and avoid scheduling just one set of an exercise per day.  
* **Handle Adjustments**: The main function, `getSchedaFullBodyIntermedio`, can accept a parameter called `volume_overrides`. This allows the adaptation logic (described below) to force a new set count for a muscle in subsequent weeks, bypassing the initial calculation.  

In practice, `creascheda.py` takes the user’s preferences and turns them into a structured workout plan for the first week.  

---  

### `adattaScheda.py` – The Performance Analyst  

This file contains the logic to analyze user-provided data after each workout and modify the plan for the following weeks. It acts as a "virtual coach" that adjusts the plan based on results.  

It consists of three main classes:  

#### 1. `PerformanceData` and `DOMSData`  
These are simple data containers (`dataclass`) to organize information:  
* **`PerformanceData`**: Stores data for a single set of an exercise: weight lifted, repetitions, mind-muscle connection (MMC), pump, and joint pain. It also automatically calculates two key metrics:  
  * **1RM (One-Rep Max)**: An estimate of maximum strength, used to track progress.  
  * **RSM (Perceived Muscle Stimulus)**: The sum of MMC and Pump, quantifying "how much the exercise was felt."  
* **`DOMSData`**: Stores the level of muscle soreness (DOMS) reported by the user for a specific muscle.  

#### 2. `TrainingAlgorithm`  
This is the main class that orchestrates the entire 3-week adaptation cycle.  

* **At the End of Week 1 (to Create Week 2)**:  
  1. **Calculates SFR**: For each exercise, it computes the **Stimulus-Fatigue-Ratio (SFR)**, an index that compares positive sensations (RSM) with negative ones (joint pain). A high SFR indicates an effective and safe exercise.  
  2. **Analyzes DOMS**: It uses the muscle soreness value (DOMS) reported by the user at the start of Week 2.  
  3. **Suggests New Volume**: By combining SFR and DOMS, it suggests whether to increase, decrease, or maintain the number of sets for each muscle group in Week 2 (e.g., `"+2/4 sets"`, `"keep"`, `"-2 sets"`).  

* **At the End of Week 2 (to Create Week 3)**:  
  1. **Measures Improvements**: It compares strength (1RM) from Week 2 to Week 1 for each exercise, calculating the percentage of improvement.  
  2. **Assigns Performance Points**: It converts the improvement percentage into "performance points" (e.g., if you improve by more than 5%, you get +2 points; if you regress, you get negative points).  
  3. **Suggests New Volume**: It averages the points for each muscle group and, based on this, suggests a precise adjustment for Week 3 (e.g., `"+3 sets"`, `"-1 set"`).  

* **At the End of Week 3 (Final Report)**:  
  1. **Final Analysis**: It calculates a final SFR for Week 3, accounting for any performance drop due to accumulated fatigue.  
  2. **Creates a Ranking**: It averages the SFRs from Weeks 1 and 3 to rank the exercises from most to least effective.  
  3. **Generates a Report**: It produces a comprehensive summary of the mesocycle, indicating which exercise worked best and which might need replacement in the next cycle.






# ChatBotAi

**ChatBotAi** è un’applicazione desktop sviluppata in Python con Flet, che genera schede di allenamento personalizzate e le adatta dinamicamente ai progressi dell’utente. Integra un modello MVC, un database MariaDB per la persistenza e una componente di chat AI per consigli nutrizionali.

## 📐 Architettura del Progetto

L’architettura segue il pattern **Model–View–Controller (MVC)**:

- **Model** (cartella `model/`)
  - `creascheda.py`: motore di generazione iniziale delle schede
    - Calcolo del BMR (Mifflin–St Jeor)
    - Selezione esercizi dal database
    - Distribuzione del volume (serie × ripetizioni) per gruppo muscolare
  - `adattascheda.py`: motore di adattamento settimanale
    - Calcolo DOMS e SFR (Strength‑to‑Fatigue Ratio)
    - Stima 1RM teorico
    - Regolazione di volume e intensità per le settimane successive

- **Controller** (file `controller.py`)
  - Orchestrazione delle chiamate al Model
  - Gestione delle API interne per creazione e adattamento schede
  - Persistenza su MariaDB con interfaccia SQL
  - Logica di routing verso le View

- **View** (cartella `view/`)
  - **Layout principale** (`main.py`)
    - Definizione della sidebar e del sistema di routing
    - Container unico per le View caricate dinamicamente
  - `home_view.py`: Schermata “Scheda Giornaliera”
  - `progress_view.py`: Schermata “Progressi” con grafici e tabelle
  - `nutrition_view.py`: Schermata “TDEE & Macronutrienti” (calcolatore)
  - `chatbot_view.py`: Schermata “Chat Coach” per integrare ChatGPT API

- **Database** (MariaDB)
  - Tabelle normalizzate: `Utenti`, `Esercizi`, `Schede`, `Scheda_Esercizi`, `Progressi`
  - Ogni generazione o adattamento crea nuove voci in `Scheda_Esercizi`
  - I feedback dell’utente (carico effettivo, DOMS) vengono salvati in `Progressi`

## ⚙️ Installazione e Setup

1. Clona il repository:
   ```bash
   git clone https://github.com/tuo-username/ChatBotAi.git
   cd ChatBotAi
   ```
2. Crea e attiva un virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\\Scripts\\activate   # Windows
   ```
3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura MariaDB:
   - Esegui lo script `schema.sql` in MariaDB per creare le tabelle
   - Imposta variabili d’ambiente con credenziali DB

5. Avvia l’app:
   ```bash
   python main.py
   ```

## 🔍 Dettaglio dei Moduli

### 1. Model
```python
# creascheda.py
class CreaScheda:
    def genera(self, utente_params, esercizi_db):
        # logica BMR, scelta esercizi, volume distribution...
```
```python
# adattascheda.py
class AdattaScheda:
    def adatta(self, scheda_precedente, feedback_utente):
        # calcolo SFR, stima 1RM, regolazione serie...
```

### 2. Controller
```python
# controller.py
class Controller:
    def crea_scheda(self, params):
        model = CreaScheda()
        scheda = model.genera(params, self.db.esercizi)
        self.db.save_scheda(scheda)
        return scheda

    def adatta_scheda(self, user_id):
        feedback = self.db.get_feedback(user_id)
        model = AdattaScheda()
        nuova_scheda = model.adatta(self.db.get_last_scheda(user_id), feedback)
        self.db.save_scheda(nuova_scheda)
        return nuova_scheda
```

### 3. View
```python
# main.py
def main(page):
    page.drawer = Sidebar([...])
    page.views.append(home_view(page))
    page.views.append(progress_view(page))
    page.views.append(nutrition_view(page))
    page.views.append(chatbot_view(page))
```
- Le view vengono caricate in base alla route: il layout `main.py` dichiara la sidebar e il `page.on_route_change` sostituisce il contenuto centrale.

## 🧪 Testing
- **Unit test** per Model: verifica output generazione e adattamento (pytest)
- **Test manuali UI** in Flet
- **Survey Google Forms** per validazione di mercato (target universitario)

## 🚀 Esempio di Esecuzione
![Screenshot dell'app](docs/screenshot.png)

## 📈 Sviluppi Futuri
- Migrazione su backend FastAPI+Flutter mobile
- Aggiunta di moduli avanzati: mesocicli custom, chat AI avanzata, gamification
- Deployment su cloud con continuous integration

---
*Documentazione generata automaticamente il 21/07/2025*

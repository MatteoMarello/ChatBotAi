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

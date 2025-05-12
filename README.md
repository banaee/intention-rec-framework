# Intention-Rec Framework

A Python-based simulation and reasoning framework for **intention recognition in human-robot collaboration**, developed for academic research and experimental modeling.

This framework models multi-agent environments (e.g., factory settings) where agents (humans, robots) interact with passive objects and perform tasks. It includes custom planning, execution, and reasoning components, integrated with a customized Mesa fork and interactive Solara-based UI.

---

## 🔧 Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application (Factory Simulation)

```bash
solara run app.py
```

---

## 🧭 Running Flow (High-Level)

1. `app.py` launches a Solara-based GUI.
2. The model (e.g., `FactoryModel`) is initialized with parameters.
3. Agents (humans, robots) are scheduled step-by-step.
4. Each agent plans its actions, executes them via microactions.
5. The robot infers human intentions from observed actions.
6. The symbolic world state is continuously updated and visualized.

---

## 📁 Key Components

* `actors/`: Human and robot definitions
* `intentions/`: Task and action models, recognizer logic
* `planning/`, `execution/`: Planning and acting pipeline
* `state/`: Symbolic state updates and predicate tracking
* `visualization/`: Solara UI, portrayal logic
* `my_mesa/`: Customized simulation core (Mesa fork)

---


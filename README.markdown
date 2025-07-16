# 🧭🤖 AI Career Navigator: Personalized Career Path & Skills Advisor 🚀
_Modern desktop application (GUI) and CLI tool for career analysis, development recommendations, and career path simulation using AI and visualizations._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-GUI-FFB300.svg)](https://wiki.python.org/moin/TkInter)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458.svg?logo=pandas)](https://pandas.pydata.org/)

---

## 📋 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Screenshots (GUI & Output)](#-screenshots-gui--output)
4. [System Requirements & Dependencies](#-system-requirements--dependencies)
5. [Installation and Setup](#️-installation-and-setup)
6. [Usage Guide (Graphical Interface)](#️-usage-guide-graphical-interface)
7. [Usage Guide (Command-Line Interface)](#️-usage-guide-command-line-interface)
8. [Project File Structure](#-project-file-structure)
9. [Technical Notes & Considerations](#-technical-notes--considerations)
10. [Contributing](#-contributing)
11. [License](#-license)
12. [Contact](#-contact)

---

## 📄 Overview

**AI Career Navigator** is a modern desktop application (GUI) and CLI tool that supports users in career planning, competency analysis, development forecasting, and professional decision-making. Through advanced CV/profile analysis, dynamic recommendations, interactive charts, and "what-if" simulations, the application enables conscious management of professional development.

---

## ✨ Key Features

- 🖥️ **Modern graphical interface (GUI):**
  - Dashboard with insights, charts, What-if section, dark mode, and responsive layout.
  - Dynamic recommendations and alerts based on profile and simulations.
- 📊 **Advanced visualizations:**
  - Radar chart (spider chart) of competency gaps.
  - Comparative salary charts (baseline vs What-if scenarios).
  - Interactive market trend charts and skill development graphs.
- 🤔 **"What-if" simulations:**
  - Ability to test how learning a new skill or changing industries will affect career path, salary, and promotions.
- 📄 **Report export:**
  - Export insights, charts, and simulations to PDF and CSV (one click).
- 📝 **CV/profile analysis:**
  - Automatic skill detection, gap analysis, development recommendations.
- 🛤️ **Personalized career paths:**
  - Generation and visualization of optimal development paths based on market and profile.
- ⚙️ **CLI mode (alternative):**
  - Complete analysis and recommendations from terminal.
- 🌙 **Dark mode:**
  - Modern, readable appearance with theme switching capability.

---

## 🖼️ Screenshots (GUI & Output)

> **Sample screens (add your own screenshots after running!):**

- **Dashboard:**
  - Insights and recommendations section (dynamic tips, alerts).
  - Radar chart of competency gaps.
  - What-if section (simulation of alternative scenarios).
  - Comparative salary chart (baseline vs What-if).
  - PDF/CSV report export button.

- **CV Analysis:**
  - Automatic skill and level detection.
  - Development recommendations.

- **Career Simulation:**
  - Interactive charts of salary growth, skills, promotion opportunities.

- **PDF/CSV Export:**
  - Reports with insights and charts ready for presentation or archiving.

---

## ⚙️ System Requirements & Dependencies

- **Python**: 3.8 or newer
- **Libraries:**
  - `tkinter` (GUI)
  - `pandas`, `numpy`, `matplotlib`, `fpdf`, `scikit-learn`, `spacy`
  - (details in `requirements.txt`)
- **System:**
  - Windows, Linux, MacOS (recommended min. 8GB RAM for smooth chart operation)

---

## 🛠️ Installation and Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Prepare data files:**
   - Ensure that `skills_database.csv`, `roles_database.csv`, `job_market_data.csv` are in the `data/` directory.
5. **Run GUI application:**
   ```bash
   python gui.py
   ```

---

## 💡 Usage Guide (Graphical Interface)

1. **Launch the application:**
   ```bash
   python gui.py
   ```
2. **Dashboard:**
   - Browse insights, charts, What-if section.
   - Export PDF/CSV reports.
3. **CV/profile analysis:**
   - Load CV or profile, view detected skills and recommendations.
4. **Simulations and What-if:**
   - Test the impact of new skills/industries on your career.
   - Compare scenarios on charts.
5. **Export:**
   - Generate PDF/CSV reports from any section.

---

## 💡 Usage Guide (Command-Line Interface)

CLI is still available as an alternative:

```bash
python main.py [--cv PATH_TO_CV.TXT] [--profile PATH_TO_PROFILE.JSON] [--target-role "TARGET_ROLE_NAME"] [--output OUTPUT_FILENAME.JSON]
```

- `--cv PATH_TO_CV.TXT`: (optional) path to CV file.
- `--profile PATH_TO_PROFILE.JSON`: (optional) path to profile file.
- `--target-role "TARGET_ROLE_NAME"`: (optional) target role.
- `--output OUTPUT_FILENAME.JSON`: (optional) output file (default: `career_recommendations.json`).

---

## 🗂️ Project File Structure
- `gui.py`: Modern graphical interface (Tkinter, dashboard, charts, insights, exports).
- `main.py`: CLI mode (analysis, recommendations, simulations from terminal).
- `modules/`: Analytical modules (`skills_analyzer.py`, `market_trends.py`, `career_path.py`, `career_simulator.py`).
- `config/`: Application configuration.
- `data/`: Data files (`skills_database.csv`, `roles_database.csv`, `job_market_data.csv`).
- `requirements.txt`: Dependencies list.
- `README.markdown`: Documentation.

---

## 📝 Technical Notes & Considerations
- **Data quality**: The better the CSV files, the more accurate the recommendations.
- **Performance**: For large files/data, environment with min. 8GB RAM is recommended.
- **AI/ML**: Modules can be expanded with more advanced algorithms (NLP, prediction, course API integrations, etc.).
- **Development**: Modular code, easy to expand with additional features and integrations.

---

## 🤝 Contributing
Want to add a new feature, better chart, API integration, or improve UX? Fork the repository, create a branch, submit a Pull Request!

---

## 📃 License
MIT License. Details in LICENSE file.

---

## 📧 Contact
Project: **Adrian Lesniak**. Questions, feedback, change proposals – open an issue or contact via GitHub.

---
✨ _Modern career path navigation with AI and visualizations!_

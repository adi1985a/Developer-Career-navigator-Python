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

**AI Career Navigator** is a modern desktop application (GUI) and CLI tool that supports users in career planning, competency analysis, development forecasting, and professional decision-making. The application features a modern, responsive interface, multi-language support, dynamic recommendations, interactive charts, and "what-if" simulations for conscious career management.

<br> 
<p align="center">
  <img src="screenshots/1.gif" width="90%">
</p>
<br>


---

## ✨ Key Features

- 🖥️ **Modern graphical interface (GUI):**
  - Large, responsive window with vertical navigation menu (icons above text)
  - Dashboard with insights, stats cards, quick access, and charts
  - All content centered and scrollable for large data
  - Dark mode and multiple color themes
  - Multi-language support (English, Norwegian, Polish)
- 👤 **User Profile Management:**
  - Create, edit, and save user profiles
  - Add/remove skills, set experience, education, and salary expectations
  - Auto-save and export profile data
- 📄 **CV Analysis:**
  - Paste or load CV for automatic skill extraction and analysis
  - Detect skill levels, experience, and generate personalized recommendations
  - Export analysis results
- 🛤️ **Career Path Generation:**
  - Set current and target roles, time horizon, and priorities
  - Generate optimal career paths with required skills and salary projections
  - Visualize career steps and missing skills
- 🧪 **Career Simulation:**
  - Simulate career progression for different scenarios (learning intensity, job change strategy, time horizon)
  - Analyze salary growth, promotion chances, and skill acquisition over time
  - Interactive charts and detailed results
- 📈 **Market Trends Analysis:**
  - Analyze job market trends by skill category and time range
  - View demand and salary trends, hot skills, and top paid skills
  - Export market analysis results
- ⚙️ **Settings:**
  - Configure output directory, export format (JSON, CSV, TXT), auto-save, and theme
  - All settings saved and loaded automatically
- 🌙 **Dark mode & themes:**
  - Switch between light, dark, blue, and green themes
- 🌐 **Multi-language UI:**
  - Switch interface language (English, Norwegian, Polish)
- 📝 **Export:**
  - Export reports, analysis, and simulations to PDF and CSV
- 🧩 **Modular design:**
  - Easily extendable with new features and integrations

---

## 🖼️ Screenshots (GUI & Output)

> **Sample screens :**

- **Dashboard:**
  - Insights, stats cards, quick access buttons, radar and bar charts
  <img src="screenshots\1.jpg" width="300"/>
- **User Profile:**
  - Personal and professional data, skills management, save/load profile
  <img src="screenshots\2.jpg" width="300"/>
- **CV Analysis:**
  - Paste or load CV, analyze skills, view recommendations
  <img src="screenshots\3.jpg" width="300"/>
- **Career Path:**
  - Set goals, generate and visualize career steps, see required skills
  <img src="screenshots\4.jpg" width="300"/>
- **Career Simulation:**
  - Set parameters, run simulation, view salary and promotion charts
  <img src="screenshots\5.jpg" width="300"/>
- **Market Trends:**
  - Analyze demand and salary trends, hot skills, top paid skills
  <img src="screenshots\6.jpg" width="300"/>
  <img src="screenshots\7.jpg" width="300"/>
- **Settings:**
  - Output, export, theme, and language options
  <img src="screenshots\8.jpg" width="300"/>

---

## ⚙️ System Requirements & Dependencies

- **Python**: 3.8 or newer
- **Libraries:**
  - `tkinter` (GUI)
  - `pandas`, `numpy`, `matplotlib`, `fpdf`, `scikit-learn`, `spacy`, `Pillow`
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
   - The app will auto-create sample data if missing.
5. **Run GUI application:**
   ```bash
   python gui.py
   ```
6. **Run CLI mode:**
   ```bash
   python main.py --cv my_cv.txt --profile my_profile.json --target-role "Senior Python Developer" --output recommendations.json
   ```

---

## 💡 Usage Guide (Graphical Interface)

1. **Launch the application:**
   ```bash
   python gui.py
   ```
2. **Navigation:**
   - Use the vertical menu to access: Dashboard, User Profile, CV Analysis, Career Path, Career Simulation, Market Trends, Settings
3. **User Profile:**
   - Fill in personal/professional data, add/remove skills, save/load profile
4. **CV Analysis:**
   - Paste or load your CV, analyze, and review recommendations
5. **Career Path:**
   - Set your current/target role, time horizon, and generate a career path
6. **Career Simulation:**
   - Set simulation parameters and run to see projected outcomes
7. **Market Trends:**
   - Analyze trends by skill category and time range
8. **Settings:**
   - Change output, export format, theme, and language
9. **Export:**
   - Export reports and results to PDF/CSV from any section

---

## 💡 Usage Guide (Command-Line Interface)

CLI is available as an alternative:

```bash
python main.py [--cv PATH_TO_CV.TXT] [--profile PATH_TO_PROFILE.JSON] [--target-role "TARGET_ROLE_NAME"] [--output OUTPUT_FILENAME.JSON]
```

- `--cv PATH_TO_CV.TXT`: (optional) path to CV file.
- `--profile PATH_TO_PROFILE.JSON`: (optional) path to profile file.
- `--target-role "TARGET_ROLE_NAME"`: (optional) target role.
- `--output OUTPUT_FILENAME.JSON`: (optional) output file (default: `career_recommendations.json`).

---

## 🗂️ Project File Structure
- `gui.py`: Modern graphical interface (Tkinter, dashboard, charts, insights, exports, multi-language)
- `main.py`: CLI mode (analysis, recommendations, simulations from terminal)
- `modules/`: Analytical modules (`skills_analyzer.py`, `market_trends.py`, `career_path.py`, `career_simulator.py`)
- `config/`: Application configuration
- `data/`: Data files (`skills_database.csv`, `roles_database.csv`, `job_market_data.csv`)
- `output/`: Exported reports and profiles
- `requirements.txt`: Dependencies list
- `README.markdown`: Documentation
- `settings.json`: User settings

---

## 📝 Technical Notes & Considerations
- **Data quality**: The better the CSV files, the more accurate the recommendations.
- **Performance**: For large files/data, environment with min. 8GB RAM is recommended.
- **AI/ML**: Modules can be expanded with more advanced algorithms (NLP, prediction, course API integrations, etc.).
- **Development**: Modular code, easy to expand with additional features and integrations.
- **Multi-language**: UI and instructions can be translated and extended.
- **Modern UI/UX**: Consistent padding, centering, icons, and scrollbars for large content.

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

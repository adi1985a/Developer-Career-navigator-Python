# 🧭🤖 AI Career Navigator: Personalized Career Path & Skills Advisor 🚀
_Nowoczesna aplikacja desktopowa (GUI) oraz narzędzie CLI do analizy kariery, rekomendacji rozwoju i symulacji ścieżek zawodowych z wykorzystaniem AI i wizualizacji._

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

**AI Career Navigator** to nowoczesna aplikacja desktopowa (GUI) oraz narzędzie CLI, które wspiera użytkownika w planowaniu kariery, analizie kompetencji, prognozowaniu rozwoju i podejmowaniu decyzji zawodowych. Dzięki zaawansowanej analizie CV/profilu, dynamicznym rekomendacjom, interaktywnym wykresom i symulacjom „co jeśli”, aplikacja pozwala świadomie zarządzać rozwojem zawodowym.

---

## ✨ Key Features

- 🖥️ **Nowoczesny interfejs graficzny (GUI):**
  - Dashboard z insightami, wykresami, sekcją What-if, dark mode i responsywnym układem.
  - Dynamiczne rekomendacje i alerty na podstawie profilu i symulacji.
- 📊 **Zaawansowane wizualizacje:**
  - Wykres radarowy (spider chart) luk kompetencyjnych.
  - Porównawcze wykresy zarobków (scenariusz bazowy vs What-if).
  - Interaktywne wykresy trendów rynkowych i rozwoju umiejętności.
- 🤔 **Symulacje „What-if”:**
  - Możliwość sprawdzenia, jak nauka nowej umiejętności lub zmiana branży wpłynie na ścieżkę kariery, zarobki i awanse.
- 📄 **Eksport raportów:**
  - Eksport insightów, wykresów i symulacji do PDF i CSV (jeden klik).
- 📝 **Analiza CV/profilu:**
  - Automatyczne wykrywanie umiejętności, luk, rekomendacje rozwoju.
- 🛤️ **Personalizowane ścieżki kariery:**
  - Generowanie i wizualizacja optymalnych ścieżek rozwoju na podstawie rynku i profilu.
- ⚙️ **Tryb CLI (alternatywa):**
  - Pełna analiza i rekomendacje z poziomu terminala.
- 🌙 **Dark mode:**
  - Nowoczesny, czytelny wygląd z możliwością zmiany motywu.

---

## 🖼️ Screenshots (GUI & Output)

> **Przykładowe ekrany (dodaj własne zrzuty po uruchomieniu!):**

- **Dashboard:**
  - Sekcja insightów i rekomendacji (dynamiczne podpowiedzi, alerty).
  - Wykres radarowy luk kompetencyjnych.
  - Sekcja What-if (symulacja alternatywnych scenariuszy).
  - Wykres porównawczy zarobków (bazowy vs What-if).
  - Przycisk eksportu raportu PDF/CSV.

- **Analiza CV:**
  - Automatyczne wykrywanie umiejętności i poziomów.
  - Rekomendacje rozwoju.

- **Symulacja kariery:**
  - Interaktywne wykresy rozwoju zarobków, umiejętności, szans na awans.

- **Eksport PDF/CSV:**
  - Raporty z insightami i wykresami gotowe do prezentacji lub archiwizacji.

---

## ⚙️ System Requirements & Dependencies

- **Python**: 3.8 lub nowszy
- **Biblioteki:**
  - `tkinter` (GUI)
  - `pandas`, `numpy`, `matplotlib`, `fpdf`, `scikit-learn`, `spacy`
  - (szczegóły w `requirements.txt`)
- **System:**
  - Windows, Linux, MacOS (zalecane min. 8GB RAM dla płynnej pracy z wykresami)

---

## 🛠️ Installation and Setup

1. **Klonuj repozytorium:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Utwórz środowisko wirtualne:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Przygotuj pliki danych:**
   - Upewnij się, że w katalogu `data/` znajdują się: `skills_database.csv`, `roles_database.csv`, `job_market_data.csv`.
5. **Uruchom aplikację GUI:**
   ```bash
   python gui.py
   ```

---

## 💡 Usage Guide (Graphical Interface)

1. **Uruchom aplikację:**
   ```bash
   python gui.py
   ```
2. **Dashboard:**
   - Przeglądaj insighty, wykresy, sekcję What-if.
   - Eksportuj raporty PDF/CSV.
3. **Analiza CV/profilu:**
   - Wczytaj CV lub profil, zobacz wykryte umiejętności i rekomendacje.
4. **Symulacje i What-if:**
   - Przetestuj wpływ nowych umiejętności/branż na swoją karierę.
   - Porównuj scenariusze na wykresach.
5. **Eksport:**
   - Generuj raporty PDF/CSV z dowolnej sekcji.

---

## 💡 Usage Guide (Command-Line Interface)

CLI jest nadal dostępny jako alternatywa:

```bash
python main.py [--cv PATH_TO_CV.TXT] [--profile PATH_TO_PROFILE.JSON] [--target-role "TARGET_ROLE_NAME"] [--output OUTPUT_FILENAME.JSON]
```

- `--cv PATH_TO_CV.TXT`: (opcjonalnie) ścieżka do pliku CV.
- `--profile PATH_TO_PROFILE.JSON`: (opcjonalnie) ścieżka do pliku profilu.
- `--target-role "TARGET_ROLE_NAME"`: (opcjonalnie) docelowa rola.
- `--output OUTPUT_FILENAME.JSON`: (opcjonalnie) plik wyjściowy (domyślnie `career_recommendations.json`).

---

## 🗂️ Project File Structure
- `gui.py`: Nowoczesny interfejs graficzny (Tkinter, dashboard, wykresy, insighty, eksporty).
- `main.py`: Tryb CLI (analiza, rekomendacje, symulacje z terminala).
- `modules/`: Moduły analityczne (`skills_analyzer.py`, `market_trends.py`, `career_path.py`, `career_simulator.py`).
- `config/`: Konfiguracja aplikacji.
- `data/`: Pliki danych (`skills_database.csv`, `roles_database.csv`, `job_market_data.csv`).
- `requirements.txt`: Lista zależności.
- `README.markdown`: Dokumentacja.

---

## 📝 Technical Notes & Considerations
- **Jakość danych**: Im lepsze pliki CSV, tym trafniejsze rekomendacje.
- **Wydajność**: Przy dużych plikach/danych zalecane jest środowisko z min. 8GB RAM.
- **AI/ML**: Moduły mogą być rozbudowywane o bardziej zaawansowane algorytmy (NLP, predykcja, integracje API kursów itp.).
- **Rozwój**: Kod modularny, łatwy do rozbudowy o kolejne funkcje i integracje.

---

## 🤝 Contributing
Chcesz dodać nową funkcję, lepszy wykres, integrację z API lub poprawić UX? Forkuj repozytorium, utwórz branch, zgłoś Pull Request!

---

## 📃 License
MIT License. Szczegóły w pliku LICENSE.

---

## 📧 Contact
Projekt: **Adrian Lesniak**. Pytania, feedback, propozycje zmian – otwórz issue lub skontaktuj się przez GitHub.

---
✨ _Nowoczesna nawigacja po ścieżce kariery z AI i wizualizacjami!_

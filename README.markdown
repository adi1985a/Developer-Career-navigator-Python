# AI Career Navigator

## Overview
AI Career Navigator is a Python command-line tool that analyzes user CVs and profiles to provide personalized career recommendations. It uses skills analysis, market trends, career path generation, and simulation to suggest roles, skills, and career progression. Outputs recommendations in JSON format.

## Features
- **Skills Analysis**: Extracts and evaluates skills from CVs or user profiles.
- **Market Trends**: Analyzes job market data to identify emerging skills and demand.
- **Career Path Generation**: Suggests career paths based on current role and skills.
- **Career Simulation**: Simulates career progression over time, including salary and promotions.
- **Command-Line Interface**: Supports CV/profile input and customizable output via arguments.

## Requirements
- Python 3.6+
- Libraries:
  - `pandas` (assumed for data handling in modules)
- Data files:
  - `data/skills_database.csv`
  - `data/roles_database.csv`
  - `data/job_market_data.csv`

Install dependencies using:
```bash
pip install pandas
```

## Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install the required library (see Requirements).
3. Place required CSV files in the `data/` directory.
4. Run the application:
   ```bash
   python main.py
   ```

## Usage
1. Run the app with command-line arguments to analyze a profile or CV:
   ```bash
   python main.py --cv path/to/cv.txt --profile path/to/profile.json --target-role "Senior Developer" --output recommendations.json
   ```
2. **Arguments**:
   - `--cv`: Path to a text file containing the CV.
   - `--profile`: Path to a JSON file with user profile data.
   - `--target-role`: Desired career role (optional).
   - `--output`: Output file for recommendations (default: `career_recommendations.json`).
3. The app generates a JSON file with career paths, skill recommendations, market insights, and simulation data.

## File Structure
- `main.py`: Main script with the `AICareerNavigator` class and CLI logic.
- `modules/`: Directory containing core modules:
  - `skills_analyzer.py`: Analyzes user skills.
  - `market_trends.py`: Processes job market data.
  - `career_path.py`: Generates career paths.
  - `career_simulator.py`: Simulates career progression.
- `config/config.py`: Configuration file with model paths and API settings.
- `data/`: Directory for CSV files (`skills_database.csv`, `roles_database.csv`, `job_market_data.csv`).
- `ai_career_navigator.log`: Log file for application events.
- `README.md`: This file, providing project documentation.

## Notes
- Ensure CSV files (`skills_database.csv`, `roles_database.csv`, `job_market_data.csv`) are in the `data/` directory with appropriate formats.
- Module implementations (`SkillsAnalyzer`, `MarketTrends`, etc.) are assumed to exist and handle data processing.
- Logging is configured to output to both `ai_career_navigator.log` and the console.
- The app uses placeholder logic for some operations (e.g., role ID lookup); actual implementations may vary.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make changes and commit (`git commit -m "Add feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or feedback, open an issue on GitHub or contact the repository owner.
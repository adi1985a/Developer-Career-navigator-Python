from flask import Flask, request, jsonify
import logging
import os
import json
from datetime import datetime

from ..modules.skills_analyzer import SkillsAnalyzer
from ..modules.market_trends import MarketTrends
from ..modules.career_path import CareerPathGenerator
from ..modules.career_simulator import CareerSimulator
from ..config.config import API_CONFIG, DATABASE_CONFIG

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Inicjalizacja aplikacji Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = API_CONFIG['secret_key']

# Inicjalizacja komponentów
skills_analyzer = SkillsAnalyzer(skills_database_path='data/skills_database.csv')
market_trends = MarketTrends(data_path='data/job_market_data.csv')
career_path_generator = CareerPathGenerator(
    skills_database_path='data/skills_database.csv',
    roles_database_path='data/roles_database.csv'
)
career_simulator = CareerSimulator(
    skills_analyzer=skills_analyzer,
    market_trends=market_trends,
    career_path_generator=career_path_generator
)

@app.route('/api/analyze-cv', methods=['POST'])
def analyze_cv():
    """Analizuje CV i zwraca zidentyfikowane umiejętności i poziomy"""
    if not request.json or 'cv_text' not in request.json or not isinstance(request.json['cv_text'], str):
        return jsonify({'error': 'Missing or invalid parameter: cv_text (string required)'}), 400
    
    cv_text = request.json['cv_text']
    
    try:
        # Ekstrakcja umiejętności
        skills = skills_analyzer.extract_skills_from_cv(cv_text)
        
        # Analiza poziomów umiejętności
        skill_levels = {}
        for skill in skills:
            level = skills_analyzer.analyze_skill_level(cv_text, skill)
            skill_levels[skill] = level
        
        return jsonify({
            'status': 'success',
            'skills': [{'name': skill, 'level': level} for skill, level in skill_levels.items()]
        })
    except Exception as e:
        logger.error(f"Błąd podczas analizy CV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-trends', methods=['GET'])
def get_market_trends():
    """Zwraca aktualne trendy rynkowe"""
    try:
        # Pobierz najważniejsze trendy
        top_skills = market_trends.get_top_emerging_skills(10)
        
        if hasattr(top_skills, 'to_dict'):
            top_skills_list = top_skills.to_dict('records')
        else:
            top_skills_list = [dict(zip(['skill', 'growth', 'demand', 'trend'], row)) for row in top_skills]
        
        return jsonify({
            'status': 'success',
            'top_emerging_skills': top_skills_list,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Błąd podczas pobierania trendów rynkowych: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-path', methods=['POST'])
def generate_career_path():
    """Generuje ścieżkę kariery na podstawie aktualnej i docelowej roli"""
    if not request.json or 'current_role_id' not in request.json or not isinstance(request.json['current_role_id'], (str, int)):
        return jsonify({'error': 'Missing or invalid parameter: current_role_id (string or int required)'}), 400
    
    current_role_id = request.json['current_role_id']
    target_role_id = request.json.get('target_role_id', None)
    max_steps = request.json.get('max_steps', 5)
    
    try:
        career_path = career_path_generator.generate_career_path(
            current_role_id, target_role_id, max_steps=max_steps
        )
        
        return jsonify({
            'status': 'success',
            'career_path': [
                {
                    'role_id': role.get('role_id', ''),
                    'name': role.get('role_name', ''),
                    'level': role.get('level', ''),
                    'salary': role.get('avg_salary', 0),
                    'experience_required': role.get('experience_years', 0)
                }
                for role in career_path
            ]
        })
    except Exception as e:
        logger.error(f"Błąd podczas generowania ścieżki kariery: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/career-simulation', methods=['POST'])
def simulate_career():
    """Symuluje przyszłą karierę na podstawie profilu użytkownika"""
    if not request.json or 'user_profile' not in request.json or not isinstance(request.json['user_profile'], dict):
        return jsonify({'error': 'Missing or invalid parameter: user_profile (dict required)'}), 400
    
    user_profile = request.json['user_profile']
    target_role = request.json.get('target_role', None)
    years = request.json.get('years', 5)
    
    try:
        simulation = career_simulator.simulate_career_progression(
            user_profile, target_role, years=years
        )
        
        # Wybierz punkty co roku dla czytelności
        key_points = simulation[simulation['date'].dt.month % 12 == 0]
        
        return jsonify({
            'status': 'success',
            'simulation': {
                'salary_projection': key_points[['date', 'salary']].to_dict('records'),
                'skills_growth': key_points[['date', 'skills_count']].to_dict('records'),
                'promotion_chances': key_points[['date', 'promotion_chance']].to_dict('records'),
                'promotions': simulation[simulation.get('event', '') == 'Awans zawodowy'][['date', 'role']].to_dict('records')
            }
        })
    except Exception as e:
        logger.error(f"Błąd podczas symulacji kariery: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommend-skills', methods=['POST'])
def recommend_skills():
    """Rekomenduje umiejętności do zdobycia dla osiągnięcia docelowej roli"""
    if not request.json or 'current_skills' not in request.json or 'target_role_id' not in request.json or not isinstance(request.json['current_skills'], list):
        return jsonify({'error': 'Missing or invalid parameters: current_skills (list) and target_role_id required'}), 400
    
    current_skills = request.json['current_skills']
    target_role_id = request.json['target_role_id']
    
    try:
        skill_recommendations = career_path_generator.recommend_skills_for_path(
            current_skills, target_role_id
        )
        
        return jsonify({
            'status': 'success',
            'recommendations': [
                {
                    'skill_id': skill_id,
                    'name': data.get('skill_name', ''),
                    'category': data.get('category', ''),
                    'priority': data.get('priority', 5),
                    'difficulty': data.get('difficulty', 3),
                    'estimated_time': data.get('estimated_time', 3)
                }
                for skill_id, data in skill_recommendations.items()
            ]
        })
    except Exception as e:
        logger.error(f"Błąd podczas rekomendacji umiejętności: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Sprawdza stan systemu"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'skills_analyzer': skills_analyzer is not None,
            'market_trends': market_trends is not None,
            'career_path_generator': career_path_generator is not None,
            'career_simulator': career_simulator is not None
        }
    })

def start_api_server():
    """Uruchamia serwer API"""
    app.run(
        host=API_CONFIG['host'],
        port=API_CONFIG['port'],
        debug=API_CONFIG['debug']
    )

if __name__ == "__main__":
    start_api_server() 
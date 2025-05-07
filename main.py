import os
import logging
import argparse
import json
from datetime import datetime

from modules.skills_analyzer import SkillsAnalyzer
from modules.market_trends import MarketTrends
from modules.career_path import CareerPathGenerator
from modules.career_simulator import CareerSimulator
from config.config import MODEL_PATHS, API_CONFIG

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_career_navigator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AICareerNavigator:
    """Główna klasa systemu AI Career Navigator"""
    
    def __init__(self):
        """Inicjalizacja systemu"""
        logger.info("Inicjalizacja AI Career Navigator")
        
        # Inicjalizacja komponentów
        self.skills_analyzer = self._init_skills_analyzer()
        self.market_trends = self._init_market_trends()
        self.career_path_generator = self._init_career_path_generator()
        self.career_simulator = self._init_career_simulator()
        self.market_trends_analyzer = MarketTrends()
        
        # Załaduj dane
        self.load_data()
        
        logger.info("Inicjalizacja systemu zakończona")
    
    def _init_skills_analyzer(self):
        """Inicjalizuje analizator umiejętności"""
        logger.info("Inicjalizacja analizatora umiejętności")
        try:
            # Initialize with just the database path
            analyzer = SkillsAnalyzer(
                skills_database_path='data/skills_database.csv'
            )
            return analyzer
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji analizatora umiejętności: {e}")
            return SkillsAnalyzer()
    
    def _init_market_trends(self):
        """Inicjalizuje analizator trendów rynkowych"""
        logger.info("Inicjalizacja analizatora trendów rynkowych")
        try:
            market_model_path = MODEL_PATHS.get('market_trends_model')
            return MarketTrends(data_path='data/job_market_data.csv')
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji analizatora trendów rynkowych: {e}")
            return MarketTrends()
    
    def _init_career_path_generator(self):
        """Inicjalizuje generator ścieżek kariery"""
        logger.info("Inicjalizacja generatora ścieżek kariery")
        try:
            return CareerPathGenerator(
                skills_database_path='data/skills_database.csv',
                roles_database_path='data/roles_database.csv'
            )
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji generatora ścieżek kariery: {e}")
            return CareerPathGenerator()
    
    def _init_career_simulator(self):
        """Inicjalizuje symulator kariery"""
        logger.info("Inicjalizacja symulatora kariery")
        try:
            return CareerSimulator(
                skills_analyzer=self.skills_analyzer,
                market_trends=self.market_trends,
                career_path_generator=self.career_path_generator
            )
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji symulatora kariery: {e}")
            return CareerSimulator()
    
    def analyze_user_profile(self, cv_text=None, profile_data=None):
        """
        Analizuje profil użytkownika na podstawie CV lub podanych danych
        
        Args:
            cv_text: Tekst CV
            profile_data: Dane profilu użytkownika
            
        Returns:
            Słownik z analizą profilu
        """
        logger.info("Rozpoczęcie analizy profilu użytkownika")
        
        # Przygotuj profil
        profile = {}
        
        # Jeśli przekazano dane profilu, użyj ich
        if profile_data:
            profile = profile_data
        
        # Jeśli przekazano CV, analizuj je
        if cv_text:
            # Ekstrakcja umiejętności
            skills = self.skills_analyzer.extract_skills_from_cv(cv_text)
            
            # Analiza poziomów umiejętności
            skill_levels = {}
            for skill in skills:
                level = self.skills_analyzer.analyze_skill_level(cv_text, skill)
                skill_levels[skill] = level
            
            # Dodaj do profilu
            profile['detected_skills'] = [
                {'name': skill, 'level': level} for skill, level in skill_levels.items()
            ]
        
        # Rozszerz profil o analizę rynkową
        if self.market_trends and 'detected_skills' in profile:
            # Pobierz trendy dla umiejętności
            skills_trends = {}
            for skill_data in profile['detected_skills']:
                skill_name = skill_data['name']
                trend = self.market_trends.predict_future_trends(skill_name)
                skills_trends[skill_name] = {
                    'current_demand': trend.iloc[-1]['value'] if not trend.empty else 0,
                    'trend': 'rising' if not trend.empty and trend.iloc[-1]['value'] > trend.iloc[0]['value'] else 'falling'
                }
            
            profile['skills_market_analysis'] = skills_trends
            
            # Dodaj rekomendowane umiejętności
            top_emerging = self.market_trends.get_top_emerging_skills(5)
            profile['recommended_emerging_skills'] = top_emerging.to_dict('records') if not top_emerging.empty else []
        
        logger.info("Analiza profilu użytkownika zakończona")
        return profile
    
    def generate_career_recommendations(self, user_profile, target_role=None):
        """
        Generuje rekomendacje kariery dla użytkownika
        
        Args:
            user_profile: Profil użytkownika
            target_role: Docelowa rola (opcjonalnie)
            
        Returns:
            Słownik z rekomendacjami
        """
        logger.info("Generowanie rekomendacji kariery")
        
        recommendations = {
            'timestamp': datetime.now().isoformat(),
            'career_paths': [],
            'skill_recommendations': [],
            'market_insights': {}
        }
        
        # Pobierz aktualną rolę
        current_role = user_profile.get('current_role', None)
        
        # Jeśli nie podano docelowej roli, wybierz najlepszą
        if target_role is None and current_role:
            # To jest uproszczone - w rzeczywistości powinniśmy mieć bardziej zaawansowaną logikę
            target_role = {
                'name': 'Senior ' + current_role.get('name', 'Specialist'),
                'level': 'Senior'
            }
        
        # Generuj ścieżkę kariery
        if self.career_path_generator and current_role:
            try:
                # Znajdź ID roli
                current_role_id = self._find_role_id(current_role.get('name', ''))
                target_role_id = self._find_role_id(target_role.get('name', '')) if target_role else None
                
                if current_role_id:
                    # Generuj ścieżkę
                    career_path = self.career_path_generator.generate_career_path(
                        current_role_id, target_role_id, max_steps=3
                    )
                    
                    # Dodaj do rekomendacji
                    recommendations['career_paths'] = [
                        {
                            'name': role.get('role_name', ''),
                            'level': role.get('level', ''),
                            'salary': role.get('avg_salary', 0),
                            'experience_required': role.get('experience_years', 0)
                        }
                        for role in career_path
                    ]
                    
                    # Dodaj rekomendacje umiejętności dla ścieżki
                    if target_role_id:
                        current_skills = [s.get('skill_id', 0) for s in user_profile.get('skills', [])]
                        skill_recommendations = self.career_path_generator.recommend_skills_for_path(
                            current_skills, target_role_id
                        )
                        
                        recommendations['skill_recommendations'] = [
                            {
                                'name': data.get('skill_name', ''),
                                'priority': data.get('priority', 5),
                                'difficulty': data.get('difficulty', 3),
                                'estimated_time': data.get('estimated_time', 3)
                            }
                            for skill_id, data in skill_recommendations.items()
                        ]
            except Exception as e:
                logger.error(f"Błąd podczas generowania ścieżki kariery: {e}")
        
        # Dodaj analizę rynkową
        if self.market_trends:
            try:
                # Pobierz najważniejsze trendy
                top_skills = self.market_trends.get_top_emerging_skills(10)
                
                recommendations['market_insights'] = {
                    'top_emerging_skills': top_skills.to_dict('records') if not top_skills.empty else [],
                    'market_outlook': 'positive'  # To powinno być oparte na głębszej analizie
                }
            except Exception as e:
                logger.error(f"Błąd podczas analizy rynkowej: {e}")
        
        # Symuluj przyszłą karierę
        if self.career_simulator and target_role:
            try:
                simulation = self.career_simulator.simulate_career_progression(
                    user_profile, target_role, years=5
                )
                
                # Dodaj kluczowe punkty symulacji
                key_points = simulation[simulation['date'].dt.month % 12 == 0]  # Co roku
                
                recommendations['career_simulation'] = {
                    'salary_projection': key_points[['date', 'salary']].to_dict('records'),
                    'skills_growth': key_points[['date', 'skills_count']].to_dict('records'),
                    'estimated_promotion_timeline': simulation[simulation.get('event', '') == 'Awans zawodowy'][['date', 'role']].to_dict('records')
                }
                
                # Oblicz ROI
                roi_data = self.career_simulator.calculate_roi(simulation)
                recommendations['roi_analysis'] = roi_data
                
            except Exception as e:
                logger.error(f"Błąd podczas symulacji kariery: {e}")
        
        logger.info("Generowanie rekomendacji kariery zakończone")
        return recommendations
    
    def _find_role_id(self, role_name):
        """Znajduje ID roli na podstawie nazwy"""
        if not self.career_path_generator or not hasattr(self.career_path_generator, 'roles_db'):
            return None
            
        matching_roles = self.career_path_generator.roles_db[
            self.career_path_generator.roles_db['role_name'] == role_name
        ]
        
        if not matching_roles.empty:
            return matching_roles.iloc[0]['role_id']
        
        return None

    def load_data(self):
        """Ładuje niezbędne dane dla aplikacji"""
        logger.info("Ładowanie danych systemowych")
        try:
            # Ładowanie baz danych umiejętności, ról zawodowych itp.
            logger.info("Ładowanie bazy danych umiejętności")
            # Tutaj kod ładujący dane z plików lub baz danych
            
            # Ładowanie danych rynkowych
            logger.info("Ładowanie danych rynkowych")
            # Tutaj kod ładujący dane rynkowe
            
            logger.info("Dane załadowane pomyślnie")
        except Exception as e:
            logger.error(f"Błąd podczas ładowania danych: {e}")
            # Wczytaj minimalne dane aby program mógł działać
            logger.info("Używanie danych domyślnych")

def main():
    """Główna funkcja aplikacji"""
    parser = argparse.ArgumentParser(description='AI Career Navigator')
    parser.add_argument('--cv', help='Ścieżka do pliku CV')
    parser.add_argument('--profile', help='Ścieżka do pliku z profilem użytkownika (JSON)')
    parser.add_argument('--target-role', help='Docelowa rola zawodowa')
    parser.add_argument('--output', help='Ścieżka do pliku wyjściowego')
    args = parser.parse_args()
    
    # Inicjalizacja systemu
    navigator = AICareerNavigator()
    
    # Wczytaj CV jeśli podano
    cv_text = None
    if args.cv and os.path.isfile(args.cv):
        with open(args.cv, 'r', encoding='utf-8') as f:
            cv_text = f.read()
    
    # Wczytaj profil jeśli podano
    profile_data = None
    if args.profile and os.path.isfile(args.profile):
        with open(args.profile, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    
    # Analizuj profil
    user_profile = navigator.analyze_user_profile(cv_text, profile_data)
    
    # Ustaw docelową rolę jeśli podano
    target_role = None
    if args.target_role:
        target_role = {'name': args.target_role}
    
    # Generuj rekomendacje
    recommendations = navigator.generate_career_recommendations(user_profile, target_role)
    
    # Zapisz wynik
    output_path = args.output if args.output else 'career_recommendations.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=4, default=str)
        
    logger.info(f"Rekomendacje zapisane do pliku: {output_path}")
    print(f"Rekomendacje zapisane do pliku: {output_path}")

if __name__ == "__main__":
    main()
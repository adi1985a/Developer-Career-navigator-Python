import pandas as pd
import numpy as np
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class SkillsAnalyzer:
    def __init__(self, skills_database_path=None):
        """
        Inicjalizacja analizatora umiejętności
        
        Args:
            skills_database_path: Ścieżka do bazy danych umiejętności
        """
        try:
            # Próba załadowania modelu polskiego
            self.nlp = spacy.load('pl_core_news_md')
        except OSError:
            try:
                # Próba załadowania modelu angielskiego jako alternatywy
                self.nlp = spacy.load('en_core_web_sm')
                print("Model języka polskiego nie został znaleziony, używam modelu angielskiego.")
            except OSError:
                # Użyj pustego modelu jako ostateczność
                self.nlp = spacy.blank('pl')
                print("Nie znaleziono żadnego modelu spaCy, używam prostego modelu zastępczego.")
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Załaduj bazę danych umiejętności
        if skills_database_path:
            self.skills_db = pd.read_csv(skills_database_path)
        else:
            # Przykładowa baza umiejętności jako fallback
            self.skills_db = pd.DataFrame({
                'skill_name': ['Python', 'Java', 'JavaScript', 'SQL', 'Machine Learning', 
                               'Deep Learning', 'Data Analysis', 'Project Management'],
                'category': ['Programming', 'Programming', 'Programming', 'Database', 
                             'AI', 'AI', 'Data Science', 'Management'],
                'relevance_score': [10, 9, 8, 9, 10, 9, 8, 7]
            })
    
    def extract_skills_from_cv(self, cv_text):
        """
        Ekstrahuje umiejętności z tekstu CV
        
        Args:
            cv_text: Tekst CV
            
        Returns:
            Lista wykrytych umiejętności
        """
        # Przetwarzanie tekstu
        doc = self.nlp(cv_text)
        
        # Wykrywanie słów kluczowych z bazy umiejętności
        skills_found = []
        for skill in self.skills_db['skill_name']:
            # Prosta detekcja - można rozszerzyć o bardziej zaawansowane techniki
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', cv_text.lower()):
                skills_found.append(skill)
        
        return skills_found
    
    def analyze_skill_level(self, cv_text, skill):
        """
        Analizuje poziom zaawansowania dla danej umiejętności
        
        Args:
            cv_text: Tekst CV
            skill: Nazwa umiejętności
            
        Returns:
            Ocena poziomu zaawansowania (1-5)
        """
        # Szukaj fraz wskazujących na poziom zaawansowania
        beginner_phrases = ['podstawowy', 'podstawowa znajomość', 'początkujący', 'podstawy']
        intermediate_phrases = ['średnio zaawansowany', 'dobra znajomość', 'kilka lat doświadczenia']
        expert_phrases = ['ekspert', 'zaawansowana znajomość', 'biegły', 'wieloletnie doświadczenie']
        
        # Znajdź kontekst umiejętności
        skill_context = self._extract_skill_context(cv_text, skill)
        
        # Ocena poziomu na podstawie kontekstu
        if any(phrase in skill_context.lower() for phrase in expert_phrases):
            return 5
        elif any(phrase in skill_context.lower() for phrase in intermediate_phrases):
            return 3
        elif any(phrase in skill_context.lower() for phrase in beginner_phrases):
            return 1
        else:
            # Domyślny poziom, gdy nie wykryto wyraźnych wskazówek
            return 2
    
    def identify_skill_gaps(self, user_skills, target_job_skills):
        """
        Identyfikuje luki w umiejętnościach
        
        Args:
            user_skills: Lista umiejętności użytkownika
            target_job_skills: Lista umiejętności wymaganych dla docelowej pozycji
            
        Returns:
            Słownik z lukami w umiejętnościach i rekomendacjami
        """
        # Przekształć listy w zbiory dla łatwiejszego porównania
        user_skills_set = set(user_skills)
        job_skills_set = set(target_job_skills)
        
        # Znajdź luki - umiejętności wymagane, których nie posiada użytkownik
        missing_skills = job_skills_set - user_skills_set
        
        # Przygotuj rekomendacje dla brakujących umiejętności
        gaps_and_recommendations = {}
        for skill in missing_skills:
            # Znajdź podobne umiejętności, które użytkownik już posiada
            similar_skills = self._find_similar_skills(skill, user_skills)
            
            # Przygotuj rekomendację
            gaps_and_recommendations[skill] = {
                'priority': self._calculate_skill_priority(skill),
                'similar_existing_skills': similar_skills,
                'recommended_resources': self._get_skill_resources(skill)
            }
        
        return gaps_and_recommendations
    
    def _extract_skill_context(self, text, skill, window_size=100):
        """Ekstrahuje kontekst wokół umiejętności z tekstu"""
        # Znajdź indeks umiejętności w tekście
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        if skill_lower not in text_lower:
            return ""
        
        # Znajdź indeks pierwszego wystąpienia
        index = text_lower.find(skill_lower)
        
        # Oblicz granice okna kontekstu
        start = max(0, index - window_size)
        end = min(len(text), index + len(skill) + window_size)
        
        return text[start:end]
    
    def _find_similar_skills(self, skill, user_skills, threshold=0.7):
        """Znajduje podobne umiejętności do danej umiejętności"""
        if not user_skills:
            return []
            
        # Wektoryzuj wszystkie umiejętności
        all_skills = [skill] + list(user_skills)
        tfidf_matrix = self.vectorizer.fit_transform(all_skills)
        
        # Oblicz podobieństwo kosinusowe
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Zwróć podobne umiejętności powyżej progu
        similar_skills = []
        for i, sim_score in enumerate(cosine_sim[0]):
            if sim_score >= threshold:
                similar_skills.append((list(user_skills)[i], sim_score))
        
        return sorted(similar_skills, key=lambda x: x[1], reverse=True)
    
    def _calculate_skill_priority(self, skill):
        """Oblicza priorytet dla danej umiejętności"""
        # Sprawdź, czy umiejętność istnieje w bazie danych
        if skill in self.skills_db['skill_name'].values:
            relevance = self.skills_db.loc[self.skills_db['skill_name'] == skill, 'relevance_score'].iloc[0]
            return min(10, relevance)  # Priorytet w skali 1-10
        return 5  # Domyślny priorytet
    
    def _get_skill_resources(self, skill):
        """Zwraca zalecane materiały do nauki danej umiejętności"""
        # Przykładowe zasoby, w rzeczywistej implementacji należałoby to połączyć z bazą danych
        resources = {
            'Python': ['Kurs Python na Udemy', 'Dokumentacja Python', 'Książka: Python dla początkujących'],
            'Java': ['Kurs Java na Coursera', 'Oracle Java Tutorials', 'Książka: Java: The Complete Reference'],
            'Machine Learning': ['Kurs Machine Learning na Coursera by Andrew Ng', 'Dokumentacja scikit-learn', 
                               'Książka: Hands-On Machine Learning with Scikit-Learn and TensorFlow']
        }
        
        return resources.get(skill, ['Brak konkretnych rekomendacji dla tej umiejętności']) 
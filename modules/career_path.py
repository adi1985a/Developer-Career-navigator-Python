import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx
import matplotlib.pyplot as plt
import logging
from datetime import datetime, timedelta

class CareerPathGenerator:
    def __init__(self, skills_database_path=None, roles_database_path=None):
        """
        Inicjalizacja generatora ścieżek kariery
        
        Args:
            skills_database_path: Ścieżka do bazy danych umiejętności
            roles_database_path: Ścieżka do bazy danych ról zawodowych
        """
        self.logger = logging.getLogger(__name__)
        
        # Załaduj dane
        if skills_database_path:
            try:
                self.skills_db = pd.read_csv(skills_database_path)
            except Exception as e:
                self.logger.error(f"Błąd podczas ładowania bazy umiejętności: {e}")
                self.skills_db = self._create_sample_skills_db()
        else:
            self.skills_db = self._create_sample_skills_db()
            
        if roles_database_path:
            try:
                self.roles_db = pd.read_csv(roles_database_path)
            except Exception as e:
                self.logger.error(f"Błąd podczas ładowania bazy ról: {e}")
                self.roles_db = self._create_sample_roles_db()
        else:
            self.roles_db = self._create_sample_roles_db()
            
        # Graf ścieżek kariery
        self.career_graph = self._build_career_graph()
    
    def _create_sample_skills_db(self):
        """Tworzy przykładową bazę danych umiejętności"""
        skills = {
            'skill_id': list(range(1, 21)),
            'skill_name': [
                'Python', 'Java', 'JavaScript', 'SQL', 'Machine Learning',
                'Deep Learning', 'Data Analysis', 'Project Management', 'Cloud Computing',
                'Docker', 'Kubernetes', 'React', 'Angular', 'DevOps', 'NoSQL',
                'Big Data', 'Mobile Development', 'UI/UX Design', 'Scrum', 'Testing'
            ],
            'category': [
                'Programming', 'Programming', 'Programming', 'Database', 'AI',
                'AI', 'Data Science', 'Management', 'Cloud', 'DevOps',
                'DevOps', 'Frontend', 'Frontend', 'DevOps', 'Database',
                'Data Science', 'Mobile', 'Design', 'Management', 'QA'
            ],
            'relevance_score': [10, 9, 9, 8, 10, 9, 8, 7, 9, 8, 8, 9, 8, 9, 7, 8, 8, 7, 7, 8],
            'learning_difficulty': [3, 4, 3, 2, 5, 5, 3, 2, 4, 3, 4, 3, 4, 4, 3, 4, 4, 3, 2, 3]
        }
        return pd.DataFrame(skills)
    
    def _create_sample_roles_db(self):
        """Tworzy przykładową bazę danych ról zawodowych"""
        roles = {
            'role_id': list(range(1, 11)),
            'role_name': [
                'Junior Python Developer', 'Python Developer', 'Senior Python Developer',
                'Data Scientist', 'Machine Learning Engineer', 'Data Engineer',
                'Full Stack Developer', 'DevOps Engineer', 'Project Manager', 'CTO'
            ],
            'level': [
                'Junior', 'Mid', 'Senior', 'Mid', 'Senior', 'Mid',
                'Mid', 'Mid', 'Senior', 'Executive'
            ],
            'avg_salary': [
                8000, 15000, 25000, 18000, 22000, 17000,
                16000, 18000, 20000, 35000
            ],
            'required_skills': [
                '1,3,4', '1,3,4,7', '1,3,4,7,15', '1,4,5,7,16', '1,5,6,16', '1,4,15,16',
                '1,2,3,12,13', '1,9,10,11,14', '8,19', '5,8,9,14,19'
            ],
            'experience_years': [0, 2, 5, 3, 5, 3, 3, 4, 6, 10]
        }
        return pd.DataFrame(roles)
    
    def _build_career_graph(self):
        """
        Buduje graf ścieżek kariery na podstawie ról i ich powiązań
        
        Returns:
            DiGraph z rolami jako węzłami i możliwymi przejściami jako krawędziami
        """
        G = nx.DiGraph()
        
        # Dodaj wszystkie role jako węzły
        for _, role in self.roles_db.iterrows():
            G.add_node(role['role_id'], 
                      name=role['role_name'],
                      level=role['level'],
                      salary=role['avg_salary'],
                      required_skills=role['required_skills'],
                      experience=role['experience_years'])
        
        # Dodaj krawędzie między rolami
        for i, role1 in self.roles_db.iterrows():
            for j, role2 in self.roles_db.iterrows():
                if i == j:
                    continue
                    
                # Sprawdź, czy istnieje ścieżka kariery między tymi rolami
                if self._can_progress(role1, role2):
                    # Dodaj krawędź z wagą reprezentującą "trudność" przejścia
                    difficulty = self._calculate_transition_difficulty(role1, role2)
                    G.add_edge(role1['role_id'], role2['role_id'], weight=difficulty)
        
        return G
    
    def _can_progress(self, role1, role2):
        """
        Sprawdza, czy istnieje możliwe przejście między rolami
        
        Args:
            role1: Rola początkowa
            role2: Rola docelowa
            
        Returns:
            True jeśli istnieje sensowna ścieżka kariery między rolami
        """
        # Sprawdź, czy poziom doświadczenia rośnie
        if role1['experience_years'] >= role2['experience_years']:
            return False
        
        # Sprawdź, czy istnieje progresja poziomu
        level_progression = {
            'Junior': ['Mid', 'Senior'],
            'Mid': ['Senior', 'Executive'],
            'Senior': ['Executive']
        }
        
        if role2['level'] not in level_progression.get(role1['level'], []):
            return False
        
        # Sprawdź nakładanie się umiejętności
        skills1 = set(role1['required_skills'].split(','))
        skills2 = set(role2['required_skills'].split(','))
        
        # Musi istnieć częściowe nakładanie się umiejętności
        if len(skills1.intersection(skills2)) < min(2, len(skills1) // 2):
            return False
            
        return True
    
    def _calculate_transition_difficulty(self, role1, role2):
        """
        Oblicza trudność przejścia między rolami
        
        Args:
            role1: Rola początkowa
            role2: Rola docelowa
            
        Returns:
            Wartość trudności przejścia (1-10)
        """
        # Różnica w latach doświadczenia
        exp_diff = role2['experience_years'] - role1['experience_years']
        
        # Różnica w umiejętnościach
        skills1 = set(role1['required_skills'].split(','))
        skills2 = set(role2['required_skills'].split(','))
        
        new_skills_needed = skills2 - skills1
        new_skills_count = len(new_skills_needed)
        
        # Obliczenie trudności na podstawie różnicy doświadczenia i nowych umiejętności
        difficulty = min(10, exp_diff + new_skills_count * 1.5)
        
        return difficulty
    
    def generate_path(self, request):
        """Generuje ścieżkę kariery na podstawie podanych parametrów
        
        Args:
            request (dict): Parametry ścieżki kariery:
                - current_role (str): Obecna rola zawodowa
                - target_role (str): Docelowa rola zawodowa
                - time_frame (int): Ramy czasowe (w latach)
                - priority (str): Priorytet (wynagrodzenie/szybkość/równowaga)
                - user_skills (list, optional): Lista posiadanych umiejętności
                - experience_years (int, optional): Lata doświadczenia
                
        Returns:
            dict: Wygenerowana ścieżka kariery
        """
        try:
            self.logger.info(f"Generuję ścieżkę kariery: {request}")
            
            # Domyślne wartości
            current_role = request.get('current_role', '')
            target_role = request.get('target_role', '')
            time_frame = request.get('time_frame', 5)
            priority = request.get('priority', 'równowaga')
            user_skills = request.get('user_skills', [])
            experience_years = request.get('experience_years', 0)
            
            # Walidacja danych wejściowych
            if not current_role or not target_role:
                raise ValueError("Brak wymaganych parametrów: current_role lub target_role")
            
            # Konwertuj time_frame z lat na miesiące
            time_months = time_frame * 12
            
            # Symulacja generowania ścieżki kariery (do zastąpienia rzeczywistym algorytmem)
            path_steps = self.simulate_career_path(current_role, target_role, time_months, priority)
            
            # Identyfikacja umiejętności do zdobycia
            skills_to_learn = self.identify_skills_to_learn(path_steps, user_skills)
            
            # Utwórz pełny wynik
            result = {
                'steps': path_steps,
                'skills_to_learn': skills_to_learn,
                'total_time_months': sum(step['time_months'] for step in path_steps),
                'salary_increase': path_steps[-1]['salary'] - path_steps[0]['salary']
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania ścieżki kariery: {e}")
            raise
    
    def simulate_career_path(self, current_role, target_role, time_months, priority):
        """Symuluje ścieżkę kariery na podstawie parametrów"""
        import random
        
        # Testowe dane - w rzeczywistości powinny być generowane na podstawie algorytmu analizy ścieżki
        steps = []
        
        # Parametry początkowe
        current_salary = 8000 + random.randint(0, 2000)
        if current_role.lower().startswith("senior"):
            current_salary = 16000 + random.randint(0, 5000)
        elif current_role.lower().startswith("mid"):
            current_salary = 12000 + random.randint(0, 3000)
        
        # Początkowy krok
        steps.append({
            'role': current_role,
            'level': self.get_role_level(current_role),
            'salary': current_salary,
            'time_months': 0,
            'required_skills': self.get_skills_for_role(current_role)
        })
        
        # Liczba pośrednich kroków
        intermediate_steps = 2
        if priority == 'szybkość':
            intermediate_steps = 1
        elif priority == 'wynagrodzenie':
            intermediate_steps = 3
        
        # Generuj pośrednie kroki
        remaining_time = time_months
        for i in range(intermediate_steps):
            # Czas trwania kroku (miesiące)
            step_time = remaining_time // (intermediate_steps - i + 1)
            remaining_time -= step_time
            
            # Nowa rola i poziom
            if i == 0:
                new_role = f"Mid {target_role.split()[-1]} Developer"
                level = "Mid"
            else:
                new_role = f"Senior {target_role.split()[-1]} Developer"
                level = "Senior"
            
            # Nowe wynagrodzenie
            salary_increase = random.randint(15, 30) / 100  # 15-30% podwyżki
            new_salary = int(steps[-1]['salary'] * (1 + salary_increase))
            
            # Umiejętności
            required_skills = self.get_skills_for_role(new_role)
            
            # Dodaj krok
            steps.append({
                'role': new_role,
                'level': level,
                'salary': new_salary,
                'time_months': step_time,
                'required_skills': required_skills
            })
        
        # Krok końcowy (docelowa rola)
        final_salary_increase = random.randint(20, 40) / 100
        final_salary = int(steps[-1]['salary'] * (1 + final_salary_increase))
        
        steps.append({
            'role': target_role,
            'level': self.get_role_level(target_role),
            'salary': final_salary,
            'time_months': remaining_time,
            'required_skills': self.get_skills_for_role(target_role)
        })
        
        return steps
    
    def get_role_level(self, role_name):
        """Określa poziom roli na podstawie jej nazwy"""
        role_lower = role_name.lower()
        
        if "junior" in role_lower:
            return "Junior"
        elif "senior" in role_lower or "lead" in role_lower or "architect" in role_lower:
            return "Senior"
        elif "mid" in role_lower:
            return "Mid"
        elif "manager" in role_lower or "director" in role_lower:
            return "Manager"
        else:
            return "Specialist"
    
    def get_skills_for_role(self, role_name):
        """Zwraca listę umiejętności wymaganych dla danej roli"""
        # Przykładowe umiejętności dla różnych ról
        role_lower = role_name.lower()
        
        # Bazowy zestaw umiejętności
        common_skills = ["Communication", "Problem Solving", "Time Management"]
        
        if "java" in role_lower:
            skills = ["Java", "Spring Boot", "Hibernate", "SQL", "Git"]
        elif "python" in role_lower:
            skills = ["Python", "Django", "Flask", "SQL", "Git"]
        elif "frontend" in role_lower:
            skills = ["JavaScript", "HTML", "CSS", "React", "TypeScript"]
        elif "backend" in role_lower:
            skills = ["API Design", "Databases", "Microservices", "Python/Java", "Docker"]
        elif "devops" in role_lower:
            skills = ["Docker", "Kubernetes", "CI/CD", "AWS/Azure", "Linux"]
        elif "data" in role_lower:
            skills = ["SQL", "Python", "Data Analysis", "Visualization", "Statistics"]
        elif "ai" in role_lower or "ml" in role_lower:
            skills = ["Python", "TensorFlow/PyTorch", "Machine Learning", "Mathematics", "Data Processing"]
        elif "architect" in role_lower:
            skills = ["System Design", "Cloud Architecture", "Scalability", "Security", "Multiple languages"]
        else:
            skills = ["Programming", "Algorithms", "Databases", "Software Testing", "Git"]
        
        # Dodaj poziom zaawansowania zależnie od poziomu stanowiska
        level = self.get_role_level(role_name)
        
        if level == "Senior" or level == "Manager":
            skills.extend(["Team Leadership", "Project Management", "Mentoring", "System Design"])
        
        # Połącz ze wspólnymi umiejętnościami
        skills.extend(common_skills)
        
        # Usuń duplikaty
        return list(set(skills))
    
    def identify_skills_to_learn(self, path_steps, user_skills):
        """Identyfikuje umiejętności, które użytkownik musi zdobyć"""
        # Przekształć user_skills na małe litery dla łatwiejszego porównania
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        # Zbierz wszystkie wymagane umiejętności ze ścieżki
        all_required_skills = set()
        for step in path_steps:
            all_required_skills.update([skill.lower() for skill in step['required_skills']])
        
        # Znajdź umiejętności, których brakuje użytkownikowi
        missing_skills = [skill for skill in all_required_skills if skill not in user_skills_lower]
        
        # Generuj informacje o brakujących umiejętnościach
        skills_to_learn = []
        import random
        
        for skill in missing_skills:
            skills_to_learn.append({
                'name': skill.title(),
                'priority': random.choice(['Wysoki', 'Średni', 'Niski']),
                'difficulty': random.randint(1, 5),
                'learning_time_months': random.randint(1, 6)
            })
        
        # Sortuj według priorytetu
        priority_order = {'Wysoki': 0, 'Średni': 1, 'Niski': 2}
        skills_to_learn.sort(key=lambda x: priority_order[x['priority']])
        
        return skills_to_learn
    
    def generate_career_path(self, current_role_id, target_role_id=None, max_steps=3):
        """
        Generuje ścieżkę kariery od aktualnej do docelowej roli
        
        Args:
            current_role_id: ID aktualnej roli
            target_role_id: ID docelowej roli (jeśli None, znajdź najlepszą)
            max_steps: Maksymalna liczba kroków w ścieżce
            
        Returns:
            Lista ról tworzących ścieżkę kariery
        """
        if current_role_id not in self.career_graph:
            self.logger.error(f"Rola początkowa {current_role_id} nie istnieje w grafie")
            return []
            
        # Jeśli cel nie jest określony, znajdź najlepszą ścieżkę
        if target_role_id is None:
            target_role_id = self._find_best_target_role(current_role_id)
            
        if target_role_id not in self.career_graph:
            self.logger.error(f"Rola docelowa {target_role_id} nie istnieje w grafie")
            return []
            
        # Znajdź najkrótszą ścieżkę
        try:
            path = nx.shortest_path(self.career_graph, current_role_id, target_role_id, weight='weight')
            
            # Ogranicz do max_steps kroków
            if len(path) - 1 > max_steps:
                self.logger.warning(f"Znaleziona ścieżka ma {len(path)-1} kroków, ograniczenie do {max_steps}")
                # Znajdź najlepsze pośrednie kroki
                path = self._find_limited_path(current_role_id, target_role_id, max_steps)
                
            # Konwertuj IDs na pełne informacje o rolach
            career_path = []
            for role_id in path:
                role_data = self.roles_db[self.roles_db['role_id'] == role_id].iloc[0].to_dict()
                career_path.append(role_data)
                
            return career_path
            
        except nx.NetworkXNoPath:
            self.logger.error(f"Nie znaleziono ścieżki między {current_role_id} a {target_role_id}")
            return []
    
    def _find_best_target_role(self, current_role_id):
        """
        Znajduje najlepszą docelową rolę na podstawie aktualnej roli
        
        Args:
            current_role_id: ID aktualnej roli
            
        Returns:
            ID najlepszej docelowej roli
        """
        current_role = self.roles_db[self.roles_db['role_id'] == current_role_id].iloc[0]
        
        # Znajdź role o wyższym poziomie i wynagrodzeniu
        better_roles = self.roles_db[
            (self.roles_db['avg_salary'] > current_role['avg_salary'] * 1.2) & 
            (self.roles_db['experience_years'] > current_role['experience_years'])
        ]
        
        if better_roles.empty:
            # Jeśli nie ma lepszych ról, zwróć aktualną
            return current_role_id
            
        # Znajdź rolę z najwyższym wynagrodzeniem
        best_role = better_roles.loc[better_roles['avg_salary'].idxmax()]
        
        return best_role['role_id']
    
    def _find_limited_path(self, start_id, end_id, max_steps):
        """
        Znajduje ścieżkę z ograniczoną liczbą kroków
        
        Args:
            start_id: ID początkowej roli
            end_id: ID docelowej roli
            max_steps: Maksymalna liczba kroków
            
        Returns:
            Lista ID ról tworzących ścieżkę
        """
        # Jeśli max_steps = 1, zwróć bezpośrednią ścieżkę
        if max_steps == 1:
            return [start_id, end_id]
            
        # Znajdź wszystkie możliwe pośrednie role
        successors = list(self.career_graph.successors(start_id))
        predecessors = list(self.career_graph.predecessors(end_id))
        
        # Znajdź wspólne role
        intermediate_candidates = set(successors).intersection(set(predecessors))
        
        if not intermediate_candidates:
            # Jeśli nie ma wspólnych ról, wybierz najlepszą pośrednią rolę
            all_nodes = set(self.career_graph.nodes())
            paths_to_end = []
            
            for node in all_nodes:
                if node == start_id or node == end_id:
                    continue
                    
                try:
                    path1 = nx.shortest_path(self.career_graph, start_id, node, weight='weight')
                    path2 = nx.shortest_path(self.career_graph, node, end_id, weight='weight')
                    
                    if len(path1) + len(path2) - 2 <= max_steps:
                        # Oblicz "jakość" tej ścieżki
                        path_quality = self._calculate_path_quality(path1 + path2[1:])
                        paths_to_end.append((path1 + path2[1:], path_quality))
                except nx.NetworkXNoPath:
                    continue
            
            if not paths_to_end:
                # Jeśli nadal nie znaleziono ścieżki, zwróć początek i koniec
                return [start_id, end_id]
                
            # Wybierz ścieżkę o najwyższej jakości
            best_path = sorted(paths_to_end, key=lambda x: x[1], reverse=True)[0][0]
            
            # Ogranicz ścieżkę do max_steps+1 węzłów
            if len(best_path) > max_steps + 1:
                intermediate_steps = max_steps - 1
                important_nodes = [start_id] + best_path[1:-1:len(best_path)//intermediate_steps][:intermediate_steps] + [end_id]
                return important_nodes
            else:
                return best_path
        else:
            # Wybierz najlepszą pośrednią rolę
            best_intermediate = None
            best_quality = -1
            
            for inter_id in intermediate_candidates:
                path = [start_id, inter_id, end_id]
                quality = self._calculate_path_quality(path)
                
                if quality > best_quality:
                    best_quality = quality
                    best_intermediate = inter_id
            
            return [start_id, best_intermediate, end_id]
    
    def _calculate_path_quality(self, path):
        """
        Oblicza jakość ścieżki kariery
        
        Args:
            path: Lista ID ról tworzących ścieżkę
            
        Returns:
            Wartość jakości ścieżki
        """
        if len(path) <= 1:
            return 0
            
        # Sprawdź wzrost wynagrodzenia
        start_role = self.roles_db[self.roles_db['role_id'] == path[0]].iloc[0]
        end_role = self.roles_db[self.roles_db['role_id'] == path[-1]].iloc[0]
        
        salary_growth = end_role['avg_salary'] / start_role['avg_salary']
        
        # Sprawdź trudność ścieżki
        total_difficulty = 0
        for i in range(len(path) - 1):
            total_difficulty += self.career_graph[path[i]][path[i+1]]['weight']
        
        avg_difficulty = total_difficulty / (len(path) - 1)
        
        # Oblicz jakość jako kombinację wzrostu wynagrodzenia i trudności
        quality = salary_growth * 10 - avg_difficulty
        
        return quality
    
    def recommend_skills_for_path(self, current_skills, target_role_id):
        """
        Rekomenduje umiejętności do zdobycia dla osiągnięcia docelowej roli
        
        Args:
            current_skills: Lista obecnych umiejętności (ID)
            target_role_id: ID docelowej roli
            
        Returns:
            Słownik z rekomendowanymi umiejętnościami i priorytetami
        """
        if target_role_id not in self.roles_db['role_id'].values:
            self.logger.error(f"Rola docelowa {target_role_id} nie istnieje")
            return {}
            
        # Pobierz wymagane umiejętności dla docelowej roli
        target_role = self.roles_db[self.roles_db['role_id'] == target_role_id].iloc[0]
        required_skills = set(target_role['required_skills'].split(','))
        
        # Przekształć ID umiejętności na liczby całkowite
        required_skills = set(int(skill_id) for skill_id in required_skills)
        current_skills_set = set(int(skill_id) for skill_id in current_skills)
        
        # Znajdź brakujące umiejętności
        missing_skills = required_skills - current_skills_set
        
        # Przygotuj rekomendacje
        recommendations = {}
        for skill_id in missing_skills:
            skill_data = self.skills_db[self.skills_db['skill_id'] == skill_id].iloc[0]
            
            recommendations[skill_id] = {
                'skill_name': skill_data['skill_name'],
                'category': skill_data['category'],
                'priority': self._calculate_skill_priority(skill_id, target_role),
                'difficulty': skill_data['learning_difficulty'],
                'estimated_time': self._estimate_learning_time(skill_id)
            }
        
        return recommendations
    
    def _calculate_skill_priority(self, skill_id, target_role):
        """
        Oblicza priorytet zdobycia umiejętności dla danej roli
        
        Args:
            skill_id: ID umiejętności
            target_role: Informacje o docelowej roli
            
        Returns:
            Wartość priorytetu (1-10)
        """
        # Pobierz dane umiejętności
        skill_data = self.skills_db[self.skills_db['skill_id'] == skill_id].iloc[0]
        
        # Sprawdź, jak często ta umiejętność występuje w podobnych rolach
        similar_roles = self.roles_db[self.roles_db['level'] == target_role['level']]
        occurrence_count = 0
        
        for _, role in similar_roles.iterrows():
            role_skills = set(role['required_skills'].split(','))
            if str(skill_id) in role_skills:
                occurrence_count += 1
        
        # Oblicz częstość występowania
        frequency = occurrence_count / len(similar_roles) if len(similar_roles) > 0 else 0
        
        # Oblicz priorytet jako kombinację wartości umiejętności i częstości występowania
        priority = skill_data['relevance_score'] * 0.7 + frequency * 10 * 0.3
        
        return min(10, round(priority, 1))
    
    def _estimate_learning_time(self, skill_id):
        """
        Szacuje czas nauki umiejętności w miesiącach
        
        Args:
            skill_id: ID umiejętności
            
        Returns:
            Szacowany czas nauki w miesiącach
        """
        # Pobierz dane umiejętności
        skill_data = self.skills_db[self.skills_db['skill_id'] == skill_id].iloc[0]
        
        # Prosta heurystyka oparta na trudności nauki
        base_time = {
            1: 1,  # 1 miesiąc dla najłatwiejszych umiejętności
            2: 2,
            3: 3, 
            4: 5,
            5: 8   # 8 miesięcy dla najtrudniejszych umiejętności
        }
        
        return base_time.get(skill_data['learning_difficulty'], 3)
    
    def visualize_career_path(self, path, output_file=None):
        """
        Wizualizuje ścieżkę kariery
        
        Args:
            path: Lista ról tworzących ścieżkę
            output_file: Ścieżka do pliku wyjściowego
            
        Returns:
            Obiekt figure matplotlib
        """
        if not path:
            self.logger.error("Nie można zwizualizować pustej ścieżki")
            return None
            
        # Utwórz podgraf ze ścieżki
        path_ids = [role['role_id'] for role in path]
        path_graph = self.career_graph.subgraph(path_ids)
        
        # Przygotuj etykiety węzłów
        labels = {}
        for role_id in path_ids:
            role = self.roles_db[self.roles_db['role_id'] == role_id].iloc[0]
            labels[role_id] = f"{role['role_name']}\n{role['avg_salary']} PLN"
        
        # Ustaw pozycje węzłów
        pos = nx.spring_layout(path_graph)
        
        # Rysuj graf
        plt.figure(figsize=(12, 8))
        
        # Rysuj węzły
        nx.draw_networkx_nodes(path_graph, pos, node_size=3000, node_color='lightblue', alpha=0.8)
        
        # Rysuj krawędzie z wagami
        edge_labels = {(u, v): f"{d['weight']:.1f}" for u, v, d in path_graph.edges(data=True)}
        nx.draw_networkx_edges(path_graph, pos, width=2, edge_color='gray', arrows=True, arrowsize=20)
        nx.draw_networkx_edge_labels(path_graph, pos, edge_labels=edge_labels, font_size=10)
        
        # Rysuj etykiety węzłów
        nx.draw_networkx_labels(path_graph, pos, labels=labels, font_size=10, font_weight='bold')
        
        # Dodaj tytuł
        plt.title('Twoja ścieżka kariery', fontsize=16)
        plt.axis('off')
        
        # Zapisz lub zwróć figure
        if output_file:
            plt.savefig(output_file, bbox_inches='tight')
            
        return plt.gcf() 
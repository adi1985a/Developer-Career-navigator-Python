import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import logging
import random

class CareerSimulator:
    def __init__(self, skills_analyzer=None, market_trends=None, career_path_generator=None):
        """
        Inicjalizacja symulatora kariery
        
        Args:
            skills_analyzer: Obiekt analizatora umiejętności
            market_trends: Obiekt analizy trendów rynkowych
            career_path_generator: Obiekt generatora ścieżek kariery
        """
        self.skills_analyzer = skills_analyzer
        self.market_trends = market_trends
        self.path_generator = career_path_generator
        self.logger = logging.getLogger(__name__)
        
        # Współczynniki wpływające na progres kariery
        self.progression_factors = {
            'skill_match': 0.4,      # Wpływ dopasowania umiejętności
            'experience': 0.3,        # Wpływ doświadczenia
            'market_demand': 0.2,     # Wpływ popytu rynkowego
            'education': 0.1          # Wpływ edukacji
        }
        
        # Poziomy edukacji i ich wartości
        self.education_levels = {
            'Szkoła średnia': 1,
            'Licencjat': 2,
            'Inżynier': 2.5,
            'Magister': 3,
            'Doktor': 4
        }
    
    def simulate_career_progression(self, user_profile, target_role, years=5, simulate_market_changes=True):
        """
        Symuluje progresję kariery użytkownika do docelowej roli
        
        Args:
            user_profile: Profil użytkownika (umiejętności, doświadczenie, edukacja)
            target_role: Docelowa rola zawodowa
            years: Liczba lat do zasymulowania
            simulate_market_changes: Czy symulować zmiany rynkowe
            
        Returns:
            DataFrame z symulacją kariery w czasie
        """
        # Przygotuj strukturę wyniku
        simulation_data = []
        current_date = datetime.now()
        
        # Utwórz kopię profilu użytkownika, aby go modyfikować
        profile = user_profile.copy()
        
        # Początkowe wartości
        current_role = profile.get('current_role', {})
        current_skills = profile.get('skills', [])
        current_salary = current_role.get('salary', 0)
        
        # Dodaj pierwszy punkt symulacji
        simulation_data.append({
            'date': current_date,
            'role': current_role.get('name', 'Brak roli'),
            'salary': current_salary,
            'skills_count': len(current_skills),
            'promotion_chance': 0,
            'skill_match': self._calculate_skill_match(current_skills, target_role),
            'market_demand': 1.0  # Początkowa wartość
        })
        
        # Główna pętla symulacji (co kwartał)
        quarters = years * 4
        for i in range(1, quarters + 1):
            # Aktualizuj datę (co 3 miesiące)
            current_date = current_date + timedelta(days=90)
            
            # Symuluj zdobywanie nowych umiejętności
            new_skills = self._simulate_skill_acquisition(profile, target_role, i)
            profile['skills'].extend(new_skills)
            
            # Aktualizuj doświadczenie
            profile['experience'] = profile.get('experience', 0) + 0.25  # dodaj ćwierć roku
            
            # Aktualizuj popyt rynkowy jeśli potrzeba
            market_demand = 1.0
            if simulate_market_changes and self.market_trends:
                market_demand = self._simulate_market_demand(profile, i)
            
            # Oblicz szansę na awans
            promotion_chance = self._calculate_promotion_chance(profile, target_role, market_demand)
            
            # Sprawdź, czy nastąpił awans
            if self._check_promotion(promotion_chance, i):
                # Aktualizuj rolę i wynagrodzenie
                new_role = self._get_next_role(profile, target_role)
                profile['current_role'] = new_role
                current_salary = new_role.get('salary', current_salary)
                
                # Dodaj dodatkową notatkę o awansie w symulacji
                simulation_data.append({
                    'date': current_date,
                    'role': new_role.get('name', 'Nowa rola'),
                    'salary': current_salary,
                    'skills_count': len(profile['skills']),
                    'promotion_chance': promotion_chance,
                    'skill_match': self._calculate_skill_match(profile['skills'], target_role),
                    'market_demand': market_demand,
                    'event': 'Awans zawodowy'
                })
            else:
                # Aktualizuj wynagrodzenie (niewielki wzrost co roku)
                if i % 4 == 0:  # co roku
                    current_salary *= 1.03  # 3% wzrost roczny
            
            # Dodaj punkt symulacji
            simulation_data.append({
                'date': current_date,
                'role': profile['current_role'].get('name', 'Brak roli'),
                'salary': current_salary,
                'skills_count': len(profile['skills']),
                'promotion_chance': promotion_chance,
                'skill_match': self._calculate_skill_match(profile['skills'], target_role),
                'market_demand': market_demand
            })
        
        # Konwersja do DataFrame
        return pd.DataFrame(simulation_data)
    
    def _simulate_skill_acquisition(self, profile, target_role, quarter):
        """
        Symuluje zdobywanie nowych umiejętności
        
        Args:
            profile: Profil użytkownika
            target_role: Rola docelowa
            quarter: Numer kwartału symulacji
            
        Returns:
            Lista nowo zdobytych umiejętności
        """
        # Pobierz bieżące umiejętności
        current_skills = profile.get('skills', [])
        current_skill_names = [s.get('name', '') for s in current_skills]
        
        # Pobierz umiejętności wymagane dla docelowej roli
        target_skills = target_role.get('required_skills', [])
        target_skill_names = [s.get('name', '') for s in target_skills]
        
        # Znajdź brakujące umiejętności
        missing_skills = [s for s in target_skills if s.get('name', '') not in current_skill_names]
        
        # Ustal liczbę umiejętności do zdobycia w tym kwartale
        skills_per_quarter = 0.5  # Średnio pół umiejętności na kwartał
        
        # Dodaj losowość
        skills_count = np.random.poisson(skills_per_quarter)
        
        # Ogranicz do liczby brakujących umiejętności
        skills_count = min(skills_count, len(missing_skills))
        
        # Wybierz umiejętności do zdobycia
        if skills_count > 0:
            # Sortuj po priorytecie, jeśli jest dostępny
            missing_skills.sort(key=lambda s: s.get('priority', 0), reverse=True)
            acquired_skills = missing_skills[:skills_count]
            
            # Dodaj informację o poziomie umiejętności (początkowy)
            for skill in acquired_skills:
                skill['level'] = 1
            
            return acquired_skills
        
        return []
    
    def _simulate_market_demand(self, profile, quarter):
        """
        Symuluje zmiany popytu rynkowego
        
        Args:
            profile: Profil użytkownika
            quarter: Numer kwartału symulacji
            
        Returns:
            Współczynnik popytu rynkowego (0.5-1.5)
        """
        # Podstawowy trend rynkowy (sinusoidalny z szumem)
        base_trend = 1.0 + 0.1 * np.sin(quarter / 8.0)
        
        # Dodaj losowe wahania (szum)
        noise = 0.05 * np.random.randn()
        
        # Uwzględnij branżę z profilu użytkownika
        industry_factor = 1.0
        industry = profile.get('current_role', {}).get('industry', '')
        
        # Różne branże mogą mieć różne trendy
        industry_trends = {
            'IT': 1.2,
            'Finance': 1.1,
            'Healthcare': 1.15,
            'Manufacturing': 0.9,
            'Retail': 0.85
        }
        
        industry_factor = industry_trends.get(industry, 1.0)
        
        # Oblicz końcowy współczynnik popytu
        demand_factor = base_trend + noise
        demand_factor *= industry_factor
        
        # Ogranicz wartość
        return max(0.5, min(1.5, demand_factor))
    
    def _calculate_promotion_chance(self, profile, target_role, market_demand):
        """
        Oblicza szansę na awans
        
        Args:
            profile: Profil użytkownika
            target_role: Rola docelowa
            market_demand: Współczynnik popytu rynkowego
            
        Returns:
            Szansa na awans (0-1)
        """
        # Pobierz bieżące dane
        current_skills = profile.get('skills', [])
        experience = profile.get('experience', 0)
        education = profile.get('education', 'Szkoła średnia')
        
        # Oblicz dopasowanie umiejętności (0-1)
        skill_match = self._calculate_skill_match(current_skills, target_role)
        
        # Oblicz wpływ doświadczenia (0-1)
        required_exp = target_role.get('experience_years', 1)
        exp_factor = min(1.0, experience / required_exp)
        
        # Oblicz wpływ edukacji (0-1)
        education_value = self.education_levels.get(education, 1)
        edu_factor = min(1.0, education_value / 3.0)  # Normalizacja
        
        # Oblicz szansę na awans jako ważoną sumę czynników
        promotion_chance = (
            self.progression_factors['skill_match'] * skill_match +
            self.progression_factors['experience'] * exp_factor +
            self.progression_factors['market_demand'] * market_demand +
            self.progression_factors['education'] * edu_factor
        )
        
        # Ogranicz wynik
        return max(0.0, min(1.0, promotion_chance))
    
    def _calculate_skill_match(self, current_skills, target_role):
        """
        Oblicza stopień dopasowania umiejętności do docelowej roli
        
        Args:
            current_skills: Lista aktualnych umiejętności
            target_role: Rola docelowa
            
        Returns:
            Stopień dopasowania (0-1)
        """
        # Pobierz nazwy umiejętności
        current_skill_names = [s.get('name', '') for s in current_skills]
        
        # Pobierz wymagane umiejętności
        required_skills = target_role.get('required_skills', [])
        required_skill_names = [s.get('name', '') for s in required_skills]
        
        if not required_skill_names:
            return 0.0
        
        # Oblicz liczbę pasujących umiejętności
        matching_skills_count = sum(1 for skill in current_skill_names if skill in required_skill_names)
        
        # Oblicz stopień dopasowania
        return matching_skills_count / len(required_skill_names)
    
    def _check_promotion(self, promotion_chance, quarter):
        """
        Sprawdza, czy nastąpił awans
        
        Args:
            promotion_chance: Szansa na awans (0-1)
            quarter: Numer kwartału symulacji
            
        Returns:
            True jeśli awansował, False w przeciwnym przypadku
        """
        # Awanse są rzadsze w początkowych kwartałach
        time_factor = min(1.0, quarter / 8.0)  # Pełna szansa po 2 latach
        
        # Zastosuj czynnik czasu do szansy awansu
        effective_chance = promotion_chance * time_factor
        
        # Losuj, czy nastąpił awans
        return random.random() < effective_chance
    
    def _get_next_role(self, profile, target_role):
        """
        Wybiera następną rolę w karierze
        
        Args:
            profile: Profil użytkownika
            target_role: Docelowa rola
            
        Returns:
            Słownik z danymi następnej roli
        """
        current_role = profile.get('current_role', {})
        
        # Jeśli użytkownik nie ma aktualnej roli, przypisz podstawową
        if not current_role:
            return {
                'name': 'Junior Specialist',
                'level': 'Junior',
                'salary': 6000,
                'industry': target_role.get('industry', 'IT')
            }
        
        # Jeśli aktualną rolą jest docelowa, pozostań przy niej
        if current_role.get('name', '') == target_role.get('name', ''):
            return current_role
        
        # Jeśli mamy generator ścieżek, użyj go do znalezienia następnej roli
        if self.path_generator:
            try:
                # Znajdź ścieżkę od aktualnej do docelowej roli
                current_role_id = self._find_role_id(current_role.get('name', ''))
                target_role_id = self._find_role_id(target_role.get('name', ''))
                
                if current_role_id and target_role_id:
                    career_path = self.path_generator.generate_career_path(current_role_id, target_role_id)
                    
                    if len(career_path) > 1:
                        # Druga rola w ścieżce (indeks 1) jest następną rolą
                        next_role_data = career_path[1]
                        return {
                            'name': next_role_data.get('role_name', 'Następna rola'),
                            'level': next_role_data.get('level', 'Mid'),
                            'salary': next_role_data.get('avg_salary', current_role.get('salary', 0) * 1.2),
                            'industry': target_role.get('industry', 'IT')
                        }
            except Exception as e:
                self.logger.warning(f"Błąd podczas generowania ścieżki kariery: {e}")
        
        # Jeśli nie udało się użyć generatora ścieżek, wygeneruj następną rolę heurystycznie
        current_level = current_role.get('level', 'Junior')
        current_salary = current_role.get('salary', 6000)
        
        # Progresja poziomów
        level_progression = {
            'Junior': 'Mid',
            'Mid': 'Senior',
            'Senior': 'Lead',
            'Lead': 'Executive'
        }
        
        next_level = level_progression.get(current_level, current_level)
        
        # Oblicz nowe wynagrodzenie (wzrost 20-30%)
        salary_increase = 1.2 + 0.1 * random.random()
        new_salary = current_salary * salary_increase
        
        # Generuj nazwę następnej roli
        current_name = current_role.get('name', '')
        if 'Junior' in current_name:
            next_name = current_name.replace('Junior', 'Mid')
        elif 'Mid' in current_name:
            next_name = current_name.replace('Mid', 'Senior')
        elif 'Senior' in current_name:
            next_name = current_name.replace('Senior', 'Lead')
        else:
            next_name = 'Senior ' + current_name
        
        return {
            'name': next_name,
            'level': next_level,
            'salary': new_salary,
            'industry': current_role.get('industry', 'IT')
        }
    
    def _find_role_id(self, role_name):
        """
        Znajduje ID roli na podstawie jej nazwy
        
        Args:
            role_name: Nazwa roli
            
        Returns:
            ID roli lub None
        """
        if not self.path_generator or not hasattr(self.path_generator, 'roles_db'):
            return None
            
        matching_roles = self.path_generator.roles_db[self.path_generator.roles_db['role_name'] == role_name]
        
        if not matching_roles.empty:
            return matching_roles.iloc[0]['role_id']
        
        return None
    
    def visualize_career_simulation(self, simulation_data, output_file=None):
        """
        Wizualizuje symulację kariery
        
        Args:
            simulation_data: DataFrame z danymi symulacji
            output_file: Ścieżka do pliku wyjściowego
            
        Returns:
            Obiekt figure matplotlib
        """
        if simulation_data.empty:
            self.logger.error("Brak danych do wizualizacji")
            return None
        
        # Utwórz figurę z trzema podwykresami
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
        
        # Przygotuj oś X (daty)
        x = simulation_data['date']
        
        # Wykres 1: Wynagrodzenie
        ax1.plot(x, simulation_data['salary'], 'b-', linewidth=2)
        ax1.set_title('Prognoza wynagrodzenia', fontsize=14)
        ax1.set_ylabel('Wynagrodzenie (PLN)', fontsize=12)
        ax1.grid(True)
        
        # Zaznacz punkty awansów
        promotion_points = simulation_data[simulation_data.get('event', '') == 'Awans zawodowy']
        if not promotion_points.empty:
            ax1.scatter(promotion_points['date'], promotion_points['salary'], color='red', s=100, marker='^')
            
            # Dodaj etykiety awansów
            for _, point in promotion_points.iterrows():
                ax1.annotate(
                    point['role'],
                    (point['date'], point['salary']),
                    xytext=(10, 20),
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='->', color='red')
                )
        
        # Wykres 2: Liczba umiejętności
        ax2.plot(x, simulation_data['skills_count'], 'g-', linewidth=2)
        ax2.set_title('Rozwój umiejętności', fontsize=14)
        ax2.set_ylabel('Liczba umiejętności', fontsize=12)
        ax2.grid(True)
        
        # Wykres 3: Szansa na awans i dopasowanie umiejętności
        ax3.plot(x, simulation_data['promotion_chance'], 'r-', linewidth=2, label='Szansa na awans')
        ax3.plot(x, simulation_data['skill_match'], 'b--', linewidth=2, label='Dopasowanie umiejętności')
        ax3.plot(x, simulation_data['market_demand'], 'g-.', linewidth=2, label='Popyt rynkowy')
        ax3.set_title('Wskaźniki kariery', fontsize=14)
        ax3.set_ylabel('Wartość wskaźnika', fontsize=12)
        ax3.set_xlabel('Data', fontsize=12)
        ax3.legend()
        ax3.grid(True)
        
        # Formatuj oś X
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Zapisz lub zwróć figure
        if output_file:
            plt.savefig(output_file, bbox_inches='tight')
            
        return fig
    
    def calculate_roi(self, simulation_data, investment_costs=None):
        """
        Oblicza zwrot z inwestycji w rozwój kariery
        
        Args:
            simulation_data: DataFrame z symulacją kariery
            investment_costs: Słownik z kosztami inwestycji
            
        Returns:
            Słownik ze wskaźnikami ROI
        """
        if simulation_data.empty:
            return {'roi': 0, 'payback_period': float('inf'), 'net_gain': 0}
            
        # Jeśli nie podano kosztów, przyjmij domyślne wartości
        if investment_costs is None:
            investment_costs = {
                'education': 20000,    # Koszt edukacji
                'certifications': 5000,  # Koszt certyfikatów
                'time_value': 10000     # Wartość poświęconego czasu
            }
            
        # Oblicz całkowity koszt inwestycji
        total_cost = sum(investment_costs.values())
        
        # Oblicz łączny wzrost wynagrodzenia
        initial_salary = simulation_data.iloc[0]['salary']
        final_salary = simulation_data.iloc[-1]['salary']
        total_salary_gain = final_salary - initial_salary
        
        # Oblicz skumulowany wzrost wynagrodzenia (uwzględniając wszystkie wypłaty)
        cumulative_gain = 0
        
        # Zakładamy, że wynagrodzenie jest wypłacane co miesiąc
        for i in range(1, len(simulation_data)):
            prev_salary = simulation_data.iloc[i-1]['salary']
            curr_salary = simulation_data.iloc[i]['salary']
            
            # Oblicz liczbę miesięcy między punktami symulacji
            prev_date = simulation_data.iloc[i-1]['date']
            curr_date = simulation_data.iloc[i]['date']
            months_diff = max(1, (curr_date - prev_date).days / 30)
            
            # Dodaj przyrost wynagrodzenia za ten okres
            period_gain = (curr_salary - initial_salary) * months_diff
            cumulative_gain += period_gain
        
        # Oblicz ROI
        roi = (cumulative_gain - total_cost) / total_cost if total_cost > 0 else float('inf')
        
        # Oblicz okres zwrotu (w latach)
        monthly_gain = (final_salary - initial_salary)
        payback_period = total_cost / monthly_gain / 12 if monthly_gain > 0 else float('inf')
        
        # Przygotuj wynik
        result = {
            'total_investment': total_cost,
            'monthly_salary_increase': final_salary - initial_salary,
            'cumulative_gain': cumulative_gain,
            'roi': roi,
            'roi_percent': roi * 100,
            'payback_period': payback_period,
            'payback_period_months': payback_period * 12,
            'net_gain': cumulative_gain - total_cost
        }
        
        return result 
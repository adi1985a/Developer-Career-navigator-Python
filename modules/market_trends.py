import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from datetime import datetime, timedelta

class MarketTrends:
    def __init__(self, data_path=None):
        """
        Inicjalizacja mechanizmu analizy trendów rynkowych
        
        Args:
            data_path: Ścieżka do danych historycznych
        """
        self.data = None
        if data_path:
            try:
                self.data = pd.read_csv(data_path)
            except Exception as e:
                logging.error(f"Nie można załadować danych: {e}")
        
        self.trend_models = {}
        self.logger = logging.getLogger(__name__)
    
    def scrape_job_listings(self, sources=None, keywords=None, limit=100):
        """
        Zbiera oferty pracy z różnych portali
        
        Args:
            sources: Lista źródeł do zbadania
            keywords: Słowa kluczowe do wyszukiwania
            limit: Maksymalna liczba ofert do zebrania
            
        Returns:
            DataFrame z zebranymi ofertami pracy
        """
        if sources is None:
            sources = ["pracuj.pl", "nofluffjobs.com"]
        
        if keywords is None:
            keywords = ["python", "java", "javascript", "data science", "machine learning"]
        
        all_listings = []
        
        for source in sources:
            for keyword in keywords:
                try:
                    if source == "pracuj.pl":
                        listings = self._scrape_pracuj_pl(keyword, limit // len(keywords) // len(sources))
                    elif source == "nofluffjobs.com":
                        listings = self._scrape_nofluffjobs(keyword, limit // len(keywords) // len(sources))
                    else:
                        self.logger.warning(f"Nieznane źródło: {source}")
                        continue
                    
                    all_listings.extend(listings)
                except Exception as e:
                    self.logger.error(f"Błąd podczas zbierania danych z {source} dla {keyword}: {e}")
        
        # Konwersja do DataFrame
        if all_listings:
            return pd.DataFrame(all_listings)
        else:
            return pd.DataFrame(columns=['title', 'company', 'location', 'salary', 'skills', 'date_posted', 'source'])
    
    def _scrape_pracuj_pl(self, keyword, limit=20):
        """
        Zbiera oferty pracy z pracuj.pl (implementacja przykładowa)
        
        W rzeczywistej implementacji należy uwzględnić aktualne struktury stron
        i polityki robotów.txt. Ten kod jest pokazowy i powinien być dostosowany 
        do aktualnych wymagań.
        """
        self.logger.info(f"Scraping pracuj.pl for: {keyword}")
        listings = []
        
        try:
            # Ten URL jest przykładowy - w rzeczywistości trzeba sprawdzić aktualny format
            url = f"https://www.pracuj.pl/praca/{keyword.replace(' ', '%20')};kw"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Przykładowe selektory - wymagają aktualizacji
            job_items = soup.select('.results__list-container-item')[:limit]
            
            for item in job_items:
                try:
                    title = item.select_one('.offer-details__title-link').text.strip()
                    company = item.select_one('.offer-company__name').text.strip()
                    location = item.select_one('.offer-labels__item--location').text.strip()
                    
                    # Opcjonalne pola
                    salary_elem = item.select_one('.offer-labels__item--salary')
                    salary = salary_elem.text.strip() if salary_elem else "Nie podano"
                    
                    # Umiejętności mogą być ukryte w szczegółach oferty
                    skills = ["Brak danych"]  # W rzeczywistości wymagałoby to dodatkowego pobierania stron szczegółowych
                    
                    listings.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'skills': skills,
                        'date_posted': datetime.now().strftime("%Y-%m-%d"),
                        'source': "pracuj.pl"
                    })
                except Exception as e:
                    self.logger.warning(f"Błąd podczas przetwarzania oferty: {e}")
            
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania danych z pracuj.pl: {e}")
        
        return listings
    
    def _scrape_nofluffjobs(self, keyword, limit=20):
        """
        Zbiera oferty pracy z nofluffjobs.com (implementacja przykładowa)
        """
        self.logger.info(f"Scraping nofluffjobs.com for: {keyword}")
        listings = []
        
        try:
            # Ten URL jest przykładowy - w rzeczywistości trzeba sprawdzić aktualny format
            url = f"https://nofluffjobs.com/pl/praca/{keyword.replace(' ', '+')}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Przykładowe selektory - wymagają aktualizacji
            job_items = soup.select('.posting-list-item')[:limit]
            
            for item in job_items:
                try:
                    title = item.select_one('.posting-title__position').text.strip()
                    company = item.select_one('.posting-title__company').text.strip()
                    location = item.select_one('.posting-info__location').text.strip()
                    
                    # Opcjonalne pola
                    salary_elem = item.select_one('.salary-range')
                    salary = salary_elem.text.strip() if salary_elem else "Nie podano"
                    
                    # Pobranie umiejętności
                    skills_elems = item.select('.posting-info__tags .btn-main')
                    skills = [skill.text.strip() for skill in skills_elems] if skills_elems else ["Brak danych"]
                    
                    listings.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'skills': skills,
                        'date_posted': datetime.now().strftime("%Y-%m-%d"),
                        'source': "nofluffjobs.com"
                    })
                except Exception as e:
                    self.logger.warning(f"Błąd podczas przetwarzania oferty: {e}")
            
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania danych z nofluffjobs.com: {e}")
        
        return listings
    
    def analyze_skills_demand(self, job_listings=None):
        """
        Analizuje popyt na umiejętności na podstawie ofert pracy
        
        Args:
            job_listings: DataFrame z ofertami pracy
            
        Returns:
            DataFrame z analizą popytu na umiejętności
        """
        if job_listings is None and self.data is not None:
            job_listings = self.data
        elif job_listings is None:
            self.logger.error("Brak danych do analizy popytu na umiejętności")
            return pd.DataFrame()
        
        # Liczenie wystąpień umiejętności
        all_skills = []
        
        # Sprawdź, czy skills to lista
        for skills in job_listings['skills']:
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                # Próbuj parsować jako JSON jeśli to string
                try:
                    skills_list = json.loads(skills.replace("'", "\""))
                    all_skills.extend(skills_list)
                except:
                    # Jeśli nie jest to JSON, potraktuj jako pojedynczą umiejętność
                    all_skills.append(skills)
        
        # Liczenie częstotliwości
        skills_count = pd.Series(all_skills).value_counts().reset_index()
        skills_count.columns = ['skill', 'count']
        
        # Dodawanie dodatkowych metryk
        skills_count['percentage'] = skills_count['count'] / len(job_listings) * 100
        
        # Dodawanie analizy wynagrodzeń
        skills_salary = self._analyze_skills_salary(job_listings)
        if not skills_salary.empty:
            skills_count = pd.merge(skills_count, skills_salary, on='skill', how='left')
        
        return skills_count.sort_values('count', ascending=False)
    
    def _analyze_skills_salary(self, job_listings):
        """
        Analizuje wynagrodzenia powiązane z umiejętnościami
        
        Args:
            job_listings: DataFrame z ofertami pracy
            
        Returns:
            DataFrame z analizą wynagrodzeń dla umiejętności
        """
        # Przygotowanie danych
        salary_data = []
        
        for _, row in job_listings.iterrows():
            skills = row['skills']
            salary = row['salary']
            
            # Przeskocz oferty bez podanego wynagrodzenia
            if salary == "Nie podano" or not isinstance(skills, list):
                continue
            
            # Ekstrakcja wartości liczbowej z wynagrodzenia
            salary_value = self._extract_salary(salary)
            if salary_value is None:
                continue
            
            # Dodaj każdą umiejętność z odpowiadającą pensją
            for skill in skills:
                salary_data.append({
                    'skill': skill,
                    'salary': salary_value
                })
        
        if not salary_data:
            return pd.DataFrame()
        
        # Grupowanie i obliczanie statystyk
        df = pd.DataFrame(salary_data)
        salary_stats = df.groupby('skill')['salary'].agg(['mean', 'median', 'min', 'max', 'count']).reset_index()
        
        return salary_stats
    
    def _extract_salary(self, salary_text):
        """
        Ekstrahuje wartość liczbową z tekstu wynagrodzenia
        
        Args:
            salary_text: Tekst z wynagrodzeniem
            
        Returns:
            Średnia wartość wynagrodzenia jako liczba lub None
        """
        try:
            # Wyszukaj wzorce liczb z tekstu
            numbers = re.findall(r'\d+\s*\d*', salary_text)
            if not numbers:
                return None
            
            # Konwersja tekstów na liczby
            values = []
            for num in numbers:
                num = num.replace(" ", "")
                try:
                    values.append(float(num))
                except ValueError:
                    pass
            
            if len(values) == 1:
                return values[0]
            elif len(values) >= 2:
                # Jeśli są podane widełki, zwróć średnią
                return sum(values) / len(values)
            else:
                return None
        except:
            return None
    
    def predict_future_trends(self, skill, time_periods=4):
        """
        Przewiduje przyszłe trendy dla danej umiejętności
        
        Args:
            skill: Nazwa umiejętności do analizy
            time_periods: Liczba okresów do przewidzenia w przyszłość
            
        Returns:
            DataFrame z prognozą
        """
        if self.data is None:
            self.logger.error("Brak danych historycznych do przewidywania trendów")
            return pd.DataFrame()
        
        # Przygotuj dane historyczne dla umiejętności
        skill_data = self._prepare_skill_time_series(skill)
        
        if skill_data.empty or len(skill_data) < 3:  # Potrzebujemy min. 3 punktów do sensownej predykcji
            self.logger.warning(f"Niewystarczające dane historyczne dla umiejętności: {skill}")
            return pd.DataFrame()
        
        # Przygotuj model
        if skill not in self.trend_models:
            X = np.array(range(len(skill_data))).reshape(-1, 1)
            y = skill_data['value'].values
            model = LinearRegression()
            model.fit(X, y)
            self.trend_models[skill] = model
        else:
            model = self.trend_models[skill]
        
        # Utwórz punkty w przyszłości
        future_periods = np.array(range(len(skill_data), len(skill_data) + time_periods)).reshape(-1, 1)
        predictions = model.predict(future_periods)
        
        # Utwórz DataFrame z prognozą
        last_date = skill_data['date'].iloc[-1]
        future_dates = [pd.to_datetime(last_date) + pd.DateOffset(months=i+1) for i in range(time_periods)]
        
        forecast = pd.DataFrame({
            'date': future_dates,
            'value': predictions,
            'type': 'forecast'
        })
        
        # Połącz dane historyczne z prognozą
        skill_data['type'] = 'historical'
        result = pd.concat([skill_data, forecast], ignore_index=True)
        
        return result
    
    def _prepare_skill_time_series(self, skill):
        """
        Przygotowuje szereg czasowy dla umiejętności
        
        Args:
            skill: Nazwa umiejętności
            
        Returns:
            DataFrame z danymi historycznymi
        """
        # Ta funkcja powinna przygotować dane w postaci:
        # date, value
        # gdzie value to może być liczba ofert pracy, średnia pensja, itp.
        
        # W rzeczywistej implementacji należałoby wykorzystać dane historyczne
        # W tym przykładzie tworzymy sztuczne dane
        
        # Przykładowe dane
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        
        if skill == "Python":
            values = [100, 110, 115, 120, 140, 160, 165, 180, 200, 220, 240, 250]
        elif skill == "Java":
            values = [150, 145, 140, 135, 130, 125, 120, 115, 110, 105, 100, 95]
        elif skill == "Machine Learning":
            values = [50, 60, 75, 85, 100, 120, 150, 180, 210, 240, 260, 270]
        else:
            # Losowe wartości dla innych umiejętności
            values = np.random.randint(50, 200, size=12).tolist()
        
        return pd.DataFrame({
            'date': dates,
            'value': values
        })

    def get_top_emerging_skills(self, n=10):
        """
        Zwraca najszybciej rozwijające się umiejętności
        
        Args:
            n: Liczba umiejętności do zwrócenia
            
        Returns:
            DataFrame z najszybciej rozwijającymi się umiejętnościami
        """
        if self.data is None:
            self.logger.error("Brak danych historycznych do analizy trendów")
            return pd.DataFrame()
        
        # W rzeczywistej implementacji należałoby przeanalizować historyczne dane
        # i obliczyć trendy dla wszystkich umiejętności
        
        # Przykładowe dane
        emerging_skills = [
            {"skill": "Transformers", "growth_rate": 123.5, "current_demand": 75},
            {"skill": "Kubernetes", "growth_rate": 98.3, "current_demand": 120},
            {"skill": "MLOps", "growth_rate": 87.2, "current_demand": 60},
            {"skill": "React", "growth_rate": 76.5, "current_demand": 200},
            {"skill": "FastAPI", "growth_rate": 70.1, "current_demand": 50},
            {"skill": "Terraform", "growth_rate": 65.8, "current_demand": 85},
            {"skill": "GraphQL", "growth_rate": 63.2, "current_demand": 70},
            {"skill": "Streamlit", "growth_rate": 58.9, "current_demand": 40},
            {"skill": "PyTorch", "growth_rate": 55.4, "current_demand": 90},
            {"skill": "Rust", "growth_rate": 53.7, "current_demand": 45},
            {"skill": "TypeScript", "growth_rate": 50.2, "current_demand": 150},
            {"skill": "Flutter", "growth_rate": 48.6, "current_demand": 80},
            {"skill": "Golang", "growth_rate": 45.1, "current_demand": 110},
            {"skill": "Snowflake", "growth_rate": 43.8, "current_demand": 55},
            {"skill": "Spark", "growth_rate": 40.5, "current_demand": 95}
        ]
        
        # Utwórz DataFrame i wybierz top N
        df = pd.DataFrame(emerging_skills)
        return df.nlargest(n, 'growth_rate')

    def get_high_paying_skills(self, top_n=10):
        """Zwraca listę najlepiej płatnych umiejętności"""
        try:
            # Sprawdź czy mamy dane
            if self.data is None or self.data.empty:
                return []
            
            # Grupuj według umiejętności i znajdź średnie wynagrodzenie
            skills_salary = self.data.groupby('skill')['salary'].mean().reset_index()
            
            # Sortuj malejąco według wynagrodzenia
            skills_salary = skills_salary.sort_values('salary', ascending=False)
            
            # Zwróć najlepiej płatne umiejętności
            return skills_salary.head(top_n).to_dict('records')
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania najlepiej płatnych umiejętności: {e}")
            return [] 
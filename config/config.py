import os
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych
load_dotenv()

# Konfiguracja bazy danych
DATABASE_CONFIG = {
    'postgresql': {
        'host': os.getenv('PG_HOST', 'localhost'),
        'port': os.getenv('PG_PORT', '5432'),
        'user': os.getenv('PG_USER', 'postgres'),
        'password': os.getenv('PG_PASSWORD', ''),
        'database': os.getenv('PG_DATABASE', 'career_navigator')
    },
    'mongodb': {
        'uri': os.getenv('MONGO_URI', 'mongodb://localhost:27017/'),
        'database': os.getenv('MONGO_DB', 'career_navigator')
    }
}

# Konfiguracja API
API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 5000)),
    'debug': os.getenv('API_DEBUG', 'False').lower() == 'true',
    'secret_key': os.getenv('SECRET_KEY', 'tajny-klucz-domyslny-zmienic-w-produkcji')
}

# Ścieżki do modeli
MODEL_PATHS = {
    'skills_model': os.getenv('SKILLS_MODEL_PATH', 'models/skills_model.pkl'),
    'market_trends_model': os.getenv('MARKET_TRENDS_MODEL_PATH', 'models/market_trends_model.pkl'),
    'career_path_model': os.getenv('CAREER_PATH_MODEL_PATH', 'models/career_path_model.pkl'),
    'career_simulator_model': os.getenv('CAREER_SIMULATOR_MODEL_PATH', 'models/career_simulator_model.pkl')
}

# Konfiguracja bezpieczeństwa
SECURITY_CONFIG = {
    'password_salt': os.getenv('PASSWORD_SALT', 'sol-domyslna-zmienic-w-produkcji'),
    'token_expiration': int(os.getenv('TOKEN_EXPIRATION', 86400)),  # 24 godziny w sekundach
    'encryption_key': os.getenv('ENCRYPTION_KEY', 'klucz-szyfrowania-zmienic-w-produkcji')
} 
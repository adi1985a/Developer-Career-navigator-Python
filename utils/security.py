import os
import jwt
import hashlib
import binascii
import logging
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from ..config.config import SECURITY_CONFIG

logger = logging.getLogger(__name__)

class SecurityManager:
    """Klasa zarządzająca bezpieczeństwem danych i uwierzytelnianiem"""
    
    def __init__(self):
        """Inicjalizacja menedżera bezpieczeństwa"""
        self.secret_key = SECURITY_CONFIG['encryption_key']
        self.token_expiration = SECURITY_CONFIG['token_expiration']
        self.password_salt = SECURITY_CONFIG['password_salt']
        
        # Inicjalizacja Fernet dla szyfrowania symetrycznego
        try:
            # Klucz Fernet musi być 32-bajtowy, zakodowany w base64
            key = hashlib.sha256(self.secret_key.encode()).digest()
            self.cipher = Fernet(binascii.b2a_base64(key))
        except Exception as e:
            logger.error(f"Błąd podczas inicjalizacji szyfrowania: {e}")
            self.cipher = None
    
    def hash_password(self, password):
        """
        Hashuje hasło z wykorzystaniem soli
        
        Args:
            password: Hasło do zahashowania
            
        Returns:
            Zahashowane hasło
        """
        # Dodaj sól do hasła
        salted_password = password + self.password_salt
        
        # Użyj SHA-256 do hashowania
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        
        return hashed
    
    def verify_password(self, password, hashed_password):
        """
        Weryfikuje hasło
        
        Args:
            password: Hasło do sprawdzenia
            hashed_password: Zahashowane hasło z bazy
            
        Returns:
            True jeśli hasło jest poprawne, False w przeciwnym razie
        """
        # Zahashuj podane hasło w taki sam sposób
        hashed = self.hash_password(password)
        
        # Porównaj hashe
        return hashed == hashed_password
    
    def generate_token(self, user_id, additional_data=None):
        """
        Generuje token JWT dla użytkownika
        
        Args:
            user_id: ID użytkownika
            additional_data: Dodatkowe dane do umieszczenia w tokenie
            
        Returns:
            Token JWT
        """
        # Przygotuj dane do umieszczenia w tokenie
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiration)
        }
        
        # Dodaj dodatkowe dane jeśli podano
        if additional_data:
            payload.update(additional_data)
        
        # Generuj token
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        
        return token
    
    def verify_token(self, token):
        """
        Weryfikuje token JWT
        
        Args:
            token: Token JWT do weryfikacji
            
        Returns:
            Zdekodowane dane z tokenu lub None jeśli token jest nieprawidłowy
        """
        try:
            # Dekoduj token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token wygasł")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Nieprawidłowy token")
            return None
    
    def encrypt_data(self, data):
        """
        Szyfruje dane
        
        Args:
            data: Dane do zaszyfrowania (string)
            
        Returns:
            Zaszyfrowane dane (string) lub None w przypadku błędu
        """
        if not self.cipher:
            logger.error("Szyfrowanie nie jest dostępne")
            return None
            
        try:
            # Szyfruj dane
            encrypted = self.cipher.encrypt(data.encode())
            
            # Zwróć jako string
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Błąd podczas szyfrowania danych: {e}")
            return None
    
    def decrypt_data(self, encrypted_data):
        """
        Deszyfruje dane
        
        Args:
            encrypted_data: Zaszyfrowane dane (string)
            
        Returns:
            Odszyfrowane dane (string) lub None w przypadku błędu
        """
        if not self.cipher:
            logger.error("Szyfrowanie nie jest dostępne")
            return None
            
        try:
            # Deszyfruj dane
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            
            # Zwróć jako string
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Błąd podczas deszyfrowania danych: {e}")
            return None 
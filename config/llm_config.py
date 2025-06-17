"""
LLM Configuration for AutoGen Agents
Konfiguracja modeli językowych dla agentów AutoGen
"""

import os
from typing import Dict, Any


def get_llm_config() -> Dict[str, Any]:
    """
    Pobiera konfigurację LLM dla agentów AutoGen.

    Returns:
        Dict: Konfiguracja modelu językowego
    """
    return {
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY"),
        "temperature": 0.7,
        "max_tokens": 1500,
        "timeout": 30,
        "retry_wait_time": 5,
        "max_retry_period": 60,
    }


def get_data_collector_config() -> Dict[str, Any]:
    """Konfiguracja dla DATA_COLLECTOR_agent - precyzyjna, deterministyczna"""
    config = get_llm_config()
    config.update(
        {
            "temperature": 0.0,  # Precyzja dla zbierania danych
            "max_tokens": 1000,
        }
    )
    return config


def get_price_analyzer_config() -> Dict[str, Any]:
    """Konfiguracja dla PRICE_ANALYZER_agent - analityczna"""
    config = get_llm_config()
    config.update(
        {
            "temperature": 0.3,  # Lekka kreatywność dla analizy
            "max_tokens": 1200,
        }
    )
    return config


def get_review_generator_config() -> Dict[str, Any]:
    """Konfiguracja dla REVIEW_GENERATOR_agent - kreatywna ale obiektywna"""
    config = get_llm_config()
    config.update(
        {
            "temperature": 0.6,  # Kreatywność dla generowania opinii
            "max_tokens": 2000,  # Więcej tokenów dla długich opinii
        }
    )
    return config


def get_quality_assurance_config() -> Dict[str, Any]:
    """Konfiguracja dla QUALITY_ASSURANCE_agent - krytyczna ocena"""
    config = get_llm_config()
    config.update(
        {
            "temperature": 0.2,  # Niska temperatura dla obiektywnej oceny
            "max_tokens": 1000,
        }
    )
    return config


def get_user_proxy_config() -> Dict[str, Any]:
    """Konfiguracja dla USER_PROXY - komunikacja z użytkownikiem"""
    config = get_llm_config()
    config.update(
        {
            "temperature": 0.4,  # Balans między precyzją a naturalnością
            "max_tokens": 1500,
        }
    )
    return config


# API Key validation
def validate_api_key() -> bool:
    """
    Weryfikuje czy klucz API OpenAI jest ustawiony.

    Returns:
        bool: True jeśli klucz API jest dostępny
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ BŁĄD: Brak klucza OPENAI_API_KEY w zmiennych środowiskowych!")
        print("💡 Ustaw klucz: export OPENAI_API_KEY='twój_klucz_api'")
        return False
    return True

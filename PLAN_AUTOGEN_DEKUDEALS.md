# 🎮 AutoGen: Agent do Analizy i Generowania Opinii o Produktach z DekuDeals

## 🎯 Cele Projektu

**Główny Cel:** Stworzyć inteligentny system agentów AutoGen, który automatycznie analizuje gry z DekuDeals.com i generuje szczegółowe, użyteczne opinie dla użytkowników.

**Wartość Biznesowa:**
- Automatyzacja procesu research'u gier
- Obiektywne analizy wartości za pieniądze
- Personalizowane rekomendacje zakupów
- Tracking najlepszych ofert i okazji

---

## 🏗️ Architektura Systemu

### 📊 Obecne Możliwości (Analiza `deku_tools.py`)

**Dostępne Dane:**
- ✅ Podstawowe info: tytuł, deweloper, wydawca
- ✅ Ceny: MSRP, aktualna cena, najniższa historyczna
- ✅ Oceny: Metacritic, OpenCritic scores
- ✅ Metadata: platformy, gatunki, daty wydania
- ✅ Strukturalne parsowanie dat wydania

**Funkcjonalności:**
- ✅ `search_deku_deals()` - wyszukiwanie gier
- ✅ `scrape_game_details()` - pobieranie szczegółów
- ✅ `parse_release_dates()` - przetwarzanie dat

---

## 🤖 Struktura Agentów AutoGen

### Agent 1: **DATA_COLLECTOR_agent**
```python
# Rola: Pobieranie i walidacja danych z DekuDeals
system_message = """
Jesteś ekspertem od zbierania danych o grach z DekuDeals.com.
Twoje zadania:
- Wyszukaj grę podaną przez użytkownika
- Pobierz wszystkie dostępne dane o grze
- Zwaliduj kompletność danych
- Przekaż czytelny raport z zebranymi informacjami

Zakończ gdy: Uzyskasz kompletne dane o grze lub stwierdzisz, że gra nie istnieje.
"""
```

### Agent 2: **PRICE_ANALYZER_agent**
```python
# Rola: Analiza cen, wartości i trendów
system_message = """
Jesteś analitykiem cen i wartości gier.
Twoje zadania:
- Oceń stosunek ceny do wartości (price-to-value ratio)
- Porównaj aktualną cenę z MSRP i najniższą historyczną
- Określ, czy to dobry moment na zakup
- Wygeneruj rekomendacje cenowe

Zakończ gdy: Dostarczysz kompletną analizę cenową z rekomendacjami.
"""
```

### Agent 3: **REVIEW_GENERATOR_agent**
```python
# Rola: Generowanie szczegółowych opinii
system_message = """
Jesteś krytykiem gier specjalizującym się w obiektywnych recenzjach.
Twoje zadania:
- Przeanalizuj wszystkie zebrane dane o grze
- Uwzględnij oceny Metacritic i OpenCritic
- Oceń gatunki i target audience
- Wygeneruj kompleksową, obiektywną opinię
- Podaj jasne zalecenia "Kup/Czekaj/Omijaj"

Zakończ gdy: Stworzysz kompletną opinię z argumentacją i rekomendacją.
"""
```

### Agent 4: **QUALITY_ASSURANCE_agent**
```python
# Rola: Weryfikacja jakości i kompletności analiz
system_message = """
Jesteś kontrolerem jakości analiz gier.
Twoje zadania:
- Sprawdź kompletność wszystkich analiz
- Zweryfikuj logiczność argumentacji
- Upewnij się, że opinia jest obiektywna i użyteczna
- Zasugeruj poprawki jeśli potrzeba

Zakończ gdy: Potwierdzisz wysoką jakość finalnej opinii lub zasugerujesz konkretne poprawki.
"""
```

### Agent 5: **USER_PROXY** (Interfejs Użytkownika)
```python
# Rola: Komunikacja z użytkownikiem i koordynacja
system_message = """
Jesteś interfejsem między użytkownikiem a zespołem analityków gier.
Twoje zadania:
- Przyjmij zapytanie użytkownika o grę
- Koordynuj pracę zespołu analityków
- Prezentuj wyniki w czytelnej formie
- Odpowiadaj na dodatkowe pytania użytkownika

Zakończ gdy: Użytkownik otrzyma kompletną analizę i będzie zadowolony z odpowiedzi.
"""
```

---

## 🛠️ Narzędzia do Implementacji

### Narzędzie 1: `search_and_scrape_game`
```python
@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description="Wyszukuje grę na DekuDeals i pobiera wszystkie dane - Input: nazwa_gry (str) - Output: Dict z danymi gry"
)
def search_and_scrape_game(game_name: str) -> Dict:
    """
    OPIS: Łączy wyszukiwanie i scraping w jedną funkcję
    ARGS: 
        game_name (str): Nazwa gry do wyszukania
    RETURNS:
        Dict: Kompletne dane o grze lub komunikat o błędzie
    RAISES:
        Exception: Gdy nie można znaleźć lub zescrapować gry
    """
    try:
        # Walidacja wejścia
        if not game_name or not game_name.strip():
            raise ValueError("Nazwa gry nie może być pusta")
        
        # Wyszukaj URL gry
        game_url = search_deku_deals(game_name.strip())
        if not game_url:
            return {"error": "Nie znaleziono gry", "game_name": game_name}
        
        # Pobierz szczegóły
        game_details = scrape_game_details(game_url)
        if not game_details:
            return {"error": "Nie udało się pobrać danych", "game_url": game_url}
        
        # Dodaj URL do danych
        game_details["source_url"] = game_url
        game_details["search_query"] = game_name
        
        return game_details
    
    except Exception as e:
        logger.error(f"Błąd w search_and_scrape_game: {e}")
        return {"error": str(e), "game_name": game_name}
```

### Narzędzie 2: `calculate_value_score`
```python
@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description="Oblicza wartość za pieniądze na podstawie ceny i ocen - Input: game_data (Dict) - Output: Dict z analizą wartości"
)
def calculate_value_score(game_data: Dict) -> Dict:
    """
    OPIS: Oblicza obiektywny wskaźnik wartości za pieniądze
    ARGS:
        game_data (Dict): Dane gry z cename i ocenami
    RETURNS:
        Dict: Analiza wartości, rekomendacje cenowe
    RAISES:
        ValueError: Gdy brakuje kluczowych danych
    """
    try:
        # Wyciągnij kluczowe dane
        current_price = extract_price(game_data.get('current_eshop_price', 'N/A'))
        msrp = extract_price(game_data.get('MSRP', 'N/A'))
        lowest_price = extract_price(game_data.get('lowest_historical_price', 'N/A'))
        
        metacritic = extract_score(game_data.get('metacritic_score', '0'))
        opencritic = extract_score(game_data.get('opencritic_score', '0'))
        
        # Oblicz wskaźniki
        value_analysis = {
            "current_price": current_price,
            "price_vs_msrp": calculate_discount_percentage(current_price, msrp),
            "price_vs_lowest": calculate_price_difference(current_price, lowest_price),
            "average_score": (metacritic + opencritic) / 2 if metacritic > 0 and opencritic > 0 else max(metacritic, opencritic),
            "value_score": calculate_value_ratio(current_price, metacritic, opencritic),
            "recommendation": generate_price_recommendation(current_price, msrp, lowest_price, metacritic),
            "buy_timing": assess_buy_timing(current_price, lowest_price)
        }
        
        return value_analysis
        
    except Exception as e:
        logger.error(f"Błąd w calculate_value_score: {e}")
        return {"error": str(e), "analysis": "incomplete"}
```

### Narzędzie 3: `generate_game_review`
```python
@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description="Generuje kompleksową opinię o grze - Input: game_data (Dict), value_analysis (Dict) - Output: Dict z opinią"
)
def generate_game_review(game_data: Dict, value_analysis: Dict) -> Dict:
    """
    OPIS: Tworzy szczegółową opinię na podstawie wszystkich dostępnych danych
    ARGS:
        game_data (Dict): Podstawowe dane o grze
        value_analysis (Dict): Analiza wartości za pieniądze
    RETURNS:
        Dict: Strukturalna opinia z oceną i rekomendacjami
    RAISES:
        ValueError: Gdy brakuje kluczowych danych do opinii
    """
    try:
        review = {
            "game_title": game_data.get('title', 'Unknown'),
            "overall_rating": calculate_overall_rating(game_data, value_analysis),
            "strengths": identify_game_strengths(game_data),
            "weaknesses": identify_potential_weaknesses(game_data),
            "target_audience": determine_target_audience(game_data),
            "genre_analysis": analyze_genre_performance(game_data),
            "price_opinion": value_analysis.get('recommendation', 'No recommendation'),
            "final_verdict": generate_final_verdict(game_data, value_analysis),
            "confidence_level": assess_recommendation_confidence(game_data)
        }
        
        return review
        
    except Exception as e:
        logger.error(f"Błąd w generate_game_review: {e}")
        return {"error": str(e), "review": "incomplete"}
```

---

## 🔄 Workflow Konwersacji

### Faza 1: Inicjalizacja
```python
# USER_PROXY inicjuje konwersację
user_request = "Przeanalizuj grę: The Legend of Zelda: Tears of the Kingdom"

# Przekazuje zadanie do DATA_COLLECTOR_agent
```

### Faza 2: Zbieranie Danych
```python
# DATA_COLLECTOR_agent:
# 1. Używa search_and_scrape_game()
# 2. Waliduje kompletność danych
# 3. Przekazuje dane do PRICE_ANALYZER_agent
```

### Faza 3: Analiza Cenowa
```python
# PRICE_ANALYZER_agent:
# 1. Używa calculate_value_score()
# 2. Analizuje trendy cenowe
# 3. Generuje rekomendacje zakupowe
# 4. Przekazuje analizę do REVIEW_GENERATOR_agent
```

### Faza 4: Generowanie Opinii
```python
# REVIEW_GENERATOR_agent:
# 1. Używa generate_game_review()
# 2. Tworzy kompleksową opinię
# 3. Przekazuje draft do QUALITY_ASSURANCE_agent
```

### Faza 5: Kontrola Jakości
```python
# QUALITY_ASSURANCE_agent:
# 1. Weryfikuje kompletność i logiczność
# 2. Sugeruje poprawki jeśli potrzeba
# 3. Zatwierdza finalną wersję
# 4. Przekazuje do USER_PROXY
```

### Faza 6: Prezentacja Wyników
```python
# USER_PROXY:
# 1. Formatuje opinię dla użytkownika
# 2. Prezentuje wyniki
# 3. Odpowiada na dodatkowe pytania
```

---

## 📁 Struktura Plików Projektu

```
autogen-dekudeals/
├── deku_tools.py                 # ✅ Istniejące narzędzia scraping
├── autogen_agents.py            # 🆕 Definicje agentów AutoGen
├── agent_tools.py               # 🆕 Narzędzia dla agentów
├── conversation_manager.py      # 🆕 Zarządzanie workflow
├── utils/
│   ├── price_calculator.py      # 🆕 Kalkulacje cenowe
│   ├── review_templates.py      # 🆕 Szablony opinii
│   └── data_validator.py        # 🆕 Walidacja danych
├── config/
│   ├── agent_configs.py         # 🆕 Konfiguracje agentów
│   └── llm_config.py           # 🆕 Konfiguracje modeli LLM
├── tests/
│   ├── test_agents.py          # 🆕 Testy agentów
│   └── test_tools.py           # 🆕 Testy narzędzi
├── examples/
│   ├── basic_analysis.py       # 🆕 Przykład prostej analizy
│   └── batch_analysis.py       # 🆕 Analiza wielu gier
├── logs/                       # 🆕 Logi systemu
├── requirements.txt            # ✅ Istniejące zależności
└── README.md                   # 🆕 Dokumentacja projektu
```

---

## 🚀 Plan Implementacji (Fazy)

### FAZA 1: Fundament (Tydzień 1)
- [ ] Stworzenie podstawowej struktury agentów
- [ ] Implementacja `search_and_scrape_game` tool
- [ ] Prosty workflow między agentami
- [ ] Podstawowe testy

### FAZA 2: Analiza Cenowa (Tydzień 2)
- [ ] Implementacja `calculate_value_score`
- [ ] Algorytmy oceny wartości za pieniądze
- [ ] Rekomendacje timing zakupu
- [ ] Testy analizy cenowej

### FAZA 3: Generowanie Opinii (Tydzień 3)
- [ ] Implementacja `generate_game_review`
- [ ] Szablony strukturalnej opinii
- [ ] System oceny confidence level
- [ ] Testy jakości opinii

### FAZA 4: Kontrola Jakości (Tydzień 4)
- [ ] QA Agent z validation rules
- [ ] Automatyczne sprawdzanie kompletności
- [ ] Feedback loop dla poprawek
- [ ] Metryki jakości

### FAZA 5: Interfejs i UX (Tydzień 5)
- [ ] Polished user interface
- [ ] Czytelne formatowanie wyników
- [ ] Handling edge cases
- [ ] Error messages i recovery

### FAZA 6: Optymalizacja (Tydzień 6)
- [ ] Performance optimization
- [ ] Parallel processing
- [ ] Caching mechanizmy
- [ ] Rate limiting dla API

---

## 🎯 Metryki Sukcesu

### Jakość Opinii
- **Kompletność:** 95% opinii zawiera wszystkie sekcje
- **Dokładność:** Weryfikacja przez porównanie z recenzjami ekspertów
- **Użyteczność:** Feedback użytkowników na rekomendacje

### Wydajność
- **Czas analizy:** < 30 sekund na grę
- **Dostępność:** 99% uptime scraping
- **Skalowanie:** Możliwość analizy 100+ gier/dzień

### User Experience
- **Ease of use:** Prosta komenda → kompleksowa analiza
- **Personalizacja:** Dostosowanie do preferencji użytkownika
- **Reliability:** Consistent quality of recommendations

---

## 🎪 Przykład Użycia

```python
# Inicjalizacja
conversation_manager = ConversationManager()

# Analiza gry
user_query = "Przeanalizuj Hollow Knight - czy warto kupić?"

# Automatyczny workflow
result = conversation_manager.analyze_game(user_query)

# Wynik:
{
    "game_title": "Hollow Knight",
    "overall_rating": 9.2,
    "price_recommendation": "STRONG BUY - Excellent value",
    "target_audience": "Metroidvania fans, challenge seekers",
    "final_verdict": "Exceptional indie game with incredible value...",
    "confidence_level": "High"
}
```

---

## 🎈 Następne Kroki

1. **Utworzenie podstawowej struktury agentów** (`autogen_agents.py`)
2. **Implementacja pierwszego narzędzia** (`search_and_scrape_game`)
3. **Przetestowanie prostego workflow** między agentami
4. **Iteracyjne rozwijanie** kolejnych funkcjonalności

**Gotowy na rozpoczęcie implementacji?** 🚀 
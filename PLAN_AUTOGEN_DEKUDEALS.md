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

### FAZA 0: Setup i Planowanie ✅ UKOŃCZONA
- [x] **Stworzenie instrukcji AI** - `.cursor/rules/cursor-instructions.md`
- [x] **Wstępna analiza `deku_tools.py`** - implementacja `parse_release_dates()`
- [x] **Dokumentacja planu** - `PLAN_AUTOGEN_DEKUDEALS.md` + `AUTOGEN_PLAN.md`
- [x] **Struktura katalogów i konfiguracja środowiska**

### FAZA 1: Fundament ✅ UKOŃCZONA
- [x] **Stworzenie podstawowej struktury agentów** - `autogen_agents.py`
  - 5 wyspecjalizowanych agentów: DATA_COLLECTOR, PRICE_ANALYZER, REVIEW_GENERATOR, QUALITY_ASSURANCE, USER_PROXY
  - Konfiguracje LLM z agent-specific temperature (0.0-0.6)
- [x] **Implementacja `search_and_scrape_game` tool** - `agent_tools.py`
  - Narzędzia podstawowe: search, validation, formatting
- [x] **Prosty workflow między agentami** - `conversation_manager.py`
  - GameAnalysisManager class + workflow orchestration
- [x] **Podstawowe testy** - `tests/test_phase1.py`
  - 11 testów, wszystkie przeszły
- [x] **Dokumentacja** - `README.md` + przykłady w `examples/basic_analysis.py`

### FAZA 2: Analiza Cenowa ✅ UKOŃCZONA KOMPLEKSOWO

#### **Punkt 2.1: Basic Value Analysis** ✅ UKOŃCZONA
- [x] **Implementacja `calculate_value_score`** - `utils/price_calculator.py`
  - `extract_price()`: Multi-format parsing (PLN, USD, etc.)
  - `extract_score()`: Score normalization (0-100 scale)
  - `calculate_discount_percentage()`, `calculate_price_difference()`, `calculate_value_ratio()`
  - `assess_buy_timing()`: 5-tier timing (EXCELLENT→WAIT)
  - `generate_price_recommendation()`: STRONG BUY→SKIP algorithm
- [x] **Integracja z agent_tools.py** - `calculate_value_score()` function
- [x] **Real-world testing** - Hollow Knight, Zelda TOTK, Celeste

#### **Punkt 2.2: Advanced Value Algorithms** ✅ UKOŃCZONA
- [x] **Zaawansowane algorytmy** - `utils/advanced_value_algorithms.py`
  - **Genre profiles**: 13 gatunków z expected hours, replay value, price tolerance
  - **Developer reputation**: Multipliers (Nintendo: 1.3x, Team Cherry: 1.2x, etc.)
  - **Market position matrix**: Quality vs Price (20 kategorii od "Hidden Gem" do "Scam")
  - **Age factor**: Depreciation based on release year (new: 1.0x → old: 0.8x)
  - **Comprehensive scoring**: Genre (40%) + Market (40%) + Age (20%)
- [x] **Enhanced functionality** - `calculate_advanced_value_analysis()`
  - Insights generation + confidence levels
- [x] **Real-world validation** - INSIDE: "INSTANT BUY - Hidden Gem!" (11.21 score)

#### **Punkt 2.3: Recommendation System Integration** ✅ UKOŃCZONA  
- [x] **System rekomendacji** - `utils/recommendation_engine.py`
  - **UserPreference enum**: 8 typów użytkowników (BARGAIN_HUNTER→CASUAL_PLAYER)
  - **UserProfile dataclass**: Budget range, preferred genres, minimum scores
  - **RecommendationEngine class**: Personalized scoring (value + user preferences)
  - **5 gotowych profili**: Bargain Hunter, Quality Seeker, Indie Lover, AAA Gamer, Casual Player
  - **GameRecommendation dataclass**: Structured output z reasons, confidence, warnings
- [x] **Integracja z agentami** - wszystkie narzędzia zarejestrowane z decorators
- [x] **Comprehensive testing** - wszystkie komponenty przetestowane na rzeczywistych danych

**FAZA 2 SZCZEGÓŁOWE PODSUMOWANIE SUKCESU:**
🎯 **3 główne komponenty**: price_calculator.py + advanced_value_algorithms.py + recommendation_engine.py
🎯 **5 user profiles** gotowych do użycia z różnymi charakterystykami
🎯 **3 nowe narzędzia** AutoGen: `calculate_value_score()`, `calculate_advanced_value_analysis()`, `get_personalized_recommendation()`
🎯 **Sophisticated scoring**: Multi-dimensional analysis z confidence levels
🎯 **Real-world proven**: INSIDE (Hidden Gem 7.19 zł vs 71.99 zł), Baten Kaitos (SKIP 3.56 score)
✅ **Type safety**: Full type hints + error handling + logging
✅ **AutoGen integration**: Wszystkie tools registered z proper decorators

### FAZA 3: Generowanie Opinii (Tydzień 3) 🚧 W TRAKCIE
- [ ] **Implementacja `generate_game_review`** - kompleksowe generowanie opinii
  - Strukturalne opinie z ocenami i argumentacją
  - Target audience identification
  - Strengths/weaknesses analysis
- [ ] **Szablony strukturalnej opinii** - standardowe formaty review
  - Opinion templates dla różnych gatunków
  - Adaptive formatting based on data availability
- [ ] **System oceny confidence level** - pewność rekomendacji
  - Confidence scoring algorithm
  - Data completeness impact on confidence
- [ ] **Testy jakości opinii** - walidacja generowanych review
  - Automated quality checks
  - Comparison with expert reviews

### FAZA 4: Kontrola Jakości (Tydzień 4)
- [ ] **QA Agent z validation rules** - automatyczna weryfikacja
  - Completeness validation
  - Logic consistency checks
  - Opinion objectivity assessment
- [ ] **Automatyczne sprawdzanie kompletności** - data validation
  - Required field checking
  - Score threshold validation
  - Price data completeness
- [ ] **Feedback loop dla poprawek** - iterative improvement
  - Correction suggestion system
  - Quality improvement tracking
- [ ] **Metryki jakości** - quality measurement
  - Opinion completeness metrics
  - User satisfaction tracking

### FAZA 5: Interfejs i UX (Tydzień 5)
- [ ] **Polished user interface** - user experience enhancement
  - CLI interface improvements
  - Result presentation formatting
  - Interactive elements
- [ ] **Czytelne formatowanie wyników** - output optimization
  - Structured opinion display
  - Color-coded recommendations
  - Summary sections
- [ ] **Handling edge cases** - error management
  - Game not found scenarios
  - Missing data handling
  - API timeout management
- [ ] **Error messages i recovery** - user guidance
  - Helpful error descriptions
  - Recovery suggestions
  - Fallback options

### FAZA 6: Optymalizacja (Tydzień 6)
- [ ] **Performance optimization** - speed improvements
  - Parallel agent execution
  - Optimized data processing
  - Memory usage optimization
- [ ] **Parallel processing** - concurrency
  - Multiple game analysis
  - Batch processing capabilities
  - Background task management
- [ ] **Caching mechanizmy** - data persistence
  - Game data caching
  - Analysis result caching
  - Smart cache invalidation
- [ ] **Rate limiting dla API** - responsible usage
  - Request throttling
  - Retry mechanisms
  - API quota management

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

### ✅ UKOŃCZONE KOMPLEKSOWO:
1. **✓ FAZA 0: Setup i Planowanie** - Instrukcje AI, dokumentacja, konfiguracja
2. **✓ FAZA 1: Fundament** - Agenci AutoGen, podstawowe narzędzia, workflow, testy
3. **✓ FAZA 2.1: Basic Value Analysis** - `price_calculator.py`, podstawowe kalkulacje wartości
4. **✓ FAZA 2.2: Advanced Algorithms** - `advanced_value_algorithms.py`, genre/market/age analysis  
5. **✓ FAZA 2.3: Recommendation Engine** - `recommendation_engine.py`, personalizowane rekomendacje
6. **✓ Integracja wszystkich narzędzi** - wszystkie tools registered z AutoGen decorators
7. **✓ Real-world testing** - walidacja na rzeczywistych danych DekuDeals

### 🚧 OBECNY STATUS:
**FAZA 2 UKOŃCZONA W 100%** - Kompletny system analizy wartości i rekomendacji gotowy do użycia

### 🎯 NASTĘPNE DO ZROBIENIA (FAZA 3 - GENEROWANIE OPINII):
1. **🔥 PRIORYTET: `generate_game_review` implementation**
   - Kompleksowe generowanie opinii na podstawie wszystkich zebranych danych
   - Strukturalne output z ratings, strengths, weaknesses, target audience
   - Integracja z istniejącymi systemami value analysis i recommendations

2. **Review Templates & Formatting**
   - Szablony opinii dla różnych gatunków gier
   - Adaptive formatting w zależności od dostępności danych
   - Professional presentation layer

3. **Quality Assurance Integration**
   - Confidence level assessment dla generowanych opinii
   - Automated validation checks
   - Consistency verification z existing tools

4. **Testing & Validation**
   - End-to-end testing całego pipeline
   - Porównanie z expert reviews
   - User acceptance validation

**Status: Gotowy do rozpoczęcia FAZY 3! Solidny fundament i narzędzia value analysis gotowe.** 🚀

### 📊 CURRENT SYSTEM CAPABILITIES:
✅ **Data Collection**: `search_and_scrape_game()` w pełni funkcjonalne  
✅ **Price Analysis**: Podstawowa + zaawansowana analiza wartości  
✅ **Personalization**: 5 user profiles + recommendation engine  
✅ **Agent Infrastructure**: 5 specialized AutoGen agents  
✅ **Testing**: Wszystkie komponenty przetestowane na real data  

**Następny milestone: Kompleksowe generowanie opinii na poziomie professional game reviews** 🎮 
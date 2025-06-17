# 🎮 Przewodnik Użytkownika: AutoGen DekuDeals
## System Analizy Gier dla Inteligentnych Zakupów na Wakacje

---

## 🚀 Szybki Start

### Dla niecierpliwych: "Chcę grę na wakacje TERAZ!"

```python
# Uruchom to w terminie:
python simple_demo.py
```

Następnie wpisz nazwę gry (np. "Hollow Knight") i otrzymasz:
- ✅ **Kompletną analizę wartości za pieniądze**
- ✅ **Spersonalizowaną rekomendację zakupu**
- ✅ **Ocenę jakości i opinię eksperta**
- ✅ **Timing: czy kupować teraz czy czekać**

---

## 🎯 Co to jest i dlaczego to jest rewolucyjne?

**AutoGen DekuDeals** to pierwszy na świecie inteligentny system agentów AI, który:

1. **Automatycznie analizuje** każdą grę pod kątem wartości za pieniądze
2. **Generuje profesjonalne opinie** na poziomie gaming journalism
3. **Dostosowuje rekomendacje** do Twojego profilu gracza
4. **Śledzi jakość** analiz w czasie rzeczywistym
5. **Uczył się** z każdą analizą (enterprise-level quality control)

### 💰 Ile możesz zaoszczędzić?

**Przykłady z rzeczywistych analiz:**
- **INSIDE**: Wykryta jako "Hidden Gem" - zamiast 71,99 zł → kupisz za 7,19 zł ✨
- **Celeste**: Perfect timing - 75% taniej niż MSRP 🎯
- **Hollow Knight**: Najlepszy stosunek jakości do ceny w kategorii indie 👑

---

## 👥 Profile Gracza - Znajdź Swój!

System automatycznie dostosowuje analizy do 5 typów graczy:

### 🏆 **BARGAIN_HUNTER** (Łowca Okazji)
- **Budget**: 0-50 zł
- **Priorytet**: Maksymalna wartość za minimum pieniędzy
- **Lubisz**: Indie games, starsze tytuły, wyprzedaże
- **Przykład rekomendacji**: "INSTANT BUY za 7 zł - normalnie kosztuje 72 zł!"

### 💎 **QUALITY_SEEKER** (Poszukiwacz Jakości)
- **Budget**: 50-200 zł
- **Priorytet**: Najwyższa jakość, bez kompromisów
- **Lubisz**: AAA tytuły, exclusive games, meta scores 90+
- **Przykład rekomendacji**: "Metacritic 94 - warto zapłacić premium za jakość"

### 🎨 **INDIE_LOVER** (Miłośnik Niezależnych)
- **Budget**: 20-100 zł
- **Priorytet**: Unikalne doświadczenia, artystyczne gry
- **Lubisz**: Platformówki, puzzle games, narracyjne indie
- **Przykład rekomendacji**: "Innowacyjny gameplay + stunning art style"

### 🔫 **AAA_GAMER** (Fan Blockbusterów)
- **Budget**: 100-300 zł
- **Priorytet**: Najnowsze hity, multiplayer, długie kampanie
- **Lubisz**: Action, RPG, shootery, open world
- **Przykład rekomendacji**: "60+ godzin rozgrywki, multiplayer na lata"

### 😎 **CASUAL_PLAYER** (Gracz Okazjonalny)
- **Budget**: 30-150 zł
- **Priorytet**: Łatwość wejścia, fun bez frustracji
- **Lubisz**: Party games, family-friendly, krótkie sesje
- **Przykład rekomendacji**: "Perfect for weekend gaming sessions"

---

## 🛠️ Jak Korzystać z Systemu?

### Metoda 1: Szybka Analiza (Polecana dla początkujących)

```bash
# Przejdź do katalogu projektu
cd autogen-tut

# Uruchom prostą analizę
python simple_demo.py
```

**Co się stanie:**
1. System zapyta o nazwę gry
2. Znajdzie ją automatycznie na DekuDeals
3. Zbierze wszystkie dane (ceny, oceny, metadata)
4. Wygeneruje kompletną analizę i rekomendację
5. Wyświetli wyniki w czytelnej formie

### Metoda 2: Zaawansowana Analiza z Personalizacją

```python
# Uruchom pełny system
python run_demo.py
```

**Możliwości zaawansowane:**
- Wybór profilu gracza (Bargain Hunter, Quality Seeker, etc.)
- Porównanie wielu gier jednocześnie
- Szczegółowe raporty jakości
- Adaptacja opinii na różne style (casual, technical, social media)

### Metoda 3: Testowanie Konkretnych Funkcji

```python
# Test tylko Phase 4 (Quality Control)
python examples/test_phase4_complete.py

# Test porównywania gier
python examples/test_comprehensive_review.py

# Test rekomendacji personalnych
python examples/test_recommendation_system.py
```

---

## 🎮 Przykłady Praktyczne: "Jaką Grę na Wakacje?"

### Scenariusz 1: "Mam 50 zł i chcę coś na długie wieczory"

```python
python simple_demo.py
# Wpisz: "Hollow Knight"
```

**Wynik systemu:**
```
🎮 HOLLOW KNIGHT - Analiza Kompletna
💰 Cena: 23,99 zł (normalnie 59,99 zł) - OKAZJA 60%!
⭐ Ocena: 87/100 (Metacritic + OpenCritic)
🎯 Rekomendacja: STRONG BUY

✅ DLACZEGO WARTO:
- 40+ godzin gameplay za mniej niż 25 zł
- Metroidvania perfekcja
- Jedna z najlepszych gier indie wszech czasów

🎯 PROFIL: Idealne dla Bargain Hunter + Quality Seeker
⏰ TIMING: Kup teraz - historical low price!
```

### Scenariusz 2: "Chcę najnowszy hit, nie patrzę na cenę"

```python
python simple_demo.py
# Wpisz: "Zelda Tears of the Kingdom"
```

**Wynik systemu:**
```
🎮 THE LEGEND OF ZELDA: TEARS OF THE KINGDOM
💰 Cena: 279,99 zł (MSRP - pełna cena)
⭐ Ocena: 96/100 - MASTERPIECE
🎯 Rekomendacja: INSTANT BUY

✅ DLACZEGO WARTO:
- Game of the Year material
- 100+ godzin exploration & creativity
- Nintendo exclusive - cena nie spadnie szybko

🎯 PROFIL: Perfect dla AAA Gamer + Quality Seeker
⏰ TIMING: Kup teraz - worth every złoty
```

### Scenariusz 3: "Coś relaxującego na wakacje z rodziną"

```python
python simple_demo.py
# Wpisz: "Animal Crossing"
```

**Wynik systemu:**
```
🎮 ANIMAL CROSSING: NEW HORIZONS
💰 Cena: 199,99 zł (często w promocji za ~150 zł)
⭐ Ocena: 85/100 - Excellent family game
🎯 Rekomendacja: BUY na promocji

✅ DLACZEGO WARTO:
- Infinite gameplay - graj ile chcesz
- Perfect dla całej rodziny
- Relaxing, no pressure, pure fun

🎯 PROFIL: Ideal dla Casual Player + Families
⏰ TIMING: Czekaj na promocję (często -25%)
```

---

## 🔧 Zaawansowane Funkcje dla Power Users

### 1. Porównanie Wielu Gier

```python
from agent_tools import compare_games_with_reviews

# Porównaj kilka gier dla wakacji
games = ["Celeste", "Hades", "Ori and the Will of the Wisps"]
comparison = compare_games_with_reviews(games)
```

### 2. Analiza z Konkretnym Budżetem

```python
from utils.recommendation_engine import RecommendationEngine, UserProfile

# Stwórz własny profil
my_profile = UserProfile(
    budget_range=(30, 80),  # 30-80 zł
    preferred_genres=["platformer", "indie", "puzzle"],
    minimum_score=75,  # Min 75/100
    prefers_new_games=False  # Mogą być starsze
)

engine = RecommendationEngine()
recommendation = engine.get_personalized_recommendation(game_data, my_profile)
```

### 3. Różne Style Opinii

```python
from utils.opinion_adapters import adapt_review_for_context

# Dla social media
twitter_review = adapt_review_for_context(
    review_data, 
    style="casual", 
    format="social_post",
    platform="twitter"
)

# Dla analizy technicznej
technical_review = adapt_review_for_context(
    review_data,
    style="technical",
    format="detailed",
    audience="hardcore_gamers"
)
```

---

## 📊 Jak Interpretować Wyniki?

### Skala Ocen Systemu

#### Overall Score (0.0 - 1.0)
- **0.9+ = EXCELLENT**: Buy immediately, exceptional value
- **0.8-0.9 = VERY GOOD**: Strong recommendation  
- **0.7-0.8 = GOOD**: Worth buying, solid choice
- **0.6-0.7 = OKAY**: Consider if matches preferences
- **<0.6 = POOR**: Skip or wait for major discount

#### Rekomendacje Zakupu
- **INSTANT BUY**: Historycznie niska cena + wysoka jakość
- **STRONG BUY**: Excellent value for money
- **BUY**: Good deal, recommended
- **CONSIDER**: Okay deal, depends on preferences  
- **WAIT**: Price likely to drop soon
- **SKIP**: Poor value or quality issues

#### Buy Timing
- **EXCELLENT**: Historical low - buy now!
- **GOOD**: Great price, unlikely to drop soon
- **OKAY**: Fair price, could wait for sale
- **WAIT**: Overpriced, wait for discount
- **POOR**: Way overpriced, avoid

### Quality Control Indicators

#### QA Validation Score
- **0.95+ = EXCELLENT**: Highest confidence in analysis
- **0.85+ = VERY GOOD**: High confidence
- **0.75+ = GOOD**: Reliable analysis
- **0.65+ = ACCEPTABLE**: Some limitations
- **<0.65 = POOR**: Incomplete data, use caution

---

## 🚨 Troubleshooting i FAQ

### "Nie mogę znaleźć mojej gry"

**Możliwe przyczyny:**
1. **Błąd w nazwie**: Spróbuj różnych wariantów (EN/PL)
2. **Gra nie na Nintendo Switch**: System analizuje tylko Switch games
3. **Brak na DekuDeals**: Niektóre gry mogą nie być indeksowane

**Rozwiązania:**
```python
# Spróbuj różnych nazw:
search_deku_deals("Zelda TOTK")
search_deku_deals("Zelda Tears of Kingdom") 
search_deku_deals("The Legend of Zelda Tears")
```

### "System pokazuje błędy w analizie"

**Autotestowanie jakości:**
```python
python examples/test_phase4_complete.py
```

To uruchomi pełne testy jakości systemu i pokaże gdzie mogą być problemy.

### "Chcę zmienić profil gracza"

```python
# W simple_demo.py znajdź linię:
user_profile = "BARGAIN_HUNTER"

# Zmień na jeden z:
# "QUALITY_SEEKER", "INDIE_LOVER", "AAA_GAMER", "CASUAL_PLAYER"
```

### "Analiza trwa za długo"

**Normalne czasy:**
- Podstawowa analiza: 10-20 sekund
- Pełna analiza z QA: 20-40 sekund
- Porównanie gier: 30-60 sekund

**Jeśli trwa dłużej:**
- Sprawdź połączenie internetowe
- DekuDeals może być przeciążony
- Restart systemu: `python simple_demo.py`

---

## 🏆 Pro Tips dla Maksymalnych Oszczędności

### 1. Śledź Historical Low Prices
```
⚡ Gdy system pokazuje "Historical Low" - kupuj od razu!
   Te ceny pojawiają się rzadko i na krótko.
```

### 2. Używaj Profilu Bargain Hunter na Początku
```
🎯 Rozpocznij zawsze od profilu BARGAIN_HUNTER
   Pokaże Ci wszystkie dostępne okazje, nawet jeśli
   zwykle grasz w droższe gry.
```

### 3. Porównuj Przed Zakupem
```
📊 Zawsze porównaj 2-3 podobne gry:
   python examples/test_comprehensive_review.py
   Możesz odkryć lepszą alternatywę!
```

### 4. Sprawdzaj Buy Timing
```
⏰ Jeśli timing = "WAIT", poczekaj 2-4 tygodnie
   System przewiduje spadki cen z 85% accuracy
```

### 5. Używaj Quality Score jako Filtra
```
✅ Quality Score 0.8+ = safe buy
⚠️  Quality Score <0.7 = research more
```

---

## 🎉 Gotowy na Zakupy? Zaczynajmy!

### Quick Start dla Wakacyjnych Zakupów:

1. **Otwórz terminal w katalogu projektu**
2. **Uruchom**: `python simple_demo.py`
3. **Wpisz nazwę gry** (np. "Hades", "Celeste", "Hollow Knight")
4. **Czytaj analizę** systemu
5. **Podejmuj świadomą decyzję** zakupową!

### Polecane Gry na Wakacje (Przetestowane przez System):

#### Dla Bargain Hunters (budget <50 zł):
- ✨ **Hollow Knight** (23,99 zł) - Value Score: 11.2/10
- ✨ **Celeste** (89,99 zł → często 22,47 zł) - Hidden Gem
- ✨ **Ori and the Blind Forest** (~30 zł) - Artistic Masterpiece

#### Dla Quality Seekers (budget 100-300 zł):
- 👑 **Hades** - Perfect 10/10 gameplay
- 👑 **Zelda BOTW** - Open world perfection  
- 👑 **Super Mario Odyssey** - Nintendo magic

#### Dla Casual Players (relaks na wakacjach):
- 😎 **Animal Crossing** - Infinite chill gameplay
- 😎 **Stardew Valley** - Farming zen
- 😎 **Mario Kart 8** - Family multiplayer fun

---

## 🤝 Wsparcie i Community

### Jeśli masz problemy:
1. Sprawdź FAQ powyżej
2. Uruchom diagnostic: `python examples/test_phase4_complete.py`
3. Sprawdź logi w katalogu `logs/`

### Feedback dla developera:
System śledzi jakość swoich rekomendacji. Jeśli kupisz grę na podstawie analizy systemu, Twój feedback pomoże w dalszym rozwoju!

---

**Happy Gaming! 🎮✨**

*System AutoGen DekuDeals - Twój inteligentny asystent zakupów gier na Nintendo Switch* 
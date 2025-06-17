# 🎮 AutoGen: Agent for Product Analysis and Opinion Generation from DekuDeals

## 🎯 Project Goals

**Main Goal:** Create an intelligent AutoGen agent system that automatically analyzes games from DekuDeals.com and generates detailed, useful opinions for users.

**Business Value:**
- Automation of game research process
- Objective value-for-money analysis
- Personalized purchase recommendations
- Tracking best deals and opportunities

---

## 🏗️ System Architecture

### 📊 Current Capabilities (Analysis of `deku_tools.py`)

**Available Data:**
- ✅ Basic info: title, developer, publisher
- ✅ Prices: MSRP, current price, lowest historical
- ✅ Ratings: Metacritic, OpenCritic scores
- ✅ Metadata: platforms, genres, release dates
- ✅ Structural parsing of release dates

**Functionalities:**
- ✅ `search_deku_deals()` - game searching
- ✅ `scrape_game_details()` - detail scraping
- ✅ `parse_release_dates()` - date processing

---

## 🤖 AutoGen Agent Structure

### Agent 1: **DATA_COLLECTOR_agent**
```python
# Role: Data collection and validation from DekuDeals
system_message = """
You are an expert at collecting game data from DekuDeals.com.
Your tasks:
- Search for the game specified by the user
- Retrieve all available game data
- Validate data completeness
- Provide a clear report with collected information

Terminate when: You obtain complete game data or determine that the game doesn't exist.
"""
```

### Agent 2: **PRICE_ANALYZER_agent**
```python
# Role: Price, value and trend analysis
system_message = """
You are a game price and value analyst.
Your tasks:
- Assess price-to-value ratio
- Compare current price with MSRP and lowest historical
- Determine if it's a good time to buy
- Generate pricing recommendations

Terminate when: You provide complete price analysis with recommendations.
"""
```

### Agent 3: **REVIEW_GENERATOR_agent**
```python
# Role: Detailed opinion generation
system_message = """
You are a game critic specializing in objective reviews.
Your tasks:
- Analyze all collected game data
- Consider Metacritic and OpenCritic scores
- Evaluate genres and target audience
- Generate comprehensive, objective opinion
- Provide clear "Buy/Wait/Skip" recommendations

Terminate when: You create a complete opinion with argumentation and recommendation.
"""
```

### Agent 4: **QUALITY_ASSURANCE_agent**
```python
# Role: Quality verification and analysis completeness
system_message = """
You are a quality controller for game analyses.
Your tasks:
- Check completeness of all analyses
- Verify logical consistency of arguments
- Ensure opinion is objective and useful
- Suggest corrections if needed

Terminate when: You confirm high quality of final opinion or suggest specific improvements.
"""
```

### Agent 5: **USER_PROXY** (User Interface)
```python
# Role: User communication and coordination
system_message = """
You are the interface between user and game analyst team.
Your tasks:
- Accept user queries about games
- Coordinate analyst team work
- Present results in readable format
- Answer additional user questions

Terminate when: User receives complete analysis and is satisfied with the response.
"""
```

---

## 🛠️ Implementation Tools

### Tool 1: `search_and_scrape_game`
```python
@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description="Search game on DekuDeals and retrieve all data - Input: game_name (str) - Output: Dict with game data"
)
def search_and_scrape_game(game_name: str) -> Dict:
    """
    DESCRIPTION: Combines searching and scraping into one function
    ARGS: 
        game_name (str): Name of game to search for
    RETURNS:
        Dict: Complete game data or error message
    RAISES:
        Exception: When game cannot be found or scraped
    """
    try:
        # Input validation
        if not game_name or not game_name.strip():
            raise ValueError("Game name cannot be empty")
        
        # Search for game URL
        game_url = search_deku_deals(game_name.strip())
        if not game_url:
            return {"error": "Game not found", "game_name": game_name}
        
        # Retrieve details
        game_details = scrape_game_details(game_url)
        if not game_details:
            return {"error": "Failed to retrieve data", "game_url": game_url}
        
        # Add URL to data
        game_details["source_url"] = game_url
        game_details["search_query"] = game_name
        
        return game_details
    
    except Exception as e:
        logger.error(f"Error in search_and_scrape_game: {e}")
        return {"error": str(e), "game_name": game_name}
```

### Tool 2: `calculate_value_score`
```python
@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description="Calculate value for money based on price and ratings - Input: game_data (Dict) - Output: Dict with value analysis"
)
def calculate_value_score(game_data: Dict) -> Dict:
    """
    DESCRIPTION: Calculate objective value-for-money indicator
    ARGS:
        game_data (Dict): Game data with prices and ratings
    RETURNS:
        Dict: Value analysis, pricing recommendations
    RAISES:
        ValueError: When key data is missing
    """
    try:
        # Extract key data
        current_price = extract_price(game_data.get('current_eshop_price', 'N/A'))
        msrp = extract_price(game_data.get('MSRP', 'N/A'))
        lowest_price = extract_price(game_data.get('lowest_historical_price', 'N/A'))
        
        metacritic = extract_score(game_data.get('metacritic_score', '0'))
        opencritic = extract_score(game_data.get('opencritic_score', '0'))
        
        # Calculate indicators
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
        logger.error(f"Error in calculate_value_score: {e}")
        return {"error": str(e), "analysis": "incomplete"}
```

### Tool 3: `generate_game_review`
```python
@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description="Generate comprehensive game opinion - Input: game_data (Dict), value_analysis (Dict) - Output: Dict with opinion"
)
def generate_game_review(game_data: Dict, value_analysis: Dict) -> Dict:
    """
    DESCRIPTION: Create detailed opinion based on all available data
    ARGS:
        game_data (Dict): Basic game data
        value_analysis (Dict): Value-for-money analysis
    RETURNS:
        Dict: Structural opinion with rating and recommendations
    RAISES:
        ValueError: When key data for opinion is missing
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
        logger.error(f"Error in generate_game_review: {e}")
        return {"error": str(e), "review": "incomplete"}
```

---

## 🔄 Conversation Workflow

### Phase 1: Initialization
```python
# USER_PROXY initiates conversation
user_request = "Analyze game: The Legend of Zelda: Tears of the Kingdom"

# Passes task to DATA_COLLECTOR_agent
```

### Phase 2: Data Collection
```python
# DATA_COLLECTOR_agent:
# 1. Uses search_and_scrape_game()
# 2. Validates data completeness
# 3. Passes data to PRICE_ANALYZER_agent
```

### Phase 3: Price Analysis
```python
# PRICE_ANALYZER_agent:
# 1. Uses calculate_value_score()
# 2. Analyzes price trends
# 3. Generates purchase recommendations
# 4. Passes analysis to REVIEW_GENERATOR_agent
```

### Phase 4: Opinion Generation
```python
# REVIEW_GENERATOR_agent:
# 1. Uses generate_game_review()
# 2. Creates comprehensive opinion
# 3. Passes draft to QUALITY_ASSURANCE_agent
```

### Phase 5: Quality Control
```python
# QUALITY_ASSURANCE_agent:
# 1. Verifies completeness and logic
# 2. Suggests corrections if needed
# 3. Approves final version
# 4. Passes to USER_PROXY
```

### Phase 6: Results Presentation
```python
# USER_PROXY:
# 1. Formats opinion for user
# 2. Presents results
# 3. Answers additional questions
```

---

## 📁 Project File Structure

```
autogen-dekudeals/
├── deku_tools.py                 # ✅ Existing scraping tools
├── autogen_agents.py            # 🆕 AutoGen agent definitions
├── agent_tools.py               # 🆕 Agent tools
├── conversation_manager.py      # 🆕 Workflow management
├── utils/
│   ├── price_calculator.py      # 🆕 Price calculations
│   ├── review_templates.py      # 🆕 Opinion templates
│   └── data_validator.py        # 🆕 Data validation
├── config/
│   ├── agent_configs.py         # 🆕 Agent configurations
│   └── llm_config.py           # 🆕 LLM model configurations
├── tests/
│   ├── test_agents.py          # 🆕 Agent tests
│   └── test_tools.py           # 🆕 Tool tests
├── examples/
│   ├── basic_analysis.py       # 🆕 Simple analysis example
│   └── batch_analysis.py       # 🆕 Multiple game analysis
├── logs/                       # 🆕 System logs
├── requirements.txt            # ✅ Existing dependencies
└── README.md                   # 🆕 Project documentation
```

---

## 🚀 Implementation Plan (Phases)

### PHASE 1: Foundation (Week 1) ✅ COMPLETED
- [x] Create basic agent structure
- [x] Implement `search_and_scrape_game` tool
- [x] Simple workflow between agents
- [x] Basic tests

### PHASE 2: Price Analysis (Week 2) ✅ COMPLETED  
- [x] Implement `calculate_value_score` (Point 1)
- [x] Value-for-money evaluation algorithms (Point 2)
- [x] Integration with recommendation system (Point 3)
- [x] Price analysis and recommendation tests

**PHASE 2 SUCCESS SUMMARY:**
🎯 **Point 1**: Basic value analysis - `utils/price_calculator.py` + `calculate_value_score()`
🎯 **Point 2**: Advanced algorithms - `utils/advanced_value_algorithms.py` + genre/market/age analysis
🎯 **Point 3**: Recommendation system - `utils/recommendation_engine.py` + personalized recommendations
✅ **5 user profiles** (Bargain Hunter, Quality Seeker, Indie Lover, AAA Gamer, Casual Player)
✅ **3 new tools** registered for AutoGen agents
✅ **Sophisticated scoring**: Genre (40%) + Market Position (40%) + Age (20%)
✅ **Real-world tested**: INSIDE identified as "Hidden Gem" (7.19 zł vs 71.99 zł MSRP, 91 Metacritic)

### PHASE 3: Opinion Generation (Week 3)
- [ ] Implement `generate_game_review`
- [ ] Structural opinion templates
- [ ] Confidence level assessment system
- [ ] Opinion quality tests

### PHASE 4: Quality Control (Week 4)
- [ ] QA Agent with validation rules
- [ ] Automatic completeness checking
- [ ] Feedback loop for corrections
- [ ] Quality metrics

### PHASE 5: Interface and UX (Week 5)
- [ ] Polished user interface
- [ ] Clear result formatting
- [ ] Edge case handling
- [ ] Error messages and recovery

### PHASE 6: Optimization (Week 6)
- [ ] Performance optimization
- [ ] Parallel processing
- [ ] Caching mechanisms
- [ ] API rate limiting

---

## 🎯 Success Metrics

### Opinion Quality
- **Completeness:** 95% of opinions contain all sections
- **Accuracy:** Verification by comparison with expert reviews
- **Usefulness:** User feedback on recommendations

### Performance
- **Analysis time:** < 30 seconds per game
- **Availability:** 99% scraping uptime
- **Scaling:** Ability to analyze 100+ games/day

### User Experience
- **Ease of use:** Simple command → comprehensive analysis
- **Personalization:** Adaptation to user preferences
- **Reliability:** Consistent quality of recommendations

---

## 🎪 Usage Example

```python
# Initialization
conversation_manager = ConversationManager()

# Game analysis
user_query = "Analyze Hollow Knight - is it worth buying?"

# Automatic workflow
result = conversation_manager.analyze_game(user_query)

# Result:
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

## 🎈 Next Steps

### ✅ COMPLETED:
1. **✓ Basic agent structure** (`autogen_agents.py`) - PHASE 1
2. **✓ Tool implementation** (`search_and_scrape_game`) - PHASE 1
3. **✓ Workflow between agents** - PHASE 1
4. **✓ Value analysis system** (`calculate_value_score`) - PHASE 2 Point 1
5. **✓ Advanced algorithms** (`advanced_value_algorithms`) - PHASE 2 Point 2
6. **✓ Recommendation system** (`recommendation_engine`) - PHASE 2 Point 3

### 🎯 NEXT TO DO (PHASE 3):
1. **Implement `generate_game_review`** - comprehensive opinion generation
2. **Structural opinion templates** - standardized review formats
3. **Confidence level assessment system** - recommendation certainty
4. **Opinion quality tests** - validation of generated reviews

**Ready for PHASE 3: Opinion Generation?** 🚀 
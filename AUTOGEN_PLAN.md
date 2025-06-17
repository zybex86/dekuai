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

### PHASE 0: Setup and Planning ✅ COMPLETED
- [x] **AI Assistant instructions creation** - `.cursor/rules/cursor-instructions.md`
- [x] **Initial `deku_tools.py` analysis** - `parse_release_dates()` implementation
- [x] **Plan documentation** - `PLAN_AUTOGEN_DEKUDEALS.md` + `AUTOGEN_PLAN.md`
- [x] **Directory structure and environment configuration**

### PHASE 1: Foundation ✅ COMPLETED
- [x] **Create basic agent structure** - `autogen_agents.py`
  - 5 specialized agents: DATA_COLLECTOR, PRICE_ANALYZER, REVIEW_GENERATOR, QUALITY_ASSURANCE, USER_PROXY
  - LLM configurations with agent-specific temperature (0.0-0.6)
- [x] **Implement `search_and_scrape_game` tool** - `agent_tools.py`
  - Core tools: search, validation, formatting
- [x] **Simple workflow between agents** - `conversation_manager.py`
  - GameAnalysisManager class + workflow orchestration
- [x] **Basic tests** - `tests/test_phase1.py`
  - 11 tests, all passed
- [x] **Documentation** - `README.md` + examples in `examples/basic_analysis.py`

### PHASE 2: Price Analysis ✅ COMPLETED COMPREHENSIVELY

#### **Point 2.1: Basic Value Analysis** ✅ COMPLETED
- [x] **Implement `calculate_value_score`** - `utils/price_calculator.py`
  - `extract_price()`: Multi-format parsing (PLN, USD, etc.)
  - `extract_score()`: Score normalization (0-100 scale)
  - `calculate_discount_percentage()`, `calculate_price_difference()`, `calculate_value_ratio()`
  - `assess_buy_timing()`: 5-tier timing (EXCELLENT→WAIT)
  - `generate_price_recommendation()`: STRONG BUY→SKIP algorithm
- [x] **Integration with agent_tools.py** - `calculate_value_score()` function
- [x] **Real-world testing** - Hollow Knight, Zelda TOTK, Celeste

#### **Point 2.2: Advanced Value Algorithms** ✅ COMPLETED
- [x] **Advanced algorithms** - `utils/advanced_value_algorithms.py`
  - **Genre profiles**: 13 genres with expected hours, replay value, price tolerance
  - **Developer reputation**: Multipliers (Nintendo: 1.3x, Team Cherry: 1.2x, etc.)
  - **Market position matrix**: Quality vs Price (20 categories from "Hidden Gem" to "Scam")
  - **Age factor**: Depreciation based on release year (new: 1.0x → old: 0.8x)
  - **Comprehensive scoring**: Genre (40%) + Market (40%) + Age (20%)
- [x] **Enhanced functionality** - `calculate_advanced_value_analysis()`
  - Insights generation + confidence levels
- [x] **Real-world validation** - INSIDE: "INSTANT BUY - Hidden Gem!" (11.21 score)

#### **Point 2.3: Recommendation System Integration** ✅ COMPLETED  
- [x] **Recommendation system** - `utils/recommendation_engine.py`
  - **UserPreference enum**: 8 user types (BARGAIN_HUNTER→CASUAL_PLAYER)
  - **UserProfile dataclass**: Budget range, preferred genres, minimum scores
  - **RecommendationEngine class**: Personalized scoring (value + user preferences)
  - **5 ready-to-use profiles**: Bargain Hunter, Quality Seeker, Indie Lover, AAA Gamer, Casual Player
  - **GameRecommendation dataclass**: Structured output with reasons, confidence, warnings
- [x] **Agent integration** - all tools registered with decorators
- [x] **Comprehensive testing** - all components tested on real data

**PHASE 2 DETAILED SUCCESS SUMMARY:**
🎯 **3 main components**: price_calculator.py + advanced_value_algorithms.py + recommendation_engine.py
🎯 **5 user profiles** ready to use with different characteristics
🎯 **3 new AutoGen tools**: `calculate_value_score()`, `calculate_advanced_value_analysis()`, `get_personalized_recommendation()`
🎯 **Sophisticated scoring**: Multi-dimensional analysis with confidence levels
🎯 **Real-world proven**: INSIDE (Hidden Gem 7.19 zł vs 71.99 zł), Baten Kaitos (SKIP 3.56 score)
✅ **Type safety**: Full type hints + error handling + logging
✅ **AutoGen integration**: All tools registered with proper decorators

### PHASE 3: Opinion Generation (Week 3) 🚧 IN PROGRESS
- [ ] **Implement `generate_game_review`** - comprehensive opinion generation
  - Structural opinions with ratings and argumentation
  - Target audience identification
  - Strengths/weaknesses analysis
- [ ] **Structural opinion templates** - standardized review formats
  - Opinion templates for different genres
  - Adaptive formatting based on data availability
- [ ] **Confidence level assessment system** - recommendation certainty
  - Confidence scoring algorithm
  - Data completeness impact on confidence
- [ ] **Opinion quality tests** - validation of generated reviews
  - Automated quality checks
  - Comparison with expert reviews

### PHASE 4: Quality Control (Week 4)
- [ ] **QA Agent with validation rules** - automatic verification
  - Completeness validation
  - Logic consistency checks
  - Opinion objectivity assessment
- [ ] **Automatic completeness checking** - data validation
  - Required field checking
  - Score threshold validation
  - Price data completeness
- [ ] **Feedback loop for corrections** - iterative improvement
  - Correction suggestion system
  - Quality improvement tracking
- [ ] **Quality metrics** - quality measurement
  - Opinion completeness metrics
  - User satisfaction tracking

### PHASE 5: Interface and UX (Week 5)
- [ ] **Polished user interface** - user experience enhancement
  - CLI interface improvements
  - Result presentation formatting
  - Interactive elements
- [ ] **Clear result formatting** - output optimization
  - Structured opinion display
  - Color-coded recommendations
  - Summary sections
- [ ] **Edge case handling** - error management
  - Game not found scenarios
  - Missing data handling
  - API timeout management
- [ ] **Error messages and recovery** - user guidance
  - Helpful error descriptions
  - Recovery suggestions
  - Fallback options

### PHASE 6: Optimization (Week 6)
- [ ] **Performance optimization** - speed improvements
  - Parallel agent execution
  - Optimized data processing
  - Memory usage optimization
- [ ] **Parallel processing** - concurrency
  - Multiple game analysis
  - Batch processing capabilities
  - Background task management
- [ ] **Caching mechanisms** - data persistence
  - Game data caching
  - Analysis result caching
  - Smart cache invalidation
- [ ] **API rate limiting** - responsible usage
  - Request throttling
  - Retry mechanisms
  - API quota management

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

### ✅ COMPLETED COMPREHENSIVELY:
1. **✓ PHASE 0: Setup and Planning** - AI instructions, documentation, configuration
2. **✓ PHASE 1: Foundation** - AutoGen agents, core tools, workflow, testing
3. **✓ PHASE 2.1: Basic Value Analysis** - `price_calculator.py`, fundamental value calculations
4. **✓ PHASE 2.2: Advanced Algorithms** - `advanced_value_algorithms.py`, genre/market/age analysis
5. **✓ PHASE 2.3: Recommendation Engine** - `recommendation_engine.py`, personalized recommendations
6. **✓ Complete tool integration** - all tools registered with AutoGen decorators
7. **✓ Real-world testing** - validation on actual DekuDeals data

### 🚧 CURRENT STATUS:
**PHASE 2 COMPLETED 100%** - Complete value analysis and recommendation system ready for use

### 🎯 NEXT TO DO (PHASE 3 - OPINION GENERATION):
1. **🔥 PRIORITY: `generate_game_review` implementation**
   - Comprehensive opinion generation based on all collected data
   - Structural output with ratings, strengths, weaknesses, target audience
   - Integration with existing value analysis and recommendation systems

2. **Review Templates & Formatting**
   - Opinion templates for different game genres
   - Adaptive formatting based on data availability
   - Professional presentation layer

3. **Quality Assurance Integration**
   - Confidence level assessment for generated opinions
   - Automated validation checks
   - Consistency verification with existing tools

4. **Testing & Validation**
   - End-to-end testing of entire pipeline
   - Comparison with expert reviews
   - User acceptance validation

**Status: Ready to begin PHASE 3! Solid foundation and value analysis tools ready.** 🚀

### 📊 CURRENT SYSTEM CAPABILITIES:
✅ **Data Collection**: `search_and_scrape_game()` fully functional  
✅ **Price Analysis**: Basic + advanced value analysis  
✅ **Personalization**: 5 user profiles + recommendation engine  
✅ **Agent Infrastructure**: 5 specialized AutoGen agents  
✅ **Testing**: All components tested on real data  

**Next milestone: Comprehensive opinion generation at professional game review level** 🎮 
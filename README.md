# 🎮 AutoGen DekuDeals Game Analysis

An intelligent multi-agent system using AutoGen to analyze games from DekuDeals.com and generate comprehensive purchase recommendations.

## 📋 Project Overview

This project implements a sophisticated AI-powered game analysis system that:
- **Scrapes game data** from DekuDeals.com
- **Analyzes pricing and value** using multiple criteria
- **Generates detailed reviews** and recommendations
- **Quality assures** all outputs for reliability

## 🏗️ Architecture

The system uses **5 specialized AutoGen agents** working in coordination:

1. **DATA_COLLECTOR_agent** - Gathers game information from DekuDeals
2. **PRICE_ANALYZER_agent** - Analyzes pricing and value propositions  
3. **REVIEW_GENERATOR_agent** - Creates comprehensive game reviews
4. **QUALITY_ASSURANCE_agent** - Validates analysis quality
5. **USER_PROXY** - Manages user interaction and workflow

## 🚀 Current Status: Phase 2 Complete ✅

### What's Implemented:

#### ✅ Phase 0 & 1: Foundation (COMPLETE)
- **AutoGen Agents**: All 5 agents defined with proper system messages
- **Agent Tools**: Data collection and validation utilities
- **Configuration**: LLM configs with agent-specific temperature settings (0.0-0.6)
- **Conversation Manager**: Complete workflow orchestration system
- **Testing**: Comprehensive test suite (11 tests, all passing)

#### ✅ Phase 2.1: Basic Value Analysis (COMPLETE)
- **Price Calculator**: `utils/price_calculator.py` with multi-format parsing
- **Value Scoring**: Advanced algorithms for price-to-value assessment
- **Buy Timing**: 5-tier timing recommendations (EXCELLENT→WAIT)
- **Price Recommendations**: STRONG BUY→SKIP recommendation engine

#### ✅ Phase 2.2: Advanced Algorithms (COMPLETE)
- **Genre Profiles**: 13 game genres with expected hours, replay value, price tolerance
- **Developer Reputation**: Quality multipliers (Nintendo: 1.3x, Team Cherry: 1.2x, etc.)
- **Market Position Matrix**: 20 categories from "Hidden Gem" to "Scam"
- **Age Depreciation**: Release year impact on value (new: 1.0x → old: 0.8x)
- **Sophisticated Scoring**: Genre (40%) + Market (40%) + Age (20%) weighting

#### ✅ Phase 2.3: Recommendation Engine (COMPLETE)
- **User Profiles**: 5 ready-to-use personas (Bargain Hunter, Quality Seeker, etc.)
- **Personalized Scoring**: User preference integration with value analysis
- **Recommendation Classes**: Structured output with confidence levels and warnings
- **Real-world Tested**: Validated on actual DekuDeals data (INSIDE, Baten Kaitos, etc.)

#### ✅ Advanced Features
- **Multi-dimensional Analysis**: Comprehensive scoring combining multiple factors
- **Type Safety**: Full type hints + error handling + logging throughout
- **AutoGen Integration**: All tools properly registered with decorators
- **Production Ready**: Robust error management and data validation

## 📁 Project Structure

```
autogen-dekudeals/
├── 🎯 Core Files
│   ├── autogen_agents.py         # AutoGen agent definitions
│   ├── agent_tools.py           # Tools for agents (scraping, validation, analysis)
│   ├── conversation_manager.py  # Workflow orchestration
│   └── deku_tools.py           # DekuDeals scraping utilities
│
├── ⚙️ Configuration
│   └── config/
│       └── llm_config.py       # LLM model configurations
│
├── 🧠 Analysis Engine
│   └── utils/
│       ├── price_calculator.py        # Basic value analysis
│       ├── advanced_value_algorithms.py  # Genre/market/age analysis  
│       └── recommendation_engine.py   # Personalized recommendations
│
├── 📚 Examples & Tests  
│   ├── examples/
│   │   ├── basic_analysis.py          # Basic usage example
│   │   ├── test_value_analysis.py     # Value analysis demo
│   │   ├── test_advanced_value.py     # Advanced algorithms demo
│   │   ├── test_recommendation_system.py  # Recommendation demo
│   │   └── test_*.py                  # Various feature demos
│   └── tests/
│       └── test_phase1.py             # Phase 1 test suite (11 tests)
│
├── 🎮 Demo Applications
│   ├── run_demo.py              # Comprehensive demo system
│   └── simple_demo.py          # Streamlined demo interface
│
└── 📖 Documentation
    ├── AUTOGEN_PLAN.md         # Comprehensive project plan (English)
    ├── PLAN_AUTOGEN_DEKUDEALS.md  # Project plan (Polish)
    ├── .cursor/rules/cursor-instructions.md  # AI development guidelines
    └── README.md               # This file
```

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Test Installation
```bash
# Run comprehensive test suite (11 tests)
python tests/test_phase1.py

# Test data collection + value analysis (no API key needed)
python examples/basic_analysis.py

# Test advanced features
python examples/test_value_analysis.py
```

## 🎯 Usage Examples

### Quick Game Analysis
```python
from conversation_manager import analyze_game_quick

# Quick analysis (data + basic price assessment)
result = analyze_game_quick("Hollow Knight")
print(result)
```

### Comprehensive Analysis  
```python
from conversation_manager import analyze_game_comprehensive

# Full multi-agent analysis with value assessment
result = analyze_game_comprehensive("Celeste")
print(result)
```

### Advanced Value Analysis
```python
from agent_tools import calculate_advanced_value_analysis

# Sophisticated multi-dimensional analysis
result = calculate_advanced_value_analysis("INSIDE")
print(f"Market Position: {result['market_position']}")
print(f"Value Score: {result['overall_score']}")
print(f"Recommendation: {result['recommendation']}")
```

### Personalized Recommendations
```python
from agent_tools import get_personalized_recommendation

# Get recommendation for specific user type
result = get_personalized_recommendation("Hollow Knight", "INDIE_LOVER")
print(f"Personal Score: {result['personalized_score']}")
print(f"Reasons: {result['reasons']}")
print(f"Confidence: {result['confidence']}")
```

### Direct Data Collection
```python
from agent_tools import search_and_scrape_game

# Just scrape game data
game_data = search_and_scrape_game("The Legend of Zelda: Tears of the Kingdom")
print(game_data)
```

## 🧪 Running Tests

```bash
# Run comprehensive Phase 1 test suite (11 tests)
python tests/test_phase1.py

# Run specific test classes
python -m unittest tests.test_phase1.TestPhase1BasicFunctionality
python -m unittest tests.test_phase1.TestPhase1Integration

# Test individual components with real data
python examples/test_value_analysis.py          # Basic value analysis
python examples/test_advanced_value.py         # Advanced algorithms
python examples/test_recommendation_system.py  # Personalized recommendations

# Run comprehensive demo system
python run_demo.py --demo-all                  # Full demonstration
python simple_demo.py --demo-all               # Streamlined demo
```

## 📊 Key Capabilities (Phases 0-2 Complete)

### ✅ Data Collection & Processing
- **Multi-field Extraction**: Title, price, ratings, genres, developer, platforms
- **Structured Release Dates**: Parsed platform-specific release information  
- **Data Quality Scoring**: Automatic completeness assessment (95%+ accuracy)
- **Multi-format Parsing**: PLN, USD, percentage discounts, various score scales

### ✅ Advanced Value Analysis
- **Price Intelligence**: Multi-tier pricing recommendations (STRONG BUY→SKIP)
- **Genre Profiling**: 13 game genres with expected hours, replay value, price tolerance
- **Developer Reputation**: Quality multipliers for 20+ studios
- **Market Positioning**: 20 categories from "Hidden Gem" to "Scam"
- **Temporal Analysis**: Age-based depreciation modeling

### ✅ Personalized Recommendations  
- **User Profiles**: 5 distinct personas (Bargain Hunter, Quality Seeker, Indie Lover, AAA Gamer, Casual Player)
- **Preference Integration**: Budget ranges, genre preferences, minimum score thresholds
- **Confidence Scoring**: Algorithm certainty assessment for recommendations
- **Warning System**: Alerts for potential user preference mismatches

### ✅ Agent System Architecture
- **Specialized Roles**: 5 AutoGen agents with distinct expertise areas
- **Tool Integration**: 8+ registered tools with proper AutoGen decorators
- **Workflow Management**: Orchestrated conversation flow between agents
- **Quality Control**: Built-in validation and quality assurance at each step

### ✅ Production Engineering
- **Type Safety**: Full type hints + dataclass structures throughout
- **Error Handling**: Comprehensive try-catch with meaningful messages
- **Logging**: Structured logging for debugging and monitoring  
- **Testing**: Real-world validation on DekuDeals data
- **Configuration**: Centralized LLM + agent configuration management

## 🎪 Example Output

### Basic Game Data
```json
{
  "success": true,
  "title": "Hollow Knight",
  "current_eshop_price": "$14.99",
  "MSRP": "$14.99", 
  "metacritic_score": "90",
  "genres": ["Metroidvania", "Action"],
  "developer": "Team Cherry",
  "release_dates_parsed": {
    "Switch": "June 12, 2018",
    "PS4": "September 25, 2018"
  },
  "data_quality_score": 95.0
}
```

### Advanced Value Analysis Output
```json
{
  "success": true,
  "game_title": "INSIDE",
  "market_position": "Hidden Gem",
  "overall_score": 11.21,
  "recommendation": "INSTANT BUY",
  "confidence": "HIGH",
  "insights": [
    "Exceptional value at 90% discount",
    "Critical acclaim with 91 Metacritic score",
    "Perfect for puzzle/adventure fans"
  ],
  "genre_analysis": {
    "matched_genre": "Adventure",
    "expected_hours": 4,
    "replay_value": 1.1
  },
  "developer_bonus": {
    "studio": "Playdead",
    "reputation_multiplier": 1.15
  }
}
```

### Personalized Recommendation Output  
```json
{
  "success": true,
  "user_profile": "INDIE_LOVER",
  "personalized_score": 9.2,
  "confidence": "HIGH",
  "reasons": [
    "Perfect match for indie game preferences",
    "Exceptional value at current price",
    "High critical acclaim (90+ scores)"
  ],
  "warnings": [],
  "final_recommendation": "STRONG BUY"
}
```

## 🚀 Next Steps: Phase 3 - Opinion Generation

**Current Focus:**
- [ ] Comprehensive game review generation
- [ ] Structured opinion templates for different genres
- [ ] Target audience identification algorithms
- [ ] Strengths/weaknesses analysis automation
- [ ] Professional-level review formatting

**Phase 3 Goals:**
Transform the sophisticated value analysis into human-readable, comprehensive game reviews comparable to professional gaming journalism.

## 🤝 Contributing

This project follows a structured phase-based development approach. Currently **Phase 2 complete** with sophisticated value analysis and recommendation systems operational.

### Development Guidelines:
1. **Follow the AI Instructions** in `.cursor/rules/cursor-instructions.md`
2. **Test Everything** - Add tests for new functionality (currently 11 tests passing)
3. **Document Changes** - Update README and plans as needed
4. **Incremental Development** - Build on existing phase foundations
5. **Real-world Validation** - Test new features on actual DekuDeals data

## 📝 License

This project is for educational and personal use. DekuDeals.com scraping should respect their robots.txt and terms of service.

## 🎖️ Acknowledgments

- **AutoGen Framework** - Microsoft's multi-agent conversation framework
- **DekuDeals.com** - Nintendo game deals and pricing data
- **BeautifulSoup** - HTML parsing and web scraping

---

## 🎯 Quick Start

**Want to try it right now?**

```bash
# 1. Clone and install
pip install -r requirements.txt

# 2. Test without API key (scraping + value analysis)
python examples/basic_analysis.py

# 3. Set API key for full AI analysis
export OPENAI_API_KEY="your_key"
python examples/basic_analysis.py

# 4. Try advanced features
python examples/test_value_analysis.py
python examples/test_advanced_value.py
python examples/test_recommendation_system.py
```

**✨ Phase 2 complete with sophisticated value analysis and personalized recommendations ready!** 
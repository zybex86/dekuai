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

## 🚀 Current Status: Phase 1 Complete ✅

### What's Implemented:

#### ✅ Core Infrastructure
- **AutoGen Agents**: All 5 agents defined with proper system messages
- **Agent Tools**: Data collection and validation utilities
- **Configuration**: LLM configs with appropriate temperature settings
- **Conversation Manager**: Workflow orchestration system

#### ✅ Key Features
- **Game Data Scraping**: Enhanced DekuDeals scraping with structured output
- **Data Validation**: Completeness scoring and missing field detection  
- **Error Handling**: Robust error management throughout the pipeline
- **Logging**: Comprehensive logging for debugging and monitoring

#### ✅ Testing & Examples
- **Unit Tests**: Comprehensive test suite for Phase 1 functionality
- **Integration Tests**: End-to-end workflow validation
- **Basic Example**: Ready-to-run analysis example
- **Documentation**: Clear setup and usage instructions

## 📁 Project Structure

```
autogen-dekudeals/
├── 🎯 Core Files
│   ├── autogen_agents.py         # AutoGen agent definitions
│   ├── agent_tools.py           # Tools for agents (scraping, validation)
│   ├── conversation_manager.py  # Workflow orchestration
│   └── deku_tools.py           # DekuDeals scraping utilities
│
├── ⚙️ Configuration
│   └── config/
│       └── llm_config.py       # LLM model configurations
│
├── 📚 Examples & Tests  
│   ├── examples/
│   │   └── basic_analysis.py   # Basic usage example
│   └── tests/
│       └── test_phase1.py      # Phase 1 test suite
│
└── 📖 Documentation
    ├── AUTOGEN_PLAN.md         # Comprehensive project plan (English)
    ├── PLAN_AUTOGEN_DEKUDEALS.md  # Project plan (Polish)
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
# Run Phase 1 tests
python tests/test_phase1.py

# Test data collection only (no API key needed)
python examples/basic_analysis.py
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

# Full multi-agent analysis
result = analyze_game_comprehensive("Celeste")
print(result)
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
# Run all Phase 1 tests
python tests/test_phase1.py

# Run specific test classes
python -m unittest tests.test_phase1.TestPhase1BasicFunctionality
python -m unittest tests.test_phase1.TestPhase1Integration
```

## 📊 Key Capabilities (Phase 1)

### ✅ Data Collection
- **Multi-field Extraction**: Title, price, ratings, genres, developer, platforms
- **Structured Release Dates**: Parsed platform-specific release information
- **Data Quality Scoring**: Automatic completeness assessment
- **Error Recovery**: Graceful handling of missing or invalid data

### ✅ Agent System
- **Specialized Roles**: Each agent has a specific function and expertise
- **Tool Integration**: Agents can call scraping and analysis functions
- **Workflow Management**: Orchestrated conversation flow between agents
- **Quality Control**: Built-in validation and quality assurance

### ✅ Robust Engineering
- **Type Safety**: Full type hints throughout the codebase
- **Error Handling**: Try-catch blocks with meaningful error messages
- **Logging**: Structured logging for debugging and monitoring
- **Configuration**: Centralized LLM configuration management

## 🎪 Example Output

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

## 🚀 Next Steps: Phase 2

**Upcoming Features:**
- [ ] Advanced price analysis algorithms
- [ ] Value-for-money scoring system
- [ ] Historical price trend analysis
- [ ] Purchase timing recommendations
- [ ] Enhanced error recovery

## 🤝 Contributing

This project follows a structured phase-based development approach. Currently in **Phase 1** with basic infrastructure complete.

### Development Guidelines:
1. **Follow the AI Instructions** in `.cursor/rules/cursor-instructions.md`
2. **Test Everything** - Add tests for new functionality
3. **Document Changes** - Update README and plans as needed
4. **Incremental Development** - Build on existing phase foundations

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

# 2. Test without API key (scraping only)
python examples/basic_analysis.py

# 3. Set API key for full AI analysis
export OPENAI_API_KEY="your_key"
python examples/basic_analysis.py
```

**✨ Phase 1 is complete and ready for Phase 2 development!** 
"""
AutoGen Agents for DekuDeals Game Analysis
Agenci AutoGen do analizy gier z DekuDeals
"""

import autogen
from typing import Dict, Any, Optional
from config.llm_config import (
    get_data_collector_config,
    get_price_analyzer_config,
    get_review_generator_config,
    get_quality_assurance_config,
    get_user_proxy_config,
    validate_api_key,
)
from agent_tools import (
    search_and_scrape_game,
    validate_game_data,
    format_game_summary,
    extract_key_metrics,
)

# Validate API key before creating agents
if not validate_api_key():
    raise ValueError(
        "OpenAI API key is required. Set OPENAI_API_KEY environment variable."
    )

# Agent 1: DATA_COLLECTOR_agent
data_collector = autogen.AssistantAgent(
    name="DATA_COLLECTOR_agent",
    system_message="""You are an expert at collecting game data from DekuDeals.com.

Your tasks:
- Search for the game specified by the user
- Retrieve all available game data using the search_and_scrape_game tool
- Validate data completeness and quality
- Provide a clear, structured report with collected information
- Identify any missing or incomplete data fields

Always use the search_and_scrape_game function to get game data.
Format your response clearly and pass complete data to the next agent.

Terminate when: You obtain complete game data or determine that the game doesn't exist.
Reply 'TERMINATE' when your task is complete.""",
    llm_config=get_data_collector_config(),
)

# Agent 2: PRICE_ANALYZER_agent
price_analyzer = autogen.AssistantAgent(
    name="PRICE_ANALYZER_agent",
    system_message="""You are a game price and value analyst.

Your tasks:
- Analyze price data from the game information received
- Assess price-to-value ratio based on available scores and pricing
- Compare current price with MSRP and historical data if available
- Determine if it's a good time to buy based on price trends
- Generate clear pricing recommendations (BUY/WAIT/SKIP)

Focus on:
- Value for money assessment
- Price comparison analysis
- Purchase timing recommendations
- Deal quality evaluation

Terminate when: You provide complete price analysis with clear recommendations.
Reply 'TERMINATE' when your analysis is complete.""",
    llm_config=get_price_analyzer_config(),
)

# Agent 3: REVIEW_GENERATOR_agent
review_generator = autogen.AssistantAgent(
    name="REVIEW_GENERATOR_agent",
    system_message="""You are a game critic specializing in objective reviews.

Your tasks:
- Analyze all collected game data comprehensively
- Consider Metacritic and OpenCritic scores in your evaluation
- Evaluate genres and determine target audience
- Generate comprehensive, objective opinion based on available data
- Provide clear "Buy/Wait/Skip" recommendations with reasoning

Your review should include:
- Overall assessment based on available data
- Strengths and potential weaknesses
- Target audience identification  
- Genre-specific analysis
- Final verdict with confidence level

Be objective and base your opinion on data, not speculation.

Terminate when: You create a complete opinion with argumentation and recommendation.
Reply 'TERMINATE' when your review is complete.""",
    llm_config=get_review_generator_config(),
)

# Agent 4: QUALITY_ASSURANCE_agent
quality_assurance = autogen.AssistantAgent(
    name="QUALITY_ASSURANCE_agent",
    system_message="""You are a quality controller for game analyses.

Your tasks:
- Review all analyses from previous agents for completeness
- Verify logical consistency of arguments and recommendations  
- Ensure opinion is objective and based on available data
- Check that recommendations align with the evidence presented
- Suggest specific corrections if needed

Quality checkpoints:
- Data completeness verification
- Logical consistency of price analysis
- Objectivity of review and recommendations
- Clarity and usefulness of final assessment

Terminate when: You confirm high quality of final analysis or suggest specific improvements.
Reply 'TERMINATE' when quality check is complete.""",
    llm_config=get_quality_assurance_config(),
)

# Agent 5: USER_PROXY (Human Interface)
user_proxy = autogen.UserProxyAgent(
    name="USER_PROXY",
    system_message="""You are the interface between users and the game analysis team.

Your tasks:
- Accept user queries about games
- Coordinate the analyst team workflow
- Present results in a clear, readable format
- Handle follow-up questions from users

You can execute functions and coordinate the conversation flow.""",
    human_input_mode="NEVER",  # Automated for now
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "logs", "use_docker": False},
)


# Register tools for agents
@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description="Search for a game on DekuDeals and retrieve all available data - Input: game_name (str) - Output: Dict with complete game data"
)
def get_game_data(game_name: str) -> Dict[str, Any]:
    """Wrapper function for search_and_scrape_game tool"""
    return search_and_scrape_game(game_name)


@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description="Validate completeness of game data - Input: game_data (dict) - Output: validation report"
)
def check_data_quality(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for validate_game_data tool"""
    return validate_game_data(game_data)


@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description="Extract key metrics from game data for analysis - Input: game_data (dict) - Output: metrics summary"
)
def get_analysis_metrics(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for extract_key_metrics tool"""
    return extract_key_metrics(game_data)


def create_analysis_team() -> list:
    """
    Tworzy zespół agentów do analizy gier.

    Returns:
        list: Lista agentów w kolejności workflow
    """
    return [
        user_proxy,
        data_collector,
        price_analyzer,
        review_generator,
        quality_assurance,
    ]


def get_agent_by_name(name: str) -> Optional[autogen.Agent]:
    """
    Pobiera agenta po nazwie.

    Args:
        name (str): Nazwa agenta

    Returns:
        Optional[autogen.Agent]: Agent lub None jeśli nie znaleziono
    """
    agents = {
        "DATA_COLLECTOR_agent": data_collector,
        "PRICE_ANALYZER_agent": price_analyzer,
        "REVIEW_GENERATOR_agent": review_generator,
        "QUALITY_ASSURANCE_agent": quality_assurance,
        "USER_PROXY": user_proxy,
    }
    return agents.get(name)

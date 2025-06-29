"""
AutoGen Agents for DekuDeals Game Analysis
Agenci AutoGen do analizy gier z DekuDeals
"""

import autogen
from typing import Dict, Any, Optional, List
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
    calculate_value_score,
    calculate_advanced_value_analysis,
    generate_personalized_recommendations,
    compare_games_for_user,
    get_recommendation_insights,
    # Phase 3 tools - Review Generation
    generate_comprehensive_game_review,
    generate_quick_game_opinion,
    compare_games_with_reviews,
    # Category scraping tools for diverse testing
    scrape_dekudeals_category,
    get_games_from_popular_categories,
    get_random_game_sample,
    # Phase 3 Point 2 - Opinion Adaptations
    adapt_review_for_context,
    create_multi_platform_opinions,
    get_available_adaptation_options,
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
    description=(
        "Search for a game on DekuDeals and retrieve all available data - "
        "Input: game_name (str) - Output: Dict with complete game data"
    )
)
def get_game_data(game_name: str) -> Dict[str, Any]:
    """Wrapper function for search_and_scrape_game tool"""
    return search_and_scrape_game(game_name)


@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description=(
        "Validate completeness of game data - "
        "Input: game_data (dict) - Output: validation report"
    )
)
def check_data_quality(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for validate_game_data tool"""
    return validate_game_data(game_data)


@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description=(
        "Extract key metrics from game data for analysis - "
        "Input: game_data (dict) - Output: metrics summary"
    )
)
def get_analysis_metrics(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for extract_key_metrics tool"""
    return extract_key_metrics(game_data)


@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description=(
        "Calculate value for money based on price and ratings - "
        "Input: game_data (Dict) - Output: Dict with comprehensive value analysis"
    )
)
def analyze_game_value(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for calculate_value_score tool"""
    return calculate_value_score(game_data)


@user_proxy.register_for_execution()
@price_analyzer.register_for_llm(
    description=(
        "Perform advanced comprehensive value analysis with genre factors, "
        "market position, and age considerations - "
        "Input: game_data (Dict) - Output: Dict with advanced analysis"
    )
)
def analyze_advanced_value(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for calculate_advanced_value_analysis tool (Point 2 of Phase 2)"""
    return calculate_advanced_value_analysis(game_data)


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Generate personalized game recommendations based on user preferences - "
        "Input: games_list (List[str]), user_preference (str), max_recommendations (int) - "
        "Output: Dict with personalized recommendations"
    )
)
def get_personalized_recommendations(
    games_list: List[str],
    user_preference: str = "bargain_hunter",
    max_recommendations: int = 5,
) -> Dict[str, Any]:
    """Wrapper function for generate_personalized_recommendations tool (Point 3 of Phase 2)"""
    return generate_personalized_recommendations(
        games_list, user_preference, max_recommendations
    )


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Compare games for specific user preferences and provide ranked recommendations - "
        "Input: game_names (List[str]), user_preference (str) - "
        "Output: Dict with comparison and ranking"
    )
)
def compare_games_by_preference(
    game_names: List[str], user_preference: str = "bargain_hunter"
) -> Dict[str, Any]:
    """Wrapper function for compare_games_for_user tool (Point 3 of Phase 2)"""
    return compare_games_for_user(game_names, user_preference)


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Analyze how a game fits different user preference types - "
        "Input: game_name (str), user_preferences (List[str]) - "
        "Output: Dict with multi-user analysis"
    )
)
def analyze_game_for_users(
    game_name: str, user_preferences: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Wrapper function for get_recommendation_insights tool (Point 3 of Phase 2)"""
    return get_recommendation_insights(game_name, user_preferences)


# Phase 3 Point 1: Comprehensive Review Generation Tools
@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Generate comprehensive game review combining all analyses from Phase 1, 2, and 3 "
        "with detailed ratings and recommendations - Input: game_name (str), "
        "include_recommendations (bool) - Output: Dict with complete review including "
        "rating, verdict, strengths, weaknesses"
    )
)
def create_comprehensive_review(
    game_name: str, include_recommendations: bool = True
) -> Dict[str, Any]:
    """Wrapper function for generate_comprehensive_game_review tool (Phase 3 Point 1)"""
    return generate_comprehensive_game_review(game_name, include_recommendations)


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Generate quick game opinion with essential analysis for fast assessment - "
        "Input: game_name (str) - Output: Dict with summarized opinion including "
        "rating, recommendation, and key points"
    )
)
def create_quick_opinion(game_name: str) -> Dict[str, Any]:
    """Wrapper function for generate_quick_game_opinion tool (Phase 3 Point 1)"""
    return generate_quick_game_opinion(game_name)


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Compare multiple games with full review analysis and detailed ranking - "
        "Input: game_names (List[str]), comparison_focus (str) - "
        "Output: Dict with detailed comparison including winner, ranking, and explanations"
    )
)
def compare_games_with_full_reviews(
    game_names: List[str], comparison_focus: str = "overall"
) -> Dict[str, Any]:
    """Wrapper function for compare_games_with_reviews tool (Phase 3 Point 1)"""
    return compare_games_with_reviews(game_names, comparison_focus)


# Category Scraping Tools for Diverse Testing
@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description=(
        "Scrape games from specific DekuDeals category pages for diverse testing data - "
        "Input: category (str), max_games (int), include_details (bool) - "
        "Output: Dict with games list and metadata"
    )
)
def get_games_from_category(
    category: str, max_games: int = 20, include_details: bool = False
) -> Dict[str, Any]:
    """Wrapper function for scrape_dekudeals_category tool"""
    return scrape_dekudeals_category(category, max_games, include_details)


@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description=(
        "Get games from multiple popular DekuDeals categories for comprehensive testing - "
        "Input: max_games_per_category (int), categories (List[str]) - "
        "Output: Dict with categorized games"
    )
)
def collect_games_from_categories(
    max_games_per_category: int = 10, categories: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Wrapper function for get_games_from_popular_categories tool"""
    return get_games_from_popular_categories(max_games_per_category, categories)


@user_proxy.register_for_execution()
@data_collector.register_for_llm(
    description=(
        "Get random sample of games from DekuDeals for unbiased testing - "
        "Input: sample_size (int), category_preference (str) - "
        "Output: Dict with random game selection"
    )
)
def get_random_games_sample(
    sample_size: int = 5, category_preference: str = "mixed"
) -> Dict[str, Any]:
    """Wrapper function for get_random_game_sample tool"""
    return get_random_game_sample(sample_size, category_preference)


# Phase 3 Point 2: Opinion Adaptation Tools
@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Adapt game review to specific communication context and audience - "
        "Input: game_name (str), style (str), format_type (str), audience (str), "
        "platform (str), max_length (int) - Output: Dict with adapted review content"
    )
)
def adapt_game_review_style(
    game_name: str,
    style: str = "casual",
    format_type: str = "summary",
    audience: str = "general_public",
    platform: str = "website",
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """Wrapper function for adapt_review_for_context tool (Phase 3 Point 2)"""
    return adapt_review_for_context(
        game_name, style, format_type, audience, platform, max_length
    )


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Create game opinions for multiple platforms simultaneously with "
        "platform-specific adaptations - Input: game_name (str), platforms (List[str]) - "
        "Output: Dict with platform-specific review adaptations"
    )
)
def create_platform_specific_reviews(
    game_name: str, platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Wrapper function for create_multi_platform_opinions tool (Phase 3 Point 2)"""
    return create_multi_platform_opinions(game_name, platforms)


@user_proxy.register_for_execution()
@review_generator.register_for_llm(
    description=(
        "Get available adaptation options for review customization - "
        "Input: none - Output: Dict with all available styles, formats, "
        "audiences, and platforms"
    )
)
def get_adaptation_options() -> Dict[str, Any]:
    """Wrapper function for get_available_adaptation_options tool (Phase 3 Point 2)"""
    return get_available_adaptation_options()


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

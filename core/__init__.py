"""
Core Business Logic for AutoGen DekuDeals
Główna logika biznesowa dla AutoGen DekuDeals

This package contains the reorganized core functionality split by phases:
- data_collection: Phase 1 - Data scraping and validation ✅ COMPLETED
- recommendations: Phase 2 Point 3 - Personalized recommendations ✅ COMPLETED
- value_analysis: Phase 2 - Price and value analysis (TODO)
- review_generation: Phase 3 - Review and opinion generation (TODO)
- opinion_adaptation: Phase 3 - Style and format adaptations (TODO)
- quality_control: Phase 4 - Quality validation and control (TODO)
"""

# Re-export main functions for backward compatibility
# Step 1: Only data_collection module implemented so far
from .data_collection import (
    search_and_scrape_game,
    validate_game_data,
    format_game_summary,
    extract_key_metrics,
    scrape_dekudeals_category,
    get_games_from_popular_categories,
    get_random_game_sample,
)

# Step 2: Recommendation system integration (STEP 2 COMPLETED)
from .recommendations import (
    generate_personalized_recommendations,
    compare_games_for_user,
    get_recommendation_insights,
    get_available_user_preferences,
    get_user_preference_descriptions,
)

# TODO: Implement in subsequent steps
# from .value_analysis import (
#     calculate_value_score,
#     calculate_advanced_value_analysis,
# )
#
# from .review_generation import (
#     generate_comprehensive_game_review,
#     generate_quick_game_opinion,
#     compare_games_with_reviews,
# )
#
# from .opinion_adaptation import (
#     adapt_review_for_context,
#     create_multi_platform_opinions,
#     get_available_adaptation_options,
# )
#
# from .quality_control import (
#     perform_quality_validation,
# )

__all__ = [
    # Phase 1 - Data Collection (STEP 1 COMPLETED)
    "search_and_scrape_game",
    "validate_game_data",
    "format_game_summary",
    "extract_key_metrics",
    "scrape_dekudeals_category",
    "get_games_from_popular_categories",
    "get_random_game_sample",
    # Phase 2 - Recommendations (STEP 2 COMPLETED)
    "generate_personalized_recommendations",
    "compare_games_for_user",
    "get_recommendation_insights",
    "get_available_user_preferences",
    "get_user_preference_descriptions",
    # TODO: Add in subsequent steps
    # Phase 2 - Value Analysis
    # 'calculate_value_score',
    # 'calculate_advanced_value_analysis',
    #
    # Phase 3 - Review Generation
    # 'generate_comprehensive_game_review',
    # 'generate_quick_game_opinion',
    # 'compare_games_with_reviews',
    #
    # Phase 3 - Opinion Adaptation
    # 'adapt_review_for_context',
    # 'create_multi_platform_opinions',
    # 'get_available_adaptation_options',
    #
    # Phase 4 - Quality Control
    # 'perform_quality_validation',
]

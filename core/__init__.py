"""
Core Business Logic for AutoGen DekuDeals
Główna logika biznesowa dla AutoGen DekuDeals

This package contains the reorganized core functionality split by phases:
- data_collection: Phase 1 - Data scraping and validation ✅ COMPLETED
- recommendations: Phase 2 Point 3 - Personalized recommendations ✅ COMPLETED
- value_analysis: Phase 2 Points 1-2 - Price and value analysis ✅ COMPLETED
- review_generation: Phase 3 Point 1 - Review and opinion generation ✅ COMPLETED
- opinion_adaptation: Phase 3 Point 2 - Style and format adaptations ✅ COMPLETED
- quality_control: Phase 4 - Quality validation and control ✅ COMPLETED

🎉 ALL CORE INTEGRATIONS COMPLETE - Full AutoGen DekuDeals functionality available through core package!
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

# Step 3: Value analysis integration (STEP 3 COMPLETED)
from .value_analysis import (
    calculate_value_score,
    calculate_advanced_value_analysis,
    get_value_analysis_summary,
)

# Step 4: Review generation integration (STEP 4 COMPLETED)
from .review_generation import (
    generate_comprehensive_game_review,
    generate_quick_game_opinion,
    compare_games_with_reviews,
    get_review_generation_capabilities,
)

# Step 5: Opinion adaptation integration (STEP 5 COMPLETED)
from .opinion_adaptation import (
    adapt_review_for_context,
    create_multi_platform_opinions,
    get_available_adaptation_options,
    get_adaptation_presets,
    get_platform_specific_guidelines,
)

# Step 6: Quality control integration (STEP 6 COMPLETED)
from .quality_control import (
    perform_quality_validation,
    get_quality_control_capabilities,
    get_quality_standards,
    validate_analysis_pipeline,
)

# PHASE 4: Enhanced Quality Control - NEW ADVANCED FUNCTIONS
from agent_tools import (
    enhanced_qa_validation,
    automatic_completeness_check,
    track_quality_metrics,
    process_feedback_loop,
)

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
    # Phase 2 - Value Analysis (STEP 3 COMPLETED)
    "calculate_value_score",
    "calculate_advanced_value_analysis",
    "get_value_analysis_summary",
    # Phase 3 - Review Generation (STEP 4 COMPLETED)
    "generate_comprehensive_game_review",
    "generate_quick_game_opinion",
    "compare_games_with_reviews",
    "get_review_generation_capabilities",
    # Phase 3 - Opinion Adaptation (STEP 5 COMPLETED)
    "adapt_review_for_context",
    "create_multi_platform_opinions",
    "get_available_adaptation_options",
    "get_adaptation_presets",
    "get_platform_specific_guidelines",
    # Phase 4 - Quality Control (STEP 6 COMPLETED)
    "perform_quality_validation",
    "get_quality_control_capabilities",
    "get_quality_standards",
    "validate_analysis_pipeline",
    # Phase 4 - Enhanced Quality Control (FAZA 4 COMPLETED)
    "enhanced_qa_validation",
    "automatic_completeness_check",
    "track_quality_metrics",
    "process_feedback_loop",
]

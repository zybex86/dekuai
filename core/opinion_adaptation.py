"""
Phase 3 Point 2: Opinion Adaptation Integration
Punkt 2 Fazy 3: Integracja adaptacji opinii

Core opinion adaptation module wrapping agent_tools adaptation functionality
Główny moduł adaptacji opinii opakowujący funkcjonalność z agent_tools
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Import opinion adaptation functions from agent_tools
from agent_tools import (
    adapt_review_for_context as _adapt_review_for_context,
    create_multi_platform_opinions as _create_multi_platform_opinions,
    get_available_adaptation_options as _get_available_adaptation_options,
)


def adapt_review_for_context(
    game_name: str,
    style: str = "casual",
    format_type: str = "summary",
    audience: str = "general_public",
    platform: str = "website",
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Adaptuje recenzję gry do konkretnego kontekstu komunikacyjnego.

    Core interface for review adaptation to specific communication context.
    Główny interfejs dla adaptacji recenzji do konkretnego kontekstu komunikacyjnego.

    Args:
        game_name (str): Nazwa gry do analizy
        style (str): Styl komunikacji (technical, casual, social_media, professional, gaming_enthusiast, beginner_friendly)
        format_type (str): Format wyjściowy (detailed, summary, bullet_points, social_post, comparison_table, recommendation_card)
        audience (str): Grupa docelowa (bargain_hunters, quality_seekers, casual_gamers, hardcore_gamers, indie_lovers, family_oriented, general_public)
        platform (str): Platforma docelowa (twitter, reddit, facebook, website, blog, newsletter)
        max_length (Optional[int]): Maksymalna długość tekstu w znakach

    Returns:
        Dict: Adaptowana zawartość recenzji z metadanymi

    Example:
        >>> adapted = adapt_review_for_context("Hollow Knight", "social_media", "social_post", "indie_lovers", "twitter")
        >>> print(adapted["adapted_content"])
        >>> print(adapted["character_count"])
    """
    try:
        logger.info(
            f"🎨 Core: Adapting review for '{game_name}' to {style}/{format_type} style..."
        )
        logger.info(f"👥 Audience: {audience}, Platform: {platform}")

        result = _adapt_review_for_context(
            game_name, style, format_type, audience, platform, max_length
        )

        if result.get("success", False):
            char_count = result.get("character_count", 0)
            adaptation_context = result.get("adaptation_context", {})

            logger.info(
                f"✅ Core: Review adapted successfully - {char_count} characters, "
                f"Style: {adaptation_context.get('style', 'Unknown')}"
            )
        else:
            logger.warning(
                f"⚠️ Core: Review adaptation failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core review adaptation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.opinion_adaptation.adapt_review_for_context",
        }


def create_multi_platform_opinions(
    game_name: str, platforms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Tworzy opinie o grze dla wielu platform jednocześnie.

    Core interface for creating multi-platform game opinions simultaneously.
    Główny interfejs dla tworzenia opinii o grach dla wielu platform jednocześnie.

    Args:
        game_name (str): Nazwa gry do analizy
        platforms (Optional[List[str]]): Lista platform (twitter, reddit, facebook, website, blog, newsletter)
                                       Default: ["twitter", "reddit", "website", "blog"]

    Returns:
        Dict: Opinie dostosowane do różnych platform z metadanymi

    Example:
        >>> opinions = create_multi_platform_opinions("Celeste", ["twitter", "reddit", "blog"])
        >>> print(opinions["platform_opinions"]["twitter"]["content"])
        >>> print(opinions["generation_summary"]["total_characters"])
    """
    try:
        logger.info(f"🌐 Core: Creating multi-platform opinions for '{game_name}'...")

        if platforms:
            logger.info(f"📱 Platforms: {platforms}")
        else:
            logger.info("📱 Using default platforms: twitter, reddit, website, blog")

        result = _create_multi_platform_opinions(game_name, platforms)

        if result.get("success", False):
            platforms_generated = result.get("platforms_generated", 0)
            total_chars = result.get("generation_summary", {}).get(
                "total_characters", 0
            )

            logger.info(
                f"✅ Core: Multi-platform opinions created - {platforms_generated} platforms, "
                f"{total_chars} total characters"
            )
        else:
            logger.warning(
                f"⚠️ Core: Multi-platform creation failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core multi-platform creation error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.opinion_adaptation.create_multi_platform_opinions",
        }


def get_available_adaptation_options() -> Dict[str, Any]:
    """
    Zwraca dostępne opcje adaptacji opinii.

    Core interface for getting available adaptation options.
    Główny interfejs dla pobierania dostępnych opcji adaptacji.

    Returns:
        Dict: Wszystkie dostępne opcje adaptacji z opisami

    Example:
        >>> options = get_available_adaptation_options()
        >>> print(options["communication_styles"])
        >>> print(options["supported_platforms"])
    """
    try:
        logger.info("📋 Core: Getting available adaptation options...")

        result = _get_available_adaptation_options()

        if result.get("success", False):
            styles_count = len(result.get("communication_styles", {}))
            formats_count = len(result.get("output_formats", {}))
            platforms_count = len(result.get("supported_platforms", {}))

            logger.info(
                f"✅ Core: Adaptation options retrieved - {styles_count} styles, "
                f"{formats_count} formats, {platforms_count} platforms"
            )
        else:
            logger.warning(
                f"⚠️ Core: Options retrieval failed - {result.get('error', 'Unknown error')}"
            )

        return result

    except Exception as e:
        error_msg = f"Core adaptation options error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.opinion_adaptation.get_available_adaptation_options",
        }


def get_adaptation_presets() -> Dict[str, Any]:
    """
    Zwraca gotowe presety adaptacji dla popularnych przypadków użycia.

    Returns ready-to-use adaptation presets for popular use cases.
    Zwraca gotowe presety adaptacji dla popularnych przypadków użycia.

    Returns:
        Dict: Predefiniowane kombinacje parametrów adaptacji
    """
    try:
        logger.info("🎯 Core: Getting adaptation presets...")

        presets = {
            "success": True,
            "presets": {
                "twitter_promotion": {
                    "description": "Promocja gry na Twitterze",
                    "style": "social_media",
                    "format_type": "social_post",
                    "audience": "general_public",
                    "platform": "twitter",
                    "max_length": 280,
                    "use_case": "Quick social media promotion with hashtags",
                },
                "reddit_discussion": {
                    "description": "Dyskusja na Reddit",
                    "style": "gaming_enthusiast",
                    "format_type": "detailed",
                    "audience": "hardcore_gamers",
                    "platform": "reddit",
                    "use_case": "In-depth discussion for gaming communities",
                },
                "blog_review": {
                    "description": "Recenzja na bloga",
                    "style": "professional",
                    "format_type": "detailed",
                    "audience": "general_public",
                    "platform": "blog",
                    "use_case": "Professional blog post review",
                },
                "casual_recommendation": {
                    "description": "Zwykła rekomendacja",
                    "style": "casual",
                    "format_type": "summary",
                    "audience": "casual_gamers",
                    "platform": "website",
                    "use_case": "Friendly recommendation for casual users",
                },
                "bargain_alert": {
                    "description": "Alert o dobrej ofercie",
                    "style": "casual",
                    "format_type": "bullet_points",
                    "audience": "bargain_hunters",
                    "platform": "newsletter",
                    "use_case": "Deal alert for price-conscious users",
                },
                "technical_analysis": {
                    "description": "Analiza techniczna",
                    "style": "technical",
                    "format_type": "detailed",
                    "audience": "quality_seekers",
                    "platform": "website",
                    "use_case": "Detailed technical analysis for informed buyers",
                },
                "family_guide": {
                    "description": "Przewodnik dla rodzin",
                    "style": "beginner_friendly",
                    "format_type": "recommendation_card",
                    "audience": "family_oriented",
                    "platform": "website",
                    "use_case": "Family-friendly game recommendations",
                },
                "indie_spotlight": {
                    "description": "Przedstawienie gry indie",
                    "style": "gaming_enthusiast",
                    "format_type": "summary",
                    "audience": "indie_lovers",
                    "platform": "blog",
                    "use_case": "Highlighting interesting indie games",
                },
            },
            "usage_examples": [
                {
                    "scenario": "Promoting a great indie game deal on Twitter",
                    "preset": "twitter_promotion",
                    "example_call": "adapt_review_for_context('INSIDE', **presets['twitter_promotion'])",
                },
                {
                    "scenario": "Writing detailed review for gaming blog",
                    "preset": "blog_review",
                    "example_call": "adapt_review_for_context('Hollow Knight', **presets['blog_review'])",
                },
                {
                    "scenario": "Quick family game recommendation",
                    "preset": "family_guide",
                    "example_call": "adapt_review_for_context('Mario Odyssey', **presets['family_guide'])",
                },
            ],
        }

        logger.info(f"✅ Core: {len(presets['presets'])} adaptation presets available")
        return presets

    except Exception as e:
        error_msg = f"Core adaptation presets error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.opinion_adaptation.get_adaptation_presets",
        }


def get_platform_specific_guidelines() -> Dict[str, Any]:
    """
    Zwraca wytyczne specyficzne dla platform.

    Returns platform-specific guidelines for optimal content adaptation.
    Zwraca wytyczne specyficzne dla platform dla optymalnej adaptacji treści.

    Returns:
        Dict: Wytyczne i ograniczenia dla każdej platformy
    """
    try:
        logger.info("📐 Core: Getting platform-specific guidelines...")

        guidelines = {
            "success": True,
            "platforms": {
                "twitter": {
                    "character_limit": 280,
                    "recommended_length": "200-250 characters",
                    "hashtag_limit": "1-3 hashtags",
                    "best_practices": [
                        "Use engaging hooks",
                        "Include relevant hashtags",
                        "Keep it concise and punchy",
                        "Use emojis sparingly",
                    ],
                },
                "reddit": {
                    "character_limit": None,
                    "recommended_length": "500-2000 characters",
                    "best_practices": [
                        "Provide detailed analysis",
                        "Use proper formatting",
                        "Include reasoning and evidence",
                        "Engage with community discussion style",
                    ],
                },
                "facebook": {
                    "character_limit": None,
                    "recommended_length": "200-500 characters",
                    "best_practices": [
                        "Conversational tone",
                        "Visual content friendly",
                        "Call-to-action oriented",
                        "Community engagement focus",
                    ],
                },
                "blog": {
                    "character_limit": None,
                    "recommended_length": "1000+ characters",
                    "best_practices": [
                        "Professional formatting",
                        "Comprehensive analysis",
                        "SEO considerations",
                        "Reader value focus",
                    ],
                },
                "newsletter": {
                    "character_limit": None,
                    "recommended_length": "300-800 characters",
                    "best_practices": [
                        "Scannable format",
                        "Action-oriented content",
                        "Clear value proposition",
                        "Direct and informative",
                    ],
                },
                "website": {
                    "character_limit": None,
                    "recommended_length": "400-1200 characters",
                    "best_practices": [
                        "Clear structure",
                        "User experience focus",
                        "Balanced detail level",
                        "Conversion optimization",
                    ],
                },
            },
        }

        logger.info(
            f"✅ Core: Guidelines for {len(guidelines['platforms'])} platforms available"
        )
        return guidelines

    except Exception as e:
        error_msg = f"Core platform guidelines error: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "module": "core.opinion_adaptation.get_platform_specific_guidelines",
        }

"""
Opinion Adapters for AutoGen DekuDeals
Adaptery opinii dla AutoGen DekuDeals

Phase 3 Point 2: Opinion adaptations for different contexts and audiences
Faza 3 Punkt 2: Adaptacje opinii dla różnych kontekstów i odbiorców
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from utils.review_generator import GameReview, ReviewConfidence, RecommendationType

logger = logging.getLogger(__name__)


class CommunicationStyle(Enum):
    """Style komunikacji."""

    TECHNICAL = "technical"  # Szczegółowy, analityczny
    CASUAL = "casual"  # Swobodny, przyjazny
    SOCIAL_MEDIA = "social_media"  # Krótki, engaging
    PROFESSIONAL = "professional"  # Formalny, biznesowy
    GAMING_ENTHUSIAST = "gaming_enthusiast"  # Dla zapalonych graczy
    BEGINNER_FRIENDLY = "beginner_friendly"  # Dla początkujących


class OutputFormat(Enum):
    """Formaty wyjściowe."""

    DETAILED = "detailed"  # Pełna, szczegółowa opinia
    SUMMARY = "summary"  # Krótkie podsumowanie
    BULLET_POINTS = "bullet_points"  # Lista punktów
    SOCIAL_POST = "social_post"  # Post social media
    COMPARISON_TABLE = "comparison_table"  # Tabela porównawcza
    RECOMMENDATION_CARD = "recommendation_card"  # Karta rekomendacji


class AudienceType(Enum):
    """Typy odbiorców."""

    BARGAIN_HUNTERS = "bargain_hunters"  # Łowcy okazji
    QUALITY_SEEKERS = "quality_seekers"  # Poszukiwacze jakości
    CASUAL_GAMERS = "casual_gamers"  # Casual gracze
    HARDCORE_GAMERS = "hardcore_gamers"  # Hardcore gracze
    INDIE_LOVERS = "indie_lovers"  # Miłośnicy indie
    FAMILY_ORIENTED = "family_oriented"  # Rodzinni gracze
    GENERAL_PUBLIC = "general_public"  # Ogólna publiczność


@dataclass
class AdaptationContext:
    """Kontekst adaptacji opinii."""

    style: CommunicationStyle
    format: OutputFormat
    audience: AudienceType
    platform: str = "general"  # e.g., "twitter", "reddit", "website"
    max_length: Optional[int] = None
    include_emoji: bool = True
    include_price_focus: bool = True
    include_technical_details: bool = False
    emphasis_areas: List[str] = field(
        default_factory=list
    )  # e.g., ["price", "quality", "gameplay"]


@dataclass
class AdaptedOpinion:
    """Adaptowana opinia."""

    content: str
    metadata: Dict[str, Any]
    style_used: CommunicationStyle
    format_used: OutputFormat
    audience_targeted: AudienceType
    adaptation_timestamp: datetime = field(default_factory=datetime.now)
    character_count: int = 0
    engagement_elements: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None


class OpinionAdapter:
    """Główny adapter opinii do różnych kontekstów."""

    def __init__(self):
        self.style_templates = self._initialize_style_templates()
        self.format_processors = self._initialize_format_processors()
        self.audience_preferences = self._initialize_audience_preferences()

    def _initialize_style_templates(self) -> Dict[CommunicationStyle, Dict[str, str]]:
        """Inicjalizuje szablony dla różnych stylów komunikacji."""
        return {
            CommunicationStyle.TECHNICAL: {
                "intro": "Technical Analysis: {game_title}",
                "rating_phrase": "Overall assessment yields {rating}/10 based on comprehensive metrics",
                "recommendation_phrase": "Algorithmic recommendation: {recommendation}",
                "price_analysis": "Price-to-value ratio analysis indicates {value_assessment}",
                "conclusion": "Data-driven conclusion: {final_verdict}",
                "confidence_indicator": "Analysis confidence: {confidence}% based on available data points",
            },
            CommunicationStyle.CASUAL: {
                "intro": "Hey! Let's talk about {game_title} 🎮",
                "rating_phrase": "I'd give this one a solid {rating}/10",
                "recommendation_phrase": "My take? {recommendation}!",
                "price_analysis": "Price-wise, {value_assessment}",
                "conclusion": "Bottom line: {final_verdict}",
                "confidence_indicator": "Pretty confident about this one!",
            },
            CommunicationStyle.SOCIAL_MEDIA: {
                "intro": "🎮 {game_title} Review Thread 🧵",
                "rating_phrase": "⭐ {rating}/10",
                "recommendation_phrase": "🎯 {recommendation}",
                "price_analysis": "💰 {value_assessment}",
                "conclusion": "🔥 {final_verdict}",
                "confidence_indicator": "📊 High confidence analysis",
            },
            CommunicationStyle.PROFESSIONAL: {
                "intro": "Game Review Assessment: {game_title}",
                "rating_phrase": "Overall rating: {rating}/10",
                "recommendation_phrase": "Our recommendation: {recommendation}",
                "price_analysis": "Value proposition: {value_assessment}",
                "conclusion": "Executive summary: {final_verdict}",
                "confidence_indicator": "Assessment reliability: {confidence}",
            },
            CommunicationStyle.GAMING_ENTHUSIAST: {
                "intro": "Fellow gamers! Deep dive into {game_title} 🔥",
                "rating_phrase": "This beauty scores {rating}/10 in my book",
                "recommendation_phrase": "For the gaming community: {recommendation}",
                "price_analysis": "Value analysis for your gaming budget: {value_assessment}",
                "conclusion": "Gamer's verdict: {final_verdict}",
                "confidence_indicator": "Based on extensive gaming experience",
            },
            CommunicationStyle.BEGINNER_FRIENDLY: {
                "intro": "New to gaming? Let me explain {game_title} simply 🌟",
                "rating_phrase": "I'd rate this {rating} out of 10 (10 being amazing!)",
                "recommendation_phrase": "Should you get it? {recommendation}",
                "price_analysis": "About the price: {value_assessment}",
                "conclusion": "In simple terms: {final_verdict}",
                "confidence_indicator": "Don't worry - this advice is reliable!",
            },
        }

    def _initialize_format_processors(self) -> Dict[OutputFormat, callable]:
        """Inicjalizuje procesory dla różnych formatów."""
        return {
            OutputFormat.DETAILED: self._format_detailed,
            OutputFormat.SUMMARY: self._format_summary,
            OutputFormat.BULLET_POINTS: self._format_bullet_points,
            OutputFormat.SOCIAL_POST: self._format_social_post,
            OutputFormat.COMPARISON_TABLE: self._format_comparison_table,
            OutputFormat.RECOMMENDATION_CARD: self._format_recommendation_card,
        }

    def _initialize_audience_preferences(self) -> Dict[AudienceType, Dict[str, Any]]:
        """Inicjalizuje preferencje różnych odbiorców."""
        return {
            AudienceType.BARGAIN_HUNTERS: {
                "focus_areas": ["price", "value", "deals", "timing"],
                "language_tone": "enthusiastic",
                "key_concerns": ["price_drops", "historical_lows", "sale_timing"],
                "avoid_topics": ["premium_features"],
                "preferred_length": "medium",
            },
            AudienceType.QUALITY_SEEKERS: {
                "focus_areas": ["quality", "ratings", "critical_reception", "gameplay"],
                "language_tone": "analytical",
                "key_concerns": [
                    "metacritic_scores",
                    "long_term_value",
                    "replay_value",
                ],
                "avoid_topics": ["budget_considerations"],
                "preferred_length": "detailed",
            },
            AudienceType.CASUAL_GAMERS: {
                "focus_areas": ["accessibility", "fun_factor", "time_commitment"],
                "language_tone": "friendly",
                "key_concerns": ["ease_of_play", "learning_curve", "casual_enjoyment"],
                "avoid_topics": ["technical_specifications", "hardcore_mechanics"],
                "preferred_length": "short",
            },
            AudienceType.HARDCORE_GAMERS: {
                "focus_areas": ["depth", "mechanics", "challenge", "technical_aspects"],
                "language_tone": "expert",
                "key_concerns": ["gameplay_depth", "technical_merit", "innovation"],
                "avoid_topics": ["simplification"],
                "preferred_length": "detailed",
            },
            AudienceType.INDIE_LOVERS: {
                "focus_areas": [
                    "creativity",
                    "innovation",
                    "developer_story",
                    "uniqueness",
                ],
                "language_tone": "passionate",
                "key_concerns": ["artistic_merit", "developer_support", "originality"],
                "avoid_topics": ["mainstream_comparison"],
                "preferred_length": "medium",
            },
            AudienceType.FAMILY_ORIENTED: {
                "focus_areas": ["family_friendly", "educational_value", "co_op_play"],
                "language_tone": "wholesome",
                "key_concerns": ["age_appropriateness", "family_bonding", "safety"],
                "avoid_topics": ["mature_content", "violence"],
                "preferred_length": "medium",
            },
            AudienceType.GENERAL_PUBLIC: {
                "focus_areas": ["general_appeal", "accessibility", "value"],
                "language_tone": "balanced",
                "key_concerns": ["broad_appeal", "ease_of_understanding"],
                "avoid_topics": ["technical_jargon"],
                "preferred_length": "medium",
            },
        }

    def adapt_opinion(
        self, review: GameReview, context: AdaptationContext
    ) -> AdaptedOpinion:
        """
        Adaptuje opinię do określonego kontekstu.

        Args:
            review: Oryginalna opinia z review_generator
            context: Kontekst adaptacji

        Returns:
            AdaptedOpinion: Adaptowana opinia
        """
        try:
            logger.info(
                f"🎭 Adapting opinion for {context.style.value} style, {context.format.value} format"
            )

            # Get style template
            style_template = self.style_templates.get(context.style, {})

            # Get audience preferences
            audience_prefs = self.audience_preferences.get(context.audience, {})

            # Prepare opinion data
            opinion_data = self._prepare_opinion_data(review, context, audience_prefs)

            # Apply style transformation
            styled_content = self._apply_style_transformation(
                opinion_data, style_template, context
            )

            # Apply format transformation
            format_processor = self.format_processors.get(context.format)
            if format_processor:
                formatted_content = format_processor(
                    styled_content, context, audience_prefs
                )
            else:
                formatted_content = str(styled_content)

            # Post-process for platform and constraints
            final_content = self._apply_final_processing(
                formatted_content, context, audience_prefs
            )

            # Generate engagement elements
            engagement_elements = self._generate_engagement_elements(
                review, context, audience_prefs
            )

            # Generate call to action
            call_to_action = self._generate_call_to_action(
                review, context, audience_prefs
            )

            adapted_opinion = AdaptedOpinion(
                content=final_content,
                metadata={
                    "original_rating": review.overall_rating,
                    "original_recommendation": review.recommendation.value,
                    "adaptation_context": {
                        "style": context.style.value,
                        "format": context.format.value,
                        "audience": context.audience.value,
                        "platform": context.platform,
                    },
                    "content_stats": {
                        "character_count": len(final_content),
                        "word_count": len(final_content.split()),
                        "estimated_read_time": max(
                            1, len(final_content.split()) // 200
                        ),  # words per minute
                    },
                },
                style_used=context.style,
                format_used=context.format,
                audience_targeted=context.audience,
                character_count=len(final_content),
                engagement_elements=engagement_elements,
                call_to_action=call_to_action,
            )

            logger.info(
                f"✅ Opinion adapted: {len(final_content)} chars, {context.style.value} style"
            )
            return adapted_opinion

        except Exception as e:
            logger.error(f"❌ Error adapting opinion: {e}")
            # Return fallback adapted opinion
            return AdaptedOpinion(
                content=f"Review for {review.game_title}: {review.overall_rating:.1f}/10 - {review.recommendation.value}",
                metadata={"error": str(e)},
                style_used=context.style,
                format_used=context.format,
                audience_targeted=context.audience,
                character_count=0,
            )

    def _prepare_opinion_data(
        self,
        review: GameReview,
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Przygotowuje dane opinii do adaptacji."""

        # Focus areas based on audience
        focus_areas = audience_prefs.get("focus_areas", [])

        # Create opinion data structure
        opinion_data = {
            "game_title": review.game_title,
            "rating": review.overall_rating,
            "recommendation": self._adapt_recommendation_text(
                review.recommendation, context.style
            ),
            "confidence": review.confidence.value.replace("_", " ").title(),
            "value_assessment": self._focus_value_assessment(
                review.value_assessment, focus_areas
            ),
            "final_verdict": self._adapt_verdict(review.final_verdict, context.style),
            "strengths": self._filter_by_focus(review.strengths, focus_areas),
            "weaknesses": self._filter_by_focus(review.weaknesses, focus_areas),
            "target_audience": review.target_audience,
            "price_info": review.price_recommendation,
            "timing_advice": review.timing_advice,
        }

        return opinion_data

    def _adapt_recommendation_text(
        self, recommendation: RecommendationType, style: CommunicationStyle
    ) -> str:
        """Adaptuje tekst rekomendacji do stylu."""

        recommendation_adaptations = {
            CommunicationStyle.TECHNICAL: {
                RecommendationType.INSTANT_BUY: "Immediate acquisition recommended",
                RecommendationType.STRONG_BUY: "Strong positive recommendation",
                RecommendationType.BUY: "Purchase recommended",
                RecommendationType.CONSIDER: "Consider based on preferences",
                RecommendationType.WAIT_FOR_SALE: "Await price reduction",
                RecommendationType.WAIT: "Delay purchase decision",
                RecommendationType.SKIP: "Avoid acquisition",
            },
            CommunicationStyle.CASUAL: {
                RecommendationType.INSTANT_BUY: "Buy it right now!",
                RecommendationType.STRONG_BUY: "Definitely get this one",
                RecommendationType.BUY: "Go for it",
                RecommendationType.CONSIDER: "Think about it",
                RecommendationType.WAIT_FOR_SALE: "Wait for a sale",
                RecommendationType.WAIT: "Maybe wait a bit",
                RecommendationType.SKIP: "Skip this one",
            },
            CommunicationStyle.SOCIAL_MEDIA: {
                RecommendationType.INSTANT_BUY: "BUY NOW! 🔥",
                RecommendationType.STRONG_BUY: "GET IT! 💯",
                RecommendationType.BUY: "Worth it! ✨",
                RecommendationType.CONSIDER: "Maybe? 🤔",
                RecommendationType.WAIT_FOR_SALE: "Wait for sale 💰",
                RecommendationType.WAIT: "Hold up ⏳",
                RecommendationType.SKIP: "Pass 👎",
            },
        }

        style_adaptations = recommendation_adaptations.get(style, {})
        return style_adaptations.get(
            recommendation, recommendation.value.replace("_", " ").title()
        )

    def _focus_value_assessment(
        self, value_assessment: str, focus_areas: List[str]
    ) -> str:
        """Dostosowuje ocenę wartości do obszarów zainteresowania."""
        if not focus_areas:
            return value_assessment

        # Adjust emphasis based on focus areas
        if "price" in focus_areas or "value" in focus_areas:
            return value_assessment
        elif "quality" in focus_areas:
            return value_assessment.replace("value for money", "quality experience")
        else:
            return value_assessment

    def _adapt_verdict(self, verdict: str, style: CommunicationStyle) -> str:
        """Adaptuje werdykt do stylu komunikacji."""
        if style == CommunicationStyle.SOCIAL_MEDIA:
            # Shorten and add engagement
            return verdict[:100] + "..." if len(verdict) > 100 else verdict
        elif style == CommunicationStyle.TECHNICAL:
            # Make more analytical
            return verdict.replace("great", "high-quality").replace(
                "amazing", "exceptional"
            )
        elif style == CommunicationStyle.CASUAL:
            # Make more conversational
            return verdict.replace("This game", "This one").replace("players", "you")

        return verdict

    def _filter_by_focus(self, items: List[str], focus_areas: List[str]) -> List[str]:
        """Filtruje elementy na podstawie obszarów zainteresowania."""
        if not focus_areas:
            return items[:3]  # Default limit

        # Simple keyword matching for focus filtering
        focus_keywords = {
            "price": ["price", "value", "cost", "budget", "deal"],
            "quality": ["quality", "rating", "score", "critical", "acclaim"],
            "gameplay": ["gameplay", "mechanics", "controls", "play"],
            "technical": ["technical", "performance", "graphics", "engine"],
        }

        relevant_items = []
        for item in items:
            item_lower = item.lower()
            for focus_area in focus_areas:
                keywords = focus_keywords.get(focus_area, [focus_area])
                if any(keyword in item_lower for keyword in keywords):
                    relevant_items.append(item)
                    break

        # If no focus matches, return first few items
        return relevant_items[:3] if relevant_items else items[:2]

    def _apply_style_transformation(
        self,
        opinion_data: Dict[str, Any],
        style_template: Dict[str, str],
        context: AdaptationContext,
    ) -> Dict[str, str]:
        """Aplikuje transformację stylu."""

        styled_content = {}

        for key, template in style_template.items():
            try:
                if key == "rating_phrase":
                    styled_content[key] = template.format(rating=opinion_data["rating"])
                elif key == "recommendation_phrase":
                    styled_content[key] = template.format(
                        recommendation=opinion_data["recommendation"]
                    )
                elif key == "price_analysis":
                    styled_content[key] = template.format(
                        value_assessment=opinion_data["value_assessment"]
                    )
                elif key == "conclusion":
                    styled_content[key] = template.format(
                        final_verdict=opinion_data["final_verdict"]
                    )
                elif key == "confidence_indicator":
                    styled_content[key] = template.format(
                        confidence=opinion_data["confidence"]
                    )
                else:
                    styled_content[key] = template.format(**opinion_data)
            except KeyError as e:
                logger.warning(f"⚠️ Template formatting issue for {key}: {e}")
                styled_content[key] = template

        return styled_content

    def _apply_final_processing(
        self, content: str, context: AdaptationContext, audience_prefs: Dict[str, Any]
    ) -> str:
        """Stosuje finalne przetwarzanie."""

        # Apply length constraints
        if context.max_length and len(content) > context.max_length:
            content = content[: context.max_length - 3] + "..."

        # Remove emoji if not wanted
        if not context.include_emoji:
            import re

            content = re.sub(r"[^\w\s.,!?()-]", "", content)

        # Platform-specific adjustments
        if context.platform == "twitter":
            # Twitter-specific processing
            content = content.replace("\n\n", "\n")  # Reduce spacing
        elif context.platform == "reddit":
            # Reddit-specific processing
            content = content.replace(". ", ".\n\n")  # Add more spacing

        return content.strip()

    def _generate_engagement_elements(
        self,
        review: GameReview,
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> List[str]:
        """Generuje elementy angażujące."""
        elements = []

        if context.style == CommunicationStyle.SOCIAL_MEDIA:
            elements.extend(["hashtags", "emojis", "questions"])

        if context.audience == AudienceType.BARGAIN_HUNTERS:
            elements.extend(["price_alerts", "deal_comparisons"])

        if context.audience == AudienceType.GAMING_ENTHUSIAST:
            elements.extend(["technical_discussion", "community_input"])

        return elements

    def _generate_call_to_action(
        self,
        review: GameReview,
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> Optional[str]:
        """Generuje wezwanie do działania."""

        if review.recommendation in [
            RecommendationType.INSTANT_BUY,
            RecommendationType.STRONG_BUY,
        ]:
            if context.audience == AudienceType.BARGAIN_HUNTERS:
                return "Check current deals and grab this bargain!"
            elif context.style == CommunicationStyle.SOCIAL_MEDIA:
                return "What's your take? Share in comments! 👇"
            else:
                return "Consider adding this to your gaming library."

        elif review.recommendation == RecommendationType.WAIT_FOR_SALE:
            return "Set up a price alert to catch the next sale!"

        return None

    # Format processors
    def _format_detailed(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje szczegółową opinię."""
        sections = [
            styled_content.get("intro", ""),
            "",
            styled_content.get("rating_phrase", ""),
            styled_content.get("recommendation_phrase", ""),
            "",
            styled_content.get("price_analysis", ""),
            styled_content.get("conclusion", ""),
            "",
            styled_content.get("confidence_indicator", ""),
        ]
        return "\n".join(filter(None, sections))

    def _format_summary(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje krótkie podsumowanie."""
        key_parts = [
            styled_content.get("rating_phrase", ""),
            styled_content.get("recommendation_phrase", ""),
            styled_content.get("price_analysis", ""),
        ]
        return " | ".join(filter(None, key_parts))

    def _format_bullet_points(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje listę punktów."""
        points = [
            f"• {styled_content.get('rating_phrase', '')}",
            f"• {styled_content.get('recommendation_phrase', '')}",
            f"• {styled_content.get('price_analysis', '')}",
            f"• {styled_content.get('conclusion', '')}",
        ]
        return "\n".join(filter(lambda x: len(x) > 2, points))

    def _format_social_post(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje post na social media."""
        post_parts = [
            styled_content.get("intro", ""),
            "",
            styled_content.get("rating_phrase", ""),
            styled_content.get("recommendation_phrase", ""),
            "",
            styled_content.get("price_analysis", ""),
            "",
            "#GameReview #Gaming #Nintendo",
        ]
        return "\n".join(filter(None, post_parts))

    def _format_comparison_table(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje tabelę porównawczą."""
        # Simple table format
        return f"""
Game Review Summary
------------------
Rating: {styled_content.get('rating_phrase', 'N/A')}
Recommendation: {styled_content.get('recommendation_phrase', 'N/A')}
Value: {styled_content.get('price_analysis', 'N/A')}
Verdict: {styled_content.get('conclusion', 'N/A')}
        """.strip()

    def _format_recommendation_card(
        self,
        styled_content: Dict[str, str],
        context: AdaptationContext,
        audience_prefs: Dict[str, Any],
    ) -> str:
        """Formatuje kartę rekomendacji."""
        card = f"""
┌─ GAME RECOMMENDATION ─┐
│                       │
│ {styled_content.get('rating_phrase', 'N/A')[:20].ljust(20)} │
│ {styled_content.get('recommendation_phrase', 'N/A')[:20].ljust(20)} │
│                       │
└───────────────────────┘
        """.strip()
        return card


def create_context_presets() -> Dict[str, AdaptationContext]:
    """Tworzy predefiniowane konteksty adaptacji."""
    return {
        "twitter_bargain": AdaptationContext(
            style=CommunicationStyle.SOCIAL_MEDIA,
            format=OutputFormat.SOCIAL_POST,
            audience=AudienceType.BARGAIN_HUNTERS,
            platform="twitter",
            max_length=280,
            include_emoji=True,
            emphasis_areas=["price", "deals"],
        ),
        "reddit_detailed": AdaptationContext(
            style=CommunicationStyle.GAMING_ENTHUSIAST,
            format=OutputFormat.DETAILED,
            audience=AudienceType.HARDCORE_GAMERS,
            platform="reddit",
            include_technical_details=True,
            emphasis_areas=["gameplay", "technical"],
        ),
        "casual_summary": AdaptationContext(
            style=CommunicationStyle.CASUAL,
            format=OutputFormat.SUMMARY,
            audience=AudienceType.CASUAL_GAMERS,
            platform="website",
            max_length=200,
            emphasis_areas=["fun_factor", "accessibility"],
        ),
        "professional_report": AdaptationContext(
            style=CommunicationStyle.PROFESSIONAL,
            format=OutputFormat.COMPARISON_TABLE,
            audience=AudienceType.GENERAL_PUBLIC,
            platform="business",
            include_emoji=False,
            include_technical_details=True,
        ),
        "beginner_guide": AdaptationContext(
            style=CommunicationStyle.BEGINNER_FRIENDLY,
            format=OutputFormat.BULLET_POINTS,
            audience=AudienceType.FAMILY_ORIENTED,
            platform="website",
            emphasis_areas=["accessibility", "family_friendly"],
        ),
        "indie_showcase": AdaptationContext(
            style=CommunicationStyle.GAMING_ENTHUSIAST,
            format=OutputFormat.DETAILED,
            audience=AudienceType.INDIE_LOVERS,
            platform="blog",
            emphasis_areas=["creativity", "innovation", "developer_story"],
        ),
    }


def format_for_multiple_platforms(
    review: GameReview, platforms: List[str]
) -> Dict[str, AdaptedOpinion]:
    """
    Formatuje opinię dla wielu platform jednocześnie.

    Args:
        review: Oryginalna opinia
        platforms: Lista platform ("twitter", "reddit", "facebook", etc.)

    Returns:
        Dict z opiniami dla każdej platformy
    """
    adapter = OpinionAdapter()
    presets = create_context_presets()
    results = {}

    platform_mapping = {
        "twitter": "twitter_bargain",
        "reddit": "reddit_detailed",
        "facebook": "casual_summary",
        "website": "professional_report",
        "blog": "indie_showcase",
        "newsletter": "beginner_guide",
    }

    for platform in platforms:
        preset_name = platform_mapping.get(platform, "casual_summary")
        context = presets.get(preset_name)

        if context:
            adapted = adapter.adapt_opinion(review, context)
            results[platform] = adapted

    return results

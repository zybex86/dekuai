#!/usr/bin/env python3
"""
🎮 AutoGen DekuDeals - Demo Runner
Demonstracja wszystkich funkcji systemu analizy gier

Ten skrypt pokazuje jak korzystać z pełnego systemu AutoGen DekuDeals
z wszystkimi zaimplementowanymi funkcjami Fazy 1, 2 i 3.
"""

import sys
import os
import time
import argparse
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all available components
from conversation_manager import (
    GameAnalysisManager,
    analyze_game_quick,
    analyze_game_comprehensive,
)
from agent_tools import (
    # Phase 1 & 2 tools
    search_and_scrape_game,
    calculate_value_score,
    calculate_advanced_value_analysis,
    generate_personalized_recommendations,
    # Phase 3 Point 1 - Comprehensive Reviews
    generate_comprehensive_game_review,
    generate_quick_game_opinion,
    compare_games_with_reviews,
    # Phase 3 Point 2 - Opinion Adaptations
    adapt_review_for_context,
    create_multi_platform_opinions,
    get_available_adaptation_options,
    # Category scraping for game lists
    scrape_dekudeals_category,
    get_games_from_popular_categories,
    get_random_game_sample,
)

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutoGenDekuDealsDemo:
    """Główna klasa demonstracyjna systemu AutoGen DekuDeals."""

    def __init__(self):
        self.manager = GameAnalysisManager()

    def show_welcome(self):
        """Wyświetla powitanie i dostępne opcje."""
        print("=" * 80)
        print("🎮 AutoGen DekuDeals - System Analizy Gier Nintendo Switch")
        print("=" * 80)
        print("🚀 Zaimplementowane funkcje:")
        print("   📊 Phase 1: Podstawowa analiza cen i wartości")
        print("   🎯 Phase 2: Zaawansowane algorytmy rekomendacji")
        print("   📝 Phase 3.1: Kompleksowe generowanie recenzji")
        print("   🎭 Phase 3.2: Adaptacje opinii do różnych kontekstów")
        print("   🎲 Kategorie DekuDeals: Losowe próbki z 13 kategorii")
        print("=" * 80)

    def get_available_game_categories(self) -> Dict[str, List[str]]:
        """Zwraca dostępne kategorie gier."""
        return {
            "💰 Deal Categories": [
                "hottest",  # Hottest Deals
                "recent-drops",  # Recent Price Drops
                "eshop-sales",  # eShop Sales
                "deepest-discounts",  # Deepest Discounts
                "bang-for-your-buck",  # Bang for your Buck
                "ending-soon",  # Ending Soon
            ],
            "⭐ Quality Categories": [
                "highest-rated",  # Highest Rated
                "staff-picks",  # Staff Picks
                "most-wanted",  # Most Wanted
            ],
            "📈 Trending Categories": [
                "trending",  # Trending Games
                "recently-released",  # Recently Released
                "upcoming-releases",  # Upcoming Releases
                "newest-listings",  # Newly Listed
            ],
        }

    def demo_category_browsing(self):
        """Demonstracja przeglądania kategorii gier."""
        print("\n🎲 DEMO: Przeglądanie Kategorii Gier")
        print("-" * 50)

        categories = self.get_available_game_categories()

        for category_group, category_list in categories.items():
            print(f"\n{category_group}:")
            for category in category_list:
                display_name = category.replace("-", " ").title()
                print(f"   • {category} ({display_name})")

        print(f"\n💡 Przykłady użycia:")
        print(f"   python run_demo.py --category hottest --count 5")
        print(f"   python run_demo.py --random-sample 3 mixed")
        print(f"   python run_demo.py --multi-category hottest highest-rated")

    def demo_single_game_analysis(
        self, game_name: str, analysis_type: str = "comprehensive"
    ):
        """Demonstracja analizy pojedynczej gry."""
        print(f"\n🎮 DEMO: Analiza Gry - {game_name}")
        print("-" * 50)

        if analysis_type == "quick":
            print("⚡ Uruchamianie szybkiej analizy...")
            result = analyze_game_quick(game_name)
        else:
            print("🔍 Uruchamianie pełnej analizy...")
            result = analyze_game_comprehensive(game_name)

        if result.get("success", False):
            print(f"✅ Analiza zakończona pomyślnie!")
            print(f"📊 Typ: {result.get('analysis_type', 'unknown')}")
            print(f"🎮 Gra: {result.get('game_name', 'Unknown')}")
            print(f"⏰ Czas: {result.get('timestamp', 'N/A')}")

            # Show conversation summary if available
            conversation = result.get("raw_conversation", "")
            if conversation and len(conversation) > 100:
                print(f"💬 Podgląd konwersacji:")
                print(f"   {conversation[:200]}...")

        else:
            print(
                f"❌ Analiza nie powiodła się: {result.get('error', 'Nieznany błąd')}"
            )

        return result

    def demo_comprehensive_review(self, game_name: str):
        """Demonstracja kompleksowego generowania recenzji."""
        print(f"\n📝 DEMO: Kompleksowa Recenzja - {game_name}")
        print("-" * 50)

        print("🎬 Generowanie kompleksowej recenzji...")
        result = generate_comprehensive_game_review(
            game_name, include_recommendations=True
        )

        if result.get("success", False):
            print("✅ Recenzja wygenerowana pomyślnie!")

            # Display key metrics
            review_data = result.get("review_data", {})
            print(f"⭐ Ocena: {review_data.get('overall_rating', 'N/A')}/10")
            print(f"🎯 Rekomendacja: {review_data.get('recommendation', 'N/A')}")
            print(f"📊 Pewność: {review_data.get('confidence', 'N/A')}")

            # Show verdict preview
            verdict = review_data.get("final_verdict", "")
            if verdict:
                print(
                    f"📄 Werdykt: {verdict[:100]}..."
                    if len(verdict) > 100
                    else f"📄 Werdykt: {verdict}"
                )

            # Show strengths and weaknesses
            strengths = review_data.get("strengths", [])
            if strengths:
                print(f"💪 Zalety: {', '.join(strengths[:3])}")

            weaknesses = review_data.get("weaknesses", [])
            if weaknesses:
                print(f"⚠️ Wady: {', '.join(weaknesses[:3])}")

        else:
            print(
                f"❌ Generowanie recenzji nie powiodło się: {result.get('error', 'Nieznany błąd')}"
            )

        return result

    def demo_opinion_adaptations(self, game_name: str):
        """Demonstracja adaptacji opinii do różnych kontekstów."""
        print(f"\n🎭 DEMO: Adaptacje Opinii - {game_name}")
        print("-" * 50)

        # Test different styles
        styles_to_test = [
            ("casual", "summary", "general_public", "website"),
            ("social_media", "social_post", "bargain_hunters", "twitter"),
            ("technical", "detailed", "hardcore_gamers", "blog"),
        ]

        successful_adaptations = []

        for style, format_type, audience, platform in styles_to_test:
            print(f"\n🎨 Testowanie: {style} → {format_type} → {audience} → {platform}")

            result = adapt_review_for_context(
                game_name=game_name,
                style=style,
                format_type=format_type,
                audience=audience,
                platform=platform,
            )

            if result.get("success", False):
                char_count = result.get("character_count", 0)
                print(f"   ✅ Sukces: {char_count} znaków")

                # Show content preview
                content = result.get("adapted_content", "")
                preview = content[:80] + "..." if len(content) > 80 else content
                print(f"   📄 Podgląd: {preview}")

                successful_adaptations.append(result)
            else:
                print(f"   ❌ Błąd: {result.get('error', 'Nieznany')}")

        print(
            f"\n📊 Podsumowanie adaptacji: {len(successful_adaptations)}/{len(styles_to_test)} udanych"
        )
        return successful_adaptations

    def demo_multi_platform_opinions(self, game_name: str):
        """Demonstracja generowania opinii dla wielu platform."""
        print(f"\n🌐 DEMO: Opinie Multi-Platform - {game_name}")
        print("-" * 50)

        platforms = ["twitter", "reddit", "website", "blog"]
        print(f"🎯 Platformy docelowe: {', '.join(platforms)}")

        result = create_multi_platform_opinions(game_name, platforms)

        if result.get("success", False):
            print("✅ Opinie multi-platform wygenerowane!")
            print(f"🌐 Wygenerowane platformy: {result.get('platforms_generated', 0)}")
            print(f"⭐ Bazowa ocena: {result.get('base_review_rating', 'N/A')}/10")

            # Show platform summaries
            platform_opinions = result.get("platform_opinions", {})
            for platform, opinion in platform_opinions.items():
                char_count = opinion.get("character_count", 0)
                style = opinion.get("style", "unknown")
                print(f"   📱 {platform.upper()}: {char_count} znaków ({style})")

        else:
            print(
                f"❌ Generowanie opinii nie powiodło się: {result.get('error', 'Nieznany błąd')}"
            )

        return result

    def demo_category_games(self, category: str, count: int = 5):
        """Demonstracja pobierania gier z kategorii."""
        print(f"\n📂 DEMO: Gry z Kategorii '{category}'")
        print("-" * 50)

        result = scrape_dekudeals_category(category, max_games=count)

        if result.get("success", False):
            print(f"✅ Pobrano gry z kategorii!")
            print(f"📂 Kategoria: {result.get('category_name', category)}")
            print(f"🎮 Znalezione gry: {result.get('games_found', 0)}")

            # Show games
            game_titles = result.get("game_titles", [])
            if game_titles:
                print(f"\n🎮 Lista gier:")
                for i, title in enumerate(game_titles[:count], 1):
                    print(f"   {i}. {title}")

            return game_titles
        else:
            print(
                f"❌ Pobieranie gier nie powiodło się: {result.get('error', 'Nieznany błąd')}"
            )
            return []

    def demo_random_sample(self, sample_size: int = 3, preference: str = "mixed"):
        """Demonstracja losowej próbki gier."""
        print(f"\n🎲 DEMO: Losowa Próbka - {sample_size} gier ({preference})")
        print("-" * 50)

        result = get_random_game_sample(sample_size, preference)

        if result.get("success", False):
            print(f"✅ Wygenerowano losową próbkę!")
            print(f"🎯 Żądane: {result.get('sample_size_requested', 0)}")
            print(f"🎮 Otrzymane: {result.get('sample_size_actual', 0)}")
            print(
                f"📂 Kategorie źródłowe: {', '.join(result.get('categories_used', []))}"
            )

            # Show games
            selected_games = result.get("selected_games", [])
            if selected_games:
                print(f"\n🎮 Wybrane gry:")
                for i, game in enumerate(selected_games, 1):
                    print(f"   {i}. {game}")

            return selected_games
        else:
            print(
                f"❌ Generowanie próbki nie powiodło się: {result.get('error', 'Nieznany błąd')}"
            )
            return []

    def demo_game_comparison(self, games: List[str]):
        """Demonstracja porównania gier."""
        print(f"\n🆚 DEMO: Porównanie Gier")
        print("-" * 50)

        if len(games) < 2:
            print("❌ Potrzeba co najmniej 2 gier do porównania")
            return None

        print(f"🎮 Porównywane gry: {', '.join(games[:3])}")

        result = compare_games_with_reviews(games[:3], "overall")

        if result.get("success", False):
            print("✅ Porównanie zakończone!")

            winner = result.get("winner", {})
            if winner:
                winner_title = winner.get("game_title", "Unknown")
                print(f"🏆 Zwycięzca: {winner_title}")

            games_compared = result.get("games_compared", 0)
            print(f"📊 Porównane gry: {games_compared}")

            # Show comparison reasoning
            reasoning = result.get("comparison_reasoning", "")
            if reasoning:
                print(f"🤔 Uzasadnienie: {reasoning[:150]}...")

        else:
            print(
                f"❌ Porównanie nie powiodło się: {result.get('error', 'Nieznany błąd')}"
            )

        return result


def main():
    """Główna funkcja demonstracyjna."""
    parser = argparse.ArgumentParser(description="AutoGen DekuDeals Demo Runner")

    # Main actions
    parser.add_argument("--game", type=str, help="Analiza konkretnej gry")
    parser.add_argument(
        "--quick", action="store_true", help="Szybka analiza zamiast pełnej"
    )
    parser.add_argument("--category", type=str, help="Pobierz gry z kategorii")
    parser.add_argument("--count", type=int, default=5, help="Liczba gier z kategorii")
    parser.add_argument("--random-sample", type=int, help="Losowa próbka gier")
    parser.add_argument(
        "--preference",
        type=str,
        default="mixed",
        choices=["mixed", "deals", "quality", "trending"],
        help="Preferencje dla losowej próbki",
    )
    parser.add_argument("--multi-category", nargs="+", help="Gry z wielu kategorii")
    parser.add_argument("--compare", nargs="+", help="Porównaj podane gry")
    parser.add_argument(
        "--demo-all", action="store_true", help="Uruchom pełną demonstrację"
    )
    parser.add_argument(
        "--list-categories", action="store_true", help="Pokaż dostępne kategorie"
    )

    # Feature flags
    parser.add_argument(
        "--no-review", action="store_true", help="Pomiń generowanie recenzji"
    )
    parser.add_argument(
        "--no-adaptations", action="store_true", help="Pomiń adaptacje opinii"
    )
    parser.add_argument(
        "--no-multi-platform", action="store_true", help="Pomiń multi-platform"
    )

    args = parser.parse_args()

    # Initialize demo
    demo = AutoGenDekuDealsDemo()
    demo.show_welcome()

    try:
        if args.list_categories:
            demo.demo_category_browsing()

        elif args.demo_all:
            # Full demo with sample game
            sample_game = "INSIDE"
            print(f"\n🎬 PEŁNA DEMONSTRACJA z grą: {sample_game}")

            # 1. Basic analysis
            demo.demo_single_game_analysis(sample_game, "comprehensive")

            # 2. Comprehensive review
            if not args.no_review:
                demo.demo_comprehensive_review(sample_game)

            # 3. Opinion adaptations
            if not args.no_adaptations:
                demo.demo_opinion_adaptations(sample_game)

            # 4. Multi-platform opinions
            if not args.no_multi_platform:
                demo.demo_multi_platform_opinions(sample_game)

            # 5. Category sampling
            print("\n🎲 Demonstracja próbkowania kategorii...")
            sample_games = demo.demo_random_sample(3, "mixed")

            # 6. Game comparison
            if len(sample_games) >= 2:
                demo.demo_game_comparison(sample_games)

        elif args.game:
            # Single game analysis
            analysis_type = "quick" if args.quick else "comprehensive"
            demo.demo_single_game_analysis(args.game, analysis_type)

            if not args.no_review:
                demo.demo_comprehensive_review(args.game)

            if not args.no_adaptations:
                demo.demo_opinion_adaptations(args.game)

            if not args.no_multi_platform:
                demo.demo_multi_platform_opinions(args.game)

        elif args.category:
            # Category browsing
            games = demo.demo_category_games(args.category, args.count)

            # Analyze first game from category
            if games and not args.no_review:
                print(f"\n🔍 Analizowanie pierwszej gry z kategorii...")
                demo.demo_comprehensive_review(games[0])

        elif args.random_sample:
            # Random sample
            games = demo.demo_random_sample(args.random_sample, args.preference)

            # Compare games if we have multiple
            if len(games) >= 2:
                demo.demo_game_comparison(games)

        elif args.multi_category:
            # Multi-category collection
            print(f"\n📂 DEMO: Gry z Wielu Kategorii")
            print("-" * 50)

            result = get_games_from_popular_categories(
                max_games_per_category=3, categories=args.multi_category
            )

            if result.get("success", False):
                print(
                    f"✅ Pobrano gry z {result.get('categories_processed', 0)} kategorii"
                )
                all_titles = result.get("all_unique_titles", [])
                print(f"🎮 Łącznie unikalne gry: {len(all_titles)}")

                # Show sample
                for i, title in enumerate(all_titles[:5], 1):
                    print(f"   {i}. {title}")

                if len(all_titles) > 5:
                    print(f"   ... i {len(all_titles) - 5} więcej")

        elif args.compare:
            # Direct game comparison
            demo.demo_game_comparison(args.compare)

        else:
            # Show help and examples
            demo.demo_category_browsing()
            print(f"\n💡 Przykłady użycia:")
            print(f"   python run_demo.py --demo-all")
            print(f"   python run_demo.py --game 'Hollow Knight'")
            print(f"   python run_demo.py --game 'Celeste' --quick")
            print(f"   python run_demo.py --category hottest --count 10")
            print(f"   python run_demo.py --random-sample 5 deals")
            print(f"   python run_demo.py --compare 'INSIDE' 'Celeste' 'Hollow Knight'")
            print(f"   python run_demo.py --multi-category hottest highest-rated")
            print(f"\n📖 Użyj --help aby zobaczyć wszystkie opcje")

    except KeyboardInterrupt:
        print(f"\n\n⏹️ Demo przerwane przez użytkownika")
    except Exception as e:
        print(f"\n❌ Błąd podczas demonstracji: {e}")
        logger.exception("Demo error")

    print(f"\n🏁 Demo zakończone!")


if __name__ == "__main__":
    main()

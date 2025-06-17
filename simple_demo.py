#!/usr/bin/env python3
"""
🎮 AutoGen DekuDeals - Simple Demo
Prosta demonstracja funkcji bez konwersacji AutoGen

Ten skrypt pokazuje główne funkcje systemu bez uruchamiania konwersacji AutoGen.
"""

import sys
import os
import argparse
from typing import List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import direct tools (without AutoGen)
from agent_tools import (
    # Phase 1 & 2 tools
    search_and_scrape_game,
    calculate_value_score,
    calculate_advanced_value_analysis,
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


def show_welcome():
    """Wyświetla powitanie."""
    print("=" * 80)
    print("🎮 AutoGen DekuDeals - Simple Demo (bez AutoGen konwersacji)")
    print("=" * 80)
    print("🚀 Dostępne funkcje:")
    print("   📊 Podstawowa analiza cen i wartości")
    print("   🎯 Zaawansowane algorytmy rekomendacji")
    print("   📝 Kompleksowe generowanie recenzji")
    print("   🎭 Adaptacje opinii do różnych kontekstów")
    print("   🎲 Kategorie DekuDeals: Losowe próbki z 13 kategorii")
    print("=" * 80)


def demo_single_game_comprehensive(game_name: str):
    """Demonstracja pełnej analizy pojedynczej gry."""
    print(f"\n🎮 DEMO: Pełna Analiza Gry - {game_name}")
    print("-" * 60)

    print("🎬 Generowanie kompleksowej recenzji...")
    result = generate_comprehensive_game_review(game_name, include_recommendations=True)

    if result.get("success", False):
        print("✅ Recenzja wygenerowana pomyślnie!")

        # Display key metrics
        review_data = result.get("review_data", {})
        print(f"⭐ Ocena: {review_data.get('overall_rating', 'N/A')}/10")
        print(f"🎯 Rekomendacja: {review_data.get('recommendation', 'N/A')}")
        print(f"📊 Pewność: {review_data.get('confidence', 'N/A')}")

        # Show verdict
        verdict = review_data.get("final_verdict", "")
        if verdict:
            print(f"📄 Werdykt: {verdict}")

        # Show strengths and weaknesses
        strengths = review_data.get("strengths", [])
        if strengths:
            print(f"💪 Zalety: {', '.join(strengths)}")

        weaknesses = review_data.get("weaknesses", [])
        if weaknesses:
            print(f"⚠️ Wady: {', '.join(weaknesses)}")

        # Show price recommendation
        price_rec = review_data.get("price_recommendation", "")
        if price_rec:
            print(f"💰 Rekomendacja cenowa: {price_rec}")

        return True
    else:
        print(f"❌ Analiza nie powiodła się: {result.get('error', 'Nieznany błąd')}")
        return False


def demo_opinion_adaptations(game_name: str):
    """Demonstracja adaptacji opinii."""
    print(f"\n🎭 DEMO: Adaptacje Opinii - {game_name}")
    print("-" * 60)

    # Test different styles
    styles_to_test = [
        ("casual", "summary", "general_public", "website"),
        ("social_media", "social_post", "bargain_hunters", "twitter"),
        ("technical", "bullet_points", "hardcore_gamers", "blog"),
    ]

    for i, (style, format_type, audience, platform) in enumerate(styles_to_test, 1):
        print(f"\n🎨 {i}. {style} → {format_type} → {audience} → {platform}")

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
            if content and len(content) > 0:
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"   📄 Treść: {preview}")

        else:
            print(f"   ❌ Błąd: {result.get('error', 'Nieznany')}")


def demo_category_games(category: str, count: int = 5):
    """Demonstracja pobierania gier z kategorii."""
    print(f"\n📂 DEMO: Gry z Kategorii '{category}' (max {count})")
    print("-" * 60)

    result = scrape_dekudeals_category(category, max_games=count)

    if result.get("success", False):
        print(f"✅ Pobrano gry z kategorii!")
        print(f"📂 Kategoria: {result.get('category_name', category)}")
        print(f"🎮 Znalezione gry: {result.get('games_found', 0)}")

        # Show games
        game_titles = result.get("game_titles", [])
        if game_titles:
            print(f"\n🎮 Lista gier:")
            for i, title in enumerate(game_titles, 1):
                print(f"   {i}. {title}")

        return game_titles
    else:
        print(f"❌ Pobieranie nie powiodło się: {result.get('error', 'Nieznany błąd')}")
        available = result.get("available_categories", [])
        if available:
            print(f"💡 Dostępne kategorie: {', '.join(available[:5])}")
        return []


def demo_random_sample(sample_size: int = 3, preference: str = "mixed"):
    """Demonstracja losowej próbki gier."""
    print(f"\n🎲 DEMO: Losowa Próbka - {sample_size} gier ({preference})")
    print("-" * 60)

    result = get_random_game_sample(sample_size, preference)

    if result.get("success", False):
        print(f"✅ Wygenerowano losową próbkę!")
        print(f"🎯 Żądane: {result.get('sample_size_requested', 0)}")
        print(f"🎮 Otrzymane: {result.get('sample_size_actual', 0)}")

        # Show games
        selected_games = result.get("selected_games", [])
        if selected_games:
            print(f"\n🎮 Wybrane gry:")
            for i, game in enumerate(selected_games, 1):
                print(f"   {i}. {game}")

        return selected_games
    else:
        print(
            f"❌ Generowanie nie powiodło się: {result.get('error', 'Nieznany błąd')}"
        )
        return []


def demo_quick_opinions(games: List[str]):
    """Demonstracja szybkich opinii o grach."""
    print(f"\n⚡ DEMO: Szybkie Opinie")
    print("-" * 60)

    opinions = []
    for i, game in enumerate(games, 1):
        print(f"\n📝 {i}. Analiza: {game}")

        result = generate_quick_game_opinion(game)

        if result.get("success", False):
            summary = result.get("quick_summary", {})
            rating = summary.get("rating", "N/A")
            recommendation = summary.get("recommendation", "N/A")

            print(f"   ⭐ Ocena: {rating}")
            print(f"   🎯 Rekomendacja: {recommendation}")

            opinions.append(result)
        else:
            print(f"   ❌ Błąd: {result.get('error', 'Nieznany')}")

    return opinions


def demo_game_comparison(games: List[str]):
    """Demonstracja porównania gier."""
    if len(games) < 2:
        print("❌ Potrzeba co najmniej 2 gier do porównania")
        return

    print(f"\n🆚 DEMO: Porównanie Gier")
    print("-" * 60)
    print(f"🎮 Porównywane: {', '.join(games[:3])}")

    result = compare_games_with_reviews(games[:3], "overall")

    if result.get("success", False):
        print("✅ Porównanie zakończone!")

        winner = result.get("winner", {})
        if winner:
            winner_title = winner.get("game_title", "Unknown")
            print(f"🏆 Zwycięzca: {winner_title}")

        # Show reasoning
        reasoning = result.get("comparison_reasoning", "")
        if reasoning:
            print(f"🤔 Uzasadnienie: {reasoning}")
    else:
        print(f"❌ Porównanie nie powiodło się: {result.get('error', 'Nieznany błąd')}")


def list_available_categories():
    """Lista dostępnych kategorii."""
    print("\n📂 DOSTĘPNE KATEGORIE GIER")
    print("-" * 60)

    categories = {
        "💰 Deal Categories": [
            "hottest",
            "recent-drops",
            "eshop-sales",
            "deepest-discounts",
            "bang-for-your-buck",
            "ending-soon",
        ],
        "⭐ Quality Categories": ["highest-rated", "staff-picks", "most-wanted"],
        "📈 Trending Categories": [
            "trending",
            "recently-released",
            "upcoming-releases",
            "newest-listings",
        ],
    }

    for group, cat_list in categories.items():
        print(f"\n{group}:")
        for cat in cat_list:
            display_name = cat.replace("-", " ").title()
            print(f"   • {cat} ({display_name})")


def main():
    """Główna funkcja."""
    parser = argparse.ArgumentParser(description="AutoGen DekuDeals Simple Demo")

    # Main actions
    parser.add_argument("--game", type=str, help="Analiza konkretnej gry")
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
    parser.add_argument("--compare", nargs="+", help="Porównaj podane gry")
    parser.add_argument(
        "--list-categories", action="store_true", help="Pokaż kategorie"
    )
    parser.add_argument("--demo-all", action="store_true", help="Pełna demonstracja")

    args = parser.parse_args()

    show_welcome()

    try:
        if args.list_categories:
            list_available_categories()

        elif args.demo_all:
            # Full demo
            sample_game = "INSIDE"
            print(f"\n🎬 PEŁNA DEMONSTRACJA z grą: {sample_game}")

            # 1. Comprehensive analysis
            demo_single_game_comprehensive(sample_game)

            # 2. Opinion adaptations
            demo_opinion_adaptations(sample_game)

            # 3. Category sampling
            sample_games = demo_random_sample(3, "mixed")

            # 4. Quick opinions
            if sample_games:
                demo_quick_opinions(sample_games)

            # 5. Comparison
            if len(sample_games) >= 2:
                demo_game_comparison(sample_games)

        elif args.game:
            # Single game analysis
            demo_single_game_comprehensive(args.game)
            demo_opinion_adaptations(args.game)

        elif args.category:
            # Category browsing
            games = demo_category_games(args.category, args.count)

            # Analyze first game
            if games:
                demo_single_game_comprehensive(games[0])

        elif args.random_sample:
            # Random sample
            games = demo_random_sample(args.random_sample, args.preference)

            # Quick opinions
            if games:
                demo_quick_opinions(games)

            # Compare if multiple
            if len(games) >= 2:
                demo_game_comparison(games)

        elif args.compare:
            # Direct comparison
            demo_game_comparison(args.compare)

        else:
            # Show examples
            list_available_categories()
            print(f"\n💡 PRZYKŁADY UŻYCIA:")
            print(f"   python simple_demo.py --demo-all")
            print(f"   python simple_demo.py --game 'Hollow Knight'")
            print(f"   python simple_demo.py --category hottest --count 10")
            print(f"   python simple_demo.py --random-sample 5 deals")
            print(f"   python simple_demo.py --compare 'INSIDE' 'Celeste'")
            print(f"   python simple_demo.py --list-categories")
            print(f"\n📖 Użyj --help dla pełnej listy opcji")

    except KeyboardInterrupt:
        print(f"\n⏹️ Demo przerwane")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")

    print(f"\n🏁 Demo zakończone!")


if __name__ == "__main__":
    main()

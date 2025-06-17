"""
Basic Game Analysis Example
Podstawowy przykład analizy gry z użyciem AutoGen

This example demonstrates how to use the AutoGen agents to analyze a game.
Ten przykład pokazuje jak używać agentów AutoGen do analizy gry.
"""

import os
import sys

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Only import AutoGen components if API key is available
autogen_available = bool(os.environ.get("OPENAI_API_KEY"))

if autogen_available:
    from autogen_agents import (
        user_proxy,
        data_collector,
        price_analyzer,
        review_generator,
        quality_assurance,
    )
    import autogen


def analyze_game_basic(game_name: str) -> None:
    """
    Przeprowadza podstawową analizę gry używając zespołu agentów AutoGen.

    Args:
        game_name (str): Nazwa gry do analizy
    """
    if not autogen_available:
        print("❌ AutoGen not available - OPENAI_API_KEY required for full analysis")
        print("🔧 Running data collection test instead...")
        simple_data_collection_test(game_name)
        return

    print(f"🎮 Starting analysis for: {game_name}")
    print("=" * 50)

    # Create initial message
    initial_message = f"""
Please analyze the game: {game_name}

I need a comprehensive analysis including:
1. Game data collection from DekuDeals
2. Price and value analysis 
3. Detailed review and recommendation
4. Quality assurance check

Please start by collecting the game data.
"""

    try:
        # Start the conversation
        print("🚀 Starting AutoGen conversation...")

        # Initialize group chat with all agents
        groupchat = autogen.GroupChat(
            agents=[
                user_proxy,
                data_collector,
                price_analyzer,
                review_generator,
                quality_assurance,
            ],
            messages=[],
            max_round=20,
            speaker_selection_method="round_robin",
        )

        manager = autogen.GroupChatManager(
            groupchat=groupchat, llm_config={"model": "gpt-4"}
        )

        # Start the analysis
        user_proxy.initiate_chat(manager, message=initial_message)

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        print("💡 Make sure OPENAI_API_KEY is set in your environment variables")


def simple_data_collection_test(game_name: str) -> None:
    """
    Prosty test zbierania danych bez pełnego workflow AutoGen.

    Args:
        game_name (str): Nazwa gry do przetestowania
    """
    print(f"🔍 Testing data collection for: {game_name}")

    try:
        # Import the tool directly
        from agent_tools import search_and_scrape_game, format_game_summary

        # Test data collection
        print("📡 Collecting game data...")
        game_data = search_and_scrape_game(game_name)

        if game_data.get("success", False):
            print("✅ Data collection successful!")
            print("\n" + "=" * 50)
            print("📊 GAME SUMMARY:")
            print("=" * 50)
            print(format_game_summary(game_data))
        else:
            print("❌ Data collection failed:")
            print(f"Error: {game_data.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error during data collection test: {e}")


if __name__ == "__main__":
    # Test games
    test_games = [
        "Hollow Knight",
        "Celeste",
        "The Legend of Zelda: Tears of the Kingdom",
    ]

    print("🎯 AutoGen DekuDeals Game Analysis - Basic Example")
    print("=" * 60)

    # Check API key status and run appropriate tests
    if autogen_available:
        print("✅ OPENAI_API_KEY found - running full AI analysis")
        print("")

        # Choose first game for full analysis
        selected_game = test_games[0]
        print(f"🎮 Selected game for analysis: {selected_game}")

        # Run full analysis
        analyze_game_basic(selected_game)
    else:
        print("⚠️  OPENAI_API_KEY not found in environment variables")
        print("🔧 Running data collection tests only (no AI analysis)")
        print("")

        for game in test_games:
            simple_data_collection_test(game)
            print("\n" + "-" * 60 + "\n")

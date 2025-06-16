"""
Conversation Manager for AutoGen DekuDeals Analysis
Menedżer konwersacji do zarządzania workflow analizy gier
"""

import autogen
from typing import Dict, Any, List, Optional
from autogen_agents import (
    user_proxy,
    data_collector,
    price_analyzer, 
    review_generator,
    quality_assurance,
    create_analysis_team
)
from config.llm_config import get_llm_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameAnalysisManager:
    """
    Menedżer do koordynacji analizy gier przez zespół agentów AutoGen.
    """
    
    def __init__(self):
        """Inicjalizuje menedżera z zespołem agentów."""
        self.agents = create_analysis_team()
        self.analysis_results = {}
        
    def analyze_game(self, game_name: str, max_rounds: int = 15) -> Dict[str, Any]:
        """
        Przeprowadza pełną analizę gry używając zespołu agentów.
        
        Args:
            game_name (str): Nazwa gry do analizy
            max_rounds (int): Maksymalna liczba rund konwersacji
            
        Returns:
            Dict: Wyniki analizy lub komunikat o błędzie
        """
        logger.info(f"🎮 Starting comprehensive analysis for: {game_name}")
        
        try:
            # Prepare initial message
            initial_message = self._create_analysis_prompt(game_name)
            
            # Create group chat
            groupchat = autogen.GroupChat(
                agents=self.agents,
                messages=[],
                max_round=max_rounds,
                speaker_selection_method="auto",
                allow_repeat_speaker=False
            )
            
            # Create manager
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=get_llm_config()
            )
            
            # Start analysis
            logger.info("🚀 Initiating agent conversation...")
            
            result = user_proxy.initiate_chat(
                manager,
                message=initial_message,
                silent=False
            )
            
            # Extract and structure results
            analysis_results = self._extract_results(result, game_name)
            
            logger.info("✅ Analysis completed successfully")
            return analysis_results
            
        except Exception as e:
            error_msg = f"Error during game analysis: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "game_name": game_name
            }
    
    def quick_analysis(self, game_name: str) -> Dict[str, Any]:
        """
        Przeprowadza szybką analizę (tylko zbieranie danych + podstawowa ocena).
        
        Args:
            game_name (str): Nazwa gry
            
        Returns:
            Dict: Podstawowe wyniki analizy
        """
        logger.info(f"⚡ Starting quick analysis for: {game_name}")
        
        try:
            # Just use data collector and one analysis agent
            quick_agents = [user_proxy, data_collector, price_analyzer]
            
            initial_message = f"""
Please perform a quick analysis of the game: {game_name}

Tasks:
1. Collect game data from DekuDeals
2. Provide basic price/value assessment  
3. Give a simple BUY/WAIT/SKIP recommendation

Keep it concise and focused.
"""
            
            groupchat = autogen.GroupChat(
                agents=quick_agents,
                messages=[],
                max_round=8,
                speaker_selection_method="round_robin"
            )
            
            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config=get_llm_config()
            )
            
            result = user_proxy.initiate_chat(
                manager,
                message=initial_message,
                silent=False
            )
            
            quick_results = self._extract_quick_results(result, game_name)
            
            logger.info("✅ Quick analysis completed")
            return quick_results
            
        except Exception as e:
            error_msg = f"Error during quick analysis: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "game_name": game_name
            }
    
    def _create_analysis_prompt(self, game_name: str) -> str:
        """Tworzy szczegółowy prompt do pełnej analizy."""
        return f"""
Please conduct a comprehensive analysis of the game: {game_name}

Required workflow:
1. DATA_COLLECTOR_agent: Search and collect all available game data from DekuDeals 
2. PRICE_ANALYZER_agent: Analyze pricing, value, and purchase recommendations
3. REVIEW_GENERATOR_agent: Create detailed review with pros/cons and target audience
4. QUALITY_ASSURANCE_agent: Review all analyses for completeness and accuracy

Each agent should:
- Use available tools when appropriate
- Provide clear, structured output
- Pass relevant information to the next agent
- Terminate with 'TERMINATE' when complete

Start with data collection and proceed through each step systematically.
"""
    
    def _extract_results(self, conversation_result: Any, game_name: str) -> Dict[str, Any]:
        """Wyciąga ustrukturyzowane wyniki z konwersacji agentów."""
        
        # This is a simplified extraction - in practice, you'd parse the conversation
        # to extract specific outputs from each agent
        
        return {
            "success": True,
            "game_name": game_name,
            "analysis_type": "comprehensive",
            "conversation_summary": "Full analysis completed by agent team",
            "timestamp": self._get_timestamp(),
            "agents_involved": [agent.name for agent in self.agents],
            "raw_conversation": str(conversation_result) if conversation_result else "No conversation data"
        }
    
    def _extract_quick_results(self, conversation_result: Any, game_name: str) -> Dict[str, Any]:
        """Wyciąga wyniki z szybkiej analizy."""
        
        return {
            "success": True,
            "game_name": game_name,
            "analysis_type": "quick",
            "conversation_summary": "Quick analysis completed",
            "timestamp": self._get_timestamp(),
            "raw_conversation": str(conversation_result) if conversation_result else "No conversation data"
        }
    
    def _get_timestamp(self) -> str:
        """Pobiera aktualny timestamp."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Convenience functions for easy usage
def analyze_game_comprehensive(game_name: str) -> Dict[str, Any]:
    """
    Funkcja pomocnicza do przeprowadzenia pełnej analizy gry.
    
    Args:
        game_name (str): Nazwa gry
        
    Returns:
        Dict: Wyniki analizy
    """
    manager = GameAnalysisManager()
    return manager.analyze_game(game_name)

def analyze_game_quick(game_name: str) -> Dict[str, Any]:
    """
    Funkcja pomocnicza do przeprowadzenia szybkiej analizy gry.
    
    Args:
        game_name (str): Nazwa gry
        
    Returns:
        Dict: Wyniki analizy
    """
    manager = GameAnalysisManager()
    return manager.quick_analysis(game_name)

if __name__ == "__main__":
    # Test the conversation manager
    test_game = "Hollow Knight"
    
    print("🧪 Testing GameAnalysisManager")
    print("=" * 50)
    
    manager = GameAnalysisManager()
    
    # Test quick analysis
    print(f"⚡ Testing quick analysis for: {test_game}")
    result = manager.quick_analysis(test_game)
    print(f"Result: {result.get('success', False)}")
    
    if result.get("success"):
        print("✅ Quick analysis test passed!")
    else:
        print(f"❌ Quick analysis test failed: {result.get('error', 'Unknown error')}") 
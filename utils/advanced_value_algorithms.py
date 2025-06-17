"""
Advanced Value Analysis Algorithms for AutoGen DekuDeals
Zaawansowane algorytmy analizy wartości dla AutoGen DekuDeals

Point 2 of Phase 2: Advanced value-for-money evaluation algorithms
Punkt 2 Fazy 2: Zaawansowane algorytmy oceny wartości za pieniądze
"""

import re
import logging
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from utils.price_calculator import extract_price, extract_score

logger = logging.getLogger(__name__)

# Genre-based value expectations and multipliers
GENRE_VALUE_PROFILES = {
    "Action": {"expected_hours": 15, "replay_value": 1.2, "price_tolerance": 1.0},
    "Adventure": {"expected_hours": 20, "replay_value": 1.1, "price_tolerance": 1.1},
    "Role-Playing": {"expected_hours": 50, "replay_value": 1.5, "price_tolerance": 1.3},
    "Strategy": {"expected_hours": 30, "replay_value": 1.8, "price_tolerance": 1.2},
    "Simulation": {"expected_hours": 40, "replay_value": 1.6, "price_tolerance": 1.1},
    "Sports": {"expected_hours": 25, "replay_value": 1.4, "price_tolerance": 0.9},
    "Racing": {"expected_hours": 20, "replay_value": 1.3, "price_tolerance": 0.9},
    "Puzzle": {"expected_hours": 10, "replay_value": 1.0, "price_tolerance": 0.8},
    "Platformer": {"expected_hours": 12, "replay_value": 1.2, "price_tolerance": 0.9},
    "Fighting": {"expected_hours": 15, "replay_value": 1.7, "price_tolerance": 1.0},
    "Shooter": {"expected_hours": 12, "replay_value": 1.5, "price_tolerance": 1.0},
    "Metroidvania": {"expected_hours": 25, "replay_value": 1.4, "price_tolerance": 1.0},
    "Indie": {"expected_hours": 8, "replay_value": 1.1, "price_tolerance": 0.7},
}

# Developer reputation multipliers
DEVELOPER_REPUTATION = {
    "Nintendo": 1.3,
    "Team Cherry": 1.2,
    "Supergiant Games": 1.2,
    "CD Projekt RED": 1.1,
    "FromSoftware": 1.3,
    "Naughty Dog": 1.2,
    "Rockstar Games": 1.1,
    "Valve": 1.2,
    "Indie": 0.9,  # Generic indie multiplier
}

def calculate_genre_value_score(
    current_price: Optional[float], 
    genres: List[str], 
    metacritic: Optional[float],
    developer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Oblicza wartość za pieniądze uwzględniając specyfikę gatunków.
    
    Args:
        current_price: Aktualna cena gry
        genres: Lista gatunków gry
        metacritic: Ocena Metacritic
        developer: Deweloper gry
        
    Returns:
        Dict: Szczegółowa analiza wartości według gatunku
    """
    if not current_price or not genres or not metacritic:
        return {"error": "Insufficient data for genre-based value analysis"}
    
    # Znajdź profil gatunku (użyj pierwszego rozpoznanego)
    genre_profile = None
    primary_genre = None
    
    for genre in genres:
        if genre in GENRE_VALUE_PROFILES:
            genre_profile = GENRE_VALUE_PROFILES[genre]
            primary_genre = genre
            break
    
    # Fallback do Action jeśli nie znaleziono
    if not genre_profile:
        genre_profile = GENRE_VALUE_PROFILES["Action"]
        primary_genre = "Action"
    
    # Podstawowy score per dollar
    base_value = metacritic / current_price
    
    # Zastosuj modyfikatory gatunku
    expected_hours = genre_profile["expected_hours"]
    replay_value = genre_profile["replay_value"]
    price_tolerance = genre_profile["price_tolerance"]
    
    # Oblicz oczekiwaną wartość za godzinę
    expected_value_per_hour = metacritic / expected_hours
    actual_cost_per_hour = current_price / expected_hours
    
    # Score uwzględniający gatunek
    genre_adjusted_value = base_value * replay_value * price_tolerance
    
    # Modyfikator dewelopera
    dev_multiplier = 1.0
    if developer:
        dev_multiplier = DEVELOPER_REPUTATION.get(developer, 1.0)
        # Sprawdź czy to indie studio
        if developer not in DEVELOPER_REPUTATION and current_price < 50:
            dev_multiplier = DEVELOPER_REPUTATION["Indie"]
    
    final_value_score = genre_adjusted_value * dev_multiplier
    
    return {
        "primary_genre": primary_genre,
        "base_value_score": round(base_value, 2),
        "genre_adjusted_score": round(genre_adjusted_value, 2),
        "final_value_score": round(final_value_score, 2),
        "expected_hours": expected_hours,
        "cost_per_hour": round(actual_cost_per_hour, 2),
        "value_per_hour": round(expected_value_per_hour, 2),
        "developer_multiplier": dev_multiplier,
        "genre_factors": {
            "replay_value": replay_value,
            "price_tolerance": price_tolerance,
        }
    }

def calculate_age_factor(release_dates: Dict[str, Any]) -> float:
    """
    Oblicza współczynnik wieku gry wpływający na wartość.
    
    Args:
        release_dates: Słownik z datami wydania gry
        
    Returns:
        float: Współczynnik wieku (1.0 = nowa gra, < 1.0 = stara gra)
    """
    if not release_dates:
        return 1.0
    
    # Spróbuj znaleźć najwcześniejszą datę wydania
    earliest_date = None
    current_year = datetime.now().year
    
    # Sprawdź różne możliwe formaty dat
    for platform, date_str in release_dates.items():
        if isinstance(date_str, str) and date_str:
            # Wyciągnij rok z daty
            year_match = re.search(r'\b(20\d{2})\b', date_str)
            if year_match:
                year = int(year_match.group(1))
                if not earliest_date or year < earliest_date:
                    earliest_date = year
    
    if not earliest_date:
        return 1.0
    
    # Oblicz wiek gry w latach
    game_age = current_year - earliest_date
    
    # Współczynnik wieku - nowe gry (0-1 rok) = 1.0, starsze maleją
    if game_age <= 1:
        return 1.0
    elif game_age <= 3:
        return 0.95  # Prawie nowe
    elif game_age <= 5:
        return 0.90  # Kilka lat
    elif game_age <= 10:
        return 0.85  # Starsze, ale nie retro
    else:
        return 0.80  # Stare/retro gry

def calculate_market_position_score(
    current_price: Optional[float],
    msrp: Optional[float], 
    metacritic: Optional[float]
) -> Dict[str, Any]:
    """
    Ocenia pozycję gry na rynku pod względem ceny i jakości.
    
    Args:
        current_price: Aktualna cena
        msrp: MSRP
        metacritic: Ocena Metacritic
        
    Returns:
        Dict: Analiza pozycji rynkowej
    """
    if not all([current_price, metacritic]):
        return {"error": "Insufficient data for market position analysis"}
    
    # Określ kategorię cenową
    price_category = "Unknown"
    if current_price and current_price <= 20:
        price_category = "Budget"
    elif current_price and current_price <= 40:
        price_category = "Mid-tier"
    elif current_price and current_price <= 70:
        price_category = "Premium"
    elif current_price:
        price_category = "AAA"
    
    # Określ kategorię jakości
    quality_category = "Unknown"
    if metacritic and metacritic >= 90:
        quality_category = "Exceptional"
    elif metacritic and metacritic >= 80:
        quality_category = "Great"
    elif metacritic and metacritic >= 70:
        quality_category = "Good"
    elif metacritic and metacritic >= 60:
        quality_category = "Average"
    elif metacritic:
        quality_category = "Poor"
    
    # Macierz pozycji rynkowej (quality vs price)
    market_position_matrix = {
        ("Exceptional", "Budget"): "Hidden Gem",
        ("Exceptional", "Mid-tier"): "Excellent Value",
        ("Exceptional", "Premium"): "Premium Quality",
        ("Exceptional", "AAA"): "Flagship Title",
        
        ("Great", "Budget"): "Great Deal",
        ("Great", "Mid-tier"): "Solid Choice",
        ("Great", "Premium"): "Worth Considering",
        ("Great", "AAA"): "Expensive",
        
        ("Good", "Budget"): "Good Value",
        ("Good", "Mid-tier"): "Fair Price",
        ("Good", "Premium"): "Overpriced",
        ("Good", "AAA"): "Poor Value",
        
        ("Average", "Budget"): "Budget Option",
        ("Average", "Mid-tier"): "Questionable",
        ("Average", "Premium"): "Avoid",
        ("Average", "AAA"): "Terrible Deal",
        
        ("Poor", "Budget"): "Still Overpriced",
        ("Poor", "Mid-tier"): "Waste of Money",
        ("Poor", "Premium"): "Avoid at All Costs",
        ("Poor", "AAA"): "Scam",
    }
    
    market_position = market_position_matrix.get(
        (quality_category, price_category), 
        "Unknown Position"
    )
    
    # Score pozycji (im lepszy positioning, tym wyższy score)
    position_scores = {
        "Hidden Gem": 10.0,
        "Excellent Value": 9.0,
        "Great Deal": 8.5,
        "Premium Quality": 8.0,
        "Solid Choice": 7.5,
        "Good Value": 7.0,
        "Worth Considering": 6.5,
        "Fair Price": 6.0,
        "Flagship Title": 5.5,
        "Budget Option": 5.0,
        "Expensive": 4.0,
        "Questionable": 3.5,
        "Overpriced": 3.0,
        "Poor Value": 2.0,
        "Avoid": 1.5,
        "Waste of Money": 1.0,
        "Still Overpriced": 0.8,
        "Avoid at All Costs": 0.5,
        "Terrible Deal": 0.3,
        "Scam": 0.1,
    }
    
    position_score = position_scores.get(market_position, 5.0)
    
    return {
        "price_category": price_category,
        "quality_category": quality_category,
        "market_position": market_position,
        "position_score": position_score,
        "value_tier": _determine_value_tier(position_score)
    }

def _determine_value_tier(position_score: float) -> str:
    """Określa tier wartości na podstawie score pozycji."""
    if position_score >= 8.0:
        return "S-Tier Value"
    elif position_score >= 7.0:
        return "A-Tier Value"
    elif position_score >= 5.5:
        return "B-Tier Value"
    elif position_score >= 3.0:
        return "C-Tier Value"
    else:
        return "D-Tier Value"

def calculate_comprehensive_value_analysis(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Przeprowadza kompleksową analizę wartości używając wszystkich zaawansowanych algorytmów.
    
    Args:
        game_data: Kompletne dane o grze
        
    Returns:
        Dict: Pełna zaawansowana analiza wartości
    """
    try:
        # Extract podstawowych danych
        current_price = extract_price(game_data.get("current_eshop_price", "N/A"))
        msrp = extract_price(game_data.get("MSRP", "N/A"))
        metacritic = extract_score(game_data.get("metacritic_score", "0"))
        opencritic = extract_score(game_data.get("opencritic_score", "0"))
        
        genres = game_data.get("genres", [])
        developer = game_data.get("developer", "Unknown")
        release_dates = game_data.get("release_dates_parsed", {})
        
        # Użyj lepszej oceny (Metacritic lub OpenCritic)
        best_score = max(metacritic or 0, opencritic or 0)
        
        if not current_price or not best_score:
            return {"error": "Insufficient data for comprehensive analysis"}
        
        # Analizy
        genre_analysis = calculate_genre_value_score(
            current_price, genres, best_score, developer
        )
        
        market_analysis = calculate_market_position_score(
            current_price, msrp, best_score
        )
        
        age_factor = calculate_age_factor(release_dates)
        
        # Skomponuj final score
        base_score = genre_analysis.get("final_value_score", 0)
        position_score = market_analysis.get("position_score", 5.0)
        
        # Ważona średnia różnych score
        comprehensive_score = (
            base_score * 0.4 +           # 40% - genre-adjusted value
            position_score * 0.4 +       # 40% - market position
            (age_factor * 10) * 0.2      # 20% - age factor
        )
        
        # Rekomendacja na podstawie comprehensive score
        recommendation = _generate_advanced_recommendation(comprehensive_score, market_analysis)
        
        return {
            "success": True,
            "comprehensive_score": round(comprehensive_score, 2),
            "genre_analysis": genre_analysis,
            "market_analysis": market_analysis,
            "age_factor": round(age_factor, 2),
            "advanced_recommendation": recommendation,
            "value_breakdown": {
                "genre_contribution": round(base_score * 0.4, 2),
                "market_contribution": round(position_score * 0.4, 2), 
                "age_contribution": round((age_factor * 10) * 0.2, 2),
            },
            "analysis_summary": _generate_comprehensive_summary(
                comprehensive_score, market_analysis, genre_analysis, age_factor
            )
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive value analysis: {e}")
        return {"error": str(e), "analysis": "incomplete"}

def _generate_advanced_recommendation(
    comprehensive_score: float, 
    market_analysis: Dict[str, Any]
) -> str:
    """Generuje zaawansowaną rekomendację na podstawie comprehensive score."""
    market_position = market_analysis.get("market_position", "Unknown")
    
    # Uwzględnij zarówno score jak i market position
    if comprehensive_score >= 8.0 and "Gem" in market_position:
        return "INSTANT BUY - Hidden Gem!"
    elif comprehensive_score >= 7.5:
        return "STRONG BUY"
    elif comprehensive_score >= 6.5:
        return "BUY"
    elif comprehensive_score >= 5.5:
        return "CONSIDER"
    elif comprehensive_score >= 4.0:
        return "WAIT FOR SALE"
    else:
        return "SKIP"

def _generate_comprehensive_summary(
    score: float, 
    market_analysis: Dict[str, Any], 
    genre_analysis: Dict[str, Any], 
    age_factor: float
) -> str:
    """Generuje tekstowe podsumowanie comprehensive analysis."""
    market_position = market_analysis.get("market_position", "Unknown")
    value_tier = market_analysis.get("value_tier", "Unknown")
    primary_genre = genre_analysis.get("primary_genre", "Unknown")
    cost_per_hour = genre_analysis.get("cost_per_hour", 0)
    
    summary_parts = [
        f"🎯 {market_position}",
        f"🏆 {value_tier}", 
        f"🎮 {primary_genre} game",
        f"💰 ~{cost_per_hour:.1f} per expected hour",
    ]
    
    if age_factor < 0.9:
        years_old = int((1.0 - age_factor) / 0.05 * 2)  # Rough estimate
        summary_parts.append(f"📅 ~{years_old}+ years old")
    
    return " | ".join(summary_parts) 
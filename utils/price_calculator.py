"""
Price Calculator Utilities for AutoGen DekuDeals Analysis
Narzędzia kalkulacji cen i analizy wartości dla AutoGen
"""

import re
import logging
from typing import Optional, Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_price(price_text: Optional[str]) -> Optional[float]:
    """
    Wyciąga numeryczną wartość ceny z tekstu.
    
    Args:
        price_text (Optional[str]): Tekst zawierający cenę (np. "53,99 zł", "$19.99")
        
    Returns:
        Optional[float]: Wartość numeryczna ceny lub None jeśli nie można wyciągnąć
    """
    if not price_text or price_text in ["N/A", "Brak danych", "Unknown"]:
        return None
    
    # Remove leading colons and whitespace
    clean_text = str(price_text).lstrip(":").strip()
    
    # Try to extract number with various formats
    # Polish format: "53,99 zł" -> 53.99
    # US format: "$19.99" -> 19.99
    # Simple format: "20.50" -> 20.50
    
    price_patterns = [
        r"([\d,]+\.?\d*)\s*zł",  # Polish: "53,99 zł"
        r"\$([\d,]+\.?\d*)",      # US: "$19.99"
        r"([\d,]+\.?\d*)",        # Simple: "19.99" or "53,99"
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, clean_text)
        if match:
            price_str = match.group(1)
            try:
                # Handle both comma and dot as decimal separators
                if "," in price_str and "." not in price_str:
                    # Polish format: "53,99" -> 53.99
                    price_str = price_str.replace(",", ".")
                elif "," in price_str and "." in price_str:
                    # Format like "1,234.56" - remove comma thousands separator
                    price_str = price_str.replace(",", "")
                
                return float(price_str)
            except ValueError:
                continue
    
    logger.warning(f"Could not extract price from: {price_text}")
    return None

def extract_score(score_text: Optional[str]) -> Optional[float]:
    """
    Wyciąga numeryczną wartość oceny z tekstu.
    
    Args:
        score_text (Optional[str]): Tekst zawierający ocenę (np. "92", "8.7")
        
    Returns:
        Optional[float]: Wartość numeryczna oceny lub None jeśli nie można wyciągnąć
    """
    if not score_text or score_text in ["Brak oceny", "No score", "N/A", "Unknown"]:
        return None
    
    # Clean the text
    clean_text = str(score_text).strip()
    
    # Try to extract score
    score_patterns = [
        r"(\d+\.?\d*)",  # Simple number: "92" or "8.7"
        r"(\d+,\d+)",    # Polish decimal: "8,7"
    ]
    
    for pattern in score_patterns:
        match = re.search(pattern, clean_text)
        if match:
            score_str = match.group(1)
            try:
                # Handle comma as decimal separator
                if "," in score_str:
                    score_str = score_str.replace(",", ".")
                
                score = float(score_str)
                
                # Normalize score to 0-100 scale if needed
                if score <= 10:  # Assume 0-10 scale, convert to 0-100
                    score = score * 10
                
                return min(100.0, max(0.0, score))  # Clamp between 0-100
            except ValueError:
                continue
    
    logger.warning(f"Could not extract score from: {score_text}")
    return None

def calculate_discount_percentage(current_price: Optional[float], msrp: Optional[float]) -> Optional[float]:
    """
    Oblicza procent zniżki względem MSRP.
    
    Args:
        current_price (Optional[float]): Aktualna cena
        msrp (Optional[float]): Cena sugerowana (MSRP)
        
    Returns:
        Optional[float]: Procent zniżki (pozytywny = zniżka, negatywny = podwyżka)
    """
    if current_price is None or msrp is None or msrp <= 0:
        return None
    
    discount = ((msrp - current_price) / msrp) * 100
    return round(discount, 2)

def calculate_price_difference(current_price: Optional[float], lowest_price: Optional[float]) -> Optional[float]:
    """
    Oblicza różnicę między aktualną ceną a najniższą historyczną.
    
    Args:
        current_price (Optional[float]): Aktualna cena
        lowest_price (Optional[float]): Najniższa historyczna cena
        
    Returns:
        Optional[float]: Różnica w walucie (pozytywna = drożej niż najniższa)
    """
    if current_price is None or lowest_price is None:
        return None
    
    difference = current_price - lowest_price
    return round(difference, 2)

def calculate_value_ratio(current_price: Optional[float], metacritic: Optional[float], opencritic: Optional[float]) -> Optional[float]:
    """
    Oblicza obiektywny wskaźnik wartości za pieniądze.
    
    Formuła: (średnia_ocen / cena) * 100
    
    Args:
        current_price (Optional[float]): Aktualna cena
        metacritic (Optional[float]): Ocena Metacritic (0-100)
        opencritic (Optional[float]): Ocena OpenCritic (0-100)
        
    Returns:
        Optional[float]: Wskaźnik wartości (wyższy = lepsza wartość)
    """
    if current_price is None or current_price <= 0:
        return None
    
    # Calculate average score
    scores = [score for score in [metacritic, opencritic] if score is not None]
    if not scores:
        return None
    
    average_score = sum(scores) / len(scores)
    
    # Calculate value ratio (score per unit price)
    value_ratio = (average_score / current_price) * 10  # Scale by 10 for readability
    
    return round(value_ratio, 2)

def assess_buy_timing(current_price: Optional[float], lowest_price: Optional[float]) -> str:
    """
    Ocenia timing zakupu na podstawie różnicy cen.
    
    Args:
        current_price (Optional[float]): Aktualna cena
        lowest_price (Optional[float]): Najniższa historyczna cena
        
    Returns:
        str: Rekomendacja timing ("EXCELLENT", "GOOD", "FAIR", "POOR", "WAIT")
    """
    if current_price is None or lowest_price is None:
        return "UNKNOWN"
    
    if current_price <= 0 or lowest_price <= 0:
        return "UNKNOWN"
    
    # Calculate how much more expensive current price is vs lowest
    price_multiplier = current_price / lowest_price
    
    if price_multiplier <= 1.0:
        return "EXCELLENT"  # At or below historical low
    elif price_multiplier <= 1.15:
        return "GOOD"       # Within 15% of historical low
    elif price_multiplier <= 1.35:
        return "FAIR"       # Within 35% of historical low
    elif price_multiplier <= 1.75:
        return "POOR"       # Within 75% of historical low
    else:
        return "WAIT"       # More than 75% above historical low

def generate_price_recommendation(
    current_price: Optional[float], 
    msrp: Optional[float], 
    lowest_price: Optional[float], 
    metacritic: Optional[float]
) -> str:
    """
    Generuje rekomendację zakupu na podstawie analizy cen i ocen.
    
    Args:
        current_price (Optional[float]): Aktualna cena
        msrp (Optional[float]): MSRP
        lowest_price (Optional[float]): Najniższa historyczna cena
        metacritic (Optional[float]): Ocena Metacritic
        
    Returns:
        str: Rekomendacja ("STRONG BUY", "BUY", "HOLD", "WAIT", "SKIP")
    """
    if current_price is None:
        return "INSUFFICIENT DATA"
    
    # Initialize scoring factors
    score_factor = 0
    price_factor = 0
    timing_factor = 0
    
    # Score factor (based on Metacritic)
    if metacritic is not None:
        if metacritic >= 90:
            score_factor = 3  # Excellent
        elif metacritic >= 80:
            score_factor = 2  # Good
        elif metacritic >= 70:
            score_factor = 1  # Decent
        elif metacritic >= 60:
            score_factor = 0  # Mediocre
        else:
            score_factor = -2  # Poor
    
    # Price factor (based on discount from MSRP)
    if msrp is not None and msrp > 0:
        discount = calculate_discount_percentage(current_price, msrp)
        if discount is not None:
            if discount >= 50:
                price_factor = 3    # Deep discount
            elif discount >= 30:
                price_factor = 2    # Good discount
            elif discount >= 10:
                price_factor = 1    # Some discount
            elif discount >= 0:
                price_factor = 0    # No discount
            else:
                price_factor = -1   # Price increase
    
    # Timing factor (based on historical low)
    timing = assess_buy_timing(current_price, lowest_price)
    timing_scores = {
        "EXCELLENT": 3,
        "GOOD": 2,
        "FAIR": 1,
        "POOR": 0,
        "WAIT": -2,
        "UNKNOWN": 0
    }
    timing_factor = timing_scores.get(timing, 0)
    
    # Calculate total recommendation score
    total_score = score_factor + price_factor + timing_factor
    
    # Generate recommendation
    if total_score >= 7:
        return "STRONG BUY"
    elif total_score >= 4:
        return "BUY"
    elif total_score >= 1:
        return "HOLD"
    elif total_score >= -2:
        return "WAIT"
    else:
        return "SKIP"

def get_price_analysis_summary(
    current_price: Optional[float],
    msrp: Optional[float], 
    lowest_price: Optional[float],
    metacritic: Optional[float],
    opencritic: Optional[float]
) -> Dict[str, Any]:
    """
    Tworzy kompletne podsumowanie analizy cenowej.
    
    Args:
        current_price: Aktualna cena
        msrp: MSRP
        lowest_price: Najniższa historyczna cena
        metacritic: Ocena Metacritic
        opencritic: Ocena OpenCritic
        
    Returns:
        Dict: Kompletne podsumowanie analizy
    """
    return {
        "price_data": {
            "current_price": current_price,
            "msrp": msrp,
            "lowest_historical": lowest_price,
            "discount_vs_msrp": calculate_discount_percentage(current_price, msrp),
            "difference_vs_lowest": calculate_price_difference(current_price, lowest_price),
        },
        "score_data": {
            "metacritic": metacritic,
            "opencritic": opencritic,
            "average_score": (metacritic + opencritic) / 2 if metacritic and opencritic else (metacritic or opencritic),
        },
        "value_analysis": {
            "value_ratio": calculate_value_ratio(current_price, metacritic, opencritic),
            "buy_timing": assess_buy_timing(current_price, lowest_price),
            "recommendation": generate_price_recommendation(current_price, msrp, lowest_price, metacritic),
        }
    } 